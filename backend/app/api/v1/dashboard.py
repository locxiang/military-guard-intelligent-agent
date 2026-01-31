"""
工作台/仪表盘相关 API
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.get(
    "/dashboard",
    summary="获取工作台数据",
    description="获取工作台统计数据、最近访问的案卷等",
    tags=["工作台"]
)
async def get_dashboard(
    token: str = Depends(oauth2_scheme)
):
    """
    获取工作台数据接口
    
    返回：
    - 统计数据（案卷总数、已数字化、待处理任务、今日新增）
    - 最近访问的案卷列表
    """
    # TODO: 实现真实的查询逻辑
    return {
        "errorCode": 0,
        "message": "success",
        "data": {
            "stats": {
                "totalCaseFiles": 0,
                "digitizedCount": 0,
                "pendingTasks": 0,
                "todayAdded": 0
            },
            "recentCaseFiles": []
        }
    }


@router.get(
    "/dashboard/stats",
    summary="获取统计数据",
    description="获取工作台统计数据",
    tags=["工作台"]
)
async def get_stats(
    token: str = Depends(oauth2_scheme)
):
    """
    获取统计数据接口
    
    返回统计数据：
    - 案卷总数
    - 已数字化数量
    - 待处理任务数
    - 今日新增数量
    """
    # TODO: 实现真实的查询逻辑
    return {
        "errorCode": 0,
        "message": "success",
        "data": {
            "totalCaseFiles": 0,
            "digitizedCount": 0,
            "pendingTasks": 0,
            "todayAdded": 0
        }
    }


@router.get(
    "/dashboard/recent-case-files",
    summary="获取最近访问的案卷",
    description="获取最近访问的案卷列表",
    tags=["工作台"]
)
async def get_recent_case_files(
    token: str = Depends(oauth2_scheme)
):
    """
    获取最近访问的案卷接口
    
    返回最近访问的案卷列表
    """
    # TODO: 实现真实的查询逻辑
    return {
        "errorCode": 0,
        "message": "success",
        "data": []
    }
