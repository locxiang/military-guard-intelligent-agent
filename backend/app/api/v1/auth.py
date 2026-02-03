"""
认证相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_active_user
from app.core.audit import AuditLogger
from app.models.user import User
from app.utils.encryption import RSAKeyManager

router = APIRouter()

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 初始化 RSA 密钥（如果不存在则生成）
RSAKeyManager.load_keys()


# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str  # 可以是明文或 RSA 加密的密码（Base64 编码）
    encrypted: bool = False  # 标识密码是否已加密


class TokenResponse(BaseModel):
    """Token响应"""
    errorCode: int = 0
    message: str = "success"
    data: dict


class UserInfo(BaseModel):
    """用户信息"""
    id: int
    username: str
    real_name: Optional[str] = None
    department: Optional[str] = None
    role: str


class LoginResponse(BaseModel):
    """登录响应"""
    errorCode: int = 0
    message: str = "success"
    data: dict


class PublicKeyResponse(BaseModel):
    """公钥响应"""
    errorCode: int = 0
    message: str = "success"
    data: dict


@router.get(
    "/public-key",
    summary="获取 RSA 公钥",
    description="获取用于加密密码的 RSA 公钥",
    response_model=PublicKeyResponse,
    tags=["认证"]
)
async def get_public_key():
    """
    获取 RSA 公钥接口
    
    前端在登录前调用此接口获取公钥，用于加密密码
    """
    try:
        public_key_info = RSAKeyManager.get_public_key_for_frontend()
        return {
            "errorCode": 0,
            "message": "success",
            "data": public_key_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取公钥失败: {str(e)}"
        )


@router.post(
    "/login",
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT Token。密码可以是明文或 RSA 加密的",
    response_model=LoginResponse,
    tags=["认证"]
)
async def login(request: LoginRequest, req: Request, db: AsyncSession = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码（明文或 RSA 加密的 Base64 字符串）
    - **encrypted**: 是否已加密（默认 false，为兼容性保留）
    
    返回 JWT Token，用于后续接口认证
    """
    client_ip = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")

    # 1. 解密密码（如果已加密）
    password = request.password
    if request.encrypted:
        try:
            password = RSAKeyManager.decrypt_password(request.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码解密失败: {str(e)}"
            )
    else:
        # 兼容旧版本：如果没有加密标识，尝试检测是否为 Base64 编码的加密数据
        # 如果解密成功，说明是加密的；否则当作明文处理
        try:
            # 尝试解密（如果失败会抛出异常）
            decrypted = RSAKeyManager.decrypt_password(request.password)
            # 如果解密成功，使用解密后的密码
            password = decrypted
        except (ValueError, Exception):
            # 解密失败，当作明文密码处理
            password = request.password
    
    # 2. 从数据库查询用户
    result = await db.execute(
        select(User).filter(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    # 3. 验证用户是否存在
    if user is None:
        await AuditLogger.log_login(db, request.username, "failure", client_ip, user_agent, error_message="用户名或密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 4. 验证用户状态
    if user.status != 1:
        await AuditLogger.log_login(db, request.username, "failure", client_ip, user_agent, user_id=user.id, error_message="用户已被禁用")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 5. 验证密码
    if not verify_password(password, user.password_hash):
        await AuditLogger.log_login(db, request.username, "failure", client_ip, user_agent, user_id=user.id, error_message="用户名或密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 6. 生成 JWT Token
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    token = create_access_token(token_data)

    # 记录登录成功审计日志
    await AuditLogger.log_login(db, user.username, "success", client_ip, user_agent, user_id=user.id)

    # 7. 返回 Token 和用户信息
    return {
        "errorCode": 0,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "realName": user.real_name or "用户",
                "role": user.role
            }
        }
    }


@router.post(
    "/logout",
    summary="用户登出",
    description="用户登出，使 Token 失效",
    tags=["认证"]
)
async def logout(
    req: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    用户登出接口
    
    需要提供有效的 JWT Token
    """
    client_ip = req.client.host if req.client else None
    await AuditLogger.log_logout(db, current_user.id, current_user.username, client_ip=client_ip)
    return {
        "errorCode": 0,
        "message": "登出成功",
        "data": {}
    }


@router.post(
    "/refresh",
    summary="刷新Token",
    description="使用旧 Token 刷新获取新 Token",
    tags=["认证"]
)
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    刷新 Token 接口
    
    使用当前有效的 Token 获取新的 Token
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的 Token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 已过期或无效")
    
    # 生成新 Token
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token_data = {
        "sub": username,
        "exp": expire,
        "user_id": payload.get("user_id", 1)
    }
    new_token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "errorCode": 0,
        "message": "Token 刷新成功",
        "data": {
            "token": new_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60
        }
    }


@router.get(
    "/me",
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
    tags=["认证"]
)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户信息
    
    需要提供有效的 JWT Token
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的 Token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 已过期或无效")
    
    # TODO: 从数据库获取用户信息
    return {
        "errorCode": 0,
        "message": "success",
        "data": {
            "id": 1,
            "username": username,
            "real_name": "管理员",
            "department": "海军保卫局",
            "role": "admin"
        }
    }
