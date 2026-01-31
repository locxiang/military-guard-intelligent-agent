"""
导入任务模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class ImportTask(Base):
    """导入任务表模型"""
    __tablename__ = "import_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="任务ID")
    task_name = Column(String(200), comment="任务名称")
    total_files = Column(Integer, default=0, comment="总文件数")
    success_files = Column(Integer, default=0, comment="成功文件数")
    failed_files = Column(Integer, default=0, comment="失败文件数")
    status = Column(String(20), default="pending", index=True, comment="状态: pending/running/paused/completed/failed")
    error_message = Column(Text, comment="错误信息")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), comment="创建人ID")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    creator = relationship("User", back_populates="import_tasks", foreign_keys=[created_by])
