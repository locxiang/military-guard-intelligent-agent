// 工具函数

// 高亮文本
export const highlightText = (text: string, keyword: string): string => {
  if (!text || !keyword) return text || ''
  const trimmedKeyword = keyword.trim()
  if (!trimmedKeyword) return String(text)
  const regex = new RegExp(`(${trimmedKeyword})`, 'gi')
  return String(text).replace(regex, '<mark class="highlight-mark">$1</mark>')
}

// 格式化日期时间
export const formatDateTime = (date: Date | string): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化日期
export const formatDate = (date: Date | string): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化文件大小
export const formatFileSize = (bytes: number): string => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 获取状态类型
export const getStatusType = (status: string): string => {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
export const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 获取文件名
export const getFileName = (filePath: string): string => {
  if (!filePath) return '未知文件'
  const parts = filePath.split('/')
  return parts[parts.length - 1] || filePath
}

// 判断文件类型
export const isPdfFile = (fileType: string): boolean => {
  if (!fileType) return false
  return ['pdf', 'PDF'].includes(fileType)
}

export const isImageFile = (fileType: string): boolean => {
  if (!fileType) return false
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'JPG', 'JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
  return imageTypes.includes(fileType)
}

export const isWordFile = (fileType: string): boolean => {
  if (!fileType) return false
  const wordTypes = ['doc', 'docx', 'DOC', 'DOCX']
  return wordTypes.includes(fileType)
}

export const isExcelFile = (fileType: string): boolean => {
  if (!fileType) return false
  const excelTypes = ['xls', 'xlsx', 'XLS', 'XLSX']
  return excelTypes.includes(fileType)
}

// 获取时间线图标
export const getTimelineIcon = (type: string, icons: any): any => {
  const iconMap: Record<string, any> = {
    incident: icons.Warning,
    investigation: icons.Search,
    filing: icons.Flag,
    judgment: icons.CircleCheck,
    system: icons.EditPen
  }
  return iconMap[type] || icons.Clock
}

// 获取时间线标签类型
export const getTimelineTagType = (type: string): string => {
  const typeMap: Record<string, string> = {
    incident: 'danger',
    investigation: 'warning',
    filing: 'info',
    judgment: 'success',
    system: ''
  }
  return typeMap[type] || ''
}
