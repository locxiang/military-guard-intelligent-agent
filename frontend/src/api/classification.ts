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

/** 卷宗审核列表项（与卷宗审核入库页展示一致） */
export interface PendingArchiveItem {
  id: number
  caseNo: string
  name: string
  batchName: string
  size: number
  fileType: string
  status: 'pending' | 'archived'
  createdAt: string | null
  extractedData: Record<string, any>
  ocrText: string
  classification: { level1?: string; level2?: string; level3?: string }
  tags: string[]
}

export const classificationApi = {
  // 获取卷宗审核列表（待审核/已入库）
  getPending(params?: { page?: number; pageSize?: number; keyword?: string; status?: string }): Promise<PaginatedResponse<PendingArchiveItem>> {
    const query: Record<string, any> = {
      page: params?.page ?? 1,
      page_size: params?.pageSize ?? 20
    }
    if (params?.keyword) query.keyword = params.keyword
    if (params?.status) query.status = params.status
    return request.get('/classification/pending', { params: query })
  },

  // 保存审核（不改变状态）
  saveReview(caseFileId: number, body: {
    caseName?: string
    incidentTime?: string
    incidentUnit?: string
    personName?: string
    personGender?: string
    personEthnicity?: string
    personBirthplace?: string
    personEnlistTime?: string
    personPosition?: string
    personCategory?: string
    charge?: string
    suicideMethod?: string
    incidentProcess?: string
    investigationProcess?: string
    investigationConclusion?: string
    causeAndLesson?: string
    caseFiling?: string
    judgment?: string
    classification?: { level1?: string; level2?: string; level3?: string }
    tags?: string[]
  }): Promise<void> {
    return request.post(`/classification/save-review/${caseFileId}`, body)
  },

  // 确认入库（审核通过后入库）
  confirmArchive(caseFileId: number, body: {
    caseName?: string
    incidentTime?: string
    incidentUnit?: string
    personName?: string
    personGender?: string
    personEthnicity?: string
    personBirthplace?: string
    personEnlistTime?: string
    personPosition?: string
    personCategory?: string
    charge?: string
    suicideMethod?: string
    incidentProcess?: string
    investigationProcess?: string
    investigationConclusion?: string
    causeAndLesson?: string
    caseFiling?: string
    judgment?: string
    classification?: { level1?: string; level2?: string; level3?: string }
    tags?: string[]
  }): Promise<void> {
    return request.post(`/classification/archive/${caseFileId}`, body)
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
