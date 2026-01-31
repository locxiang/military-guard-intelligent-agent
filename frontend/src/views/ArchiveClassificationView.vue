<template>
  <div class="archive-classification-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header mb-4">
        <h2 class="gov-card-title">卷宗审核入库</h2>
        <p class="gov-card-subtitle">审核AI提取的关键信息，确认无误后入库</p>
      </div>
      
      <!-- 业务说明 -->
      <div class="usage-scenarios-card rounded-lg p-4 mb-4">
        <div class="flex items-start gap-3">
          <el-icon class="usage-icon mt-0.5" :size="20">
            <InfoFilled />
          </el-icon>
          <div class="flex-1">
            <h4 class="usage-title text-sm font-semibold mb-2">审核流程</h4>
            <ol class="usage-list text-sm space-y-1 list-decimal list-inside">
              <li><strong>AI提取</strong>：系统自动从PDF/DOCX文件中提取关键字段信息</li>
              <li><strong>人工审核</strong>：对照原始文件，检查AI提取的字段是否正确</li>
              <li><strong>修正错误</strong>：发现错误时可直接修改字段内容</li>
              <li><strong>确认入库</strong>：审核无误后确认入库，卷宗正式进入档案库</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和统计 -->
    <div class="gov-card mb-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex flex-wrap items-center gap-3">
          <el-select
            v-model="filterStatus"
            placeholder="筛选状态"
            clearable
            style="width: 150px"
            @change="loadData"
          >
            <el-option label="全部" value="" />
            <el-option label="待审核" value="pending" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已入库" value="archived" />
          </el-select>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索卷宗名称..."
            clearable
            style="width: 250px"
            @input="loadData"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="flex items-center gap-4">
          <div class="stat-item">
            <span class="stat-label">待审核</span>
            <span class="stat-value text-yellow-600">{{ stats.pending }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已审核</span>
            <span class="stat-value text-blue-600">{{ stats.reviewed }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已入库</span>
            <span class="stat-value text-green-600">{{ stats.archived }}</span>
          </div>
          <el-button type="primary" :loading="loading" @click="loadData">
            <el-icon><Refresh /></el-icon>
            <span>刷新</span>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 卷宗列表 -->
    <div class="gov-card">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">待审核卷宗列表</h3>
        <p class="gov-card-subtitle">点击卷宗卡片开始审核</p>
      </div>

      <div v-loading="loading" class="archive-list">
        <div v-if="archiveList.length === 0" class="empty-state">
          <el-icon :size="48"><FolderOpened /></el-icon>
          <p class="mt-4">暂无待审核卷宗</p>
          <p class="text-sm text-gray-500 mt-2">导入任务完成后，卷宗会出现在这里</p>
        </div>
        <div v-else class="archive-grid">
          <div
            v-for="archive in archiveList"
            :key="archive.id"
            class="archive-card"
            :class="{
              'archive-card-pending': archive.status === 'pending',
              'archive-card-reviewed': archive.status === 'reviewed',
              'archive-card-archived': archive.status === 'archived'
            }"
            @click="viewArchiveDetail(archive)"
          >
            <div class="archive-card-header">
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <el-icon :class="['archive-status-icon', archive.status]">
                  <Clock v-if="archive.status === 'pending'" />
                  <CircleCheck v-else-if="archive.status === 'archived'" />
                  <DocumentChecked v-else />
                </el-icon>
                <div class="flex-1 min-w-0">
                  <h4 class="archive-name truncate">{{ archive.name }}</h4>
                  <p class="archive-meta text-xs text-gray-500 mt-1">
                    来源批次：{{ archive.batchName }}
                  </p>
                </div>
              </div>
              <el-tag :type="getStatusType(archive.status)" size="small">
                {{ getStatusText(archive.status) }}
              </el-tag>
            </div>
            
            <div class="archive-card-body">
              <div v-if="archive.extractedData?.caseName" class="archive-info-row">
                <span class="info-label">卷宗名：</span>
                <span class="info-value truncate">{{ archive.extractedData.caseName }}</span>
              </div>
              <div v-if="archive.extractedData?.personName" class="archive-info-row">
                <span class="info-label">涉案人员：</span>
                <span class="info-value">{{ archive.extractedData.personName }}</span>
              </div>
              <div v-if="archive.extractedData?.incidentTime" class="archive-info-row">
                <span class="info-label">发生时间：</span>
                <span class="info-value">{{ archive.extractedData.incidentTime }}</span>
              </div>
              <div v-if="archive.status === 'pending'" class="archive-hint text-xs text-gray-400 mt-2">
                <el-icon :size="12"><InfoFilled /></el-icon>
                <span class="ml-1">点击查看详情并审核</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 卷宗详情审核对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="selectedArchive ? `审核卷宗 - ${selectedArchive.name}` : '卷宗详情'"
      width="95%"
      :close-on-click-modal="false"
      class="archive-detail-dialog"
      top="5vh"
    >
      <div v-if="selectedArchive" class="archive-detail-content">
        <div class="detail-layout">
          <!-- 左侧：AI提取的关键字段 -->
          <div class="detail-left">
            <div class="detail-section">
              <div class="section-header">
                <h3 class="section-title">AI提取的关键信息</h3>
                <el-tag type="info" size="small">请对照右侧原始文件进行审核</el-tag>
              </div>
              
              <el-form :model="reviewForm" label-width="120px" class="review-form">
                <!-- 卷宗名 -->
                <el-form-item label="卷宗名" required>
                  <el-input
                    v-model="reviewForm.caseName"
                    placeholder="格式：时间+事发单位-人员类别+姓名+涉案罪名"
                    :rows="2"
                    type="textarea"
                  />
                  <div class="form-help-text">
                    格式说明：时间+事发单位-人员类别+姓名+涉案罪名(自杀方式、线索)
                  </div>
                </el-form-item>

                <!-- 发生时间 -->
                <el-form-item label="发生时间" required>
                  <el-date-picker
                    v-model="reviewForm.incidentTime"
                    type="datetime"
                    placeholder="选择发生时间"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DD HH:mm"
                    style="width: 100%"
                  />
                </el-form-item>

                <!-- 事发单位 -->
                <el-form-item label="事发单位">
                  <el-input v-model="reviewForm.incidentUnit" placeholder="填写事发单位" />
                </el-form-item>

                <!-- 人员基本信息 -->
                <el-divider content-position="left">人员基本信息</el-divider>
                
                <el-form-item label="姓名" required>
                  <el-input v-model="reviewForm.personName" placeholder="填写涉案人员姓名" />
                </el-form-item>

                <el-form-item label="性别">
                  <el-radio-group v-model="reviewForm.personGender">
                    <el-radio label="男">男</el-radio>
                    <el-radio label="女">女</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="民族">
                  <el-input v-model="reviewForm.personEthnicity" placeholder="填写民族" />
                </el-form-item>

                <el-form-item label="出生地">
                  <el-input v-model="reviewForm.personBirthplace" placeholder="填写出生地" />
                </el-form-item>

                <el-form-item label="入伍时间">
                  <el-date-picker
                    v-model="reviewForm.personEnlistTime"
                    type="date"
                    placeholder="选择入伍时间"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>

                <el-form-item label="部职别">
                  <el-input v-model="reviewForm.personPosition" placeholder="填写部职别" />
                </el-form-item>

                <el-form-item label="人员类别">
                  <el-select v-model="reviewForm.personCategory" placeholder="选择人员类别" clearable>
                    <el-option label="现役军人" value="现役军人" />
                    <el-option label="退役军人" value="退役军人" />
                    <el-option label="文职人员" value="文职人员" />
                    <el-option label="职工" value="职工" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>

                <!-- 涉案信息 -->
                <el-divider content-position="left">涉案信息</el-divider>

                <el-form-item label="涉案罪名">
                  <el-input v-model="reviewForm.charge" placeholder="填写涉案罪名" />
                </el-form-item>

                <el-form-item label="自杀方式/线索">
                  <el-input
                    v-model="reviewForm.suicideMethod"
                    placeholder="如涉及自杀，填写自杀方式或线索"
                    type="textarea"
                    :rows="2"
                  />
                </el-form-item>

                <!-- 事发经过 -->
                <el-divider content-position="left">事发经过</el-divider>

                <el-form-item label="事发经过" required>
                  <el-input
                    v-model="reviewForm.incidentProcess"
                    type="textarea"
                    :rows="4"
                    placeholder="详细描述事发经过"
                  />
                </el-form-item>

                <!-- 侦查调查 -->
                <el-divider content-position="left">侦查调查</el-divider>

                <el-form-item label="侦查调查过程">
                  <el-input
                    v-model="reviewForm.investigationProcess"
                    type="textarea"
                    :rows="4"
                    placeholder="描述侦查调查过程"
                  />
                </el-form-item>

                <el-form-item label="调查结论">
                  <el-input
                    v-model="reviewForm.investigationConclusion"
                    type="textarea"
                    :rows="3"
                    placeholder="填写调查结论"
                  />
                </el-form-item>

                <!-- 原因教训 -->
                <el-form-item label="原因教训">
                  <el-input
                    v-model="reviewForm.causeAndLesson"
                    type="textarea"
                    :rows="3"
                    placeholder="分析原因教训"
                  />
                </el-form-item>

                <!-- 立案判决 -->
                <el-divider content-position="left">立案判决</el-divider>

                <el-form-item label="立案情况">
                  <el-input
                    v-model="reviewForm.caseFiling"
                    type="textarea"
                    :rows="2"
                    placeholder="填写立案情况"
                  />
                </el-form-item>

                <el-form-item label="判决情况">
                  <el-input
                    v-model="reviewForm.judgment"
                    type="textarea"
                    :rows="2"
                    placeholder="填写判决情况"
                  />
                </el-form-item>

                <!-- 分类和标签 -->
                <el-divider content-position="left">分类标签</el-divider>

                <el-form-item label="一级分类">
                  <el-select v-model="reviewForm.classification.level1" placeholder="请选择一级分类" clearable>
                    <el-option label="刑事案件" value="刑事案件" />
                    <el-option label="行政案件" value="行政案件" />
                    <el-option label="民事案件" value="民事案件" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>

                <el-form-item v-if="reviewForm.classification.level1" label="二级分类">
                  <el-select v-model="reviewForm.classification.level2" placeholder="请选择二级分类" clearable>
                    <el-option
                      v-for="option in getLevel2Options(reviewForm.classification.level1)"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item v-if="reviewForm.classification.level2" label="三级分类">
                  <el-select v-model="reviewForm.classification.level3" placeholder="请选择三级分类" clearable>
                    <el-option
                      v-for="option in getLevel3Options(reviewForm.classification.level2)"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="标签">
                  <el-select
                    v-model="reviewForm.tags"
                    multiple
                    filterable
                    allow-create
                    placeholder="选择或输入标签"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="tag in commonTags"
                      :key="tag"
                      :label="tag"
                      :value="tag"
                    />
                  </el-select>
                </el-form-item>

                <!-- 备注 -->
                <el-form-item label="审核备注">
                  <el-input
                    v-model="reviewForm.notes"
                    type="textarea"
                    :rows="2"
                    placeholder="填写审核备注信息（可选）"
                  />
                </el-form-item>
              </el-form>
            </div>
          </div>

          <!-- 右侧：原始文件预览 -->
          <div class="detail-right">
            <div class="detail-section">
              <div class="section-header">
                <h3 class="section-title">原始文件预览</h3>
                <el-tag type="warning" size="small">{{ selectedArchive.fileType?.toUpperCase() || 'PDF' }}</el-tag>
              </div>
              
              <div class="file-preview-container">
                <!-- PDF预览 -->
                <div v-if="selectedArchive.fileType === 'pdf' || (!selectedArchive.fileType && selectedArchive.name?.toLowerCase().endsWith('.pdf'))" class="file-preview">
                  <iframe
                    :src="getFilePreviewUrl(selectedArchive)"
                    class="preview-iframe"
                    frameborder="0"
                  ></iframe>
                </div>
                
                <!-- DOCX预览 - 显示识别文字内容，模拟文档样式 -->
                <div v-else class="file-preview">
                  <div class="docx-preview-container">
                    <div class="docx-preview-header">
                      <div class="flex items-center gap-2">
                        <el-icon><DocumentCopy /></el-icon>
                        <span>原始文件内容</span>
                      </div>
                      <el-button type="primary" size="small" :href="'/case1.docx'" download>
                        <el-icon><DownloadIcon /></el-icon>
                        <span>下载原始文件</span>
                      </el-button>
                    </div>
                    <div class="docx-text-content">
                      <div v-if="selectedArchive.ocrText" class="docx-document">
                        <div class="docx-text" v-html="formatDocxText(selectedArchive.ocrText)"></div>
                      </div>
                      <div v-else class="docx-empty">
                        <el-icon :size="48"><DocumentCopy /></el-icon>
                        <p>暂无识别内容</p>
                        <p class="text-sm mt-2">请下载原始文件查看</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 文件信息 -->
                <div class="file-info-bar">
                  <div class="file-info-item">
                    <el-icon><Document /></el-icon>
                    <span>{{ selectedArchive.name }}</span>
                  </div>
                  <div class="file-info-item">
                    <el-icon><FolderOpened /></el-icon>
                    <span>{{ selectedArchive.batchName }}</span>
                  </div>
                  <div class="file-info-item">
                    <el-icon><InfoFilled /></el-icon>
                    <span>{{ formatFileSize(selectedArchive.size || 0) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between">
          <el-button @click="showDetailDialog = false">取消</el-button>
          <div class="flex gap-2">
            <el-button
              v-if="selectedArchive?.status === 'pending'"
              @click="handleSaveReview"
              type="primary"
            >
              保存审核
            </el-button>
            <el-button
              v-if="selectedArchive?.status !== 'archived'"
              @click="handleArchive"
              type="success"
              :disabled="!isFormValid"
            >
              确认入库
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Search,
  FolderOpened,
  Clock,
  CircleCheck,
  DocumentChecked,
  InfoFilled,
  DocumentCopy,
  Document,
  Warning,
  Close,
  Download as DownloadIcon
} from '@element-plus/icons-vue'

// 延时函数
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 加载状态
const loading = ref(false)

// 筛选条件
const filterStatus = ref('')
const searchKeyword = ref('')

// 卷宗列表
const archiveList = ref<any[]>([])

// 统计信息
const stats = computed(() => {
  return {
    pending: archiveList.value.filter(a => a.status === 'pending').length,
    reviewed: archiveList.value.filter(a => a.status === 'reviewed').length,
    archived: archiveList.value.filter(a => a.status === 'archived').length
  }
})

// 详情对话框
const showDetailDialog = ref(false)
const selectedArchive = ref<any>(null)

// 审核表单
const reviewForm = ref({
  caseName: '',
  incidentTime: '',
  incidentUnit: '',
  personName: '',
  personGender: '',
  personEthnicity: '',
  personBirthplace: '',
  personEnlistTime: '',
  personPosition: '',
  personCategory: '',
  charge: '',
  suicideMethod: '',
  incidentProcess: '',
  investigationProcess: '',
  investigationConclusion: '',
  causeAndLesson: '',
  caseFiling: '',
  judgment: '',
  classification: {
    level1: '',
    level2: '',
    level3: ''
  },
  tags: [] as string[],
  notes: ''
})

// 表单验证
const isFormValid = computed(() => {
  return !!(
    reviewForm.value.caseName &&
    reviewForm.value.incidentTime &&
    reviewForm.value.personName &&
    reviewForm.value.incidentProcess
  )
})

// 常用标签
const commonTags = ref(['重要', '紧急', '已归档', '待处理', '涉密', '刑事案件', '行政案件'])

// 二级分类选项
const getLevel2Options = (level1: string) => {
  const options: Record<string, Array<{ label: string; value: string }>> = {
    '刑事案件': [
      { label: '盗窃案', value: '盗窃案' },
      { label: '诈骗案', value: '诈骗案' },
      { label: '故意伤害案', value: '故意伤害案' },
      { label: '其他刑事案件', value: '其他刑事案件' }
    ],
    '行政案件': [
      { label: '违纪', value: '违纪' },
      { label: '违规', value: '违规' },
      { label: '其他行政案件', value: '其他行政案件' }
    ],
    '民事案件': [
      { label: '合同纠纷', value: '合同纠纷' },
      { label: '财产纠纷', value: '财产纠纷' },
      { label: '其他民事案件', value: '其他民事案件' }
    ],
    '其他': [
      { label: '其他', value: '其他' }
    ]
  }
  return options[level1] || []
}

// 三级分类选项
const getLevel3Options = (level2: string) => {
  const options: Record<string, Array<{ label: string; value: string }>> = {
    '盗窃案': [
      { label: '入室盗窃', value: '入室盗窃' },
      { label: '公共场所盗窃', value: '公共场所盗窃' }
    ],
    '诈骗案': [
      { label: '电信诈骗', value: '电信诈骗' },
      { label: '网络诈骗', value: '网络诈骗' }
    ]
  }
  return options[level2] || []
}

// 获取文件预览URL
const getFilePreviewUrl = (archive: any) => {
  // PDF文件使用public目录下的case2.pdf
  return window.location.origin + '/case2.pdf'
}

// 查看卷宗详情
const viewArchiveDetail = (archive: any) => {
  selectedArchive.value = archive
  
  // 初始化审核表单（使用AI提取的数据）
  const extracted = archive.extractedData || {}
  reviewForm.value = {
    caseName: extracted.caseName || '',
    incidentTime: extracted.incidentTime || '',
    incidentUnit: extracted.incidentUnit || '',
    personName: extracted.personName || '',
    personGender: extracted.personGender || '',
    personEthnicity: extracted.personEthnicity || '',
    personBirthplace: extracted.personBirthplace || '',
    personEnlistTime: extracted.personEnlistTime || '',
    personPosition: extracted.personPosition || '',
    personCategory: extracted.personCategory || '',
    charge: extracted.charge || '',
    suicideMethod: extracted.suicideMethod || '',
    incidentProcess: extracted.incidentProcess || '',
    investigationProcess: extracted.investigationProcess || '',
    investigationConclusion: extracted.investigationConclusion || '',
    causeAndLesson: extracted.causeAndLesson || '',
    caseFiling: extracted.caseFiling || '',
    judgment: extracted.judgment || '',
    classification: {
      level1: archive.classification?.level1 || '',
      level2: archive.classification?.level2 || '',
      level3: archive.classification?.level3 || ''
    },
    tags: archive.tags || [],
    notes: archive.notes || ''
  }
  
  showDetailDialog.value = true
}

// 保存审核
const handleSaveReview = async () => {
  if (!selectedArchive.value) return
  
  try {
    // 演示模式：更新本地数据
    const archive = archiveList.value.find(a => a.id === selectedArchive.value.id)
    if (archive) {
      archive.extractedData = { ...reviewForm.value }
      archive.classification = { ...reviewForm.value.classification }
      archive.tags = [...reviewForm.value.tags]
      archive.notes = reviewForm.value.notes
      archive.status = 'reviewed'
    }
    
    ElMessage.success('审核信息已保存')
    showDetailDialog.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败')
  }
}

// 确认入库
const handleArchive = async () => {
  if (!selectedArchive.value) return
  
  if (!isFormValid.value) {
    ElMessage.warning('请填写必填字段：卷宗名、发生时间、姓名、事发经过')
    return
  }
  
  try {
    // 演示模式：更新本地数据
    const archive = archiveList.value.find(a => a.id === selectedArchive.value.id)
    if (archive) {
      archive.extractedData = { ...reviewForm.value }
      archive.classification = { ...reviewForm.value.classification }
      archive.tags = [...reviewForm.value.tags]
      archive.notes = reviewForm.value.notes
      archive.status = 'archived'
      archive.archivedAt = new Date().toISOString()
    }
    
    ElMessage.success('卷宗已成功入库')
    showDetailDialog.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.message || '入库失败')
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    reviewed: 'info',
    archived: 'success'
  }
  return map[status] || 'info'
}

// 获取状态文字
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审核',
    reviewed: '已审核',
    archived: '已入库'
  }
  return map[status] || status
}

