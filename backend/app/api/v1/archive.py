"""
案卷管理相关 API
"""
import io
import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.response import ResponseModel
from app.core.security import get_current_user, decode_access_token
from app.models.archive import CaseFile
from app.models.import_task import ImportTask
from app.models.user import User
from app.services.qwen_service import qwen_service
from loguru import logger

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 允许的案卷导入格式
ALLOWED_IMPORT_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_IMPORT_FILES = 100
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


def _extract_text_from_docx(content: bytes) -> str:
    """从 DOCX 文件中提取正文（纯文本）。"""
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        parts = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)
        return "\n".join(parts) if parts else ""
    except Exception as e:
        logger.warning(f"解析 DOCX 失败: {e}")
        return ""


def _extract_text_from_pdf(content: bytes) -> str:
    """从 PDF 文件中提取正文（纯文本）。"""
    try:
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        parts = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        return "\n".join(parts).strip() if parts else ""
    except Exception as e:
        logger.warning(f"解析 PDF 失败: {e}")
        return ""


def _extract_text_from_file(content: bytes, filename: str) -> str:
    """根据文件扩展名选择解析方式，返回正文。"""
    name = (filename or "").lower()
    if name.endswith(".docx") or name.endswith(".doc"):
        return _extract_text_from_docx(content)
    if name.endswith(".pdf"):
        return _extract_text_from_pdf(content)
    return ""


