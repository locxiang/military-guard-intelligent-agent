"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(100), comment="真实姓名")
    department = Column(String(100), comment="部门")
    role = Column(String(20), default="user", index=True, comment="角色: admin/user")
    status = Column(Integer, default=1, comment="状态: 1-启用, 0-禁用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    case_files = relationship("CaseFile", back_populates="creator", foreign_keys="CaseFile.created_by")
    import_tasks = relationship("ImportTask", back_populates="creator", foreign_keys="ImportTask.created_by")
    doc_generate_tasks = relationship("DocGenerateTask", back_populates="creator", foreign_keys="DocGenerateTask.created_by")
