"""
OCR数字化相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.ocr_task import OcrTask
from app.models.archive import CaseFile

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class OcrTaskResponse(BaseModel):
    """OCR任务响应模型"""
    id: int
    case_file_id: Optional[int]
    file_name: str
    file_size: int
    file_type: str
    status: str
    progress: int
    current_step: Optional[str]
    accuracy: Optional[float]
    ocr_text: Optional[str]
    original_image_path: Optional[str]
    start_time: Optional[datetime]
    estimated_time: Optional[str]
    error_message: Optional[str]
    steps_info: Optional[dict]
    logs: Optional[List[dict]]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime


class OcrTaskListResponse(BaseModel):
    """OCR任务列表响应"""
    errorCode: int = 0
    message: str = "success"
    data: dict


@router.get(
    "/tasks",
    summary="获取OCR任务列表",
    description="获取OCR任务列表，支持按状态筛选",
    response_model=OcrTaskListResponse,
    tags=["OCR数字化"]
)
async def get_ocr_tasks(
    status: Optional[str] = Query(None, description="任务状态: pending/processing/completed/failed"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取OCR任务列表"""
    try:
        # 构建查询条件
        conditions = []
        if status:
            conditions.append(OcrTask.status == status)
        
        query = select(OcrTask)
        if conditions:
            query = query.where(and_(*conditions))
        
        # 总数查询
        count_query = select(func.count()).select_from(OcrTask)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页查询
        query = query.order_by(OcrTask.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # 转换为响应格式
        task_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "caseFileId": task.case_file_id,
                "fileName": task.file_name,
                "fileSize": task.file_size or 0,
                "fileType": task.file_type,
                "status": task.status,
                "progress": task.progress or 0,
                "currentStep": task.current_step,
                "accuracy": task.accuracy,
                "ocrText": task.ocr_text,
                "originalImage": task.original_image_path,
                "startTime": task.start_time.isoformat() if task.start_time else None,
                "estimatedTime": task.estimated_time,
                "errorMessage": task.error_message,
                "steps": task.steps_info or {},
                "logs": task.logs or [],
                "metadata": task.meta_data or {}  # API返回时仍使用metadata字段名
            }
            task_list.append(task_dict)
        
        return {
            "errorCode": 0,
            "message": "success",
            "data": task_list,
            "page": {
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tasks/{task_id}",
    summary="获取OCR任务详情",
    description="根据任务ID获取OCR任务详细信息",
    tags=["OCR数字化"]
)
async def get_ocr_task_detail(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取OCR任务详情"""
    try:
        query = select(OcrTask).where(OcrTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return {
            "errorCode": 0,
            "message": "success",
            "data": {
                "id": task.id,
                "caseFileId": task.case_file_id,
                "fileName": task.file_name,
                "fileSize": task.file_size or 0,
                "fileType": task.file_type,
                "status": task.status,
                "progress": task.progress or 0,
                "currentStep": task.current_step,
                "accuracy": task.accuracy,
                "ocrText": task.ocr_text,
                "originalImage": task.original_image_path,
                "startTime": task.start_time.isoformat() if task.start_time else None,
                "estimatedTime": task.estimated_time,
                "errorMessage": task.error_message,
                "steps": task.steps_info or {},
                "logs": task.logs or [],
                "metadata": task.meta_data or {}  # API返回时仍使用metadata字段名
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tasks/{task_id}/start",
    summary="启动OCR任务",
    description="启动指定的OCR任务进行识别处理",
    tags=["OCR数字化"]
)
async def start_ocr_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """启动OCR任务"""
    try:
        query = select(OcrTask).where(OcrTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status != "pending":
            raise HTTPException(status_code=400, detail=f"任务状态为{task.status}，无法启动")
        
        # 更新任务状态
        task.status = "processing"
        task.current_step = "preprocess"
        task.progress = 10
        task.start_time = datetime.now()
        task.steps_info = task.steps_info or {}
        task.steps_info["upload"] = "已完成"
        task.steps_info["preprocess"] = "处理中..."
        
        # TODO: 这里应该调用实际的OCR处理服务
        # 目前只是更新状态，实际处理应该在后台任务中完成
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": "OCR任务已启动",
            "data": {"task_id": task_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tasks/batch-start",
    summary="批量启动OCR任务",
    description="批量启动多个OCR任务",
    tags=["OCR数字化"]
)
async def batch_start_ocr_tasks(
    task_ids: List[int],
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """批量启动OCR任务"""
    try:
        query = select(OcrTask).where(
            and_(
                OcrTask.id.in_(task_ids),
                OcrTask.status == "pending"
            )
        )
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        started_count = 0
        for task in tasks:
            task.status = "processing"
            task.current_step = "preprocess"
            task.progress = 10
            task.start_time = datetime.now()
            task.steps_info = task.steps_info or {}
            task.steps_info["upload"] = "已完成"
            task.steps_info["preprocess"] = "处理中..."
            started_count += 1
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": f"成功启动{started_count}个任务",
            "data": {"started_count": started_count}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/tasks/{task_id}/retry",
    summary="重试OCR任务",
    description="重试失败的OCR任务",
    tags=["OCR数字化"]
)
async def retry_ocr_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """重试OCR任务"""
    try:
        query = select(OcrTask).where(OcrTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status != "failed":
            raise HTTPException(status_code=400, detail="只能重试失败的任务")
        
        # 重置任务状态
        task.status = "pending"
        task.progress = 0
        task.current_step = None
        task.error_message = None
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": "任务已重置，可以重新启动",
            "data": {"task_id": task_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/tasks/{task_id}/correct",
    summary="保存OCR校正结果",
    description="保存手动校正后的OCR文本",
    tags=["OCR数字化"]
)
async def correct_ocr_task(
    task_id: int,
    corrected_text: str = Query(..., description="校正后的文本"),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """保存OCR校正结果"""
    try:
        query = select(OcrTask).where(OcrTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 更新OCR文本
        task.ocr_text = corrected_text
        
        # 如果有关联的案卷，也更新案卷的OCR文本
        if task.case_file_id:
            case_file_query = select(CaseFile).where(CaseFile.id == task.case_file_id)
            case_file_result = await db.execute(case_file_query)
            case_file = case_file_result.scalar_one_or_none()
            if case_file:
                case_file.ocr_text = corrected_text
        
        await db.commit()
        
        return {
            "errorCode": 0,
            "message": "校正已保存",
            "data": {"task_id": task_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
