"""
案卷模型
"""
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class CaseFile(Base):
    """案卷表模型"""
    __tablename__ = "case_files"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="案卷ID")
    case_no = Column(String(50), unique=True, index=True, comment="案卷编号")
    
    # 核心字段：卷宗名（时间+事发单位-人员类别+姓名+涉案罪名）
    case_name = Column(String(500), index=True, comment="卷宗名: 时间+事发单位-人员类别+姓名+涉案罪名(自杀方式、线索)")
    
    # 核心字段：内容相关
    incident_time = Column(DateTime, index=True, comment="发生时间")
    person_name = Column(String(100), index=True, comment="姓名")
    person_info = Column(JSON, comment="人员基本情况: 性别、民族、出生地、入伍时间、部职别、人员类别")
    charge = Column(String(200), comment="涉案罪名")
    suicide_method = Column(Text, comment="自杀方式或线索（若涉及）")
    incident_process = Column(Text, comment="事发经过")
    investigation_process_and_conclusion = Column(Text, comment="侦查调查过程及结论")
    cause_and_lesson = Column(Text, comment="原因教训")
    case_filing = Column(Text, comment="立案情况")
    judgment = Column(Text, comment="判决情况")
    
    # 原有字段
    title = Column(String(500), comment="标题")
    case_type = Column(String(50), index=True, comment="案卷类型")
    source_department = Column(String(100), comment="来源部门")
    file_path = Column(String(500), comment="文件路径")
    file_size = Column(BigInteger, comment="文件大小(字节)")
    file_type = Column(String(50), comment="文件类型")
    ocr_text = Column(Text, comment="OCR识别文本")
    meta_data = Column(JSON, comment="元数据")  # 使用 meta_data 避免与 SQLAlchemy 的 metadata 保留字段冲突
    tags = Column(JSON, comment="标签")
    classification_level1 = Column(String(50), comment="一级分类")
    classification_level2 = Column(String(50), comment="二级分类")
    classification_level3 = Column(String(50), comment="三级分类")
    timeline = Column(JSON, comment="案件时间线: [{time, event, type, typeLabel, description, timestamp}]")
    status = Column(String(20), default="pending", index=True, comment="状态: pending/processing/completed/failed")
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), comment="创建人ID")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    creator = relationship("User", back_populates="case_files", foreign_keys=[created_by])
    
    # 全文索引（MySQL 需要单独创建，这里只是标记）
    __table_args__ = (
        Index("idx_fulltext", "case_name", "title", "ocr_text", mysql_prefix="FULLTEXT"),
    )
