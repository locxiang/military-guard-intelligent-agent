/**
 * 统计分析相关 API
 */
import request from './index'

export interface StatisticsParams {
  dateRange?: [Date, Date]
  caseType?: string
  department?: string
}

export interface StatisticsData {
  dimension: string
  value: number
  percentage: number
  trend: number
}

export const statisticsApi = {
  // 获取统计数据
  getStatistics(params?: StatisticsParams): Promise<{ data: StatisticsData[] }> {
    return request.get('/statistics', { params })
  },
  
  // 导出报表
  exportReport(params?: StatisticsParams): Promise<Blob> {
    return request.get('/statistics/export', { 
      params,
      responseType: 'blob'
    })
  }
}
