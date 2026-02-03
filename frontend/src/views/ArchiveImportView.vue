<template>
  <div class="case-import-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题和业务说明 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header mb-4">
        <h2 class="gov-card-title">案件导入</h2>
        <p class="gov-card-subtitle">将纸质卷宗扫描件或电子文件导入系统，系统会自动识别文字内容并进行分类</p>
      </div>
      
      <!-- 业务场景说明 -->
      <div class="usage-scenarios-card rounded-lg p-4 mb-4">
        <div class="flex items-start gap-3">
          <el-icon class="usage-icon mt-0.5" :size="20">
            <InfoFilled />
          </el-icon>
          <div class="flex-1">
            <h4 class="usage-title text-sm font-semibold mb-2">使用场景</h4>
            <ul class="usage-list text-sm space-y-1 list-disc list-inside">
              <li><strong>电子卷宗</strong>：Word文档等电子版文书材料，系统直接提取文字内容</li>
              <li><strong>扫描卷宗</strong>：纸质卷宗扫描件（PDF），系统自动进行文字识别</li>
              <li>导入后可在"导入进度管理"中查看处理进度和每个文件的详细情况</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 操作提示 -->
      <div class="tips-text flex items-center gap-2 text-sm">
        <el-icon><Warning /></el-icon>
        <span>支持格式：PDF扫描件、Word文档（DOC/DOCX）；单个文件不超过500MB，一次最多导入100个文件</span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：上传区域 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 上传文件 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">上传案件文件</h3>
            <p class="gov-card-subtitle">选择或拖拽案件文件到上传区域</p>
          </div>

          <!-- 卷宗类型选择 -->
          <div class="mb-4">
            <label class="gov-input-label mb-2 block">卷宗类型</label>
            <el-radio-group v-model="importForm.fileType" class="gov-radio-group">
              <el-radio-button label="auto">
                <el-icon><Promotion /></el-icon>
                <span>自动识别</span>
              </el-radio-button>
              <el-radio-button label="electronic">
                <el-icon><Document /></el-icon>
                <span>电子卷宗</span>
              </el-radio-button>
              <el-radio-button label="scanned">
                <el-icon><Picture /></el-icon>
                <span>扫描卷宗</span>
              </el-radio-button>
            </el-radio-group>
            <div class="gov-help-text text-xs mt-3">
              <el-icon class="gov-help-text-icon"><InfoFilled /></el-icon>
              <span v-if="importForm.fileType === 'auto'">系统将根据文件格式自动判断处理方式</span>
              <span v-else-if="importForm.fileType === 'electronic'">Word等电子版文书材料，直接提取文字内容</span>
              <span v-else>纸质卷宗扫描件、照片等，需要进行文字识别（识别完成后可校对）</span>
            </div>
          </div>

          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            :auto-upload="false"
            :limit="100"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
            multiple
            drag
            class="gov-upload-area"
          >
            <el-icon class="upload-icon" :size="48">
              <UploadFilled />
            </el-icon>
            <div class="upload-text">
              将卷宗文件拖到此处，或<em class="upload-text-emphasis">点击选择文件</em>
            </div>
            <template #tip>
              <div class="upload-tip">
                支持 PDF扫描件、Word文档（DOC/DOCX）
              </div>
            </template>
          </el-upload>

          <!-- 已选文件列表 -->
          <div v-if="fileList.length > 0" class="mt-4">
            <div class="flex items-center justify-between mb-2">
              <span class="file-count">
                已选择 <strong>{{ fileList.length }}</strong> 个文件
              </span>
              <el-button type="text" size="small" @click="handleClearFiles" class="clear-btn">
                清空列表
              </el-button>
            </div>
            <div class="file-list-container">
              <div 
                v-for="(file, index) in fileList" 
                :key="index"
                class="file-item"
              >
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span class="file-name truncate">{{ file.name }}</span>
                  <el-tag size="small" :type="getFileTypeTag(file.name)" class="file-type-tag">
                    {{ getFileTypeLabel(file.name) }}
                  </el-tag>
                  <span class="file-size">{{ formatFileSize(file.size || 0) }}</span>
                </div>
                <el-button type="text" size="small" @click="removeFile(index)" class="delete-btn">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 导入设置 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">导入设置</h3>
            <p class="gov-card-subtitle">设置本次导入的基本信息（可选）</p>
          </div>

          <el-form :model="importForm" label-width="100px" class="import-form">
            <el-form-item label="批次名称">
              <el-input
                v-model="importForm.batchName"
                placeholder="例如：2025年1月案件卷宗"
                clearable
              />
              <div class="help-text text-xs mt-1">用于标识本次导入批次，便于后续查找</div>
            </el-form-item>

            <el-form-item label="来源部门">
              <el-select v-model="importForm.sourceDepartment" placeholder="选择来源部门" clearable class="w-full">
                <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
              </el-select>
            </el-form-item>

            <el-form-item label="默认标签">
              <el-select
                v-model="importForm.defaultTags"
                multiple
                filterable
                allow-create
                placeholder="选择或输入标签"
                class="w-full"
              >
                <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
              </el-select>
            </el-form-item>
          </el-form>

          <!-- 开始导入按钮 -->
          <div class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div class="import-status-text">
              <span v-if="fileList.length === 0">请先选择要导入的案件文件</span>
              <span v-else>已选择 <strong class="text-primary">{{ fileList.length }}</strong> 个文件，准备导入</span>
            </div>
            <el-button
              type="primary"
              size="large"
              :disabled="fileList.length === 0 || importing"
              :loading="importing"
              @click="handleStartImport"
            >
              <el-icon v-if="!importing"><Upload /></el-icon>
              <span>{{ importing ? '正在导入...' : '开始导入' }}</span>
            </el-button>
          </div>

          <!-- 导入进度 - 多阶段演示 -->
          <div v-if="importProgress.show" class="mt-6 import-progress-panel">
            <!-- 阶段指示器 -->
            <div class="stage-indicator mb-4">
              <div class="stage-steps">
                <div 
                  v-for="(stage, idx) in importStages" 
                  :key="stage.key"
                  class="stage-step"
                  :class="{ 
                    'active': currentStage === stage.key,
                    'completed': getStageIndex(currentStage) > idx,
                    'pending': getStageIndex(currentStage) < idx
                  }"
                >
                  <div class="stage-icon">
                    <el-icon v-if="getStageIndex(currentStage) > idx"><CircleCheck /></el-icon>
                    <el-icon v-else-if="currentStage === stage.key" class="animate-spin"><Loading /></el-icon>
                    <span v-else>{{ idx + 1 }}</span>
                  </div>
                  <div class="stage-label">{{ stage.label }}</div>
                </div>
              </div>
            </div>

            <!-- 当前阶段详情 -->
            <div class="current-stage-detail">
              <div class="flex items-center justify-between mb-2">
                <span class="progress-label">{{ getCurrentStageName() }}</span>
                <span class="progress-count">{{ importProgress.uploaded }} / {{ importProgress.total }}</span>
              </div>
              <el-progress
                :percentage="importProgress.percentage"
                :status="importProgress.status"
                :stroke-width="16"
              />
            </div>

            <!-- 文件处理详情列表 -->
            <div v-if="processingFiles.length > 0" class="processing-files-list mt-4">
              <div class="processing-header mb-2">
                <span class="text-sm font-medium">文件处理详情</span>
              </div>
              <div class="processing-scroll-area">
                <div 
                  v-for="file in processingFiles" 
                  :key="file.name" 
                  class="processing-file-item"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <el-icon :class="['file-status-icon', file.status]">
                      <CircleCheck v-if="file.status === 'completed'" />
                      <Loading v-else-if="file.status === 'processing'" class="animate-spin" />
                      <Document v-else />
                    </el-icon>
                    <span class="file-name truncate">{{ file.name }}</span>
                    <el-tag size="small" :type="file.statusType">{{ file.statusText }}</el-tag>
                  </div>
                  <div class="file-progress-bar" v-if="file.status === 'processing'">
                    <el-progress :percentage="file.progress" :show-text="false" :stroke-width="4" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 最终状态 -->
            <div class="progress-status mt-4">
              <div v-if="importProgress.status === 'success'" class="status-success">
                <el-icon><CircleCheck /></el-icon>
                <span>全部处理完成！共处理 {{ importProgress.total }} 个文件，<template v-if="hasScannedFiles">扫描件已添加到识别队列</template></span>
              </div>
              <div v-else-if="importProgress.status === 'exception'" class="status-error">
                <el-icon><CircleClose /></el-icon>
                <span>导入失败，请检查文件和网络后重试</span>
              </div>
              <div v-else class="status-processing">
                <el-icon class="animate-spin"><Loading /></el-icon>
                <span>{{ getCurrentStageDescription() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：识别结果和导入记录 -->
      <div class="space-y-6">
        <!-- 识别结果（扫描件处理状态） -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">识别结果</h3>
                <p class="gov-card-subtitle">扫描件文字识别状态</p>
              </div>
              <el-button type="text" size="small" :loading="ocrTasksLoading" @click="loadOcrTasks">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <div v-loading="ocrTasksLoading" class="min-h-[150px]">
            <div v-if="pendingOcrTasks.length === 0 && completedOcrTasks.length === 0" class="empty-state">
              <el-icon :size="40"><DocumentCopy /></el-icon>
              <p>暂无待处理的扫描件</p>
            </div>
            
            <!-- 处理中的任务 -->
            <div v-if="pendingOcrTasks.length > 0" class="mb-4">
              <div class="section-title mb-2">处理中 ({{ pendingOcrTasks.length }})</div>
              <div class="ocr-task-list">
                <div v-for="task in pendingOcrTasks" :key="task.id" class="ocr-task-item">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="task-filename truncate">{{ task.fileName }}</span>
                    <el-tag size="small" :type="getOcrStatusType(task.status)">
                      {{ getOcrStatusText(task.status) }}
                    </el-tag>
                  </div>
                  <el-progress
                    v-if="task.status === 'processing'"
                    :percentage="task.progress || 0"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>

            <!-- 待校对的任务 -->
            <div v-if="completedOcrTasks.length > 0">
              <div class="section-title mb-2">待校对 ({{ completedOcrTasks.length }})</div>
              <div class="ocr-task-list">
                <div 
                  v-for="task in completedOcrTasks" 
                  :key="task.id" 
                  class="ocr-task-item ocr-task-clickable"
                  @click="viewOcrResult(task)"
                >
                  <div class="flex items-center justify-between">
                    <span class="task-filename truncate">{{ task.fileName }}</span>
                    <div class="flex items-center gap-2">
                      <span class="accuracy-text">准确率 {{ task.accuracy || '-' }}%</span>
                      <el-icon class="view-icon"><ArrowRight /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 导入记录 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">导入记录</h3>
                <p class="gov-card-subtitle">历史导入批次</p>
              </div>
              <el-button type="text" size="small" :loading="recordsLoading" @click="loadImportRecords">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <div v-loading="recordsLoading" class="min-h-[150px]">
            <div v-if="importRecords.length === 0" class="empty-state">
              <el-icon :size="40"><FolderOpened /></el-icon>
              <p>暂无导入记录</p>
            </div>
            <el-timeline v-else class="import-timeline">
              <el-timeline-item
                v-for="record in importRecords"
                :key="record.id"
                :timestamp="formatDate(record.createdAt)"
                placement="top"
                :type="getRecordType(record.status)"
              >
                <div class="record-item" @click="viewRecordDetail(record)">
                  <div class="flex items-center justify-between mb-1">
                    <span class="record-name truncate">{{ record.batchName || '未命名批次' }}</span>
                    <el-tag :type="getRecordStatusType(record.status)" size="small">
                      {{ getRecordStatusText(record.status) }}
                    </el-tag>
                  </div>
                  <div class="record-stats">
                    <span>文件：{{ record.totalFiles }} 个</span>
                    <span class="success-count">成功：{{ record.successFiles }}</span>
                    <span v-if="record.failedFiles > 0" class="failed-count">失败：{{ record.failedFiles }}</span>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </div>
    </div>

    <!-- OCR结果查看对话框 -->
    <el-dialog
      v-model="ocrDialogVisible"
      :title="'识别结果 - ' + (selectedOcrTask?.fileName || '')"
      width="800px"
      class="ocr-dialog"
    >
      <div v-if="selectedOcrTask" class="ocr-result-content">
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <span class="result-label">文件名：</span>
            <span class="result-value">{{ selectedOcrTask.fileName }}</span>
          </div>
          <div>
            <span class="result-label">识别准确率：</span>
            <span class="result-value accuracy">{{ selectedOcrTask.accuracy || '-' }}%</span>
          </div>
        </div>
        
        <div class="mb-4">
          <div class="result-label mb-2">识别文字内容：</div>
          <el-input
            v-model="correctedText"
            type="textarea"
            :rows="12"
            placeholder="识别结果..."
          />
          <div class="help-text text-xs mt-2">如有识别错误，可直接在上方修改，修改后点击"保存校对"</div>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-between">
          <el-button @click="handleCopyOcrText">复制文字</el-button>
          <div class="flex gap-2">
            <el-button @click="ocrDialogVisible = false">关闭</el-button>
            <el-button type="primary" @click="handleSaveOcrCorrect">保存校对</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Refresh,
  InfoFilled,
  Warning,
  Document,
  Delete,
  Upload,
  CircleCheck,
  CircleClose,
  Loading,
  DocumentCopy,
  FolderOpened,
  Picture,
  Promotion,
  ArrowRight
} from '@element-plus/icons-vue'
import { caseFileApi } from '@/api/archive'

// 文件列表
const fileList = ref<any[]>([])

// 导入阶段定义
const importStages = [
  { key: 'upload', label: '上传文件' },
  { key: 'parse', label: '解析内容' },
  { key: 'analyze', label: '智能分析' },
  { key: 'complete', label: '完成' }
]

// 当前处理阶段
const currentStage = ref<string>('')

// 正在处理的文件列表（用于显示详情）
const processingFiles = ref<Array<{
  name: string
  status: 'pending' | 'processing' | 'completed'
  statusText: string
  statusType: string
  progress: number
}>>([])

// 导入状态
const importing = ref(false)
const importProgress = reactive({
  show: false,
  percentage: 0,
  status: '' as 'success' | 'exception' | 'warning' | '',
  uploaded: 0,
  total: 0
})

// 获取阶段索引
const getStageIndex = (stage: string) => {
  return importStages.findIndex(s => s.key === stage)
}

// 获取当前阶段名称
const getCurrentStageName = () => {
  const stage = importStages.find(s => s.key === currentStage.value)
  return stage ? stage.label : '处理中'
}

// 获取当前阶段描述
const getCurrentStageDescription = () => {
  const descriptions: Record<string, string> = {
    upload: '正在上传文件到系统...',
    parse: '正在解析文件内容，提取文字信息...',
    analyze: '正在进行智能分析，识别案件要素...',
    complete: '处理完成'
  }
  return descriptions[currentStage.value] || '处理中...'
}

// 导入表单
const importForm = reactive({
  fileType: 'auto', // auto: 自动识别, electronic: 电子文档, scanned: 扫描件
  batchName: '',
  defaultTags: [] as string[],
  sourceDepartment: ''
})

// 是否有扫描件文件（PDF需要OCR识别）
const hasScannedFiles = computed(() => {
  if (importForm.fileType === 'scanned') return true
  if (importForm.fileType === 'electronic') return false
  // 自动模式下，检查是否有PDF文件
  return fileList.value.some(file => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    return ext === 'pdf'
  })
})

