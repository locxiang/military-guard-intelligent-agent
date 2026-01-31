"""
文档生成任务模型
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class DocGenerateTask(Base):
    """文档生成任务表模型"""
    __tablename__ = "doc_generate_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="任务ID")
    task_id = Column(String(50), unique=True, index=True, comment="任务编号")
    template_id = Column(String(50), comment="模板ID")
    doc_type = Column(String(50), comment="文档类型")
    status = Column(String(20), default="generating", index=True, comment="状态: generating/completed/failed")
    file_path = Column(String(500), comment="生成文件路径")
    error_message = Column(Text, comment="错误信息")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), comment="创建人ID")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    creator = relationship("User", back_populates="doc_generate_tasks", foreign_keys=[created_by])
