<template>
  <div class="archive-ocr-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <h2 class="gov-card-title mb-2">OCR数字化</h2>
          <p class="gov-card-subtitle">AI驱动的文档扫描数字化流水线，支持图像预处理、文本识别、文档解析</p>
        </div>
        <div class="flex items-center gap-3">
          <button 
            class="gov-button-primary flex items-center gap-2" 
            @click="handleBatchStart" 
            :disabled="selectedTasks.length === 0"
          >
            <el-icon><Upload /></el-icon>
            <span>批量启动OCR ({{ selectedTasks.length }})</span>
          </button>
          <button 
            class="gov-button-default flex items-center gap-2" 
            @click="loadTasks" 
            :disabled="loading"
          >
            <el-icon><Refresh /></el-icon>
            <span>{{ loading ? '刷新中...' : '刷新列表' }}</span>
          </button>
        </div>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">OCR说明</span>
        <el-tooltip
          content="OCR识别准确率约85-95%，建议对关键信息进行人工校对。批量操作最多支持100个任务同时处理"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- 左侧：任务列表 -->
      <div class="lg:col-span-1 space-y-4 sm:space-y-6">
        <!-- 任务筛选 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">任务筛选</h3>
          </div>
          <el-radio-group v-model="taskFilter" class="w-full gov-radio-group" @change="loadTasks">
            <el-radio-button label="all" class="flex-1">全部</el-radio-button>
            <el-radio-button label="pending" class="flex-1">待处理</el-radio-button>
            <el-radio-button label="processing" class="flex-1">处理中</el-radio-button>
            <el-radio-button label="completed" class="flex-1">已完成</el-radio-button>
          </el-radio-group>
          <div class="flex items-center gap-2 mt-4">
            <span class="gov-help-text-short">筛选说明</span>
            <el-tooltip
              content="按任务状态筛选，可快速定位需要处理的OCR任务"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </div>

        <!-- OCR任务列表 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <h3 class="gov-card-title">OCR任务列表</h3>
              <span class="text-sm font-semibold" style="color: var(--color-primary);">{{ tasks.length }} 个任务</span>
            </div>
          </div>
          
          <div class="space-y-3 max-h-[600px] overflow-y-auto">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              :class="[
                'gov-card gov-card-interactive p-4 cursor-pointer transition-all',
                selectedTaskId === task.id ? 'border-2 border-gov-primary bg-gov-primary/5' : '',
                task.status === 'failed' ? 'border-l-4 border-gov-error' : ''
              ]"
              @click="selectTask(task)"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <el-checkbox
                    v-if="task.status === 'pending'"
                    :model-value="selectedTasks.includes(task.id)"
                    @change="(val) => handleTaskSelect(task.id, val)"
                    @click.stop
                  />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-slate-900 truncate">{{ task.fileName }}</p>
                    <p class="text-xs text-slate-500 mt-1">{{ formatFileSize(task.fileSize) }}</p>
                  </div>
                </div>
                <el-tag :type="getStatusType(task.status)" size="small">
                  {{ getStatusText(task.status) }}
                </el-tag>
              </div>

              <!-- 处理进度 -->
              <div v-if="task.status === 'processing'" class="mb-2">
                <el-progress
                  :percentage="task.progress"
                  :status="task.progress === 100 ? 'success' : undefined"
                  :stroke-width="6"
                />
                <p class="text-xs text-slate-500 mt-1">{{ getProgressText(task.currentStep) }}</p>
              </div>

              <!-- 质量评分 -->
              <div v-if="task.status === 'completed' && task.accuracy" class="flex items-center gap-2 mb-2">
                <span class="text-xs text-slate-600">识别准确率:</span>
                <el-rate
                  :model-value="Math.round(task.accuracy / 20)"
                  disabled
                  show-score
                  :score-template="task.accuracy + '%'"
                  size="small"
                />
              </div>

              <!-- 操作按钮 -->
              <div class="flex items-center gap-2 mt-3 pt-3" style="border-top: 1px solid var(--color-border);">
                <button
                  v-if="task.status === 'pending'"
                  class="gov-button-primary gov-button-sm"
                  @click.stop="handleStartOcr(task)"
                >
                  启动OCR
                </button>
                <button
                  v-if="task.status === 'completed'"
                  class="gov-button-default gov-button-sm"
                  @click.stop="handleViewResult(task)"
                >
                  查看结果
                </button>
                <button
                  v-if="task.status === 'failed'"
                  class="gov-button-default gov-button-sm"
                  @click.stop="handleRetry(task)"
                >
                  重新处理
                </button>
                <button
                  v-if="task.status === 'completed'"
                  class="gov-button-default gov-button-sm"
                  @click.stop="handleCorrect(task)"
                >
                  手动校正
                </button>
              </div>
            </div>

            <el-empty v-if="filteredTasks.length === 0" description="暂无任务" :image-size="80" />
          </div>
        </div>
      </div>

      <!-- 右侧：处理详情和预览 -->
      <div class="lg:col-span-2 space-y-4 sm:space-y-6">
        <!-- 处理流程可视化 -->
        <div v-if="selectedTask" class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">处理流程</h3>
            <p class="gov-card-subtitle">实时显示OCR处理各阶段状态</p>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="gov-help-text-short">处理流程</span>
            <el-tooltip
              content="OCR处理包含上传、图像预处理、文本识别、文档解析、完成五个阶段"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          
          <el-steps :active="getStepActive(selectedTask)" finish-status="success" align-center>
            <el-step title="上传" :description="selectedTask.steps?.upload || '等待中'" />
            <el-step title="图像预处理" :description="selectedTask.steps?.preprocess || '等待中'" />
            <el-step title="文本识别" :description="selectedTask.steps?.recognize || '等待中'" />
            <el-step title="文档解析" :description="selectedTask.steps?.parse || '等待中'" />
            <el-step title="完成" :description="selectedTask.steps?.complete || '等待中'" />
          </el-steps>

          <!-- 处理详情 -->
          <div v-if="selectedTask && selectedTask.status === 'processing'" class="mt-6">
            <h4 class="text-sm font-medium text-slate-900 mb-2">当前处理信息</h4>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="当前步骤">{{ getProgressText(selectedTask.currentStep || '') }}</el-descriptions-item>
              <el-descriptions-item label="处理进度">{{ selectedTask.progress }}%</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ selectedTask.startTime ? formatDate(selectedTask.startTime) : '-' }}</el-descriptions-item>
              <el-descriptions-item label="预计剩余时间">{{ selectedTask.estimatedTime || '计算中...' }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- 对比预览 -->
        <div v-if="selectedTask && selectedTask.status === 'completed'" class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">对比预览</h3>
                <p class="gov-card-subtitle">对比原始图像与OCR识别结果</p>
              </div>
            <div class="flex items-center gap-2">
                <button class="gov-button-default gov-button-sm" @click="viewMode = 'split'">分屏对比</button>
                <button class="gov-button-default gov-button-sm" @click="viewMode = 'side'">左右对比</button>
                <button class="gov-button-primary gov-button-sm flex items-center gap-2" @click="handleDownloadResult">
                  <el-icon><Download /></el-icon>
                  <span>下载结果</span>
                </button>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="gov-help-text-short">对比预览</span>
            <el-tooltip
              content="对比预览可帮助您快速发现识别错误，建议对关键信息进行人工校对"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>

          <div :class="['grid gap-4', viewMode === 'split' ? 'grid-cols-1' : 'grid-cols-2']">
            <!-- 原图 -->
            <div class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-sm font-medium text-slate-900">原始图像</h4>
                <el-tag size="small">原图</el-tag>
              </div>
              <div class="bg-gray-100 rounded-lg p-4 min-h-[300px] flex items-center justify-center">
                <img
                  v-if="selectedTask.originalImage"
                  :src="selectedTask.originalImage"
                  alt="原图"
                  class="max-w-full max-h-[400px] object-contain"
                />
                <el-empty v-else description="暂无原图" :image-size="60" />
              </div>
            </div>

            <!-- OCR结果 -->
            <div class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-sm font-medium text-slate-900">OCR识别结果</h4>
                <el-tag type="success" size="small">识别准确率: {{ selectedTask.accuracy }}%</el-tag>
              </div>
              <div class="bg-gray-50 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
                <pre v-if="selectedTask && selectedTask.ocrText" class="text-sm text-slate-700 whitespace-pre-wrap font-mono">{{ selectedTask.ocrText }}</pre>
                <el-empty v-else description="暂无识别结果" :image-size="60" />
              </div>
              
              <!-- 校正编辑 -->
              <div v-if="showCorrect" class="mt-4 pt-4" style="border-top: 1px solid var(--color-border);">
                <label class="gov-input-label mb-2">手动校正文本</label>
                <el-input
                  v-model="correctedText"
                  type="textarea"
                  :rows="6"
                  placeholder="在此编辑OCR识别结果，修正识别错误..."
                  class="gov-input"
                  @blur="handleSaveCorrect"
                />
                <div class="flex items-center gap-2 mb-4">
                  <span class="gov-help-text-short">手动校正</span>
                  <el-tooltip
                    content="手动校正可提高识别准确率，校正后的文本将保存到案卷中"
                    placement="top"
                    :show-after="300"
                  >
                    <el-icon class="gov-help-icon-tooltip">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </div>
                <div class="flex items-center justify-end gap-3">
                  <button class="gov-button-default gov-button-sm" @click="showCorrect = false">取消</button>
                  <button class="gov-button-primary gov-button-sm" @click="handleSaveCorrect">保存校正</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 处理结果详情 -->
        <div v-if="selectedTask && selectedTask.status === 'completed'" class="glass glass-lg rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-xl">
          <h3 class="text-lg font-semibold text-slate-900 mb-4">处理结果详情</h3>
          
          <el-tabs v-model="resultTab">
            <el-tab-pane label="识别文本" name="text">
              <div class="bg-gray-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
                <pre v-if="selectedTask && selectedTask.ocrText" class="text-sm text-slate-700 whitespace-pre-wrap font-mono">{{ selectedTask.ocrText }}</pre>
                <el-empty v-else description="暂无识别文本" :image-size="60" />
              </div>
              <div class="flex items-center justify-end gap-2 mt-4">
                <el-button size="small" @click="handleCopyText">复制文本</el-button>
                <el-button size="small" :icon="Download" @click="handleExportText">导出文本</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="元数据" name="metadata">
            <el-descriptions :column="2" border>
              <el-descriptions-item
                v-for="(value, key) in (selectedTask.metadata || {})"
                :key="key"
                :label="key"
              >
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
            </el-tab-pane>

            <el-tab-pane label="处理日志" name="logs">
              <el-timeline v-if="selectedTask && selectedTask.logs && selectedTask.logs.length > 0">
                <el-timeline-item
                  v-for="(log, index) in selectedTask.logs"
                  :key="index"
                  :timestamp="log.time ? formatDate(log.time) : ''"
                  :type="log.type === 'success' ? 'success' : log.type === 'error' ? 'danger' : 'primary'"
                >
                  <p>{{ log.message }}</p>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-else description="暂无处理日志" :image-size="60" />
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 空状态 -->
        <div v-if="!selectedTask" class="glass glass-lg rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-xl">
          <el-empty description="请从左侧选择一个OCR任务查看详情" :image-size="120" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Download, Warning, InfoFilled } from '@element-plus/icons-vue'
