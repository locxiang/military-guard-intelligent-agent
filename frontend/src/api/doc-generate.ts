/**
 * 文档生成相关 API
 */
import request from './index'

export interface DocGenerateRequest {
  doc_type: string
  template_id?: string
  core_elements?: string
  attachments?: number[]
}

export interface DocGenerateResponse {
  task_id: string
  doc_type: string
  status: string
  estimated_time: number
}

export interface Template {
  id: string
  name: string
  doc_type: string
  description: string
}

export interface GenerateTask {
  id: number
  task_id: string
  doc_type: string
  status: string
  createdAt: Date | string
}

export interface CaseDocumentGenerateRequest {
  doc_type: string
  case_info: Record<string, any>
  related_cases?: Array<Record<string, any>>
}

export interface OfficialDocumentGenerateRequest {
  doc_type: string
  form_data: Record<string, any>
  selected_case?: Record<string, any>
}

export interface ReportGenerateRequest {
  report_type: string
  form_data: Record<string, any>
  statistics: Record<string, any>
  report_period?: string
}

/** 会议纪要生成：支持文字随记或录音转写稿 */
export interface MeetingGenerateRequest {
  input_type: 'text' | 'recording'
  meeting_notes?: string
  meeting_transcript?: string
  meeting_title?: string
  meeting_time?: string
}

export interface OfficialDocStructureRequest {
  doc_type: string
}

export interface OfficialDocGenerateContentRequest {
  doc_type: string
  form_data: Record<string, any>
}

export interface OfficialDocAssembleRequest {
  doc_type: string
  sections: Record<string, string>
  form_data: Record<string, any>
}

export interface AIGenerateResponse {
  content: string
  usage?: {
    input_tokens?: number
    output_tokens?: number
    total_tokens?: number
  }
}

export const docGenerateApi = {
  // 生成文档（旧接口，保留兼容）
  generate(data: DocGenerateRequest): Promise<DocGenerateResponse> {
    return request.post('/doc-generate/generate', data)
  },
  
  // 生成案件卷宗（AI）
  generateCaseDocument(data: CaseDocumentGenerateRequest): Promise<AIGenerateResponse> {
    return request.post('/doc-generate/case', data)
  },
  
  // 生成公文（AI）
  generateOfficialDocument(data: OfficialDocumentGenerateRequest): Promise<AIGenerateResponse> {
    return request.post('/doc-generate/official', data)
  },
  
  // 生成报告（AI）
  generateReport(data: ReportGenerateRequest): Promise<AIGenerateResponse> {
    return request.post('/doc-generate/report', data)
  },

  // 获取模板列表
  getTemplates(docType?: string): Promise<{ templates: Template[] }> {
    return request.get('/doc-generate/templates', { params: { doc_type: docType } })
  },
  
  // 查询生成状态
  getStatus(taskId: string): Promise<any> {
    return request.get(`/doc-generate/status/${taskId}`)
  },
  
  // 获取任务列表
  getTasks(): Promise<GenerateTask[]> {
    return request.get('/doc-generate/tasks')
  },

  // 获取公文结构
  getDocStructure(docType: string): Promise<any> {
    return request.get(`/doc-generate/structure/${docType}`)
  },

  // 流式生成公文内容（SSE）
  generateOfficialContent(data: OfficialDocGenerateContentRequest) {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/doc-generate/official/generate-content`
  },

  // 组装标准公文 docx
  assembleOfficialDoc(data: OfficialDocAssembleRequest): Promise<any> {
    return request.post('/doc-generate/official/assemble', data)
  }
}
