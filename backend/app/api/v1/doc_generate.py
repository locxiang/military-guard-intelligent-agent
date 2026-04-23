"""
文档生成相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import asyncio
import json

from app.core.security import decode_access_token

from app.services.qwen_service import qwen_service
from app.services.official_doc import official_doc_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# 请求模型
class DocGenerateRequest(BaseModel):
    """文档生成请求"""
    doc_type: str = Field(..., description="文档类型：立案报告/调查报告/请示/汇报/会议纪要/工作总结")
    template_id: Optional[str] = Field(None, description="模板ID")
    core_elements: Optional[str] = Field(None, description="核心要素，JSON字符串或文本")
    attachments: Optional[List[int]] = Field(None, description="关联案卷ID列表")


class DocGenerateResponse(BaseModel):
    """文档生成响应"""
    errorCode: int = 0
    message: str = "success"
    data: dict


@router.post(
    "/generate",
    summary="生成文档",
    description="基于AI智能生成各类公文、报告、纪要等文档",
    response_model=DocGenerateResponse,
    tags=["文档生成"]
)
async def generate_document(
    request: DocGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成文档接口

    - **doc_type**: 文档类型
    - **template_id**: 使用的模板ID（可选）
    - **core_elements**: 核心要素，包含案件编号、主送机关等关键信息
    - **attachments**: 关联的案卷ID列表（可选）

    返回生成任务ID，可通过任务ID查询生成状态和结果
    """
    # TODO: 实现真实的文档生成逻辑
    return {
        "errorCode": 0,
        "message": "文档生成任务已创建",
        "data": {
            "task_id": "DOC20260116001",
            "doc_type": request.doc_type,
            "status": "generating",
            "estimated_time": 30
        }
    }


@router.get(
    "/templates",
    summary="获取模板列表",
    description="获取可用的文档模板列表（供文档生成选用）",
    tags=["文档生成"]
)
async def get_templates(
    doc_type: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
):
    """
    获取模板列表接口

    - **doc_type**: 文档类型筛选（可选）

    返回启用的文档模板列表，从模板管理中同步
    """
    from app.models.template import DocTemplate
    from app.core.database import get_db
    from sqlalchemy import select

    # 使用 get_db 需在路由中注入，此处为独立路由，直接创建会话
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        q = select(DocTemplate).where(DocTemplate.status == 1)
        if doc_type:
            q = q.where(DocTemplate.doc_type == doc_type)
        q = q.order_by(DocTemplate.updated_at.desc())
        result = await db.execute(q)
        items = result.scalars().all()
        templates = [
            {"id": str(t.id), "name": t.name, "doc_type": t.doc_type, "description": t.description or ""}
            for t in items
        ]
    return {
        "errorCode": 0,
        "message": "success",
        "data": {"templates": templates}
    }


