"""
内容审查 API
上传公文 docx，由系统分析错别字、用词不当、不符合政府/部队公文写法等问题，并给出修改意见
支持 SSE 流式输出，以 Markdown 格式返回修改建议
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
import io
import json

from app.services.qwen_service import qwen_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _extract_text_from_docx(file_content: bytes) -> str:
    """
    从 docx 文件中提取正文内容（纯文本）
    用于后续送审稿专家（AI）进行审查
    """
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_content))
        parts = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.error(f"解析 docx 失败: {e}")
        raise HTTPException(status_code=400, detail="无法解析该文档，请确认是有效的 .docx 公文文件")


@router.post(
    "/review",
    summary="公文内容审查",
    description="上传 .docx 公文文件，系统将分析错别字、用词不当、不符合政府/部队公文写法等问题，并给出修改意见",
    tags=["内容审查"]
)
async def review_document(
    file: UploadFile = File(..., description="待审查的 .docx 公文文件"),
    token: str = Depends(oauth2_scheme)
):
    """
    公文内容审查接口

    - 上传一份 .docx 格式的公文
    - 系统提取正文后，由审稿规则检查：错别字、用词不当、公文规范
    - 返回问题列表及修改建议，以及总体评价
    """
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="请上传 .docx 格式的公文文件")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空，请上传有效的公文文件")

    text = _extract_text_from_docx(content)
    if not text.strip():
        return {
            "errorCode": 0,
            "message": "success",
            "data": {
                "issues": [],
                "summary": "文档中未提取到正文内容，请确认文件内是否有文字。",
                "extractedLength": 0
            }
        }

    result = qwen_service.review_document_content(text)
    if not result.get("success"):
        error_msg = result.get("error", "审查服务暂时不可用")
        raise HTTPException(status_code=500, detail=error_msg)

    return {
        "errorCode": 0,
        "message": "success",
        "data": {
            "issues": result.get("issues", []),
            "summary": result.get("summary", ""),
            "extractedLength": len(text)
        }
    }


@router.post(
    "/review/stream",
    summary="公文内容审查（流式）",
    description="上传 .docx 公文文件，系统以 SSE 流式输出 Markdown 格式的修改建议",
    tags=["内容审查"]
)
async def review_document_stream(
    file: UploadFile = File(..., description="待审查的 .docx 公文文件"),
    token: str = Depends(oauth2_scheme)
):
    """
    公文内容审查接口（SSE 流式）

    - 上传一份 .docx 格式的公文
    - 系统提取正文后，以 Markdown 格式流式输出：总体评价、问题与修改建议
    - 客户端通过 EventSource 或 fetch + ReadableStream 接收
    """
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="请上传 .docx 格式的公文文件")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="文件为空，请上传有效的公文文件")

    try:
        text = _extract_text_from_docx(content)
    except HTTPException:
        raise

    if not text.strip():
        empty_msg = "文档中未提取到正文内容，请确认文件内是否有文字。\n\n"
        async def _empty_stream():
            yield f"data: {json.dumps({'content': empty_msg})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        return StreamingResponse(
            _empty_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    async def _generate():
        async for chunk in qwen_service.review_document_content_stream(text):
            yield chunk

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
