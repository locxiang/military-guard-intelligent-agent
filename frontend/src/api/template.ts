/**
 * 模板管理相关 API
 */
import request, { type PaginatedResponse } from './index'

export interface DocTemplate {
  id: number
  name: string
  doc_type: string
  description?: string
  file_path?: string
  version: number
  status: 0 | 1
  created_at?: string
  updated_at?: string
}

export interface TemplateListParams {
  doc_type?: string
  keyword?: string
  status?: 0 | 1
  page?: number
  page_size?: number
}

export interface TemplateCreateForm {
  name: string
  doc_type: string
  description?: string
  file: File
}

export interface TemplateUpdateRequest {
  name?: string
  doc_type?: string
  description?: string
  status?: 0 | 1
}

export interface DocTypeOption {
  value: string
  label: string
}

export const templateApi = {
  /** 获取模板列表 */
  getList(params: TemplateListParams): Promise<PaginatedResponse<DocTemplate>> {
    return request.get('/template', { params })
  },

  /** 获取模板详情 */
  getDetail(id: number): Promise<DocTemplate> {
    return request.get(`/template/${id}`)
  },

  /** 新建模板（上传 docx 文件） */
  create(form: TemplateCreateForm): Promise<DocTemplate> {
    const fd = new FormData()
    fd.append('name', form.name)
    fd.append('doc_type', form.doc_type)
    if (form.description) fd.append('description', form.description)
    fd.append('file', form.file)
    return request.post('/template', fd)
  },

  /** 更新模板文件 */
  updateFile(id: number, file: File): Promise<DocTemplate> {
    const fd = new FormData()
    fd.append('file', file)
    return request.put(`/template/${id}/file`, fd)
  },

  /** 更新模板 */
  update(id: number, data: TemplateUpdateRequest): Promise<DocTemplate> {
    return request.put(`/template/${id}`, data)
  },

  /** 删除模板 */
  delete(id: number): Promise<void> {
    return request.delete(`/template/${id}`)
  },

  /** 获取文档类型选项 */
  getDocTypeOptions(): Promise<DocTypeOption[]> {
    return request.get('/template/doc-types/options')
  }
}
