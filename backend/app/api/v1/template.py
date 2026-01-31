"""
模板管理 API
管理文档生成使用的各类公文、报告模板
模板为 .docx 公文文件，供 AI 生成时参考格式
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, List
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.models.template import DocTemplate
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 模板文件存储目录
TEMPLATE_UPLOAD_DIR = "templates"


async def _save_template_file(file: UploadFile) -> str:
    """保存上传的 docx 文件，返回相对路径"""
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="请上传 .docx 格式的公文文件")

    upload_root = Path(settings.UPLOAD_DIR) / TEMPLATE_UPLOAD_DIR
    upload_root.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix
    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_root / safe_name

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return f"/{TEMPLATE_UPLOAD_DIR}/{safe_name}"


# 请求/响应模型
class TemplateUpdate(BaseModel):
    """更新模板（不含文件）"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    doc_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[int] = Field(None, ge=0, le=1)


def _template_to_response(t: DocTemplate) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "doc_type": t.doc_type,
        "description": t.description,
        "file_path": t.file_path,
        "version": t.version,
        "status": t.status,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.get(
    "",
    summary="获取模板列表",
    description="按文档类型筛选，分页获取模板列表",
)
async def list_templates(
    doc_type: Optional[str] = Query(None, description="文档类型筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（名称、说明）"),
    status: Optional[int] = Query(None, description="状态：1-启用，0-停用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """获取模板列表，支持按类型、关键词、状态筛选"""
    try:
        q = select(DocTemplate)
        count_q = select(func.count()).select_from(DocTemplate)

        if doc_type:
            q = q.where(DocTemplate.doc_type == doc_type)
            count_q = count_q.where(DocTemplate.doc_type == doc_type)
        if status is not None:
            q = q.where(DocTemplate.status == status)
            count_q = count_q.where(DocTemplate.status == status)
        if keyword:
            k = f"%{keyword}%"
            q = q.where(
                (DocTemplate.name.like(k)) | (DocTemplate.description.like(k))
            )
            count_q = count_q.where(
                (DocTemplate.name.like(k)) | (DocTemplate.description.like(k))
            )

        # 总数
        total_result = await db.execute(count_q)
        total = total_result.scalar() or 0

        # 分页
        q = q.order_by(DocTemplate.updated_at.desc())
        q = q.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(q)
        items = result.scalars().all()

        return {
            "errorCode": 0,
            "message": "success",
            "data": [_template_to_response(t) for t in items],
            "page": {"total": total, "page": page, "pageSize": page_size},
        }
    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/doc-types/options",
    summary="获取文档类型选项",
)
async def get_doc_type_options(
    token: str = Depends(oauth2_scheme),
):
    """返回文档生成支持的文档类型，供前端下拉选择"""
    options = [
        {"value": "立案报告", "label": "立案报告"},
        {"value": "调查报告", "label": "调查报告"},
        {"value": "请示", "label": "请示"},
        {"value": "汇报", "label": "汇报"},
        {"value": "通知", "label": "通知"},
        {"value": "函", "label": "函"},
        {"value": "会议纪要", "label": "会议纪要"},
        {"value": "工作总结", "label": "工作总结"},
        {"value": "统计分析报告", "label": "统计分析报告"},
        {"value": "形势分析报告", "label": "形势分析报告"},
        {"value": "案件卷宗", "label": "案件卷宗"},
    ]
    return {
        "errorCode": 0,
        "message": "success",
        "data": options,
    }


@router.get(
    "/{template_id}",
    summary="获取模板详情",
)
async def get_template(
    template_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取模板详情"""
    result = await db.execute(select(DocTemplate).where(DocTemplate.id == template_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {
        "errorCode": 0,
        "message": "success",
        "data": _template_to_response(t),
    }


@router.post(
    "",
    summary="新建模板",
)
async def create_template(
    name: str = Form(..., min_length=1, max_length=100),
    doc_type: str = Form(..., min_length=1, max_length=50),
    description: Optional[str] = Form(None),
    file: UploadFile = File(..., description=".docx 公文模板文件"),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """新建文档模板，需上传 .docx 公文文件作为模板"""
    try:
        file_path = await _save_template_file(file)
        t = DocTemplate(
            name=name.strip(),
            doc_type=doc_type,
            description=description.strip() if description else None,
            file_path=file_path,
        )
        db.add(t)
        await db.flush()
        await db.refresh(t)
        return {
            "errorCode": 0,
            "message": "模板创建成功",
            "data": _template_to_response(t),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        err_msg = str(e)
        logger.error(f"创建模板失败: {err_msg}", exc_info=True)
        detail = err_msg
        if "doesn't exist" in err_msg.lower() or "unknown table" in err_msg.lower():
            detail = "模板表未初始化，请重启后端服务以自动创建表结构"
        raise HTTPException(status_code=500, detail=detail)


@router.put(
    "/{template_id}/file",
    summary="更新模板文件",
)
async def update_template_file(
    template_id: int,
    file: UploadFile = File(..., description=".docx 公文模板文件"),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """更新模板的 docx 文件"""
    result = await db.execute(select(DocTemplate).where(DocTemplate.id == template_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    try:
        file_path = await _save_template_file(file)
        t.file_path = file_path
        await db.flush()
        await db.refresh(t)
        return {
            "errorCode": 0,
            "message": "模板文件已更新",
            "data": _template_to_response(t),
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新模板文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{template_id}",
    summary="更新模板",
)
async def update_template(
    template_id: int,
    body: TemplateUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """更新模板信息（不含文件，文件通过 PUT /{id}/file 更新）"""
    result = await db.execute(select(DocTemplate).where(DocTemplate.id == template_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")

    try:
        if body.name is not None:
            t.name = body.name
        if body.doc_type is not None:
            t.doc_type = body.doc_type
        if body.description is not None:
            t.description = body.description
        if body.status is not None:
            t.status = body.status
        await db.flush()
        await db.refresh(t)
        return {
            "errorCode": 0,
            "message": "模板更新成功",
            "data": _template_to_response(t),
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"更新模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{template_id}",
    summary="删除模板",
)
async def delete_template(
    template_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """删除模板"""
    result = await db.execute(select(DocTemplate).where(DocTemplate.id == template_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")

    try:
        await db.delete(t)
        await db.flush()
        return {"errorCode": 0, "message": "模板已删除"}
    except Exception as e:
        await db.rollback()
        logger.error(f"删除模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
