"""
数据模型模块
导入所有模型
"""
from app.core.database import Base
from app.models.user import User
from app.models.archive import CaseFile
from app.models.import_task import ImportTask
from app.models.doc_generate_task import DocGenerateTask
from app.models.ocr_task import OcrTask
from app.models.template import DocTemplate

# 导出所有模型
__all__ = ["Base", "User", "CaseFile", "ImportTask", "DocGenerateTask", "OcrTask", "DocTemplate"]
