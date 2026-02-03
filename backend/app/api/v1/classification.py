"""
智能分类相关 API（卷宗审核入库）
"""
from datetime import datetime
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import ResponseModel
from app.models.archive import CaseFile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _case_file_to_pending_item(case_file: CaseFile) -> dict:
    """将 CaseFile 转为待审核列表项（与前端卷宗审核入库页结构一致）。"""
    meta = case_file.meta_data or {}
    return {
        "id": case_file.id,
        "caseNo": case_file.case_no,
        "name": meta.get("original_filename") or case_file.case_name or "",
        "batchName": meta.get("task_name") or "",
        "size": case_file.file_size or 0,
        "fileType": (case_file.file_type or "").lower(),
        "status": "archived" if case_file.status == "completed" else ("failed" if case_file.status == "failed" else "pending"),
        "createdAt": case_file.created_at.isoformat() if case_file.created_at else None,
        "extractedData": {
            "caseName": case_file.case_name or "",
            "incidentTime": case_file.incident_time.strftime("%Y-%m-%d %H:%M") if case_file.incident_time else "",
            "incidentUnit": case_file.source_department or "",
            "personName": case_file.person_name or "",
            "personGender": (case_file.person_info or {}).get("gender", ""),
            "personEthnicity": (case_file.person_info or {}).get("ethnicity", ""),
            "personBirthplace": (case_file.person_info or {}).get("birthplace", ""),
            "personEnlistTime": (case_file.person_info or {}).get("enlistment_time", ""),
            "personPosition": (case_file.person_info or {}).get("position", ""),
            "personCategory": (case_file.person_info or {}).get("person_category", ""),
            "charge": case_file.charge or "",
            "suicideMethod": case_file.suicide_method or "",
            "incidentProcess": case_file.incident_process or "",
            "investigationProcess": case_file.investigation_process_and_conclusion or "",
            "investigationConclusion": "",
            "causeAndLesson": case_file.cause_and_lesson or "",
            "caseFiling": case_file.case_filing or "",
            "judgment": case_file.judgment or "",
        },
        "ocrText": case_file.ocr_text or "",
        "classification": {
            "level1": case_file.classification_level1,
            "level2": case_file.classification_level2,
            "level3": case_file.classification_level3,
        },
        "tags": case_file.tags or [],
    }


