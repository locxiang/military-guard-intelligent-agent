/**
 * 内容审查相关 API
 * 上传公文 docx，获取错别字、用词不当、公文规范等修改意见
 */
import { request } from './index'

/** 单条审查意见 */
export interface ContentReviewIssue {
  type: '错别字' | '用词不当' | '公文规范'
  location?: string
  original?: string
  suggestion?: string
  reason?: string
}

/** 审查结果 */
export interface ContentReviewResult {
  issues: ContentReviewIssue[]
  summary: string
  extractedLength?: number
}

export const contentReviewApi = {
  /**
   * 上传公文 docx，进行内容审查
   * 返回错别字、用词不当、不符合政府/部队公文写法等问题及修改建议
   */
  review(file: File): Promise<ContentReviewResult> {
    const formData = new FormData()
    formData.append('file', file)
    return request.upload<ContentReviewResult>('/content-review/review', formData)
  }
}