// 常用数据
const commonTags = ref(['重要', '紧急', '已归档', '待处理', '涉密'])
const departments = ref(['某试训基地保卫处', '某部队保卫科', '某单位保卫部门'])

// OCR任务
const ocrTasksLoading = ref(false)
const ocrTasks = ref<any[]>([])
const pendingOcrTasks = computed(() => 
  ocrTasks.value.filter(t => ['pending', 'processing'].includes(t.status))
)
const completedOcrTasks = computed(() => 
  ocrTasks.value.filter(t => t.status === 'completed')
)

// OCR结果对话框
const ocrDialogVisible = ref(false)
const selectedOcrTask = ref<any>(null)
const correctedText = ref('')

// 导入记录
const recordsLoading = ref(false)
const importRecords = ref<any[]>([])

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
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

// 获取文件类型标签
const getFileTypeTag = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  if (['docx', 'doc'].includes(ext || '')) return 'success' // 电子卷宗
  if (['pdf'].includes(ext || '')) return 'warning' // PDF扫描件
  return ''
}

// 获取文件类型标签文字
const getFileTypeLabel = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  if (['docx', 'doc'].includes(ext || '')) return '电子卷宗'
  if (['pdf'].includes(ext || '')) return 'PDF扫描件'
  return ext?.toUpperCase() || '未知'
}

