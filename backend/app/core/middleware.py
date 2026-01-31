"""
安全中间件模块
符合等保 2.0 规范
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import settings
from app.core.response import ResponseModel
from app.core.errors import ErrorCode


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件
    添加符合等保 2.0 规范的安全响应头
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        # 移除可能泄露信息的响应头
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    访问日志中间件
    记录所有请求的访问日志，符合等保 2.0 审计要求
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # 记录请求信息（排除敏感路径）
        if request.url.path not in ["/health", "/metrics"]:
            logger.info(
                f"请求开始 | "
                f"request_id={request_id} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"client_ip={client_ip} | "
                f"user_agent={user_agent[:100]}"
            )
        
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"请求异常 | "
                f"request_id={request_id} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"client_ip={client_ip} | "
                f"process_time={process_time:.3f}s | "
                f"error={str(e)}"
            )
            # 重新抛出异常，让全局异常处理器处理
            # 这样可以确保返回统一的 JSON 格式
            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        if request.url.path not in ["/health", "/metrics"]:
            logger.info(
                f"请求完成 | "
                f"request_id={request_id} | "
                f"method={request.method} | "
                f"path={request.url.path} | "
                f"status_code={response.status_code} | "
                f"client_ip={client_ip} | "
                f"process_time={process_time:.3f}s"
            )
        
        # 添加请求 ID 到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件
    防止暴力破解和 DDoS 攻击
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        """
        初始化速率限制中间件
        
        Args:
            app: FastAPI 应用
            calls: 允许的请求次数
            period: 时间窗口（秒）
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}  # 简单的内存存储，生产环境建议使用 Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查速率限制（排除健康检查和文档路径）
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # 清理过期记录
        current_time = time.time()
        if client_ip in self.clients:
            self.clients[client_ip] = [
                ts for ts in self.clients[client_ip]
                if current_time - ts < self.period
            ]
        else:
            self.clients[client_ip] = []
        
        # 检查是否超过限制
        if len(self.clients[client_ip]) >= self.calls:
            logger.warning(
                f"速率限制触发 | "
                f"client_ip={client_ip} | "
                f"path={request.url.path} | "
                f"requests={len(self.clients[client_ip])}"
            )
            return ResponseModel.error(
                message="请求过于频繁，请稍后再试",
                error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # 记录请求时间
        self.clients[client_ip].append(current_time)
        
        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    输入清理中间件
    防止 SQL 注入和 XSS 攻击（基础防护）
    """
    
    # SQL 注入关键词（简化版）
    SQL_KEYWORDS = [
        "union", "select", "insert", "update", "delete",
        "drop", "create", "alter", "exec", "execute",
        "--", "/*", "*/", ";", "'", '"', "xp_", "sp_"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查查询参数
        for key, value in request.query_params.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for keyword in self.SQL_KEYWORDS:
                    if keyword in value_lower:
                        logger.warning(
                            f"可疑输入检测 | "
                            f"path={request.url.path} | "
                            f"param={key} | "
                            f"value={value[:50]}"
                        )
                        return ResponseModel.error(
                            message="请求参数包含非法字符",
                            error_code=ErrorCode.INVALID_INPUT,
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
        
        return await call_next(request)
