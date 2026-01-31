"""
统一的响应封装工具
确保所有 API 响应都遵循统一的 JSON 格式
"""
from typing import Any, Optional, Dict, List
from fastapi.responses import JSONResponse
from fastapi import status

from app.core.errors import ErrorCode


class ResponseModel:
    """统一的响应模型"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        error_code: int = 0,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        成功响应
        
        Args:
            data: 响应数据，可以是任何可序列化的类型（dict, list, str, int等）
            message: 响应消息
            error_code: 错误码，成功时为0
            status_code: HTTP 状态码
        
        Returns:
            JSONResponse: 统一的 JSON 响应
        """
        response_data = {
            "errorCode": error_code,
            "message": message,
            "data": data if data is not None else {}
        }
        return JSONResponse(
            content=response_data, 
            status_code=status_code,
            media_type="application/json; charset=utf-8"
        )
    
    @staticmethod
    def error(
        message: str = "请求失败",
        error_code: int = ErrorCode.UNKNOWN_ERROR,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Any] = None
    ) -> JSONResponse:
        """
        错误响应
        
        Args:
            message: 错误消息
            error_code: 错误码，非0表示错误
            status_code: HTTP 状态码
            data: 可选的错误详情数据
        
        Returns:
            JSONResponse: 统一的 JSON 响应
        """
        response_data = {
            "errorCode": error_code,
            "message": message,
            "data": data if data is not None else {}
        }
        return JSONResponse(
            content=response_data, 
            status_code=status_code,
            media_type="application/json; charset=utf-8"
        )
    
    @staticmethod
    def from_exception(exc: Exception) -> JSONResponse:
        """
        从异常对象创建错误响应
        
        Args:
            exc: 异常对象
        
        Returns:
            JSONResponse: 统一的 JSON 响应
        """
        from app.core.errors import AppException, ErrorCode
        
        if isinstance(exc, AppException):
            return JSONResponse(
                content=exc.to_dict(),
                status_code=exc.status_code,
                media_type="application/json; charset=utf-8"
            )
        else:
            # 未知异常，返回通用错误
            return ResponseModel.error(
                message=str(exc) or "服务器内部错误",
                error_code=ErrorCode.UNKNOWN_ERROR,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "success",
        error_code: int = 0,
        meta: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        分页响应
        
        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页数量
            message: 响应消息
            error_code: 错误码
            meta: 额外的元数据信息
        
        Returns:
            JSONResponse: 包含分页信息的统一 JSON 响应
        """
        response_data = {
            "errorCode": error_code,
            "message": message,
            "data": items,
            "page": {
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        }
        if meta:
            response_data["meta"] = meta
        return JSONResponse(
            content=response_data, 
            status_code=status.HTTP_200_OK,
            media_type="application/json; charset=utf-8"
        )