// 格式化日期
const formatDate = (date: Date | string) => {
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
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化DOCX文本，模拟文档样式
const formatDocxText = (text: string) => {
  if (!text) return ''
  
  // 将文本按行分割
  const lines = text.split('\n')
  
  // 处理每一行，识别标题、段落等
  return lines.map(line => {
    const trimmed = line.trim()
    
    // 空行
    if (!trimmed) {
      return '<div class="docx-paragraph-spacing"></div>'
    }
    
    // 识别标题（以数字开头或包含特定关键词）
    if (/^\d+[、.]/.test(trimmed) || /^[一二三四五六七八九十]+[、.]/.test(trimmed)) {
      return `<div class="docx-heading">${trimmed}</div>`
    }
    
    // 识别小标题（短行且包含冒号）
    if (trimmed.length < 30 && trimmed.includes('：')) {
      return `<div class="docx-subheading">${trimmed}</div>`
    }
    
    // 普通段落
    return `<div class="docx-paragraph">${trimmed}</div>`
  }).join('')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    await delay(500)
    
    // 演示数据：从导入任务中生成的卷宗，包含AI提取的数据
    const demoTasks = [
      {
        id: 1001,
        batchName: '2025年1月卷宗导入批次',
        files: [
          {
            name: '张某案卷宗.pdf',
            size: 8 * 1024 * 1024,
            fileType: 'pdf',
            extractedData: {
              caseName: '2025-01-15 某部队-现役军人-张某-盗窃案',
              incidentTime: '2025-01-15 21:30',
              incidentUnit: '某部队营区',
              personName: '张某',
              personGender: '男',
              personEthnicity: '汉族',
              personBirthplace: '山东省济南市',
              personEnlistTime: '2020-03-01',
              personPosition: '某连队战士',
              personCategory: '现役军人',
              charge: '盗窃罪',
              incidentProcess: '2025年1月15日晚21时许，嫌疑人张某趁夜间值班人员不注意，潜入营区仓库，盗取军用物资若干。',
              investigationProcess: '接到报案后，保卫部门立即展开调查，通过监控录像和现场勘查，锁定嫌疑人张某。',
              investigationConclusion: '张某对盗窃行为供认不讳，案件事实清楚，证据确凿。',
              causeAndLesson: '暴露出营区安全管理存在漏洞，需要加强夜间巡逻和仓库管理。',
              caseFiling: '2025年1月16日立案',
              judgment: '待判决'
            }
          },
          {
            name: '李某案卷宗.docx',
            size: 12 * 1024 * 1024,
            fileType: 'docx',
            ocrText: '案件编号：2025-BW-0012\n案发时间：2025年1月10日\n案发地点：某单位办公室\n\n基本案情：\n2025年1月10日上午，李某在办公室内违规操作，导致重要文件丢失...',
            extractedData: {
              caseName: '2025-01-10 某单位-文职人员-李某-违规操作',
              incidentTime: '2025-01-10 09:00',
              incidentUnit: '某单位',
              personName: '李某',
              personGender: '女',
              personEthnicity: '汉族',
              personBirthplace: '北京市',
              personEnlistTime: '',
              personPosition: '办公室文员',
              personCategory: '文职人员',
              charge: '违规操作',
              incidentProcess: '2025年1月10日上午，李某在办公室内违规操作计算机系统，导致重要文件丢失。',
              investigationProcess: '单位保卫部门接到报告后，立即展开调查，调取监控录像和系统日志。',
              investigationConclusion: '李某承认违规操作，但声称是无意之举。',
              causeAndLesson: '需要加强员工操作规范培训，完善系统权限管理。',
              caseFiling: '2025年1月11日立案',
              judgment: '给予行政警告处分'
            }
          }
        ],
        createdAt: new Date(Date.now() - 3600000).toISOString()
      }
    ]
    
    // 生成卷宗列表
    const archives: any[] = []
    let archiveId = 1
    
    demoTasks.forEach(task => {
      task.files.forEach((file, index) => {
        const status = index === 0 ? 'pending' : 'reviewed'
        archives.push({
          id: archiveId++,
          name: file.name,
          batchName: task.batchName,
          size: file.size,
          fileType: file.fileType,
          status: status,
          createdAt: task.createdAt,
          extractedData: file.extractedData,
          ocrText: file.ocrText,
          classification: status === 'reviewed' ? {
            level1: '行政案件',
            level2: '违规'
          } : null,
          tags: status === 'reviewed' ? ['待处理'] : []
        })
      })
    })
    
    // 应用筛选
    let filtered = archives
    if (filterStatus.value) {
      filtered = filtered.filter(a => a.status === filterStatus.value)
    }
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      filtered = filtered.filter(a => a.name.toLowerCase().includes(keyword))
    }
    
    archiveList.value = filtered
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.archive-classification-view {
  font-family: var(--font-body);
}

/* 业务说明卡片 */
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

/* 统计项 */
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--military-text-muted);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