def _parse_incident_time(value: Any) -> Optional[datetime]:
    """将字符串或日期解析为 datetime。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    try:
        # 尝试 YYYY-MM-DD HH:mm 或 YYYY-MM-DD
        if " " in value:
            return datetime.strptime(value[:16], "%Y-%m-%d %H:%M")
        return datetime.strptime(value[:10], "%Y-%m-%d")
    except Exception:
        return None


def _generate_case_no() -> str:
    """生成唯一案卷编号。"""
    return f"CF{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"


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
    description="上传案卷文件，系统解析文字后由 AI 提取核心内容，写入待审核模块",
    tags=["案卷管理"]
)
async def import_case_files(
    files: List[UploadFile] = File(...),
    task_name: Optional[str] = Query(None, description="任务名称/批次名称"),
    source_department: Optional[str] = Query(None, description="来源部门"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量导入案卷接口
    
    - **files**: 上传的文件列表（支持 PDF、DOC、DOCX）
    - **task_name**: 导入任务/批次名称（可选）
    - **source_department**: 来源部门（可选）
    
    流程：文档上传 → 解析成文字 → AI 提取核心字段 → 写入待审核案卷（status=pending）
    返回导入任务ID，可通过任务ID查询导入进度；案卷在「卷宗审核入库」中审核后入库。
    """
    logger.info("[案卷导入] 接口被调用")
    try:
        logger.info(f"[案卷导入] 收到 files 数量: {len(files) if files else 0}, task_name={task_name}, source_department={source_department}")
    except Exception:
        pass
    if not files or len(files) > MAX_IMPORT_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"请上传 1～{MAX_IMPORT_FILES} 个文件",
        )
    logger.info(f"[案卷导入] 当前用户 id={current_user.id}, username={getattr(current_user, 'username', '')}")
    upload_dir = getattr(settings, "UPLOAD_DIR", "./data/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    logger.info(f"[案卷导入] 上传目录: {os.path.abspath(upload_dir)}")
    batch_name = (task_name or "").strip() or f"批次_{datetime.now().strftime('%Y%m%d%H%M')}"
    task = ImportTask(
        task_name=batch_name,
        total_files=0,
        success_files=0,
        failed_files=0,
        status="running",
        created_by=current_user.id,
    )
    db.add(task)
    await db.flush()
    task_id = task.id
    logger.info(f"[案卷导入] 创建导入任务 task_id={task_id}, batch_name={batch_name}")
    total = 0
    success_count = 0
    failed_count = 0
    for idx, uf in enumerate(files):
        logger.info(f"[案卷导入] 处理第 {idx + 1}/{len(files)} 个文件: filename={uf.filename}")
        if not uf.filename:
            logger.warning(f"[案卷导入] 第 {idx + 1} 个文件无 filename，跳过")
            failed_count += 1
            continue
        ext = os.path.splitext(uf.filename)[1].lower()
        if ext not in ALLOWED_IMPORT_EXTENSIONS:
            logger.warning(f"[案卷导入] 第 {idx + 1} 个文件扩展名 {ext} 不允许，跳过")
            failed_count += 1
            continue
        total += 1
        logger.info(f"[案卷导入] 读取文件内容: {uf.filename}")
        content = await uf.read()
        logger.info(f"[案卷导入] 读取完成，大小: {len(content)} bytes")
        if len(content) > MAX_FILE_SIZE:
            logger.warning(f"[案卷导入] 文件超过大小限制，跳过")
            failed_count += 1
            continue
        if len(content) == 0:
            logger.warning(f"[案卷导入] 文件为空，跳过")
            failed_count += 1
            continue
        logger.info(f"[案卷导入] 解析文字: {uf.filename}")
        text = _extract_text_from_file(content, uf.filename)
        logger.info(f"[案卷导入] 解析完成，文字长度: {len(text)}")
        if not (text and text.strip()):
            text = "(未识别到文字内容，请人工在卷宗审核入库中补全)"
        safe_name = re.sub(r"[^\w\u4e00-\u9fff.-]", "_", uf.filename)[:200]
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}_{safe_name}"
        file_path = os.path.join(upload_dir, save_name)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            logger.info(f"[案卷导入] 文件已保存: {file_path}")
        except Exception as e:
            logger.error(f"[案卷导入] 保存上传文件失败: {e}")
            failed_count += 1
            continue
        fields = {}
        try:
            logger.info(f"[案卷导入] 调用 AI 提取案卷字段，文本长度: {len(text)}")
            result = qwen_service.extract_case_fields(text)
            logger.info(f"[案卷导入] AI 提取结果: success={result.get('success')}, has_fields={bool(result.get('fields'))}")
            if result.get("success") and isinstance(result.get("fields"), dict):
                fields = result["fields"]
            else:
                logger.warning(f"[案卷导入] AI 提取未返回有效 fields: {result.get('error', '')[:200]}")
        except Exception as e:
            logger.warning(f"[案卷导入] AI 提取案卷字段异常: {e}", exc_info=True)
        case_no = _generate_case_no()
        incident_time = _parse_incident_time(fields.get("incident_time"))
        person_info = fields.get("person_info")
        if isinstance(person_info, dict):
            person_info = dict(person_info)
        else:
            person_info = {}
        case_file = CaseFile(
            case_no=case_no,
            case_name=fields.get("case_name") or (uf.filename or "未命名"),
            title=fields.get("title") or (uf.filename or ""),
            case_type=fields.get("case_type") or "",
            source_department=source_department or fields.get("source_department") or "",
            incident_time=incident_time,
            person_name=fields.get("person_name") or "",
            person_info=person_info,
            charge=fields.get("charge") or "",
            suicide_method=fields.get("suicide_method") or "",
            incident_process=fields.get("incident_process") or "",
            investigation_process_and_conclusion=fields.get("investigation_process_and_conclusion") or "",
            cause_and_lesson=fields.get("cause_and_lesson") or "",
            case_filing=fields.get("case_filing") or "",
            judgment=fields.get("judgment") or "",
            file_path=file_path,
            file_size=len(content),
            file_type=ext.lstrip("."),
            ocr_text=text,
            meta_data={"import_task_id": task_id, "original_filename": uf.filename, "task_name": batch_name},
            tags=[],
            classification_level1=fields.get("classification_level1"),
            classification_level2=fields.get("classification_level2"),
            classification_level3=fields.get("classification_level3"),
            status="pending",
            created_by=current_user.id,
        )
        db.add(case_file)
        success_count += 1
        logger.info(f"[案卷导入] 已创建案卷 case_no={case_no}")
    task.total_files = total
    task.success_files = success_count
    task.failed_files = failed_count
    task.status = "completed"
    logger.info(f"[案卷导入] 准备提交: total={total}, success={success_count}, failed={failed_count}")
    await db.commit()
    logger.info("[案卷导入] 提交成功，返回响应")
    return ResponseModel.success(
        data={
            "task_id": task_id,
            "total_files": total,
            "success_files": success_count,
            "failed_files": failed_count,
            "status": "completed",
        },
        message=f"导入完成：成功 {success_count} 个，失败 {failed_count} 个；请到「卷宗审核入库」中审核后入库",
    )


