"""
文档模板模型
用于文档生成功能中的模板管理
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, func
from app.core.database import Base


class DocTemplate(Base):
    """文档模板表"""
    __tablename__ = "doc_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="模板ID")
    name = Column(String(100), nullable=False, index=True, comment="模板名称")
    doc_type = Column(String(50), nullable=False, index=True, comment="文档类型：案件卷宗/立案报告/请示/汇报/会议纪要等")
    description = Column(String(500), comment="模板说明")
    file_path = Column(String(500), comment="模板文件路径（.docx 公文文件）")
    version = Column(Integer, default=1, comment="版本号")
    status = Column(Integer, default=1, comment="状态：1-启用，0-停用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
