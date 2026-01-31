/**
 * OCR数字化相关 API
 */
import request, { type PaginatedResponse } from './index'

export interface OcrTask {
  id: number
  caseFileId?: number
  fileName: string
  fileSize: number
  fileType: string
  status: string
  progress: number
  currentStep?: string
  accuracy?: number
  ocrText?: string
  originalImage?: string
  startTime?: string
  estimatedTime?: string
  errorMessage?: string
  steps?: Record<string, string>
  logs?: Array<{ time: string; type: string; message: string }>
  metadata?: Record<string, any>
}

export const ocrApi = {
  // 获取OCR任务列表
  getTasks(params?: { status?: string; page?: number; pageSize?: number }): Promise<PaginatedResponse<OcrTask>> {
    return request.get('/ocr/tasks', { params })
  },

  // 获取OCR任务详情
  getTaskDetail(taskId: number): Promise<OcrTask> {
    return request.get(`/ocr/tasks/${taskId}`)
  },

  // 启动OCR任务
  startTask(taskId: number): Promise<{ taskId: number }> {
    return request.post(`/ocr/tasks/${taskId}/start`)
  },

  // 批量启动OCR任务
  batchStartTasks(taskIds: number[]): Promise<{ startedCount: number }> {
    return request.post('/ocr/tasks/batch-start', { task_ids: taskIds })
  },

  // 重试OCR任务
  retryTask(taskId: number): Promise<{ taskId: number }> {
    return request.post(`/ocr/tasks/${taskId}/retry`)
  },

  // 保存OCR校正结果
  saveCorrect(taskId: number, correctedText: string): Promise<void> {
    return request.put(`/ocr/tasks/${taskId}/correct`, null, {
      params: { corrected_text: correctedText }
    })
  }
}
