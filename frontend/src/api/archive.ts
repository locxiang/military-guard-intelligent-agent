/**
 * 案卷管理相关 API
 */
import { request, type PaginatedResponse } from './index'

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
    personCategory?: string
  }
  charge?: string
  suicideMethod?: string
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

/** 案卷导入 SSE 单条事件（四阶段：upload / parse / analyze / complete） */
export interface ImportStreamEvent {
  stage?: 'upload' | 'parse' | 'analyze' | 'complete'
  fileIndex?: number
  fileName?: string
  total?: number
  progress?: number
  success?: boolean
  reason?: string
}

/** 案卷导入 SSE 任务结束事件 */
export interface ImportStreamTaskDone {
  event: 'task_done'
  task_id: number
  total_files: number
  success_files: number
  failed_files: number
  status: string
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
  
  // 导入案卷（文档上传 → 解析文字 → AI 提取核心内容 → 写入待审核）
  import(formData: FormData, options?: { taskName?: string; sourceDepartment?: string }): Promise<{
    task_id: number
    total_files: number
    success_files: number
    failed_files: number
    status: string
  }> {
    const params: Record<string, string> = {}
    if (options?.taskName) params.task_name = options.taskName
    if (options?.sourceDepartment) params.source_department = options.sourceDepartment
    return request.upload('/case-file/import', formData, { params: Object.keys(params).length ? params : undefined })
  },

  /**
   * 案卷导入（SSE 流式进度）
   * 四个阶段：上传 → 解析 → 智能分析 → 完成
   * @param formData 文件表单
   * @param options 批次名称、来源部门
   * @param onEvent 收到每条 SSE 事件时回调（stage: upload | parse | analyze | complete；event: task_done | error）
   * @returns 流结束后 resolve 最终结果，出错时 reject
   */
  importStream(
    formData: FormData,
    options: { taskName?: string; sourceDepartment?: string },
    onEvent: (data: ImportStreamEvent) => void
  ): Promise<ImportStreamTaskDone> {
    const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const baseUrl = base.startsWith('http') ? base : `${window.location.origin}${base.startsWith('/') ? '' : '/'}${base}`
    const url = new URL('case-file/import/stream', baseUrl.endsWith('/') ? baseUrl : baseUrl + '/')
    if (options.taskName) url.searchParams.set('task_name', options.taskName)
    if (options.sourceDepartment) url.searchParams.set('source_department', options.sourceDepartment)
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    return fetch(url.toString(), {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    }).then(async (response) => {
      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error((err as any).detail || response.statusText)
      }
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error('无法读取响应流')
      let buffer = ''
      let taskDone: ImportStreamTaskDone | null = null
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6)) as ImportStreamEvent | ImportStreamTaskDone
            if ((data as any).event === 'task_done') {
              taskDone = data as ImportStreamTaskDone
            } else if ((data as any).event === 'error') {
              throw new Error((data as any).message || '导入失败')
            } else {
              onEvent(data as ImportStreamEvent)
            }
          } catch (e) {
            if (e instanceof Error && e.message !== '导入失败') {
              // JSON 解析等错误忽略单条，继续读流
              continue
            }
            throw e
          }
        }
      }
      if (!taskDone) throw new Error('未收到任务完成事件')
      return taskDone
    })
  },
  
  // 获取导入任务列表
  getImportTasks(): Promise<any[]> {
    return request.get('/case-file/import-tasks')
  },
  
  // 删除案卷
  delete(id: number): Promise<void> {
    return request.delete(`/case-file/${id}`)
  },

  /** 根据文档重新生成案卷字段（AI 重新提取），用于卷宗审核页「AI 重新生成」 */
  reExtract(caseFileId: number): Promise<{ extractedData: Record<string, any> }> {
    return request.post(`/case-file/re-extract/${caseFileId}`).then((res: any) => res.data ?? res)
  }
}
