"""
审计日志模块
符合等保 2.0 审计要求
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """
    审计日志表模型
    记录所有重要操作，符合等保 2.0 审计要求
    """
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    
    # 用户信息
    user_id = Column(BigInteger, nullable=True, index=True, comment="用户ID")
    username = Column(String(50), nullable=True, index=True, comment="用户名")
    
    # 操作信息
    action = Column(String(50), nullable=False, index=True, comment="操作类型: login/logout/create/update/delete/query/export")
    resource_type = Column(String(50), nullable=True, index=True, comment="资源类型: user/case_file/document")
    resource_id = Column(BigInteger, nullable=True, comment="资源ID")
    
    # 请求信息
    request_id = Column(String(100), nullable=True, index=True, comment="请求ID")
    method = Column(String(10), nullable=True, comment="HTTP方法")
    path = Column(String(500), nullable=True, comment="请求路径")
    client_ip = Column(String(50), nullable=True, index=True, comment="客户端IP")
    user_agent = Column(String(500), nullable=True, comment="User Agent")
    
    # 操作详情
    description = Column(Text, nullable=True, comment="操作描述")
    details = Column(Text, nullable=True, comment="操作详情(JSON)")
    
    # 结果信息
    status = Column(String(20), nullable=False, index=True, comment="状态: success/failure")
    status_code = Column(Integer, nullable=True, comment="HTTP状态码")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 时间信息
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True, comment="创建时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "client_ip": self.client_ip,
            "status": self.status,
            "status_code": self.status_code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLogger:
    """
    审计日志记录器
    """
    
    @staticmethod
    async def log(
        db,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        request_id: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        description: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        记录审计日志
        
        Args:
            db: 数据库会话
            action: 操作类型
            user_id: 用户ID
            username: 用户名
            resource_type: 资源类型
            resource_id: 资源ID
            request_id: 请求ID
            method: HTTP方法
            path: 请求路径
            client_ip: 客户端IP
            user_agent: User Agent
            description: 操作描述
            details: 操作详情
            status: 状态 (success/failure)
            status_code: HTTP状态码
            error_message: 错误信息
        """
        import json
        
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent[:500] if user_agent else None,
            description=description,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            status=status,
            status_code=status_code,
            error_message=error_message[:1000] if error_message else None,
        )
        
        db.add(audit_log)
        await db.flush()  # 刷新但不提交，允许在事务中记录日志
        # 注意：如果外部已有事务，这里只 flush 不 commit
        # 如果需要在事务外独立记录日志，可以在这里 commit
        
        # 同时记录到应用日志
        from loguru import logger
        logger.info(
            f"审计日志 | "
            f"action={action} | "
            f"user_id={user_id} | "
            f"username={username} | "
            f"resource_type={resource_type} | "
            f"resource_id={resource_id} | "
            f"status={status} | "
            f"client_ip={client_ip}"
        )
    
    @staticmethod
    async def log_login(
        db,
        username: str,
        status: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        error_message: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        """记录登录日志"""
        await AuditLogger.log(
            db=db,
            action="login",
            user_id=user_id,
            username=username,
            resource_type="auth",
            request_id=request_id,
            method="POST",
            path="/api/v1/auth/login",
            client_ip=client_ip,
            user_agent=user_agent,
            description=f"用户 {username} 登录",
            status=status,
            status_code=200 if status == "success" else 401,
            error_message=error_message,
        )
    
    @staticmethod
    async def log_logout(
        db,
        user_id: int,
        username: str,
        client_ip: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """记录登出日志"""
        await AuditLogger.log(
            db=db,
            action="logout",
            user_id=user_id,
            username=username,
            resource_type="auth",
            request_id=request_id,
            method="POST",
            path="/api/v1/auth/logout",
            client_ip=client_ip,
            description=f"用户 {username} 登出",
            status="success",
            status_code=200,
        )
    
    @staticmethod
    async def log_operation(
        db,
        action: str,
        user_id: int,
        username: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        description: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        request_id: Optional[str] = None,
        client_ip: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
    ) -> None:
        """记录一般操作日志"""
        await AuditLogger.log(
            db=db,
            action=action,
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            description=description,
            details=details,
            status=status,
            status_code=200 if status == "success" else 500,
        )
