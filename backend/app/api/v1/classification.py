"""
智能分类相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case

from app.core.database import get_db
from app.models.archive import CaseFile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.get(
    "/pending",
    summary="获取待确认分类的案卷列表",
    description="获取需要人工确认分类的案卷",
    tags=["智能分类"]
)
async def get_pending_classifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取待确认分类的案卷列表"""
    try:
        # 查询有分类但置信度较低的案卷（这里简化处理，实际应该有置信度字段）
        # 或者查询分类不完整的案卷
        conditions = [
            CaseFile.status == "completed",
            or_(
                CaseFile.classification_level1.is_(None),
                and_(
                    CaseFile.classification_level1.isnot(None),
                    CaseFile.classification_level2.is_(None)
                )
            )
        ]
        
        count_query = select(func.count()).select_from(CaseFile).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = select(CaseFile).where(and_(*conditions))
        query = query.order_by(CaseFile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        case_files = result.scalars().all()
        
        case_file_list = []
        for case_file in case_files:
            # 模拟置信度（实际应该从分类算法结果中获取）
            confidence = 75 if case_file.classification_level1 else 0
            
            case_file_dict = {
                "id": case_file.id,
                "caseNo": case_file.case_no,
                "caseName": case_file.case_name or "",
                "title": case_file.title or "",
                "autoClassification": {
                    "level1": case_file.classification_level1,
                    "level2": case_file.classification_level2,
                    "level3": case_file.classification_level3
                },
                "manualClassification": None,
                "confidence": confidence,
                "metadata": case_file.meta_data or {}  # API返回时仍使用metadata字段名
            }
            case_file_list.append(case_file_dict)
        
        return {
            "errorCode": 0,
            "message": "success",
            "data": case_file_list,
            "page": {
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tree",
    summary="获取分类树",
    description="获取案卷分类体系树形结构",
    tags=["智能分类"]
)
async def get_classification_tree(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取分类树"""
    try:
        # 查询所有有分类的案卷，统计每个分类的数量
        query = select(
            CaseFile.classification_level1,
            CaseFile.classification_level2,
            CaseFile.classification_level3,
            func.count(CaseFile.id).label('count')
        ).where(
            CaseFile.classification_level1.isnot(None),
            CaseFile.status == "completed"
        ).group_by(
            CaseFile.classification_level1,
            CaseFile.classification_level2,
            CaseFile.classification_level3
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        # 构建分类树
        tree_dict = {}
        for row in rows:
            level1 = row.classification_level1
            level2 = row.classification_level2
            level3 = row.classification_level3
            count = row.count
            
            if level1 not in tree_dict:
                tree_dict[level1] = {
                    "id": f"l1_{level1}",
                    "name": level1,
                    "count": 0,
                    "children": {}
                }
            
            tree_dict[level1]["count"] += count
            
            if level2:
                if level2 not in tree_dict[level1]["children"]:
                    tree_dict[level1]["children"][level2] = {
                        "id": f"l2_{level1}_{level2}",
                        "name": level2,
                        "count": 0,
                        "children": []
                    }
                tree_dict[level1]["children"][level2]["count"] += count
                
                if level3:
                    tree_dict[level1]["children"][level2]["children"].append({
                        "id": f"l3_{level1}_{level2}_{level3}",
                        "name": level3,
                        "count": count
                    })
        
        # 转换为前端需要的格式
        tree_list = []
        for level1, level1_data in tree_dict.items():
            children = []
            for level2, level2_data in level1_data["children"].items():
                children.append(level2_data)
            
            tree_list.append({
                "id": level1_data["id"],
                "name": level1_data["name"],
                "count": level1_data["count"],
                "children": children
            })
        
        return {
            "errorCode": 0,
            "message": "success",
            "data": tree_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/confirm/{case_file_id}",
    summary="确认分类",
    description="确认案卷的分类，支持手动修改分类",
    tags=["智能分类"]
)
async def confirm_classification(
    case_file_id: int,
    classification: dict = Body(..., description="分类信息 {level1, level2, level3}"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """确认案卷分类"""
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        
        # 更新分类
        case_file.classification_level1 = classification.get("level1")
        case_file.classification_level2 = classification.get("level2")
        case_file.classification_level3 = classification.get("level3")
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": "分类已确认",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/batch-confirm",
    summary="批量确认分类",
    description="批量确认多个案卷的分类",
    tags=["智能分类"]
)
async def batch_confirm_classification(
    case_file_ids: List[int] = Body(..., description="案卷ID列表"),
    classification: dict = Body(..., description="分类信息 {level1, level2, level3}"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """批量确认分类"""
    try:
        query = select(CaseFile).where(CaseFile.id.in_(case_file_ids))
        result = await db.execute(query)
        case_files = result.scalars().all()
        
        updated_count = 0
        for case_file in case_files:
            case_file.classification_level1 = classification.get("level1")
            case_file.classification_level2 = classification.get("level2")
            case_file.classification_level3 = classification.get("level3")
            updated_count += 1
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": f"成功确认{updated_count}个案卷的分类",
            "data": {"count": updated_count}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/case-files/{classification_id}",
    summary="获取指定分类下的案卷",
    description="根据分类ID获取该分类下的所有案卷",
    tags=["智能分类"]
)
async def get_case_files_by_classification(
    classification_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """根据分类获取案卷列表"""
    try:
        # 解析分类ID（格式：l1_xxx, l2_xxx_xxx, l3_xxx_xxx_xxx）
        parts = classification_id.split("_")
        level = parts[0]
        
        conditions = [CaseFile.status == "completed"]
        
        if level == "l1":
            conditions.append(CaseFile.classification_level1 == parts[1])
        elif level == "l2":
            conditions.append(CaseFile.classification_level1 == parts[1])
            conditions.append(CaseFile.classification_level2 == parts[2])
        elif level == "l3":
            conditions.append(CaseFile.classification_level1 == parts[1])
            conditions.append(CaseFile.classification_level2 == parts[2])
            conditions.append(CaseFile.classification_level3 == parts[3])
        
        count_query = select(func.count()).select_from(CaseFile).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        query = select(CaseFile).where(and_(*conditions))
        query = query.order_by(CaseFile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        case_files = result.scalars().all()
        
        case_file_list = []
        for case_file in case_files:
            case_file_dict = {
                "id": case_file.id,
                "caseNo": case_file.case_no,
                "caseName": case_file.case_name or "",
                "title": case_file.title or "",
                "sourceDepartment": case_file.source_department or "",
                "tags": case_file.tags or [],
                "createdAt": case_file.created_at.isoformat() if case_file.created_at else None
            }
            case_file_list.append(case_file_dict)
        
        return {
            "errorCode": 0,
            "message": "success",
            "data": case_file_list,
            "page": {
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
