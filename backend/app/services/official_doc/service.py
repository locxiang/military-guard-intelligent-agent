"""
国标公文生成对外服务聚合
"""
from typing import Dict, Any, AsyncGenerator
from docx import Document
import io
import uuid
from datetime import datetime
from loguru import logger

from app.services.official_doc.content_generator import content_generator
from app.services.official_doc.structure_config import DocType, get_doc_structure_dict
from app.services.official_doc.builders.request_builder import RequestDocumentBuilder
from app.services.official_doc.builders.report_builder import ReportDocumentBuilder
from app.services.official_doc.builders.notice_builder import NoticeDocumentBuilder
from app.services.official_doc.builders.memo_builder import MemoDocumentBuilder
from app.services.official_doc.builders.meeting_builder import MeetingMinutesBuilder


class OfficialDocService:
    """国标公文生成服务"""

    def __init__(self):
        # Builder 映射
        self._builders = {
            DocType.REQUEST: RequestDocumentBuilder,
            DocType.REPORT: ReportDocumentBuilder,
            DocType.NOTICE: NoticeDocumentBuilder,
            DocType.MEMO: MemoDocumentBuilder,
            DocType.MEETING_MINUTES: MeetingMinutesBuilder,
        }
        # 存储生成的任务（临时，生产环境应使用数据库）
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def get_structure(self, doc_type: str) -> Dict[str, Any]:
        """
        获取公文结构

        Args:
            doc_type: 公文类型

        Returns:
            结构信息
        """
        return {
            "doc_type": doc_type,
            "sections": get_doc_structure_dict(doc_type),
        }

    async def stream_generate_content(
        self, doc_type: str, form_data: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        流式生成内容

        Args:
            doc_type: 公文类型
            form_data: 表单数据

        Yields:
            SSE 格式数据
        """
        async for chunk in content_generator.stream_generate_all(doc_type, form_data):
            yield chunk

    def assemble_docx(self, doc_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        组装 docx

        Args:
            doc_type: 公文类型
            content: 内容字典

        Returns:
            任务信息
        """
        task_id = f"DOC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        try:
            # 获取 builder
            BuilderClass = self._builders.get(doc_type)
            if not BuilderClass:
                raise ValueError(f"不支持的公文类型: {doc_type}")

            # 构建文档
            builder = BuilderClass()
            doc = builder.build(content)

            # 保存到内存
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            # 存储任务
            self._tasks[task_id] = {
                "task_id": task_id,
                "doc_type": doc_type,
                "status": "completed",
                "content": content,
                "docx_data": buffer.getvalue(),
                "created_at": datetime.now(),
            }

            logger.info(f"成功组装 docx: {task_id}")

            return {
                "task_id": task_id,
                "status": "completed",
                "docx_url": f"/api/v1/doc-generate/download/{task_id}.docx",
            }

        except Exception as e:
            logger.error(f"组装 docx 失败: {str(e)}")
            raise

    def get_docx(self, task_id: str) -> bytes:
        """
        获取生成的 docx

        Args:
            task_id: 任务 ID

        Returns:
            docx 二进制数据
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        return task["docx_data"]

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务信息

        Args:
            task_id: 任务 ID

        Returns:
            任务信息
        """
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        return {
            "task_id": task["task_id"],
            "doc_type": task["doc_type"],
            "status": task["status"],
            "created_at": task["created_at"].isoformat() if task.get("created_at") else None,
        }


# 创建全局实例
official_doc_service = OfficialDocService()