@router.get(
    "/status/{task_id}",
    summary="查询生成状态",
    description="根据任务ID查询文档生成状态和结果",
    tags=["文档生成"]
)
async def get_generate_status(
    task_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    查询生成状态接口

    - **task_id**: 生成任务ID

    返回任务状态：
    - generating: 生成中
    - completed: 已完成
    - failed: 失败

    如果已完成，返回文档下载链接
    """
    # TODO: 实现真实的状态查询逻辑
    return {
        "errorCode": 0,
        "message": "success",
        "data": {
            "task_id": task_id,
            "status": "generating",
            "progress": 50,
            "file_path": None,
            "error_message": None
        }
    }


@router.get(
    "/tasks",
    summary="获取生成任务列表",
    description="获取所有文档生成任务及其状态",
    tags=["文档生成"]
)
async def get_generate_tasks(
    token: str = Depends(oauth2_scheme)
):
    """
    获取生成任务列表接口

    返回所有文档生成任务，包括：
    - 任务ID
    - 文档类型
    - 状态（generating/completed/failed）
    - 创建时间
    """
    # TODO: 实现真实的查询逻辑
    return {
        "errorCode": 0,
        "message": "success",
        "data": []
    }


# 新增：案件卷宗生成请求模型
class CaseDocumentGenerateRequest(BaseModel):
    """案件卷宗生成请求"""
    doc_type: str = Field(..., description="文书类型：案件报告/案件总结/立案报告等")
    case_info: Dict[str, Any] = Field(..., description="案件信息")
    related_cases: Optional[List[Dict[str, Any]]] = Field(None, description="关联案件列表（可选）")


# 新增：公文生成请求模型
class OfficialDocumentGenerateRequest(BaseModel):
    """公文生成请求"""
    doc_type: str = Field(..., description="公文类型：请示/汇报/通知/函")
    form_data: Dict[str, Any] = Field(..., description="表单数据")
    selected_case: Optional[Dict[str, Any]] = Field(None, description="关联案件（可选）")


# 新增：报告生成请求模型
class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    report_type: str = Field(..., description="报告类型：工作总结/统计分析报告/形势分析报告")
    form_data: Dict[str, Any] = Field(..., description="表单数据")
    statistics: Dict[str, Any] = Field(..., description="统计数据")
    report_period: Optional[str] = Field(None, description="报告周期")


# 新增：警示小故事生成请求模型
class StoryGenerateRequest(BaseModel):
    """警示小故事生成请求"""
    story_type: str = Field(..., description="故事类型：诈骗/被骗、犯罪、工作重大失误、涉密泄密、违纪违规、其他")
    keywords: Optional[str] = Field(None, description="可选关键词或情节提示，如：网购退款、兼职刷单、小刘、某单位等")
    scene_hint: Optional[str] = Field(None, description="可选场景提示，如：某某做了什么被诈骗、某某因为什么被处分")


# 新增：会议纪要生成请求模型（支持文字随记与录音转写稿）
class MeetingGenerateRequest(BaseModel):
    """会议纪要生成请求"""
    input_type: str = Field(..., description="输入方式：text-文字随记，recording-录音（后端先转写再生成）")
    meeting_notes: Optional[str] = Field(None, description="会议随记或会议内容文字（input_type 为 text 时必填）")
    meeting_transcript: Optional[str] = Field(None, description="会议转写稿（录音转写后传入，或由前端上传录音后后端填充）")
    meeting_title: Optional[str] = Field(None, description="会议主题（可选）")
    meeting_time: Optional[str] = Field(None, description="会议时间（可选）")


@router.post(
    "/case",
    summary="生成案件卷宗（流式）",
    description="基于案件信息，使用AI流式生成案件卷宗文档",
    tags=["文档生成"]
)
async def generate_case_document(
    request: CaseDocumentGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成案件卷宗接口（SSE流式输出）

    - **doc_type**: 文书类型
    - **case_info**: 案件信息（案发时间、案件类型、涉案人员等）
    - **related_cases**: 关联案件列表（可选）

    返回SSE流式数据，客户端通过EventSource接收
    """
    async def generate():
        try:
            context = {
                "caseInfo": request.case_info,
                "relatedCases": request.related_cases or []
            }

            # 使用流式生成
            async for chunk in qwen_service.generate_document_stream(
                doc_type=request.doc_type,
                context=context,
                template_hint="当前使用的是通用模板格式，实际使用时请根据单位规定的模板进行调整。"
            ):
                yield chunk

        except Exception as e:
            logger.error(f"生成案件卷宗时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/official",
    summary="生成公文（流式）",
    description="基于表单数据，使用AI流式生成各类公文文档",
    tags=["文档生成"]
)
async def generate_official_document(
    request: OfficialDocumentGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成公文接口（SSE流式输出）

    - **doc_type**: 公文类型（请示/汇报/通知/函）
    - **form_data**: 表单数据（主送机关、主题、内容等）
    - **selected_case**: 关联案件（可选）

    返回SSE流式数据，客户端通过EventSource接收
    """
    async def generate():
        try:
            context = {
                "formData": request.form_data,
                "selectedCase": request.selected_case
            }

            # 使用流式生成
            async for chunk in qwen_service.generate_document_stream(
                doc_type=request.doc_type,
                context=context,
                template_hint="当前使用的是通用模板格式，实际使用时请根据单位规定的模板进行调整。"
            ):
                yield chunk

        except Exception as e:
            logger.error(f"生成公文时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/report",
    summary="生成报告（流式）",
    description="基于统计数据和表单信息，使用AI流式生成各类报告文档",
    tags=["文档生成"]
)
async def generate_report_document(
    request: ReportGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成报告接口（SSE流式输出）

    - **report_type**: 报告类型（工作总结/统计分析报告/形势分析报告）
    - **form_data**: 表单数据（标题、工作亮点、存在问题、下步计划等）
    - **statistics**: 统计数据（案件总数、办结率、类型分布等）
    - **report_period**: 报告周期（可选）

    返回SSE流式数据，客户端通过EventSource接收
    """
    async def generate():
        try:
            context = {
                "formData": request.form_data,
                "statistics": request.statistics,
                "reportPeriod": request.report_period
            }

            # 使用流式生成
            async for chunk in qwen_service.generate_document_stream(
                doc_type=request.report_type,
                context=context,
                template_hint="当前使用的是通用模板格式，实际使用时请根据单位规定的模板进行调整。"
            ):
                yield chunk

        except Exception as e:
            logger.error(f"生成报告时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/story",
    summary="生成警示小故事（流式）",
    description="根据故事类型和关键词，AI 生成具有生活感、易记忆的警示小故事，用于宣传教育",
    tags=["文档生成"]
)
async def generate_story_document(
    request: StoryGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成警示小故事接口（SSE 流式输出）
    - story_type: 故事类型（诈骗/被骗、犯罪、工作重大失误等）
    - keywords: 可选关键词或情节提示
    - scene_hint: 可选场景提示

    生成要求：有生活感、不爹味、让人记忆深刻，不需要深刻大道理
    """
    async def generate():
        try:
            context = {
                "storyType": request.story_type,
                "keywords": request.keywords or "",
                "sceneHint": request.scene_hint or ""
            }
            async for chunk in qwen_service.generate_story_stream(
                story_type=request.story_type,
                context=context
            ):
                yield chunk
        except Exception as e:
            logger.error(f"生成警示小故事时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/meeting",
    summary="生成会议纪要（流式）",
    description="根据会议录音转写稿或会议文字随记，AI 流式生成标准会议纪要",
    tags=["文档生成"]
)
async def generate_meeting_document(
    request: MeetingGenerateRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    生成会议纪要接口（SSE 流式输出）
    - input_type: 输入方式（text-文字随记，recording-录音转写稿）
    - meeting_notes: 会议随记（input_type 为 text 时使用）
    - meeting_transcript: 会议转写稿（录音转写后传入）
    - meeting_title / meeting_time: 可选
    """
    source_text = request.meeting_notes or request.meeting_transcript or ""
    if not source_text.strip():
        raise HTTPException(
            status_code=400,
            detail="请提供会议随记或会议转写内容后再生成纪要"
        )

    async def generate():
        try:
            context = {
                "meetingTranscript": source_text,
                "meeting_notes": source_text,
                "meetingTitle": request.meeting_title,
                "meetingTime": request.meeting_time,
            }
            async for chunk in qwen_service.generate_document_stream(
                doc_type="会议纪要",
                context=context,
                template_hint="当前使用的是通用会议纪要格式，实际使用时请根据单位规定的模板进行调整。"
            ):
                yield chunk
        except Exception as e:
            logger.error(f"生成会议纪要时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ========== 新增：国标公文格式相关 API ==========

# 请求模型
class GenerateContentRequest(BaseModel):
    """内容生成请求"""
    doc_type: str = Field(..., description="公文类型：request/report/notice/memo/meeting_minutes")
    form_data: Dict[str, Any] = Field(..., description="表单数据")


class AssembleDocxRequest(BaseModel):
    """组装 docx 请求"""
    doc_type: str = Field(..., description="公文类型：request/report/notice/memo/meeting_minutes")
    sections: Dict[str, str] = Field(..., description="分段内容字典")
    form_data: Dict[str, Any] = Field(default_factory=dict, description="表单数据")


@router.get(
    "/structure/{doc_type}",
    summary="获取公文结构",
    description="获取指定公文类型的分段结构清单",
    tags=["国标公文"]
)
async def get_document_structure(
    doc_type: str,
    token: str = Depends(oauth2_scheme),
):
    """
    获取公文结构接口

    - **doc_type**: 公文类型

    返回该类型公文需要生成哪些段落
    """
    structure = official_doc_service.get_structure(doc_type)
    return {
        "errorCode": 0,
        "message": "success",
        "data": structure
    }


@router.post(
    "/official/generate-content",
    summary="分段生成内容（流式）",
    description="基于表单数据，分段流式生成公文内容",
    tags=["国标公文"]
)
async def generate_official_content(
    request: GenerateContentRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    生成公文内容接口（SSE 流式输出）

    - **doc_type**: 公文类型
    - **form_data**: 表单数据

    返回 SSE 流式数据，客户端通过 EventSource 接收
    """
    async def generate():
        try:
            async for chunk in official_doc_service.stream_generate_content(
                doc_type=request.doc_type,
                form_data=request.form_data,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"生成公文内容时发生异常: {str(e)}")
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/official/assemble",
    summary="组装标准公文 docx",
    description="根据完整内容，组装符合 GB/T 9704-2012 标准的 docx 文件",
    tags=["国标公文"]
)
async def assemble_official_docx(
    request: AssembleDocxRequest,
    token: str = Depends(oauth2_scheme),
):
    """
    组装 docx 接口

    - **doc_type**: 公文类型
    - **sections**: 分段内容字典
    - **form_data**: 表单数据

    返回任务 ID，可通过任务 ID 下载 docx
    """
    try:
        # 合并 sections 和 form_data 为完整内容
        content = {
            **request.form_data,
            **request.sections
        }
        result = official_doc_service.assemble_docx(
            doc_type=request.doc_type,
            content=content,
        )
        return {
            "errorCode": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"组装 docx 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_token_from_header_or_query(
    request: Request,
    token: Optional[str] = Query(None, alias="token"),
) -> str:
    """
    从 header 或 query 参数获取 token
    """
    logger.info(f"[get_token] 开始获取 token, query_token: {token is not None}")

    # 1. 先从 query 参数获取
    found_token = token
    source = "query"

    # 2. 如果 query 没有，尝试从 header 获取
    if not found_token:
        auth_header = request.headers.get("Authorization")
        logger.info(f"[get_token] Authorization header: {auth_header is not None}")
        if auth_header:
            if auth_header.startswith("Bearer "):
                found_token = auth_header[7:]
            else:
                found_token = auth_header
            source = "header"

    if not found_token:
        logger.warning("[get_token] 未找到 token")
        raise HTTPException(status_code=401, detail="未提供认证 token")

    # 输出 token 预览（前10位和后10位），方便调试
    if len(found_token) > 20:
        token_preview = f"{found_token[:10]}...{found_token[-10:]}"
    else:
        token_preview = found_token
    logger.info(f"[get_token] 成功获取 token, 来源: {source}, 长度: {len(found_token)}, 预览: {token_preview}")
    return found_token


@router.get(
    "/download/{task_id}.docx",
    summary="下载生成的 docx",
    description="根据任务 ID 下载生成的标准公文 docx（免 token 验证）",
    tags=["国标公文"]
)
async def download_docx(
    task_id: str,
):
    """
    下载 docx 接口（免 token 验证）

    - **task_id**: 任务 ID

    返回 docx 文件流
    """
    logger.info(f"[download_docx] 收到下载请求（免验证）, task_id: {task_id}")
    try:
        docx_data = official_doc_service.get_docx(task_id)
        logger.info(f"[download_docx] 获取到 docx 数据, 大小: {len(docx_data)} bytes")
        return Response(
            content=docx_data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={task_id}.docx"
            }
        )
    except ValueError as e:
        logger.error(f"[download_docx] 任务不存在: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[download_docx] 下载失败: {str(e)}")
        import traceback
        logger.error(f"[download_docx] 堆栈: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
