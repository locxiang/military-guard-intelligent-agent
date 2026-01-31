"""
OCR任务模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, JSON, DateTime, Float, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class OcrTask(Base):
    """OCR任务表模型"""
    __tablename__ = "ocr_tasks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="任务ID")
    case_file_id = Column(BigInteger, ForeignKey("case_files.id", ondelete="CASCADE"), nullable=True, comment="关联案卷ID")
    file_name = Column(String(500), comment="文件名")
    file_path = Column(String(500), comment="文件路径")
    file_size = Column(BigInteger, comment="文件大小(字节)")
    file_type = Column(String(50), comment="文件类型")
    status = Column(String(20), default="pending", index=True, comment="状态: pending/processing/completed/failed")
    
    # OCR处理进度
    progress = Column(Integer, default=0, comment="处理进度(0-100)")
    current_step = Column(String(50), comment="当前步骤: upload/preprocess/recognize/parse/complete")
    steps_info = Column(JSON, comment="各步骤详细信息")
    
    # OCR结果
    ocr_text = Column(Text, comment="OCR识别文本")
    accuracy = Column(Float, comment="识别准确率(0-100)")
    original_image_path = Column(String(500), comment="原始图像路径")
    processed_image_path = Column(String(500), comment="处理后的图像路径")
    
    # 元数据和日志
    meta_data = Column(JSON, comment="提取的元数据")  # 使用 meta_data 避免与 SQLAlchemy 的 metadata 保留字段冲突
    logs = Column(JSON, comment="处理日志")
    error_message = Column(Text, comment="错误信息")
    
    # 时间戳
    start_time = Column(DateTime, comment="开始处理时间")
    end_time = Column(DateTime, comment="结束处理时间")
    estimated_time = Column(String(50), comment="预计剩余时间")
    created_at = Column(DateTime, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    case_file = relationship("CaseFile", backref="ocr_tasks", foreign_keys=[case_file_id])