def _sse_message(data: dict) -> str:
    """封装单条 SSE 数据行。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post(
    "/import/stream",
    summary="批量导入案卷（SSE 流式进度）",
    description="上传案卷文件，以 SSE 流式推送四个阶段进度：上传 → 解析 → 智能分析 → 完成",
    tags=["案卷管理"]
)
async def import_case_files_stream(
    files: List[UploadFile] = File(...),
    task_name: Optional[str] = Query(None, description="任务名称/批次名称"),
    source_department: Optional[str] = Query(None, description="来源部门"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量导入案卷接口（SSE 流式）
    
    流程分四阶段推送进度：上传文件 → 解析内容 → 智能分析 → 完成。
    客户端通过 fetch + ReadableStream 接收事件，按 stage 更新界面。
    """
    if not files or len(files) > MAX_IMPORT_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"请上传 1～{MAX_IMPORT_FILES} 个文件",
        )
    upload_dir = getattr(settings, "UPLOAD_DIR", "./data/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    batch_name = (task_name or "").strip() or f"批次_{datetime.now().strftime('%Y%m%d%H%M')}"
    task = ImportTask(
        task_name=batch_name,
        total_files=0,
        success_files=0,
        failed_files=0,
        status="running",
        created_by=current_user.id,
    )
    db.add(task)
    await db.flush()
    task_id = task.id
    total = 0
    success_count = 0
    failed_count = 0
    file_count = len(files)

    async def _stream():
        nonlocal total, success_count, failed_count
        try:
            for idx, uf in enumerate(files):
                if not uf.filename:
                    failed_count += 1
                    yield _sse_message({
                        "stage": "complete", "fileIndex": idx, "fileName": uf.filename or "",
                        "success": False, "total": file_count, "reason": "无文件名"
                    })
                    continue
                ext = os.path.splitext(uf.filename)[1].lower()
                if ext not in ALLOWED_IMPORT_EXTENSIONS:
                    failed_count += 1
                    yield _sse_message({
                        "stage": "complete", "fileIndex": idx, "fileName": uf.filename,
                        "success": False, "total": file_count, "reason": f"不支持格式 {ext}"
                    })
                    continue
                total += 1
                # 阶段1：上传（读取文件）
                yield _sse_message({
                    "stage": "upload", "fileIndex": idx, "fileName": uf.filename,
                    "total": file_count
                })
                content = await uf.read()
                yield _sse_message({
                    "stage": "upload", "fileIndex": idx, "fileName": uf.filename,
                    "progress": 100, "total": file_count
                })
                if len(content) > MAX_FILE_SIZE or len(content) == 0:
                    failed_count += 1
                    yield _sse_message({
                        "stage": "complete", "fileIndex": idx, "fileName": uf.filename,
                        "success": False, "total": file_count
                    })
                    continue
                # 阶段2：解析内容
                yield _sse_message({
                    "stage": "parse", "fileIndex": idx, "fileName": uf.filename, "total": file_count
                })
                text = _extract_text_from_file(content, uf.filename)
                yield _sse_message({
                    "stage": "parse", "fileIndex": idx, "fileName": uf.filename,
                    "progress": 100, "total": file_count
                })
                if not (text and text.strip()):
                    text = "(未识别到文字内容，请人工在卷宗审核入库中补全)"
                safe_name = re.sub(r"[^\w\u4e00-\u9fff.-]", "_", uf.filename)[:200]
                save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}_{safe_name}"
                file_path = os.path.join(upload_dir, save_name)
                try:
                    with open(file_path, "wb") as f:
                        f.write(content)
                except Exception as e:
                    logger.error(f"[案卷导入] 保存上传文件失败: {e}")
                    failed_count += 1
                    yield _sse_message({
                        "stage": "complete", "fileIndex": idx, "fileName": uf.filename,
                        "success": False, "total": file_count
                    })
                    continue
                # 阶段3：智能分析（AI 提取）
                yield _sse_message({
                    "stage": "analyze", "fileIndex": idx, "fileName": uf.filename, "total": file_count
                })
                fields = {}
                try:
                    result = qwen_service.extract_case_fields(text)
                    if result.get("success") and isinstance(result.get("fields"), dict):
                        fields = result["fields"]
                except Exception as e:
                    logger.warning(f"[案卷导入] AI 提取异常: {e}", exc_info=True)
                yield _sse_message({
                    "stage": "analyze", "fileIndex": idx, "fileName": uf.filename,
                    "progress": 100, "total": file_count
                })
                # 阶段4：完成（写入案卷）
                case_no = _generate_case_no()
                incident_time = _parse_incident_time(fields.get("incident_time"))
                person_info = fields.get("person_info")
                if isinstance(person_info, dict):
                    person_info = dict(person_info)
                else:
                    person_info = {}
                case_file = CaseFile(
                    case_no=case_no,
                    case_name=fields.get("case_name") or (uf.filename or "未命名"),
                    title=fields.get("title") or (uf.filename or ""),
                    case_type=fields.get("case_type") or "",
                    source_department=source_department or fields.get("source_department") or "",
                    incident_time=incident_time,
                    person_name=fields.get("person_name") or "",
                    person_info=person_info,
                    charge=fields.get("charge") or "",
                    suicide_method=fields.get("suicide_method") or "",
                    incident_process=fields.get("incident_process") or "",
                    investigation_process_and_conclusion=fields.get("investigation_process_and_conclusion") or "",
                    cause_and_lesson=fields.get("cause_and_lesson") or "",
                    case_filing=fields.get("case_filing") or "",
                    judgment=fields.get("judgment") or "",
                    file_path=file_path,
                    file_size=len(content),
                    file_type=ext.lstrip("."),
                    ocr_text=text,
                    meta_data={"import_task_id": task_id, "original_filename": uf.filename, "task_name": batch_name},
                    tags=[],
                    classification_level1=fields.get("classification_level1"),
                    classification_level2=fields.get("classification_level2"),
                    classification_level3=fields.get("classification_level3"),
                    status="pending",
                    created_by=current_user.id,
                )
                db.add(case_file)
                success_count += 1
                yield _sse_message({
                    "stage": "complete", "fileIndex": idx, "fileName": uf.filename,
                    "success": True, "total": file_count
                })
            task.total_files = total
            task.success_files = success_count
            task.failed_files = failed_count
            task.status = "completed"
            await db.commit()
            yield _sse_message({
                "event": "task_done",
                "task_id": task_id,
                "total_files": total,
                "success_files": success_count,
                "failed_files": failed_count,
                "status": "completed",
            })
        except Exception as e:
            logger.exception("[案卷导入] SSE 流处理异常")
            yield _sse_message({"event": "error", "message": str(e)})
            await db.rollback()

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
        
        # 人员信息转为前端驼峰命名，便于详情页展示
        pi = case_file.person_info or {}
        person_info_api = {
            "gender": pi.get("gender"),
            "nationality": pi.get("ethnicity"),
            "birthPlace": pi.get("birthplace"),
            "enlistmentTime": pi.get("enlistment_time"),
            "position": pi.get("position"),
            "personCategory": pi.get("person_category"),
        }
        
        case_file_data = {
            "id": case_file.id,
            "caseNo": case_file.case_no,
            "caseName": case_file.case_name or "",
            "title": case_file.title or "",
            "caseType": case_file.case_type or "",
            "sourceDepartment": case_file.source_department or "",
            "incidentTime": case_file.incident_time.isoformat() if case_file.incident_time else None,
            "personName": case_file.person_name or "",
            "personInfo": person_info_api,
            "charge": case_file.charge or "",
            "suicideMethod": case_file.suicide_method or "",
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


def _apply_extracted_fields_to_case_file(case_file: CaseFile, fields: dict) -> None:
    """将 AI 提取的 fields 写入 CaseFile 对象（不提交事务）。"""
    incident_time = _parse_incident_time(fields.get("incident_time"))
    person_info = fields.get("person_info")
    if isinstance(person_info, dict):
        person_info = dict(person_info)
    else:
        person_info = {}
    case_file.case_name = fields.get("case_name") or case_file.case_name
    case_file.title = fields.get("title") or case_file.title
    case_file.case_type = fields.get("case_type") or case_file.case_type
    case_file.source_department = fields.get("source_department") or case_file.source_department
    if incident_time is not None:
        case_file.incident_time = incident_time
    case_file.person_name = fields.get("person_name") or case_file.person_name
    case_file.person_info = person_info
    case_file.charge = fields.get("charge") or case_file.charge
    case_file.suicide_method = fields.get("suicide_method") or case_file.suicide_method
    case_file.incident_process = fields.get("incident_process") or case_file.incident_process
    case_file.investigation_process_and_conclusion = (
        fields.get("investigation_process_and_conclusion") or case_file.investigation_process_and_conclusion
    )
    case_file.cause_and_lesson = fields.get("cause_and_lesson") or case_file.cause_and_lesson
    case_file.case_filing = fields.get("case_filing") or case_file.case_filing
    case_file.judgment = fields.get("judgment") or case_file.judgment
    if fields.get("classification_level1") is not None:
        case_file.classification_level1 = fields.get("classification_level1")
    if fields.get("classification_level2") is not None:
        case_file.classification_level2 = fields.get("classification_level2")
    if fields.get("classification_level3") is not None:
        case_file.classification_level3 = fields.get("classification_level3")


@router.post(
    "/re-extract/{case_file_id}",
    summary="AI 重新生成案卷字段",
    description="根据案卷文档内容重新调用 AI 提取核心字段，更新案卷并返回提取结果（用于卷宗审核页「AI 重新生成」）",
    tags=["案卷管理"]
)
async def re_extract_case_file(
    case_file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    根据案卷的 OCR 文本或原始文件重新提取核心字段，更新案卷记录，并返回与审核页一致的 extractedData。
    """
    try:
        query = select(CaseFile).where(CaseFile.id == case_file_id)
        result = await db.execute(query)
        case_file = result.scalar_one_or_none()
        if not case_file:
            raise HTTPException(status_code=404, detail="案卷不存在")
        text = (case_file.ocr_text or "").strip()
        if not text:
            if case_file.file_path and os.path.isfile(case_file.file_path):
                with open(case_file.file_path, "rb") as f:
                    content = f.read()
                meta = case_file.meta_data or {}
                name = meta.get("original_filename") or ""
                text = _extract_text_from_file(content, name)
            if not (text and text.strip()):
                raise HTTPException(status_code=400, detail="案卷无可用文本，无法重新提取")
        logger.info(f"[案卷重新提取] case_file_id={case_file_id}, 文本长度={len(text)}")
        result = qwen_service.extract_case_fields(text)
        if not result.get("success") or not isinstance(result.get("fields"), dict):
            raise HTTPException(
                status_code=422,
                detail=result.get("error", "AI 提取失败，请稍后重试"),
            )
        fields = result["fields"]
        _apply_extracted_fields_to_case_file(case_file, fields)
        await db.commit()
        await db.refresh(case_file)
        # 返回与审核列表项一致的 extractedData 结构
        pi = case_file.person_info or {}
        extracted_data = {
            "caseName": case_file.case_name or "",
            "incidentTime": case_file.incident_time.strftime("%Y-%m-%d %H:%M") if case_file.incident_time else "",
            "incidentUnit": case_file.source_department or "",
            "personName": case_file.person_name or "",
            "personGender": pi.get("gender", ""),
            "personEthnicity": pi.get("ethnicity", ""),
            "personBirthplace": pi.get("birthplace", ""),
            "personEnlistTime": pi.get("enlistment_time", ""),
            "personPosition": pi.get("position", ""),
            "personCategory": pi.get("person_category", ""),
            "charge": case_file.charge or "",
            "suicideMethod": case_file.suicide_method or "",
            "incidentProcess": case_file.incident_process or "",
            "investigationProcess": case_file.investigation_process_and_conclusion or "",
            "investigationConclusion": "",
            "causeAndLesson": case_file.cause_and_lesson or "",
            "caseFiling": case_file.case_filing or "",
            "judgment": case_file.judgment or "",
        }
        return ResponseModel.success(
            data={"extractedData": extracted_data},
            message="已根据文档重新生成字段",
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("[案卷重新提取] 异常")
        raise HTTPException(status_code=500, detail=str(e))


def _get_token_for_file(request: Request) -> str:
    """从 Query 或 Header 获取 Token，便于 iframe 预览时传 token。"""
    t = request.query_params.get("token")
    if t:
        return t
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:]
    raise HTTPException(status_code=401, detail="未提供认证")


@router.get(
    "/file/{case_file_id}",
    summary="获取案卷文件",
    description="根据案卷ID返回上传的原始文件，用于预览或下载；支持 Query 传 token 便于 iframe 预览",
    tags=["案卷管理"]
)
async def get_case_file_file(
    case_file_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """返回案卷关联的原始文件（PDF/DOCX等）。支持 ?token= 或 Authorization Header。"""
    token = _get_token_for_file(request)
    try:
        decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="认证无效或已过期")
    query = select(CaseFile).where(CaseFile.id == case_file_id)
    result = await db.execute(query)
    case_file = result.scalar_one_or_none()
    if not case_file:
        raise HTTPException(status_code=404, detail="案卷不存在")
    path = case_file.file_path
    if not path or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="文件不存在")
    meta = case_file.meta_data or {}
    filename = meta.get("original_filename") or f"case_file_{case_file_id}"
    return FileResponse(path, filename=filename)


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