// OCR状态
const getOcrStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getOcrStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待识别',
    processing: '识别中',
    completed: '识别完成',
    failed: '识别失败'
  }
  return map[status] || status
}

// 导入记录状态
const getRecordType = (status: string) => {
  const map: Record<string, string> = {
    completed: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info'
  }
  return map[status] || 'info'
}

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

// 文件操作
const handleExceed = () => {
  ElMessage.warning('一次最多只能导入100个文件，请分批导入')
}

const beforeUpload = (file: File) => {
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件 "${file.name}" 超过 500MB 限制`)
    return false
  }
  return true
}

const removeFile = (index: number) => {
  fileList.value.splice(index, 1)
}

const handleClearFiles = () => {
  fileList.value = []
  ElMessage.info('已清空文件列表')
}

// 延时函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 根据 SSE 阶段返回当前文件状态文案
const getFileStatusByStage = (stage: string, progress?: number): { text: string; type: string } => {
  if (stage === 'upload') return { text: progress === 100 ? '已上传' : '上传中', type: progress === 100 ? 'success' : 'warning' }
  if (stage === 'parse') return { text: progress === 100 ? '已解析' : '解析中', type: progress === 100 ? 'success' : 'warning' }
  if (stage === 'analyze') return { text: progress === 100 ? '已分析' : '分析中', type: progress === 100 ? 'success' : 'warning' }
  if (stage === 'complete') return { text: '已导入', type: 'success' }
  return { text: '处理中', type: 'warning' }
}

// 开始导入 - 使用 SSE 流式接口，四阶段：上传 → 解析 → 智能分析 → 完成
const handleStartImport = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要导入的案件文件')
    return
  }

  const batchName = importForm.batchName.trim() || `批次_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '')}_${Math.floor(Math.random() * 1000)}`
  if (!importForm.batchName.trim()) {
    importForm.batchName = batchName
  }

  importing.value = true
  importProgress.show = true
  importProgress.percentage = 0
  importProgress.status = ''
  importProgress.total = fileList.value.length
  importProgress.uploaded = 0
  currentStage.value = 'upload'
  processingFiles.value = fileList.value.map(file => ({
    name: file.name,
    status: 'processing' as const,
    statusText: '上传中',
    statusType: 'warning',
    progress: 0
  }))

  const formData = new FormData()
  fileList.value.forEach((file, idx) => {
    const raw = (file as any).raw || file
    if (raw instanceof File) {
      formData.append('files', raw)
    }
  })
  if (formData.getAll('files').length === 0) {
    ElMessage.warning('没有可上传的文件（请确认选择的是本地文件）')
    importing.value = false
    return
  }

  try {
    const res = await caseFileApi.importStream(
      formData,
      { taskName: batchName, sourceDepartment: importForm.sourceDepartment || undefined },
      (data) => {
        const stage = data.stage
        const fileIndex = data.fileIndex ?? 0
        const total = data.total ?? importProgress.total

        if (stage) {
          currentStage.value = stage
          importProgress.total = total
        }

        const file = processingFiles.value[fileIndex]
        if (file && stage) {
          if (stage === 'complete') {
            file.status = data.success ? 'completed' : 'completed'
            file.statusText = data.success ? '已导入' : (data.reason || '失败')
            file.statusType = data.success ? 'success' : 'danger'
            file.progress = 100
            importProgress.uploaded = processingFiles.value.filter(f => f.status === 'completed').length
          } else {
            const { text, type } = getFileStatusByStage(stage, data.progress)
            file.statusText = text
            file.statusType = type
            file.progress = data.progress ?? file.progress
          }
        }

        if (total > 0 && stage === 'complete') {
          const done = processingFiles.value.filter(f => f.status === 'completed').length
          importProgress.percentage = Math.round((done / total) * 100)
        }
      }
    )

    importProgress.percentage = 100
    importProgress.status = 'success'
    importProgress.uploaded = res.success_files + res.failed_files
    importProgress.total = res.total_files
    currentStage.value = 'complete'
    processingFiles.value.forEach(f => {
      if (f.status !== 'completed') {
        f.status = 'completed'
        f.statusText = '已导入'
        f.statusType = 'success'
        f.progress = 100
      }
    })

    const successCount = res.success_files ?? 0
    const failedCount = res.failed_files ?? 0
    ElMessage.success(
      successCount > 0
        ? `导入完成：成功 ${successCount} 个${failedCount > 0 ? `，失败 ${failedCount} 个` : ''}。请到「卷宗审核入库」中审核后入库。`
        : '导入完成，无成功文件。请检查格式（支持 PDF、DOC、DOCX）。'
    )

    importRecords.value.unshift({
      id: res.task_id,
      batchName,
      taskName: batchName,
      status: 'completed',
      totalFiles: res.total_files,
      successFiles: successCount,
      failedFiles: failedCount,
      createdAt: new Date().toISOString()
    })
    loadImportRecords()

    fileList.value = []
    importForm.batchName = ''
    importForm.defaultTags = []
    importForm.sourceDepartment = ''

    setTimeout(() => {
      importProgress.show = false
      processingFiles.value = []
      currentStage.value = ''
    }, 5000)
  } catch (error: any) {
    importProgress.status = 'exception'
    ElMessage.error(error?.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// OCR结果查看
const viewOcrResult = (task: any) => {
  selectedOcrTask.value = task
  correctedText.value = task.ocrText || ''
  ocrDialogVisible.value = true
}

const handleCopyOcrText = () => {
  if (correctedText.value) {
    navigator.clipboard.writeText(correctedText.value)
    ElMessage.success('已复制到剪贴板')
  }
}

const handleSaveOcrCorrect = async () => {
  if (!selectedOcrTask.value) return
  try {
    // 演示模式：直接更新本地数据
    const task = ocrTasks.value.find(t => t.id === selectedOcrTask.value.id)
    if (task) {
      task.ocrText = correctedText.value
      task.status = 'corrected'
    }
    ElMessage.success('校对结果已保存')
    ocrDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败')
  }
}

// 查看导入记录详情
const viewRecordDetail = (record: any) => {
  ElMessage.info(`查看批次：${record.batchName || '未命名批次'}`)
}

// 加载数据 - 演示模式
const loadOcrTasks = async () => {
  ocrTasksLoading.value = true
  try {
    // 演示模式：模拟加载延迟
    await delay(500)
    // 演示模式下不初始化数据，保持为空
    // 只有在用户实际导入文件后才会生成OCR任务
  } catch (error) {
    console.error('加载OCR任务失败:', error)
  } finally {
    ocrTasksLoading.value = false
  }
}

const loadImportRecords = async () => {
  recordsLoading.value = true
  try {
    const list = await caseFileApi.getImportTasks()
    importRecords.value = (Array.isArray(list) ? list : []).map((t: any) => ({
      id: t.id,
      batchName: t.taskName || '',
      taskName: t.taskName || '',
      status: t.status || 'completed',
      totalFiles: t.totalFiles ?? 0,
      successFiles: t.successFiles ?? 0,
      failedFiles: t.failedFiles ?? 0,
      createdAt: t.createdAt
    }))
  } catch (error) {
    console.error('加载导入记录失败:', error)
    importRecords.value = []
  } finally {
    recordsLoading.value = false
  }
}

onMounted(() => {
  loadImportRecords()
  loadOcrTasks()
})
</script>

<style scoped>
.case-import-view {
  font-family: var(--font-body);
}

/* 使用场景卡片 */
.usage-scenarios-card {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.usage-icon {
  color: var(--military-primary);
}

.usage-title {
  color: var(--military-text-primary);
}

.usage-list {
  color: var(--military-text-secondary);
}

.usage-list li {
  color: inherit;
}

.usage-list strong {
  color: var(--military-text-primary);
}

/* 提示文字 */
.tips-text {
  color: var(--military-text-secondary);
}

.help-text {
  color: var(--military-text-muted);
}

.form-label {
  color: var(--military-text-primary);
  font-weight: 500;
  font-size: 14px;
}

/* 上传区域 */
:deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
  border: 2px dashed var(--military-border);
  border-radius: var(--military-radius-lg);
  background: var(--military-bg-card);
  transition: all var(--military-transition);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--military-primary);
}

.upload-icon {
  color: var(--military-primary);
}

.upload-text {
  color: var(--military-text-primary);
  font-size: 14px;
  margin-top: 16px;
}

.upload-text-emphasis {
  color: var(--military-primary);
  font-weight: 600;
  cursor: pointer;
}

.upload-tip {
  color: var(--military-text-muted);
  font-size: 12px;
  margin-top: 8px;
}

/* 文件列表 */
.file-count {
  color: var(--military-text-secondary);
  font-size: 14px;
}

.file-count strong {
  color: var(--military-primary);
}

.clear-btn {
  color: var(--military-text-muted) !important;
}

.file-list-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  padding: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: var(--military-radius-sm);
  transition: background 0.2s;
}

.file-item:hover {
  background: var(--military-bg-card-hover);
}

.file-icon {
  color: var(--military-text-muted);
}

.file-name {
  color: var(--military-text-primary);
  font-size: 14px;
}

.file-type-tag {
  font-size: 10px;
}

.file-size {
  color: var(--military-text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.delete-btn {
  color: #ef4444 !important;
}

/* 导入状态 */
.import-status-text {
  color: var(--military-text-secondary);
  font-size: 14px;
}

.import-status-text strong {
  color: var(--military-primary);
}

.progress-label {
  color: var(--military-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.progress-count {
  color: var(--military-text-muted);
  font-size: 14px;
}

.progress-status {
  font-size: 14px;
}

.status-success {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #10b981;
}

.status-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ef4444;
}

.status-processing {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--military-text-secondary);
}

/* OCR任务列表 */
.section-title {
  color: var(--military-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.ocr-task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ocr-task-item {
  padding: 10px 12px;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-sm);
}

.ocr-task-clickable {
  cursor: pointer;
  transition: all 0.2s;
}

.ocr-task-clickable:hover {
  border-color: var(--military-primary);
  background: var(--military-bg-card-hover);
}

.task-filename {
  color: var(--military-text-primary);
  font-size: 13px;
}

.accuracy-text {
  color: var(--military-text-muted);
  font-size: 12px;
}

.view-icon {
  color: var(--military-text-muted);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--military-text-muted);
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

/* 导入记录 */
.import-timeline {
  padding-left: 0;
}

.record-item {
  cursor: pointer;
  padding: 8px;
  border-radius: var(--military-radius-sm);
  transition: background 0.2s;
}

.record-item:hover {
  background: var(--military-bg-card-hover);
}

.record-name {
  color: var(--military-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.record-stats {
  display: flex;
  gap: 12px;
  color: var(--military-text-muted);
  font-size: 12px;
}

.success-count {
  color: #10b981;
}

.failed-count {
  color: #ef4444;
}

/* OCR对话框 */
.ocr-result-content {
  color: var(--military-text-primary);
}

.result-label {
  color: var(--military-text-secondary);
  font-size: 13px;
}

.result-value {
  color: var(--military-text-primary);
  font-size: 14px;
}

.result-value.accuracy {
  color: #10b981;
  font-weight: 600;
}

/* 表单 */
.import-form :deep(.el-form-item__label) {
  color: var(--military-text-primary);
}

:deep(.el-cascader),
:deep(.el-select) {
  width: 100%;
}

/* ===== 多阶段导入进度面板 ===== */
.import-progress-panel {
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-lg);
  padding: 20px;
}

/* 阶段指示器 */
.stage-indicator {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--military-border);
}

.stage-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.stage-steps::before {
  content: '';
  position: absolute;
  top: 16px;
  left: 40px;
  right: 40px;
  height: 2px;
  background: var(--military-border);
  z-index: 0;
}

.stage-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
  flex: 1;
}

.stage-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  background: var(--military-bg-card);
  border: 2px solid var(--military-border);
  color: var(--military-text-muted);
  transition: all 0.3s ease;
}

.stage-step.active .stage-icon {
  background: var(--military-primary);
  border-color: var(--military-primary);
  color: white;
}

.stage-step.completed .stage-icon {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.stage-label {
  margin-top: 8px;
  font-size: 12px;
  color: var(--military-text-muted);
  white-space: nowrap;
}

.stage-step.active .stage-label {
  color: var(--military-primary);
  font-weight: 500;
}

.stage-step.completed .stage-label {
  color: #10b981;
}

/* 当前阶段详情 */
.current-stage-detail {
  padding: 16px 0;
}

/* 文件处理详情列表 */
.processing-files-list {
  border-top: 1px solid var(--military-border);
  padding-top: 16px;
}

.processing-header {
  color: var(--military-text-primary);
}

.processing-scroll-area {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  padding: 8px;
}

.processing-file-item {
  padding: 10px 12px;
  border-radius: var(--military-radius-sm);
  transition: background 0.2s;
  margin-bottom: 4px;
}

.processing-file-item:last-child {
  margin-bottom: 0;
}

.processing-file-item:hover {
  background: var(--military-bg-card-hover);
}

.file-status-icon {
  font-size: 16px;
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

.processing-file-item .file-name {
  color: var(--military-text-primary);
  font-size: 13px;
  max-width: 200px;
}

.file-progress-bar {
  margin-top: 6px;
}

/* 动画效果 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stage-step.active .stage-icon {
  animation: pulse 1.5s ease-in-out infinite;
}

/* 滚动条样式 */
.processing-scroll-area::-webkit-scrollbar {
  width: 6px;
}

.processing-scroll-area::-webkit-scrollbar-track {
  background: var(--military-bg-card);
  border-radius: 3px;
}

.processing-scroll-area::-webkit-scrollbar-thumb {
  background: var(--military-border);
  border-radius: 3px;
}

.processing-scroll-area::-webkit-scrollbar-thumb:hover {
  background: var(--military-text-muted);
}
</style>