/* 卷宗列表 */
.archive-list {
  min-height: 400px;
}

.archive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.archive-card {
  padding: 16px;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.archive-card:hover {
  border-color: var(--military-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.archive-card-pending {
  border-left: 4px solid #f59e0b;
}

.archive-card-reviewed {
  border-left: 4px solid #3b82f6;
}

.archive-card-archived {
  border-left: 4px solid #10b981;
}

.archive-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.archive-status-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.archive-status-icon.pending {
  color: #f59e0b;
}

.archive-status-icon.reviewed {
  color: #3b82f6;
}

.archive-status-icon.archived {
  color: #10b981;
}

.archive-name {
  color: var(--military-text-primary);
  font-size: 15px;
  font-weight: 600;
}

.archive-meta {
  color: var(--military-text-muted);
}

.archive-card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.archive-info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.info-label {
  color: var(--military-text-muted);
  white-space: nowrap;
}

.info-value {
  color: var(--military-text-primary);
}

.archive-hint {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 详情对话框 */
.archive-detail-content {
  max-height: 80vh;
  overflow: hidden;
}

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  height: 75vh;
}

.detail-left {
  overflow-y: auto;
  padding-right: 12px;
}

.detail-right {
  overflow-y: auto;
  padding-left: 12px;
  border-left: 1px solid var(--military-border);
}

.detail-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  color: var(--military-text-primary);
  font-size: 16px;
  font-weight: 600;
}

/* 表单样式 */
.review-form {
  padding-right: 8px;
}

.form-help-text {
  font-size: 12px;
  color: var(--military-text-muted);
  margin-top: 4px;
}

/* 文件预览 */
.file-preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.file-preview {
  flex: 1;
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  overflow: hidden;
  background: #f5f5f5;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.docx-preview {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  background: white;
}

.docx-text {
  color: var(--military-text-primary);
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.docx-preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
}

.docx-preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--military-bg-card);
  border-bottom: 1px solid var(--military-border);
}

