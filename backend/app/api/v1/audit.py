"""
日志审计相关 API
提供操作日志查询，用于安全审计与问题追溯
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.response import ResponseModel
from app.core.security import require_admin
from app.models.user import User
from app.core.audit import AuditLog

router = APIRouter()


# 操作类型与业务名称映射（供前端展示）
ACTION_LABELS = {
    "login": "登录",
    "logout": "登出",
    "create": "新增",
    "update": "修改",
    "delete": "删除",
    "query": "查询",
    "export": "导出",
}


@router.get(
    "/list",
    summary="查询操作日志",
    description="分页查询审计日志，支持按时间范围、操作类型、操作人筛选，用于安全审计与问题追溯",
    tags=["日志审计"],
)
async def get_audit_log_list(
    start_date: Optional[str] = Query(None, alias="startDate", description="开始日期，格式 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, alias="endDate", description="结束日期，格式 YYYY-MM-DD"),
    action: Optional[str] = Query(None, description="操作类型: login/logout/create/update/delete/query/export"),
    username: Optional[str] = Query(None, description="操作人用户名（模糊）"),
    status: Optional[str] = Query(None, description="结果状态: success/failure"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    查询操作日志列表
    
    业务流程：管理员按条件筛选操作记录，用于审计谁在何时做了何种操作、结果是否成功。
    """
    conditions = []

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(AuditLog.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")
            conditions.append(AuditLog.created_at <= end_dt)
        except ValueError:
            pass
    if action:
        conditions.append(AuditLog.action == action)
    if username:
        conditions.append(AuditLog.username.like(f"%{username}%"))
    if status:
        conditions.append(AuditLog.status == status)

    # 总数
    count_query = select(func.count(AuditLog.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 列表：按时间倒序
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if conditions:
        query = query.where(and_(*conditions))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.scalars().all()

    items = []
    for r in rows:
        items.append({
            "id": r.id,
            "userId": r.user_id,
            "username": r.username,
            "action": r.action,
            "actionLabel": ACTION_LABELS.get(r.action, r.action or "—"),
            "resourceType": r.resource_type,
            "resourceId": r.resource_id,
            "description": r.description,
            "path": r.path,
            "method": r.method,
            "clientIp": r.client_ip,
            "status": r.status,
            "statusCode": r.status_code,
            "errorMessage": r.error_message,
            "createdAt": r.created_at.isoformat() if r.created_at else None,
        })

    return ResponseModel.paginated(items, total, page, page_size)
