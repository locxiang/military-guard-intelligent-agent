/**
 * 案卷管理相关 API
 */
import request, { type PaginatedResponse } from './index'

export interface CaseFile {
  id: number
  caseNo: string
  caseName: string
  title: string
  caseType: string
  sourceDepartment: string
  incidentTime?: Date | string
  personName?: string
  personInfo?: {
    gender?: string
    nationality?: string
    birthPlace?: string
    enlistmentTime?: string
    position?: string
  }
  incidentProcess?: string
  investigationProcessAndConclusion?: string
  causeAndLesson?: string
  caseFiling?: string
  judgment?: string
  filePath: string
  fileSize: number
  fileType: string
  ocrText?: string
  metadata?: Record<string, any>
  tags?: string[]
  classificationLevel1?: string
  classificationLevel2?: string
  classificationLevel3?: string
  timeline?: Array<{
    time: string
    event: string
    type: 'incident' | 'investigation' | 'filing' | 'judgment' | 'system'
    typeLabel: string
    description?: string
    timestamp: number
  }>
  status: string
  createdBy?: number
  createdAt: Date | string
  updatedAt: Date | string
}

export interface CaseFileListParams {
  keyword?: string
  caseType?: string
  status?: string
  dateRange?: [Date, Date]
  page?: number
  pageSize?: number
}

export const caseFileApi = {
  // 获取案卷列表
  getList(params: CaseFileListParams): Promise<PaginatedResponse<CaseFile>> {
    // 将驼峰命名转换为下划线命名，以匹配后端 API
    const queryParams: Record<string, any> = {
      keyword: params.keyword,
      case_type: params.caseType,
      status: params.status,
      page: params.page || 1,
      page_size: params.pageSize || 20
    }
    // 处理日期范围
    if (params.dateRange && params.dateRange.length === 2) {
      queryParams.start_date = params.dateRange[0]
      queryParams.end_date = params.dateRange[1]
    }
    return request.get('/case-file/list', { params: queryParams })
  },
  
  // 获取案卷详情
  getDetail(id: number): Promise<CaseFile> {
    return request.get(`/case-file/detail/${id}`)
  },
  
  // 搜索案卷（全文检索）
  search(params: {
    keyword: string
    searchMode?: 'fuzzy' | 'exact'
    searchScope?: string
    caseType?: string
    department?: string
    sortBy?: 'relevance' | 'time' | 'title'
    page?: number
    pageSize?: number
  }): Promise<PaginatedResponse<{
    id: number
    caseNo: string
    caseName: string
    title: string
    caseType: string
    sourceDepartment: string
    date: string
    relevance: number
    relevanceScore: string
    fragments: string[]
    tags: string[]
  }> & { meta: { took: number; keyword: string } }> {
    // 将参数转换为查询字符串
    const queryParams: Record<string, any> = {
      keyword: params.keyword,
      search_mode: params.searchMode || 'fuzzy',
      search_scope: params.searchScope || 'title,content,metadata,tags',
      sort_by: params.sortBy || 'relevance',
      page: params.page || 1,
      page_size: params.pageSize || 20
    }
    if (params.caseType) queryParams.case_type = params.caseType
    if (params.department) queryParams.department = params.department
    
    return request.post('/case-file/search', null, { params: queryParams })
  },
  
  // 导入案卷
  import(formData: FormData): Promise<{ taskId: string }> {
    return request.upload('/case-file/import', formData)
  },
  
  // 获取导入任务列表
  getImportTasks(): Promise<any[]> {
    return request.get('/case-file/import-tasks')
  },
  
  // 删除案卷
  delete(id: number): Promise<void> {
    return request.delete(`/case-file/${id}`)
  }
}
