"""
用户管理相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from datetime import datetime

from app.core.database import get_db
from app.core.response import ResponseModel
from app.core.security import get_current_active_user, require_admin, get_password_hash
from app.models.user import User
from app.utils.encryption import RSAKeyManager

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# 请求模型
class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., description="密码（可以是明文或 RSA 加密的）")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    role: str = Field("user", description="角色: admin/user")
    encrypted: bool = Field(False, description="密码是否已加密")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    role: Optional[str] = Field(None, description="角色: admin/user")
    status: Optional[int] = Field(None, description="状态: 1-启用, 0-禁用")


class UserPasswordResetRequest(BaseModel):
    """重置密码请求"""
    password: str = Field(..., description="新密码（可以是明文或 RSA 加密的）")
    encrypted: bool = Field(False, description="密码是否已加密")


class UserStatusRequest(BaseModel):
    """用户状态请求"""
    status: int = Field(..., description="状态: 1-启用, 0-禁用")


# 响应模型
class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    real_name: Optional[str]
    department: Optional[str]
    role: str
    status: int
    created_at: datetime
    updated_at: datetime


@router.get(
    "/list",
    summary="获取用户列表",
    description="分页查询用户列表，支持关键词搜索、角色筛选、状态筛选",
    tags=["用户管理"]
)
async def get_user_list(
    keyword: Optional[str] = Query(None, description="关键词（用户名、真实姓名、部门）"),
    role: Optional[str] = Query(None, description="角色筛选: admin/user"),
    user_status: Optional[int] = Query(None, alias="status", description="状态筛选: 1-启用, 0-禁用"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    获取用户列表接口
    
    需要管理员权限
    """
    try:
        # 构建查询条件
        conditions = []
        
        if keyword:
            conditions.append(
                or_(
                    User.username.like(f"%{keyword}%"),
                    User.real_name.like(f"%{keyword}%"),
                    User.department.like(f"%{keyword}%")
                )
            )
        
        if role:
            conditions.append(User.role == role)
        
        if user_status is not None:
            conditions.append(User.status == user_status)
        
        # 查询总数
        count_query = select(func.count(User.id))
        if conditions:
            count_query = count_query.where(*conditions)
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 查询列表
        query = select(User).order_by(User.created_at.desc())
        if conditions:
            query = query.where(*conditions)
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        # 转换为响应格式
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "department": user.department,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            for user in users
        ]
        
        return ResponseModel.paginated(
            items=user_list,
            total=total,
            page=page,
            page_size=page_size,
            message="获取用户列表成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get(
    "/{user_id}",
    summary="获取用户详情",
    description="根据用户ID获取用户详细信息",
    tags=["用户管理"]
)
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取用户详情接口"""
    try:
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return ResponseModel.success(
            data={
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "department": user.department,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            },
            message="获取用户详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )


@router.post(
    "",
    summary="创建用户",
    description="创建新用户",
    tags=["用户管理"]
)
async def create_user(
    request: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """创建用户接口"""
    try:
        # 检查用户名是否已存在
        existing_user = await db.execute(
            select(User).filter(User.username == request.username)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 验证角色
        if request.role not in ["admin", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色必须是 admin 或 user"
            )
        
        # 解密密码（如果已加密）
        password = request.password
        if request.encrypted:
            try:
                password = RSAKeyManager.decrypt_password(request.password)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"密码解密失败: {str(e)}"
                )
        
        # 创建用户
        password_hash = get_password_hash(password)
        new_user = User(
            username=request.username,
            password_hash=password_hash,
            real_name=request.real_name,
            department=request.department,
            role=request.role,
            status=1
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return ResponseModel.success(
            data={
                "id": new_user.id,
                "username": new_user.username,
                "real_name": new_user.real_name,
                "department": new_user.department,
                "role": new_user.role,
                "status": new_user.status,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None
            },
            message="创建用户成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.put(
    "/{user_id}",
    summary="更新用户",
    description="更新用户信息",
    tags=["用户管理"]
)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户接口"""
    try:
        # 查询用户
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不能禁用自己
        if user_id == current_user.id and request.status == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己"
            )
        
        # 不能修改自己的角色
        if user_id == current_user.id and request.role and request.role != user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能修改自己的角色"
            )
        
        # 验证角色
        if request.role and request.role not in ["admin", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色必须是 admin 或 user"
            )
        
        # 更新字段
        if request.real_name is not None:
            user.real_name = request.real_name
        if request.department is not None:
            user.department = request.department
        if request.role is not None:
            user.role = request.role
        if request.status is not None:
            user.status = request.status
        
        await db.commit()
        await db.refresh(user)
        
        return ResponseModel.success(
            data={
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "department": user.department,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            },
            message="更新用户成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    summary="删除用户",
    description="删除用户（软删除，将状态设为禁用）",
    tags=["用户管理"]
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除用户接口"""
    try:
        # 不能删除自己
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己"
            )
        
        # 查询用户
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 软删除：将状态设为禁用
        user.status = 0
        await db.commit()
        
        return ResponseModel.success(
            data={},
            message="删除用户成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )


@router.put(
    "/{user_id}/status",
    summary="启用/禁用用户",
    description="修改用户状态",
    tags=["用户管理"]
)
async def update_user_status(
    user_id: int,
    request: UserStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """启用/禁用用户接口"""
    try:
        # 不能禁用自己
        if user_id == current_user.id and request.status == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己"
            )
        
        # 查询用户
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.status = request.status
        await db.commit()
        await db.refresh(user)
        
        return ResponseModel.success(
            data={
                "id": user.id,
                "status": user.status
            },
            message="更新用户状态成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户状态失败: {str(e)}"
        )


@router.put(
    "/{user_id}/password",
    summary="重置密码",
    description="重置用户密码",
    tags=["用户管理"]
)
async def reset_user_password(
    user_id: int,
    request: UserPasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """重置用户密码接口"""
    try:
        # 查询用户
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 解密密码（如果已加密）
        password = request.password
        if request.encrypted:
            try:
                password = RSAKeyManager.decrypt_password(request.password)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"密码解密失败: {str(e)}"
                )
        
        # 更新密码
        user.password_hash = get_password_hash(password)
        await db.commit()
        
        return ResponseModel.success(
            data={},
            message="重置密码成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置密码失败: {str(e)}"
        )
