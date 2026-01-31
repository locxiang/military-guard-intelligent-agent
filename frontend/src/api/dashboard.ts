/**
 * 工作台/仪表盘相关 API
 */
import request from './index'

export interface DashboardStats {
  totalCaseFiles: number
  digitizedCount: number
  pendingTasks: number
  todayAdded: number
  trends?: {
    totalCaseFiles?: number
    digitizedCount?: number
    todayAdded?: number
  }
}

export interface RecentCaseFile {
  id: number
  caseNo: string
  caseName?: string
  title: string
  caseType: string
  updatedAt: Date | string
}

export interface DashboardData {
  stats: DashboardStats
  recentCaseFiles: RecentCaseFile[]
}

export const dashboardApi = {
  // 获取工作台数据
  getDashboardData(): Promise<DashboardData> {
    return request.get('/dashboard')
  },
  
  // 获取统计数据
  getStats(): Promise<DashboardStats> {
    return request.get('/dashboard/stats')
  },
  
  // 获取最近访问的案卷
  getRecentCaseFiles(): Promise<RecentCaseFile[]> {
    return request.get('/dashboard/recent-case-files')
  }
}
