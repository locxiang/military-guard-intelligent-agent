"""
保卫核心业务智能体 - FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from loguru import logger
import traceback

from app.core.config import settings
from app.core.response import ResponseModel
from app.core.errors import AppException, ErrorCode
from app.core.middleware import (
    SecurityHeadersMiddleware,
    AccessLogMiddleware,
    RateLimitMiddleware,
    InputSanitizationMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时检查并初始化数据库（每个表独立检查）
    """
    logger.info("🚀 应用启动中...")
    
    # 初始化数据库（检查每个表，为空则初始化，结构不一致则同步）
    try:
        from app.core.database_init import initialize_database
        await initialize_database()
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {str(e)}")
        # 根据环境决定是否阻止启动
        if settings.APP_ENV == "production":
            raise  # 生产环境失败则阻止启动
        else:
            logger.warning("⚠️  开发环境：数据库初始化失败，但应用将继续启动")
    
    yield
    
    # 关闭时执行（如果需要）
    logger.info("应用正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    保卫核心业务智能体 API 文档
    
    ## 功能模块
    
    * **认证模块**: 用户登录、登出、Token刷新
    * **案卷管理**: 案卷导入、列表查询、详情查看、全文检索
    * **文档生成**: 智能文档生成、模板管理
    * **知识图谱**: 实体查询、关系查询
    * **统计分析**: 数据统计、可视化分析
    
    ## 认证方式
    
    使用 JWT Token 进行身份认证，在请求头中添加：
    ```
    Authorization: Bearer <token>
    ```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "开发团队",
        "email": "dev@example.com",
    },
    license_info={
        "name": "内部使用",
    },
    tags_metadata=[
        {
            "name": "认证",
            "description": "用户认证相关接口，包括登录、登出、Token刷新等",
        },
        {
            "name": "案卷管理",
            "description": "数字卷宗案卷管理，包括导入、查询、检索等功能",
        },
        {
            "name": "文档生成",
            "description": "智能文档生成功能，支持多种文档类型",
        },
        {
            "name": "知识图谱",
            "description": "知识图谱查询，实体和关系查询",
        },
        {
            "name": "统计分析",
            "description": "数据统计分析，可视化数据",
        },
    ],
)

# 配置CORS（生产环境需要严格配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# 添加安全中间件（符合等保 2.0 规范）
# 顺序很重要：从外到内依次执行
app.add_middleware(InputSanitizationMiddleware)  # 输入清理
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware, calls=settings.RATE_LIMIT_CALLS, period=settings.RATE_LIMIT_PERIOD)  # 速率限制
app.add_middleware(AccessLogMiddleware)  # 访问日志
app.add_middleware(SecurityHeadersMiddleware)  # 安全响应头


@app.get("/")
async def root():
    """根路径"""
    return ResponseModel.success(
        data={
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        message="欢迎使用保卫核心业务智能体API"
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return ResponseModel.success(
        data={"status": "healthy"},
        message="服务运行正常"
    )


# 全局异常处理器 - 确保所有错误都返回统一的 JSON 格式
# 注意：异常处理器的顺序很重要，应该从最具体到最通用


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理应用自定义异常"""
    logger.error(
        f"应用异常 | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"error_code={exc.error_code} | "
        f"message={exc.detail}"
    )
    return ResponseModel.from_exception(exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常"""
    logger.error(
        f"HTTP异常 | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"status_code={exc.status_code} | "
        f"detail={exc.detail}"
    )
    # 将 HTTP 状态码映射到错误码
    error_code = ErrorCode.get_error_code_from_http_status(exc.status_code)
    return ResponseModel.error(
        message=str(exc.detail) or "请求失败",
        error_code=error_code,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    errors = exc.errors()
    error_details = []
    for error in errors:
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    logger.error(
        f"请求验证失败 | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"errors={error_details}"
    )
    return ResponseModel.error(
        message="请求参数验证失败",
        error_code=ErrorCode.VALIDATION_ERROR,
        status_code=400,
        data={"errors": error_details}
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    """处理响应验证异常"""
    errors = exc.errors()
    error_details = []
    for error in errors:
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "input": str(error.get("input", ""))[:100]  # 限制输入长度
        })
    logger.error(
        f"响应验证失败 | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"errors={error_details}"
    )
    return ResponseModel.error(
        message="响应数据验证失败",
        error_code=ErrorCode.INTERNAL_ERROR,
        status_code=500,
        data={"errors": error_details}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    处理所有其他未捕获的异常
    这是最后的异常处理器，确保任何异常都会返回 JSON 格式
    """
    error_traceback = traceback.format_exc()
    logger.error(
        f"未处理的异常 | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"exception_type={type(exc).__name__} | "
        f"message={str(exc)}"
    )
    logger.error(f"异常堆栈: {error_traceback}")
    
    # 在生产环境中，不返回详细的错误信息
    if settings.APP_ENV == "production":
        message = "服务器内部错误"
        error_data = {}
    else:
        message = f"服务器错误: {str(exc)}"
        error_data = {
            "exception_type": type(exc).__name__,
            "traceback": error_traceback
        }
    
    return ResponseModel.error(
        message=message,
        error_code=ErrorCode.INTERNAL_ERROR,
        status_code=500,
        data=error_data
    )


# 注册路由
from app.api.v1 import api_router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
