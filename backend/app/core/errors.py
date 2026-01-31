"""
统一的错误码定义和自定义异常类
确保所有错误都返回统一的 JSON 格式
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class ErrorCode:
    """错误码定义 - 非 0 表示错误"""
    
    # 成功
    SUCCESS = 0
    
    # 通用错误 (1-99)
    UNKNOWN_ERROR = 1
    INVALID_REQUEST = 2
    MISSING_PARAMETER = 3
    INVALID_PARAMETER = 4
    
    # 认证相关错误 (100-199)
    AUTH_REQUIRED = 100
    AUTH_FAILED = 101
    TOKEN_INVALID = 102
    TOKEN_EXPIRED = 103
    TOKEN_MISSING = 104
    PASSWORD_ERROR = 105
    USER_NOT_FOUND = 106
    PERMISSION_DENIED = 107
    
    # 请求相关错误 (200-299)
    BAD_REQUEST = 200
    VALIDATION_ERROR = 201
    RATE_LIMIT_EXCEEDED = 202
    INVALID_INPUT = 203
    
    # 资源相关错误 (300-399)
    NOT_FOUND = 300
    ALREADY_EXISTS = 301
    RESOURCE_CONFLICT = 302
    
    # 服务器错误 (500-599)
    INTERNAL_ERROR = 500
    DATABASE_ERROR = 501
    EXTERNAL_SERVICE_ERROR = 502
    TIMEOUT_ERROR = 503
    
    # 业务逻辑错误 (600-699)
    BUSINESS_LOGIC_ERROR = 600
    OPERATION_FAILED = 601
    INVALID_STATE = 602
    
    # HTTP 状态码映射到错误码
    HTTP_STATUS_TO_ERROR_CODE = {
        status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
        status.HTTP_401_UNAUTHORIZED: AUTH_REQUIRED,
        status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
        status.HTTP_404_NOT_FOUND: NOT_FOUND,
        status.HTTP_409_CONFLICT: RESOURCE_CONFLICT,
        status.HTTP_429_TOO_MANY_REQUESTS: RATE_LIMIT_EXCEEDED,
        status.HTTP_500_INTERNAL_SERVER_ERROR: INTERNAL_ERROR,
    }
    
    @classmethod
    def get_error_code_from_http_status(cls, http_status: int) -> int:
        """从 HTTP 状态码获取对应的错误码"""
        return cls.HTTP_STATUS_TO_ERROR_CODE.get(http_status, cls.UNKNOWN_ERROR)


class AppException(HTTPException):
    """
    应用自定义异常类
    所有业务异常都应该使用此类，确保返回统一的 JSON 格式
    """
    
    def __init__(
        self,
        message: str = "请求失败",
        error_code: int = ErrorCode.UNKNOWN_ERROR,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        初始化应用异常
        
        Args:
            message: 错误消息
            error_code: 错误码（非 0 表示错误）
            status_code: HTTP 状态码
            data: 可选的错误详情数据
        """
        self.error_code = error_code
        self.data = data or {}
        super().__init__(status_code=status_code, detail=message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于 JSON 响应"""
        return {
            "errorCode": self.error_code,
            "message": self.detail,
            "data": self.data
        }


class BusinessException(AppException):
    """业务逻辑异常"""
    
    def __init__(
        self,
        message: str = "业务处理失败",
        error_code: int = ErrorCode.BUSINESS_LOGIC_ERROR,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )


class AuthException(AppException):
    """认证异常"""
    
    def __init__(
        self,
        message: str = "认证失败",
        error_code: int = ErrorCode.AUTH_FAILED,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
            data=data
        )


class NotFoundException(AppException):
    """资源不存在异常"""
    
    def __init__(
        self,
        message: str = "资源不存在",
        error_code: int = ErrorCode.NOT_FOUND,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )


class ValidationException(AppException):
    """参数验证异常"""
    
    def __init__(
        self,
        message: str = "参数验证失败",
        error_code: int = ErrorCode.VALIDATION_ERROR,
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )
