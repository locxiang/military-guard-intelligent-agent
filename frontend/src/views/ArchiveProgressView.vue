<template>
  <div class="archive-progress-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header mb-4">
        <h2 class="gov-card-title">导入进度管理</h2>
        <p class="gov-card-subtitle">查看所有导入任务的处理进度和每个文件的详细情况</p>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="gov-card mb-6">
      <div class="gov-card-header mb-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="gov-card-title">导入任务列表</h3>
            <p class="gov-card-subtitle">点击任务卡片查看详细信息</p>
          </div>
          <el-button type="primary" :loading="recordsLoading" @click="loadImportRecords">
            <el-icon><Refresh /></el-icon>
            <span>刷新列表</span>
          </el-button>
        </div>
      </div>

      <!-- 筛选和搜索 -->
      <div class="mb-4 flex flex-wrap items-center gap-3">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索批次名称..."
          clearable
          style="width: 250px"
          @input="filterTasks"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterStatus"
          placeholder="筛选状态"
          clearable
          style="width: 150px"
          @change="filterTasks"
        >
          <el-option label="全部" value="" />
          <el-option label="处理中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </div>

      <!-- 任务列表 -->
      <div v-loading="recordsLoading" class="task-list-container">
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <el-icon :size="48"><FolderOpened /></el-icon>
          <p class="mt-4">暂无导入任务</p>
          <p class="text-sm text-gray-500 mt-2">请在"案件导入"页面中导入案件文件</p>
        </div>
        <div v-else class="task-list">
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="task-item"
            @click="viewTaskDetail(task)"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <h4 class="task-name truncate">{{ task.batchName || '未命名批次' }}</h4>
                  <el-tag :type="getRecordStatusType(task.status)" size="small">
                    {{ getRecordStatusText(task.status) }}
                  </el-tag>
                </div>
                <div class="task-meta text-sm text-gray-500">
                  <span>创建时间：{{ formatDate(task.createdAt) }}</span>
                  <span class="mx-2">|</span>
                  <span>文件数：{{ task.totalFiles }} 个</span>
                  <span class="mx-2">|</span>
                  <span class="text-green-600">成功：{{ task.successFiles }}</span>
                  <span v-if="task.failedFiles > 0" class="ml-2 text-red-600">失败：{{ task.failedFiles }}</span>
                </div>
                <!-- 整体进度条 -->
                <div v-if="task.status === 'running'" class="mt-2">
                  <el-progress
                    :percentage="getTaskProgress(task)"
                    :stroke-width="6"
                    :show-text="true"
                  />
                </div>
                <!-- 点击提示 -->
                <div class="task-hint text-xs text-gray-400 mt-2 flex items-center gap-1">
                  <el-icon :size="12"><InfoFilled /></el-icon>
                  <span>点击查看文件处理详情</span>
                </div>
              </div>
              <el-icon class="task-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Refresh,
  Search,
  FolderOpened,
  ArrowRight,
  InfoFilled
} from '@element-plus/icons-vue'
// 演示模式：不需要后端API
// import { caseFileApi } from '@/api/archive'

// 延时函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

const router = useRouter()

// 导入记录
const recordsLoading = ref(false)
const importRecords = ref<any[]>([])

// 分析进度管理相关状态
const searchKeyword = ref('')
const filterStatus = ref('')

// 筛选后的任务列表
const filteredTasks = computed(() => {
  let tasks = importRecords.value
  
  // 按关键词筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    tasks = tasks.filter(task => 
      (task.batchName || '').toLowerCase().includes(keyword) ||
      (task.taskName || '').toLowerCase().includes(keyword)
    )
  }
  
  // 按状态筛选
  if (filterStatus.value) {
    tasks = tasks.filter(task => task.status === filterStatus.value)
  }
  
  // 按创建时间倒序排列
  return tasks.sort((a, b) => {
    const timeA = new Date(a.createdAt).getTime()
    const timeB = new Date(b.createdAt).getTime()
    return timeB - timeA
  })
})

// 筛选任务
const filterTasks = () => {
  // 计算属性会自动更新
}

// 查看任务详情
const viewTaskDetail = (task: any) => {
  router.push(`/case-file/progress/${task.id}`)
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

// 加载导入记录 - 演示模式
const loadImportRecords = async () => {
  recordsLoading.value = true
  try {
    // 演示模式：模拟加载延迟
    await delay(500)
    
    // 使用假数据（演示模式）
    const now = Date.now()
    importRecords.value = [
      {
        id: 1001,
        batchName: '2025年1月卷宗导入批次',
        taskName: '2025年1月卷宗导入批次',
        status: 'running',
        totalFiles: 8,
        successFiles: 5,
        failedFiles: 0,
        createdAt: new Date(now - 3600000).toISOString(), // 1小时前
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
        createdAt: new Date(now - 86400000 * 2).toISOString(), // 2天前
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
        createdAt: new Date(now - 86400000 * 3).toISOString(), // 3天前
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
        createdAt: new Date(now - 86400000 * 5).toISOString(), // 5天前
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
        createdAt: new Date(now - 86400000 * 7).toISOString(), // 7天前
        files: generateDemoFiles(3, 0, 'failed')
      }
    ]
  } catch (error) {
    console.error('加载导入记录失败:', error)
  } finally {
    recordsLoading.value = false
  }
}

onMounted(() => {
  loadImportRecords()
})
</script>

<style scoped>
.archive-progress-view {
  font-family: var(--font-body);
}

/* 任务列表容器 */
.task-list-container {
  min-height: 300px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 16px;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.task-item:hover {
  border-color: var(--military-primary);
  background: var(--military-bg-card-hover);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}


.task-name {
  color: var(--military-text-primary);
  font-size: 15px;
  font-weight: 600;
}

.task-meta {
  color: var(--military-text-muted);
  font-size: 13px;
  margin-top: 8px;
}

.task-arrow {
  color: var(--military-text-muted);
  font-size: 18px;
  flex-shrink: 0;
}

.task-item:hover .task-arrow {
  color: var(--military-primary);
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

/* 任务详情 */
.task-detail-info {
  padding: 16px;
  background: var(--military-bg-card);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
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

/* 文件详情 */
.file-detail-section {
  margin-top: 24px;
}

.section-title {
  color: var(--military-text-primary);
  font-size: 15px;
  font-weight: 600;
}

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

.task-hint {
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
</style>