import { ocrApi } from '@/api/ocr'

// 加载状态
const loading = ref(false)

// 任务筛选
const taskFilter = ref('all')

// 任务列表
const tasks = ref<any[]>([])

// 选中的任务ID
const selectedTaskId = ref<number | null>(null)
const selectedTask = computed(() => {
  return tasks.value.find(t => t.id === selectedTaskId.value) || null
})

// 批量选中的任务
const selectedTasks = ref<number[]>([])

// 视图模式
const viewMode = ref<'split' | 'side'>('side')
const resultTab = ref('text')

// 校正相关
const showCorrect = ref(false)
const correctedText = ref('')

// 过滤后的任务列表
const filteredTasks = computed(() => {
  if (taskFilter.value === 'all') return tasks.value
  return tasks.value.filter(t => t.status === taskFilter.value)
})

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 格式化日期
const formatDate = (date: Date | string) => {
  if (!date) return '-'
  try {
    const d = typeof date === 'string' ? new Date(date) : date
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 获取进度文本
const getProgressText = (step: string) => {
  const map: Record<string, string> = {
    upload: '文件上传中',
    preprocess: '图像预处理中',
    recognize: '文本识别中',
    parse: '文档解析中',
    complete: '处理完成'
  }
  return map[step] || step
}

// 获取步骤激活状态
const getStepActive = (task: any) => {
  const stepMap: Record<string, number> = {
    upload: 0,
    preprocess: 1,
    recognize: 2,
    parse: 3,
    complete: 4
  }
  return stepMap[task.currentStep] || 0
}

// 选择任务
const selectTask = (task: any) => {
  selectedTaskId.value = task.id
  if (task.ocrText) {
    correctedText.value = task.ocrText
  }
}

// 任务选择（复选框）
const handleTaskSelect = (taskId: number, checked: boolean) => {
  if (checked) {
    selectedTasks.value.push(taskId)
  } else {
    selectedTasks.value = selectedTasks.value.filter(id => id !== taskId)
  }
}

// 启动OCR
const handleStartOcr = async (task: any) => {
  try {
    await ocrApi.startTask(task.id)
    ElMessage.success('OCR任务已启动')
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(error?.message || '启动OCR失败')
  }
}

// 批量启动OCR
const handleBatchStart = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要处理的任务')
    return
  }

  try {
    await ocrApi.batchStartTasks(selectedTasks.value)
    ElMessage.success(`成功启动 ${selectedTasks.value.length} 个OCR任务`)
    selectedTasks.value = []
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(error?.message || '批量启动失败')
  }
}

