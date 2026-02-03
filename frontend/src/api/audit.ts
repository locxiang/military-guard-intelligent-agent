/**
 * 日志审计相关 API
 * 用于查询系统操作记录，支持安全审计与问题追溯
 */
import request, { type PaginatedResponse } from './index'

/** 操作类型 */
export type AuditAction =
  | 'login'
  | 'logout'
  | 'create'
  | 'update'
  | 'delete'
  | 'query'
  | 'export'

export interface AuditLogItem {
  id: number
  userId: number | null
  username: string | null
  action: string
  actionLabel: string
  resourceType: string | null
  resourceId: number | null
  description: string | null
  path: string | null
  method: string | null
  clientIp: string | null
  status: string
  statusCode: number | null
  errorMessage: string | null
  createdAt: string | null
}

export interface AuditLogListParams {
  startDate?: string
  endDate?: string
  action?: AuditAction | string
  username?: string
  status?: 'success' | 'failure'
  page?: number
  pageSize?: number
}

export const auditApi = {
  /** 分页查询操作日志 */
  getList(params: AuditLogListParams): Promise<PaginatedResponse<AuditLogItem>> {
    return request.get('/audit/list', { params }) as Promise<PaginatedResponse<AuditLogItem>>
  }
}
