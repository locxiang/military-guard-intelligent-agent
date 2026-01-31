<template>
  <div class="archive-progress-detail-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题和返回按钮 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header mb-4">
        <div class="flex items-center gap-4">
          <el-button type="text" @click="goBack" class="back-button">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </el-button>
          <div class="flex-1">
            <h2 class="gov-card-title">任务详情</h2>
            <p class="gov-card-subtitle">{{ taskInfo?.batchName || '未命名批次' }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-loading="loading" class="detail-content">
      <div v-if="taskInfo" class="space-y-6">
        <!-- 任务基本信息 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">基本信息</h3>
          </div>
          <div class="task-detail-info">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="info-item">
                <div class="info-label">批次名称</div>
                <div class="info-value">{{ taskInfo.batchName || '未命名批次' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">任务状态</div>
                <div class="info-value">
                  <el-tag :type="getRecordStatusType(taskInfo.status)" size="small">
                    {{ getRecordStatusText(taskInfo.status) }}
                  </el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">创建时间</div>
                <div class="info-value">{{ formatDate(taskInfo.createdAt) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">总文件数</div>
                <div class="info-value">{{ taskInfo.totalFiles }} 个</div>
              </div>
            </div>
            
            <!-- 统计信息 -->
            <div class="stats-row mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-6">
                <div class="stat-item">
                  <div class="stat-label">成功</div>
                  <div class="stat-value text-green-600">{{ taskInfo.successFiles }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">失败</div>
                  <div class="stat-value text-red-600">{{ taskInfo.failedFiles || 0 }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">处理中</div>
                  <div class="stat-value text-yellow-600">{{ getProcessingFileCount() }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-label">等待处理</div>
                  <div class="stat-value text-gray-500">{{ getPendingFileCount() }}</div>
                </div>
              </div>
            </div>
            
            <!-- 整体进度条 -->
            <div v-if="taskInfo.status === 'running'" class="mt-4">
              <div class="flex items-center justify-between mb-2">
                <span class="progress-label">整体进度</span>
                <span class="progress-percentage">{{ getTaskProgress(taskInfo) }}%</span>
              </div>
              <el-progress
                :percentage="getTaskProgress(taskInfo)"
                :stroke-width="10"
                :show-text="false"
              />
            </div>
          </div>
        </div>

        <!-- 文件处理详情 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <h3 class="gov-card-title">文件处理详情</h3>
              <div class="file-stats text-sm text-gray-500">
                <span>共 {{ taskInfo.files?.length || 0 }} 个文件</span>
                <span class="mx-2">|</span>
                <span class="text-green-600">已完成 {{ getCompletedFileCount() }}</span>
                <span v-if="getProcessingFileCount() > 0" class="ml-2 text-yellow-600">处理中 {{ getProcessingFileCount() }}</span>
                <span v-if="getFailedFileCount() > 0" class="ml-2 text-red-600">失败 {{ getFailedFileCount() }}</span>
              </div>
            </div>
          </div>
          
          <div class="file-detail-list">
            <div
              v-for="(file, index) in taskInfo.files || []"
              :key="index"
              class="file-detail-item"
            >
              <div class="file-detail-header">
                <div class="flex items-center gap-3 flex-1 min-w-0">
                  <el-icon :class="['file-status-icon', file.status]">
                    <CircleCheck v-if="file.status === 'completed'" />
                    <Loading v-else-if="file.status === 'processing'" class="animate-spin" />
                    <CircleClose v-else-if="file.status === 'failed'" />
                    <Clock v-else />
                  </el-icon>
                  <div class="flex-1 min-w-0">
                    <div class="file-detail-name truncate">{{ file.name }}</div>
                    <div v-if="file.processStage" class="file-stage text-xs text-gray-500 mt-1">
                      当前阶段：{{ file.processStage }}
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                  <el-tag size="small" :type="getFileStatusType(file.status)">
                    {{ getFileStatusText(file.status) }}
                  </el-tag>
                  <span class="file-detail-size">{{ formatFileSize(file.size || 0) }}</span>
                </div>
              </div>
              
              <!-- 处理进度 -->
              <div v-if="file.status === 'processing'" class="file-progress mt-2">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs text-gray-500">处理进度</span>
                  <span class="text-xs text-gray-500">{{ file.progress || 0 }}%</span>
                </div>
                <el-progress :percentage="file.progress || 0" :stroke-width="6" :show-text="false" />
              </div>
              
              <!-- 处理时间信息 -->
              <div v-if="file.processTime" class="file-time text-xs text-gray-500 mt-2">
                <el-icon :size="12"><Clock /></el-icon>
                <span class="ml-1">处理时间：{{ file.processTime }}</span>
              </div>
              
              <!-- 错误信息 -->
              <div v-if="file.error" class="file-error mt-2">
                <div class="flex items-start gap-2">
                  <el-icon class="error-icon"><Warning /></el-icon>
                  <div class="flex-1">
                    <div class="error-title text-sm font-medium text-red-600">处理失败</div>
                    <div class="error-message text-sm text-red-500 mt-1">{{ file.error }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 成功信息 -->
              <div v-if="file.status === 'completed' && file.completedTime" class="file-success text-xs text-green-600 mt-2">
                <el-icon :size="12"><CircleCheck /></el-icon>
                <span class="ml-1">完成时间：{{ file.completedTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <el-icon :size="48"><DocumentCopy /></el-icon>
        <p class="mt-4">任务不存在</p>
        <el-button type="primary" @click="goBack" class="mt-4">返回列表</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  CircleCheck,
  Loading,
  CircleClose,
  Clock,
  Warning,
  DocumentCopy
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const taskInfo = ref<any>(null)

// 生成演示文件列表 - 每个文件代表一个独立的卷宗
const generateDemoFiles = (count: number, successCount: number, status: string) => {
  // 卷宗名称列表 - 每个文件是一个完整的卷宗
  const archiveNames = [
    '张某案卷宗.pdf',
    '李某案卷宗.pdf',
    '王某案卷宗.pdf',
    '赵某案卷宗.pdf',
    '刘某案卷宗.pdf',
    '陈某案卷宗.pdf',
    '周某案卷宗.pdf',
    '吴某案卷宗.pdf',
    '郑某案卷宗.pdf',
    '孙某案卷宗.pdf',
    '钱某案卷宗.pdf',
    '冯某案卷宗.pdf',
    '韩某案卷宗.pdf',
    '杨某案卷宗.pdf',
    '朱某案卷宗.pdf',
    '秦某案卷宗.pdf',
    '许某案卷宗.pdf',
    '何某案卷宗.pdf',
    '吕某案卷宗.pdf',
    '施某案卷宗.pdf'
  ]
  
  const processStages = ['上传文件', '解析内容', '智能分析', '文字识别', '内容提取']
  
  const now = Date.now()
  
  return Array.from({ length: count }, (_, i) => {
    // 每个文件是一个独立的卷宗
    const fileName = archiveNames[i] || `案件卷宗_${i + 1}.pdf`
    const isSuccess = i < successCount
    const fileStatus = status === 'running' && i < successCount ? 'completed' : 
                      status === 'running' && i === successCount ? 'processing' :
                      status === 'running' ? 'pending' :
                      isSuccess ? 'completed' : 'failed'
    
    const progress = fileStatus === 'processing' ? Math.floor(30 + Math.random() * 40) : 
                    (fileStatus === 'completed' ? 100 : 0)
    
    // 生成处理时间
    const processTime = fileStatus === 'processing' ? 
      new Date(now - Math.floor(Math.random() * 3600000)).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }) : undefined
    
    const completedTime = fileStatus === 'completed' ?
      new Date(now - Math.floor(Math.random() * 86400000)).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }) : undefined
    
    return {
      name: fileName,
      status: fileStatus,
      progress: progress,
      size: Math.floor(Math.random() * 20 * 1024 * 1024) + 5 * 1024 * 1024, // 5MB - 25MB (卷宗文件通常较大)
      processStage: fileStatus === 'processing' ? processStages[Math.floor(Math.random() * processStages.length)] : undefined,
      processTime: processTime,
      completedTime: completedTime,
      error: fileStatus === 'failed' ? '文件格式不支持或文件损坏，请检查文件后重新上传' : undefined
    }
  })
}

// 加载任务详情
const loadTaskDetail = async () => {
  loading.value = true
  try {
    const taskId = route.params.id as string
    
    // 演示模式：从演示数据中查找任务
    const demoTasks = [
      {
        id: 1001,
        batchName: '2025年1月卷宗导入批次',
        taskName: '2025年1月卷宗导入批次',
        status: 'running',
        totalFiles: 8,
        successFiles: 5,
        failedFiles: 0,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        files: generateDemoFiles(8, 5, 'running')
      },
      {
        id: 1002,
        batchName: '2025年1月卷宗批量导入',
        taskName: '2025年1月卷宗批量导入',
        status: 'completed',
        totalFiles: 12,
        successFiles: 12,
        failedFiles: 0,
        createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
        files: generateDemoFiles(12, 12, 'completed')
      },
      {
        id: 1003,
        batchName: '2024年12月卷宗归档导入',
        taskName: '2024年12月卷宗归档导入',
        status: 'completed',
        totalFiles: 6,
        successFiles: 6,
        failedFiles: 0,
        createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
        files: generateDemoFiles(6, 6, 'completed')
      },
      {
        id: 1004,
        batchName: '2024年12月历史卷宗导入',
        taskName: '2024年12月历史卷宗导入',
        status: 'completed',
        totalFiles: 15,
        successFiles: 14,
        failedFiles: 1,
        createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
        files: generateDemoFiles(15, 14, 'completed')
      },
      {
        id: 1005,
        batchName: '2024年11月卷宗补充导入',
        taskName: '2024年11月卷宗补充导入',
        status: 'failed',
        totalFiles: 3,
        successFiles: 0,
        failedFiles: 3,
        createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
        files: generateDemoFiles(3, 0, 'failed')
      }
    ]
    
    const task = demoTasks.find(t => t.id.toString() === taskId)
    if (task) {
      taskInfo.value = task
    }
  } catch (error) {
    console.error('加载任务详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/case-file/progress')
}

// 格式化日期
const formatDate = (date: Date | string) => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 导入记录状态
const getRecordStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getRecordStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待处理',
    running: '处理中',
    completed: '已完成',
    failed: '导入失败'
  }
  return map[status] || status
}

// 获取任务进度百分比
const getTaskProgress = (task: any) => {
  if (task.status === 'completed') return 100
  if (task.status === 'failed') return 0
  if (task.totalFiles > 0) {
    return Math.round((task.successFiles / task.totalFiles) * 100)
  }
  return 0
}

// 获取文件状态类型
const getFileStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取文件状态文字
const getFileStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '处理失败'
  }
  return map[status] || status
}

// 统计文件数量
const getCompletedFileCount = () => {
  if (!taskInfo.value?.files) return 0
  return taskInfo.value.files.filter((f: any) => f.status === 'completed').length
}

const getProcessingFileCount = () => {
  if (!taskInfo.value?.files) return 0
  return taskInfo.value.files.filter((f: any) => f.status === 'processing').length
}

const getFailedFileCount = () => {
  if (!taskInfo.value?.files) return 0
  return taskInfo.value.files.filter((f: any) => f.status === 'failed').length
}

const getPendingFileCount = () => {
  if (!taskInfo.value?.files) return 0
  return taskInfo.value.files.filter((f: any) => f.status === 'pending').length
}

onMounted(() => {
  loadTaskDetail()
})
</script>

<style scoped>
.archive-progress-detail-view {
  font-family: var(--font-body);
}

.back-button {
  color: var(--military-text-primary);
  padding: 8px 12px;
}

.back-button:hover {
  background: var(--military-bg-card-hover);
}

.detail-content {
  min-height: 400px;
}

/* 任务详情 */
.task-detail-info {
  padding: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  color: var(--military-text-muted);
  font-size: 12px;
}

.info-value {
  color: var(--military-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.stats-row {
  border-top: 1px solid var(--military-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: var(--military-text-muted);
  font-size: 12px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.progress-label {
  color: var(--military-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.progress-percentage {
  color: var(--military-primary);
  font-size: 14px;
  font-weight: 600;
}

/* 文件详情 */
.file-detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-detail-item {
  padding: 16px;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  transition: all 0.2s;
}

.file-detail-item:hover {
  border-color: var(--military-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.file-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.file-detail-name {
  color: var(--military-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.file-stage {
  color: var(--military-text-muted);
}

.file-detail-size {
  color: var(--military-text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.file-progress {
  margin-top: 8px;
}

.file-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-error {
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid #ef4444;
  border-radius: var(--military-radius-sm);
}

.error-icon {
  color: #ef4444;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.error-title {
  color: #ef4444;
}

.error-message {
  color: #dc2626;
}

.file-success {
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-stats {
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-status-icon {
  font-size: 18px;
}

.file-status-icon.pending {
  color: var(--military-text-muted);
}

.file-status-icon.processing {
  color: #f59e0b;
}

.file-status-icon.completed {
  color: #10b981;
}

.file-status-icon.failed {
  color: #ef4444;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--military-text-muted);
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}
</style>
