"""
案卷管理相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case
from sqlalchemy.sql import text

from app.core.database import get_db
from app.core.response import ResponseModel
from app.models.archive import CaseFile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# 请求模型
class CaseFileListParams(BaseModel):
    """案卷列表查询参数"""
    keyword: Optional[str] = Field(None, description="关键词搜索")
    case_type: Optional[str] = Field(None, description="案卷类型")
    status: Optional[str] = Field(None, description="状态: pending/processing/completed/failed")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class CaseFileResponse(BaseModel):
    """案卷响应模型"""
    id: int
    caseNo: str
    caseName: str
    title: str
    caseType: str
    sourceDepartment: str
    incidentTime: Optional[datetime]
    personName: Optional[str]
    status: str
    createdAt: datetime
    updatedAt: datetime


@router.post(
    "/import",
    summary="批量导入案卷",
    description="支持批量上传案卷文件，单次最多1000个文件，单个文件最大500MB",
    tags=["案卷管理"]
)
async def import_case_files(
    files: List[UploadFile] = File(...),
    task_name: Optional[str] = Query(None, description="任务名称"),
    token: str = Depends(oauth2_scheme)
):
    """
    批量导入案卷接口
    
    - **files**: 上传的文件列表（支持 PDF、JPG、PNG、DOCX、XLSX 格式）
    - **task_name**: 导入任务名称（可选）
    
    返回导入任务ID，可通过任务ID查询导入进度
    """
    # TODO: 实现真实的导入逻辑
    return ResponseModel.success(
        data={
            "task_id": "task_20260116001",
            "total_files": len(files),
            "status": "pending"
        },
        message="导入任务已创建"
    )


@router.get(
    "/list",
    summary="获取案卷列表",
    description="分页查询案卷列表，支持关键词搜索、类型筛选、状态筛选",
    tags=["案卷管理"]
)
async def get_case_file_list(
    keyword: Optional[str] = Query(None, description="关键词（案卷编号、卷宗名、标题、内容）"),
    case_type: Optional[str] = Query(None, description="案卷类型"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    获取案卷列表接口
    
    - **keyword**: 搜索关键词，支持案卷编号、卷宗名、标题、OCR文本全文搜索
    - **case_type**: 案卷类型筛选
    - **status**: 状态筛选（pending/processing/completed/failed）
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    
    返回分页的案卷列表
    """
    try:
        # 构建查询条件
        conditions = []
        
        if keyword:
            # 全文搜索（使用LIKE，如果数据库支持全文索引会更快）
            keyword_condition = or_(
                CaseFile.case_no.like(f"%{keyword}%"),
                CaseFile.case_name.like(f"%{keyword}%"),
                CaseFile.title.like(f"%{keyword}%"),
                CaseFile.ocr_text.like(f"%{keyword}%")
            )
            conditions.append(keyword_condition)
        
        if case_type:
            conditions.append(CaseFile.case_type == case_type)
        
        if status:
            conditions.append(CaseFile.status == status)
        
        # 总数查询
        count_query = select(func.count()).select_from(CaseFile)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 列表查询
        query = select(CaseFile)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(CaseFile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        case_files = result.scalars().all()
        
        # 转换为响应格式
        case_file_list = []
        for case_file in case_files:
            case_file_dict = {
                "id": case_file.id,
                "caseNo": case_file.case_no,
                "caseName": case_file.case_name or "",
                "title": case_file.title or "",
                "caseType": case_file.case_type or "",
                "sourceDepartment": case_file.source_department or "",
                "incidentTime": case_file.incident_time.isoformat() if case_file.incident_time else None,
                "personName": case_file.person_name or "",
                "status": case_file.status,
                "createdAt": case_file.created_at.isoformat() if case_file.created_at else None,
                "updatedAt": case_file.updated_at.isoformat() if case_file.updated_at else None,
                "fileSize": case_file.file_size,
                "fileType": case_file.file_type,
                "classificationLevel1": case_file.classification_level1,
                "classificationLevel2": case_file.classification_level2,
                "classificationLevel3": case_file.classification_level3,
                "tags": case_file.tags or []
            }
            case_file_list.append(case_file_dict)
        
        # 使用统一的响应封装
        return ResponseModel.paginated(
            items=case_file_list,
            total=total,
            page=page,
            page_size=page_size
        )
    except HTTPException:
        raise
    except Exception as e:
        # 异常会被全局异常处理器捕获，确保返回 JSON 格式
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/detail/{case_file_id}",
    summary="获取案卷详情",
    description="根据案卷ID获取详细信息，包括核心字段、OCR文本、元数据、标签等",
    tags=["案卷管理"]
)
async def get_case_file_detail(
    case_file_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    获取案卷详情接口
    
    - **case_file_id**: 案卷ID
    
    返回案卷的完整信息，包括：
    - 基本信息（编号、卷宗名、标题、类型等）
    - 核心字段（发生时间、姓名、人员基本情况、事发经过、侦查调查过程及结论、原因教训、立案、判决情况）
    - OCR识别文本
    - 元数据
    - 标签
    - 分类信息
    """
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        
        case_file_data = {
            "id": case_file.id,
            "caseNo": case_file.case_no,
            "caseName": case_file.case_name or "",
            "title": case_file.title or "",
            "caseType": case_file.case_type or "",
            "sourceDepartment": case_file.source_department or "",
            "incidentTime": case_file.incident_time.isoformat() if case_file.incident_time else None,
            "personName": case_file.person_name or "",
            "personInfo": case_file.person_info or {},
            "incidentProcess": case_file.incident_process or "",
            "investigationProcessAndConclusion": case_file.investigation_process_and_conclusion or "",
            "causeAndLesson": case_file.cause_and_lesson or "",
            "caseFiling": case_file.case_filing or "",
            "judgment": case_file.judgment or "",
            "status": case_file.status,
            "filePath": case_file.file_path or "",
            "fileSize": case_file.file_size or 0,
            "fileType": case_file.file_type or "",
            "ocrText": case_file.ocr_text or "",
            "metadata": case_file.meta_data or {},  # API返回时仍使用metadata字段名
            "tags": case_file.tags or [],
            "classificationLevel1": case_file.classification_level1,
            "classificationLevel2": case_file.classification_level2,
            "classificationLevel3": case_file.classification_level3,
            "timeline": case_file.timeline or [],
            "createdAt": case_file.created_at.isoformat() if case_file.created_at else None,
            "updatedAt": case_file.updated_at.isoformat() if case_file.updated_at else None
        }
        
        # 使用统一的响应封装
        return ResponseModel.success(data=case_file_data)
    except HTTPException:
        raise
    except Exception as e:
        # 异常会被全局异常处理器捕获，确保返回 JSON 格式
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/search",
    summary="全文检索",
    description="对案卷进行全文检索，支持模糊匹配和相关性排序",
    tags=["案卷管理"]
)
async def search_case_files(
    keyword: str = Query(..., description="搜索关键词"),
    search_mode: Optional[str] = Query("fuzzy", description="搜索模式: fuzzy/exact"),
    search_scope: Optional[str] = Query("title,content,metadata,tags", description="搜索范围，逗号分隔"),
    case_type: Optional[str] = Query(None, description="案卷类型筛选"),
    department: Optional[str] = Query(None, description="部门筛选"),
    sort_by: Optional[str] = Query("relevance", description="排序: relevance/time/title"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    全文检索接口
    
    - **keyword**: 搜索关键词
    - **search_mode**: 搜索模式（模糊/精确）
    - **search_scope**: 搜索范围（title,content,metadata,tags）
    - **sort_by**: 排序方式（relevance/time/title）
    
    对案卷的卷宗名、标题、OCR文本、元数据进行全文检索，
    返回按相关性排序的结果
    """
    try:
        import time
        start_time = time.time()
        
        # 构建搜索条件
        conditions = []
        scopes = [s.strip() for s in search_scope.split(",")] if search_scope else []
        
        if keyword:
            if search_mode == "exact":
                # 精确匹配
                if "title" in scopes:
                    conditions.append(CaseFile.title == keyword)
                if "content" in scopes:
                    conditions.append(CaseFile.ocr_text == keyword)
                # 元数据和标签的精确匹配需要JSON查询
            else:
                # 模糊匹配
                keyword_like = f"%{keyword}%"
                search_conditions = []
                if "title" in scopes or not scopes:
                    search_conditions.append(CaseFile.case_name.like(keyword_like))
                    search_conditions.append(CaseFile.title.like(keyword_like))
                if "content" in scopes or not scopes:
                    search_conditions.append(CaseFile.ocr_text.like(keyword_like))
                if search_conditions:
                    conditions.append(or_(*search_conditions))
        
        if case_type:
            conditions.append(CaseFile.case_type == case_type)
        
        if department:
            conditions.append(CaseFile.source_department == department)
        
        # 查询总数
        count_query = select(func.count()).select_from(CaseFile)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        query = select(CaseFile)
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序
        if sort_by == "time":
            query = query.order_by(CaseFile.created_at.desc())
        elif sort_by == "title":
            query = query.order_by(CaseFile.case_name.asc())
        else:  # relevance - 默认按创建时间倒序
            query = query.order_by(CaseFile.created_at.desc())
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        case_files = result.scalars().all()
        
        # 构建搜索结果（包含匹配片段）
        results = []
        for case_file in case_files:
            # 计算相关性（简单算法：关键词出现次数）
            relevance = 0
            fragments = []
            
            if case_file.case_name and keyword.lower() in case_file.case_name.lower():
                relevance += 15
                # 提取匹配片段
                idx = case_file.case_name.lower().find(keyword.lower())
                start = max(0, idx - 20)
                end = min(len(case_file.case_name), idx + len(keyword) + 20)
                fragments.append(case_file.case_name[start:end])
            
            if case_file.title and keyword.lower() in case_file.title.lower():
                relevance += 10
                # 提取匹配片段
                idx = case_file.title.lower().find(keyword.lower())
                start = max(0, idx - 20)
                end = min(len(case_file.title), idx + len(keyword) + 20)
                fragments.append(case_file.title[start:end])
            
            if case_file.ocr_text and keyword.lower() in case_file.ocr_text.lower():
                relevance += 5
                # 提取匹配片段（最多3个）
                text_lower = case_file.ocr_text.lower()
                keyword_lower = keyword.lower()
                idx = 0
                fragment_count = 0
                while idx < len(text_lower) and fragment_count < 3:
                    idx = text_lower.find(keyword_lower, idx)
                    if idx == -1:
                        break
                    start = max(0, idx - 30)
                    end = min(len(case_file.ocr_text), idx + len(keyword) + 30)
                    fragments.append(case_file.ocr_text[start:end].strip())
                    idx += len(keyword_lower)
                    fragment_count += 1
            
            relevance_score = min(100, relevance * 10)
            
            case_file_dict = {
                "id": case_file.id,
                "caseNo": case_file.case_no,
                "caseName": case_file.case_name or "",
                "title": case_file.title or "",
                "caseType": case_file.case_type or "",
                "sourceDepartment": case_file.source_department or "",
                "date": case_file.created_at.isoformat() if case_file.created_at else None,
                "relevance": min(5, relevance // 2),  # 转换为1-5星
                "relevanceScore": f"{relevance_score}%",
                "fragments": fragments[:3],  # 最多返回3个片段
                "tags": case_file.tags or []
            }
            results.append(case_file_dict)
        
        # 按相关性排序
        if sort_by == "relevance":
            results.sort(key=lambda x: int(x["relevanceScore"].replace("%", "")), reverse=True)
        
        took = int((time.time() - start_time) * 1000)
        
        # 使用统一的响应封装，分页数据，包含 meta 信息
        return ResponseModel.paginated(
            items=results,
            total=total,
            page=page,
            page_size=page_size,
            meta={
                "took": took,
                "keyword": keyword
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        # 异常会被全局异常处理器捕获，确保返回 JSON 格式
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/import-tasks",
    summary="获取导入任务列表",
    description="获取所有案卷导入任务及其状态",
    tags=["案卷管理"]
)
async def get_import_tasks(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    获取导入任务列表接口
    
    返回所有导入任务，包括：
    - 任务名称
    - 状态（pending/running/completed/failed）
    - 文件数量统计
    - 创建时间
    """
    try:
        from app.models.import_task import ImportTask
        
        query = select(ImportTask).order_by(ImportTask.created_at.desc())
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        task_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "taskName": task.task_name or "",
                "totalFiles": task.total_files or 0,
                "successFiles": task.success_files or 0,
                "failedFiles": task.failed_files or 0,
                "status": task.status,
                "createdAt": task.created_at.isoformat() if task.created_at else None,
                "updatedAt": task.updated_at.isoformat() if task.updated_at else None
            }
            task_list.append(task_dict)
        
        # 使用统一的响应封装
        return ResponseModel.success(data=task_list)
    except HTTPException:
        raise
    except Exception as e:
        # 异常会被全局异常处理器捕获，确保返回 JSON 格式
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{case_file_id}",
    summary="删除案卷",
    description="根据案卷ID删除案卷",
    tags=["案卷管理"]
)
async def delete_case_file(
    case_file_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    删除案卷接口
    
    - **case_file_id**: 案卷ID
    
    删除指定的案卷记录
    """
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        
        await db.delete(case_file)
        await db.commit()
        
        # 使用统一的响应封装
        return ResponseModel.success(message="删除成功", data={})
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        # 异常会被全局异常处理器捕获，确保返回 JSON 格式
        raise HTTPException(status_code=500, detail=str(e))