@router.get(
    "/pending",
    summary="获取卷宗审核列表",
    description="获取待审核/已入库的案卷，用于卷宗审核入库页；支持按状态筛选",
    tags=["智能分类"]
)
async def get_pending_classifications(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索卷宗名称/案卷编号"),
    status: Optional[str] = Query(None, description="状态：pending=待审核，failed=审核失败，archived=已入库，空=仅待审核+审核失败"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取卷宗审核列表。空=仅待审核与审核失败（不包含已入库）；pending=待审核；failed=审核失败；archived=已入库。"""
    try:
        conditions = []
        if status == "pending":
            conditions.append(CaseFile.status == "pending")
        elif status == "failed":
            conditions.append(CaseFile.status == "failed")
        elif status == "archived":
            conditions.append(CaseFile.status == "completed")
        else:
            # 全部 / 未指定：只显示待审核和审核失败，不显示已入库
            conditions.append(CaseFile.status.in_(["pending", "failed"]))
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    CaseFile.case_name.like(kw),
                    CaseFile.case_no.like(kw),
                    CaseFile.title.like(kw),
                    CaseFile.person_name.like(kw),
                )
            )
        count_query = select(func.count()).select_from(CaseFile)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        query = select(CaseFile)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(CaseFile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        case_files = result.scalars().all()
        case_file_list = [_case_file_to_pending_item(cf) for cf in case_files]
        return ResponseModel.paginated(
            items=case_file_list,
            total=total,
            page=page,
            page_size=page_size,
        )
    except HTTPException:
        raise
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
        case_file.classification_level1 = classification.get("level1")
        case_file.classification_level2 = classification.get("level2")
        case_file.classification_level3 = classification.get("level3")
        await db.commit()
        return ResponseModel.success(message="分类已确认", data={})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


class ArchiveConfirmBody(BaseModel):
    """确认入库请求体（与前端审核表单一致）"""
    caseName: Optional[str] = None
    incidentTime: Optional[str] = None
    incidentUnit: Optional[str] = None
    personName: Optional[str] = None
    personGender: Optional[str] = None
    personEthnicity: Optional[str] = None
    personBirthplace: Optional[str] = None
    personEnlistTime: Optional[str] = None
    personPosition: Optional[str] = None
    personCategory: Optional[str] = None
    charge: Optional[str] = None
    suicideMethod: Optional[str] = None
    incidentProcess: Optional[str] = None
    investigationProcess: Optional[str] = None
    investigationConclusion: Optional[str] = None
    causeAndLesson: Optional[str] = None
    caseFiling: Optional[str] = None
    judgment: Optional[str] = None
    classification: Optional[dict] = None  # { level1, level2, level3 }
    tags: Optional[List[str]] = None


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        if " " in s:
            return datetime.strptime(s[:16], "%Y-%m-%d %H:%M")
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except Exception:
        return None


@router.post(
    "/save-review/{case_file_id}",
    summary="保存审核",
    description="保存审核内容，不改变状态；用于暂存人工修改的案卷信息",
    tags=["智能分类"]
)
async def save_review(
    case_file_id: int,
    body: ArchiveConfirmBody = Body(..., description="审核后的案卷信息"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """保存审核内容（案卷仍为待审核状态）。"""
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        case_file.case_name = body.caseName or case_file.case_name
        case_file.incident_time = _parse_dt(body.incidentTime) or case_file.incident_time
        case_file.source_department = body.incidentUnit or case_file.source_department
        case_file.person_name = body.personName or case_file.person_name
        person_info = dict(case_file.person_info or {})
        if body.personGender is not None:
            person_info["gender"] = body.personGender
        if body.personEthnicity is not None:
            person_info["ethnicity"] = body.personEthnicity
        if body.personBirthplace is not None:
            person_info["birthplace"] = body.personBirthplace
        if body.personEnlistTime is not None:
            person_info["enlistment_time"] = body.personEnlistTime
        if body.personPosition is not None:
            person_info["position"] = body.personPosition
        if body.personCategory is not None:
            person_info["person_category"] = body.personCategory
        case_file.person_info = person_info
        case_file.charge = body.charge if body.charge is not None else case_file.charge
        case_file.suicide_method = body.suicideMethod if body.suicideMethod is not None else case_file.suicide_method
        case_file.incident_process = body.incidentProcess or case_file.incident_process
        case_file.investigation_process_and_conclusion = (
            (body.investigationProcess or "") + "\n" + (body.investigationConclusion or "")
        ).strip() or case_file.investigation_process_and_conclusion
        case_file.cause_and_lesson = body.causeAndLesson or case_file.cause_and_lesson
        case_file.case_filing = body.caseFiling or case_file.case_filing
        case_file.judgment = body.judgment or case_file.judgment
        if body.classification:
            case_file.classification_level1 = body.classification.get("level1")
            case_file.classification_level2 = body.classification.get("level2")
            case_file.classification_level3 = body.classification.get("level3")
        if body.tags is not None:
            case_file.tags = body.tags
        await db.commit()
        return ResponseModel.success(message="审核已保存", data={})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/archive/{case_file_id}",
    summary="确认入库",
    description="审核通过后确认案卷入库，更新案卷字段并将状态设为已入库",
    tags=["智能分类"]
)
async def confirm_archive(
    case_file_id: int,
    body: ArchiveConfirmBody = Body(..., description="审核后的案卷信息"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """确认卷宗入库：更新案卷字段并设置 status=completed。"""
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        if case_file.status == "completed":
            return ResponseModel.success(message="该案卷已入库", data={})
        case_file.case_name = body.caseName or case_file.case_name
        case_file.incident_time = _parse_dt(body.incidentTime) or case_file.incident_time
        case_file.source_department = body.incidentUnit or case_file.source_department
        case_file.person_name = body.personName or case_file.person_name
        person_info = dict(case_file.person_info or {})
        if body.personGender is not None:
            person_info["gender"] = body.personGender
        if body.personEthnicity is not None:
            person_info["ethnicity"] = body.personEthnicity
        if body.personBirthplace is not None:
            person_info["birthplace"] = body.personBirthplace
        if body.personEnlistTime is not None:
            person_info["enlistment_time"] = body.personEnlistTime
        if body.personPosition is not None:
            person_info["position"] = body.personPosition
        if body.personCategory is not None:
            person_info["person_category"] = body.personCategory
        case_file.person_info = person_info
        case_file.charge = body.charge if body.charge is not None else case_file.charge
        case_file.suicide_method = body.suicideMethod if body.suicideMethod is not None else case_file.suicide_method
        case_file.incident_process = body.incidentProcess or case_file.incident_process
        case_file.investigation_process_and_conclusion = (
            (body.investigationProcess or "") + "\n" + (body.investigationConclusion or "")
        ).strip() or case_file.investigation_process_and_conclusion
        case_file.cause_and_lesson = body.causeAndLesson or case_file.cause_and_lesson
        case_file.case_filing = body.caseFiling or case_file.case_filing
        case_file.judgment = body.judgment or case_file.judgment
        if body.classification:
            case_file.classification_level1 = body.classification.get("level1")
            case_file.classification_level2 = body.classification.get("level2")
            case_file.classification_level3 = body.classification.get("level3")
        if body.tags is not None:
            case_file.tags = body.tags
        case_file.status = "completed"
        await db.commit()
        return ResponseModel.success(message="卷宗已入库", data={})
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