// 查看结果
const handleViewResult = (task: any) => {
  selectTask(task)
  resultTab.value = 'text'
}

// 重试
const handleRetry = async (task: any) => {
  try {
    await ocrApi.retryTask(task.id)
    ElMessage.success('任务已重置，可以重新启动')
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(error?.message || '重试失败')
  }
}

// 手动校正
const handleCorrect = (task: any) => {
  selectTask(task)
  showCorrect.value = true
  correctedText.value = task.ocrText || ''
}

// 保存校正
const handleSaveCorrect = async () => {
  if (!selectedTask.value) return
  
  try {
    await ocrApi.saveCorrect(selectedTask.value.id, correctedText.value)
    ElMessage.success('校正已保存')
    if (selectedTask.value) {
      selectedTask.value.ocrText = correctedText.value
    }
    showCorrect.value = false
    await loadTasks()
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败')
  }
}

// 复制文本
const handleCopyText = () => {
  if (selectedTask.value?.ocrText) {
    navigator.clipboard.writeText(selectedTask.value.ocrText)
    ElMessage.success('文本已复制到剪贴板')
  }
}

// 导出文本
const handleExportText = () => {
  if (!selectedTask.value?.ocrText) return
  // TODO: 实现文本导出
  ElMessage.info('正在导出文本...')
}

// 下载结果
const handleDownloadResult = () => {
  if (!selectedTask.value) return
  // TODO: 实现结果下载
  ElMessage.info('正在下载结果...')
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const status = taskFilter.value === 'all' ? undefined : taskFilter.value
    const response = await ocrApi.getTasks({
      status,
      page: 1,
      pageSize: 100
    })
    
    // 转换数据格式
    tasks.value = response.data.map(task => ({
      id: task.id,
      fileName: task.fileName,
      fileSize: task.fileSize,
      fileType: task.fileType,
      status: task.status,
      progress: task.progress,
      currentStep: task.currentStep,
      accuracy: task.accuracy,
      ocrText: task.ocrText,
      originalImage: task.originalImage,
      startTime: task.startTime ? new Date(task.startTime) : undefined,
      estimatedTime: task.estimatedTime,
      errorMessage: task.errorMessage,
      stepsInfo: task.steps,
      logs: task.logs || [],
      metadata: task.metadata || {}
    }))
  } catch (error: any) {
    ElMessage.error(error?.message || '加载任务列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.archive-ocr-view {
  font-family: var(--font-body);
}
</style>