.docx-text-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  background: #f5f5f5;
}

.docx-document {
  background: white;
  min-height: 100%;
  padding: 72px 96px;
  margin: 0 auto;
  max-width: 816px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.docx-text {
  font-family: 'SimSun', '宋体', 'Times New Roman', serif;
  font-size: 16px;
  line-height: 1.5;
  color: #000;
  text-align: justify;
}

.docx-heading {
  font-size: 18px;
  font-weight: bold;
  margin: 24px 0 12px 0;
  color: #000;
  text-align: left;
}

.docx-subheading {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #333;
  text-align: left;
}

.docx-paragraph {
  margin: 12px 0;
  text-indent: 2em;
  line-height: 1.8;
  color: #000;
}

.docx-paragraph-spacing {
  height: 12px;
}

.docx-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--military-text-muted);
  padding: 40px;
}

.docx-empty p {
  margin-top: 12px;
  font-size: 14px;
}

.file-info-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: var(--military-bg-card);
  border-top: 1px solid var(--military-border);
  margin-top: 8px;
}

.file-info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--military-text-muted);
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

/* 滚动条样式 */
.detail-left::-webkit-scrollbar,
.detail-right::-webkit-scrollbar {
  width: 6px;
}

.detail-left::-webkit-scrollbar-track,
.detail-right::-webkit-scrollbar-track {
  background: var(--military-bg-card);
}

.detail-left::-webkit-scrollbar-thumb,
.detail-right::-webkit-scrollbar-thumb {
  background: var(--military-border);
  border-radius: 3px;
}

.detail-left::-webkit-scrollbar-thumb:hover,
.detail-right::-webkit-scrollbar-thumb:hover {
  background: var(--military-text-muted);
}
</style>
