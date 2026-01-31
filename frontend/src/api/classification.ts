/**
 * 智能分类相关 API
 */
import request, { type PaginatedResponse } from './index'

export interface PendingCaseFile {
  id: number
  caseNo: string
  caseName?: string
  title: string
  autoClassification: {
    level1?: string
    level2?: string
    level3?: string
  }
  manualClassification?: string[]
  confidence: number
  metadata?: Record<string, any>
}

export interface ClassificationTree {
  id: string
  name: string
  count: number
  children: Array<{
    id: string
    name: string
    count: number
    children?: Array<{
      id: string
      name: string
      count: number
    }>
  }>
}

export const classificationApi = {
  // 获取待确认分类的案卷列表
  getPending(params?: { page?: number; pageSize?: number }): Promise<PaginatedResponse<PendingCaseFile>> {
    return request.get('/classification/pending', { params })
  },

  // 获取分类树
  getTree(): Promise<ClassificationTree[]> {
    return request.get('/classification/tree').then(res => Array.isArray(res) ? res : (res.data || []))
  },

  // 确认分类
  confirmClassification(caseFileId: number, classification: {
    level1?: string
    level2?: string
    level3?: string
  }): Promise<void> {
    return request.post(`/classification/confirm/${caseFileId}`, classification)
  },

  // 批量确认分类
  batchConfirm(caseFileIds: number[], classification: {
    level1?: string
    level2?: string
    level3?: string
  }): Promise<{ count: number }> {
    return request.post('/classification/batch-confirm', {
      case_file_ids: caseFileIds,
      classification
    })
  },

  // 获取指定分类下的案卷
  getCaseFilesByClassification(classificationId: string, params?: {
    page?: number
    pageSize?: number
  }): Promise<PaginatedResponse<any>> {
    return request.get(`/classification/case-files/${classificationId}`, { params })
  }
}
