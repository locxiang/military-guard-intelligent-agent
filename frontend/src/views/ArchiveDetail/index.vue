<template>
  <div class="archive-detail-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 顶部操作栏 -->
    <TopActionBar
      :search-keyword="searchKeyword"
      :has-file="!!caseFile.filePath"
      @update:search-keyword="searchKeyword = $event"
      @view-document="showDocumentPreview = true"
      @download="handleDownload"
      @print="showPrintPreview = true"
    />

    <div v-loading="loading" class="space-y-4">
      <!-- 案件核心信息卡片 -->
      <CaseHeaderCard
        :case-file="caseFile"
        :highlight-text="(text: string) => highlightText(text, searchKeyword)"
        :format-date-time="formatDateTime"
        :get-status-type="getStatusType"
        :get-status-text="getStatusText"
      />

      <!-- 案件状态引导 -->
      <CaseStatusGuide
        :case-file="caseFile"
        :highlight-text="(text: string) => highlightText(text, searchKeyword)"
      />

      <!-- 主内容区域：左右分栏布局 -->
      <div class="main-content-layout">
        <!-- 左侧：案件核心内容 -->
        <div class="main-content-left">
          <!-- 1. 涉案人员信息 -->
          <CaseContentSection
            :number="1"
            title="涉案人员"
            subtitle="了解案件涉及的人员信息"
            :show="!!(caseFile.personName || caseFile.personInfo)"
          >
            <template #action>
              <button
                v-if="caseFile.personName"
                class="section-action-button"
                @click="searchRelatedByPerson"
              >
                <el-icon><Search /></el-icon>
                <span>查找相关案件</span>
              </button>
            </template>
            <div class="person-card">
              <div class="person-name-large" v-html="highlightText(caseFile.personName || '未知', searchKeyword)"></div>
              <div class="person-info-detail" v-if="caseFile.personInfo && Object.keys(caseFile.personInfo).length > 0">
                <div class="person-detail-row" v-if="caseFile.personInfo.gender">
                  <span class="detail-label">性别</span>
                  <span class="detail-value">{{ caseFile.personInfo.gender }}</span>
                </div>
                <div class="person-detail-row" v-if="caseFile.personInfo.nationality">
                  <span class="detail-label">民族</span>
                  <span class="detail-value">{{ caseFile.personInfo.nationality }}</span>
                </div>
                <div class="person-detail-row" v-if="caseFile.personInfo.birthPlace">
                  <span class="detail-label">出生地</span>
                  <span class="detail-value">{{ caseFile.personInfo.birthPlace }}</span>
                </div>
                <div class="person-detail-row" v-if="caseFile.personInfo.enlistmentTime">
                  <span class="detail-label">入伍时间</span>
                  <span class="detail-value">{{ formatDate(caseFile.personInfo.enlistmentTime) }}</span>
                </div>
                <div class="person-detail-row" v-if="caseFile.personInfo.position">
                  <span class="detail-label">部职别</span>
                  <span class="detail-value">{{ caseFile.personInfo.position }}</span>
                </div>
                <div class="person-detail-row" v-if="caseFile.personInfo.personCategory">
                  <span class="detail-label">人员类别</span>
                  <span class="detail-value">{{ caseFile.personInfo.personCategory }}</span>
                </div>
              </div>
              <div class="person-detail-row mt-2" v-if="caseFile.charge">
                <span class="detail-label">涉案罪名</span>
                <span class="detail-value">{{ caseFile.charge }}</span>
              </div>
              <div class="person-detail-row" v-if="caseFile.suicideMethod">
                <span class="detail-label">自杀方式/线索</span>
                <span class="detail-value">{{ caseFile.suicideMethod }}</span>
              </div>
            </div>
          </CaseContentSection>

          <!-- 案发位置地图 -->
          <CaseLocationMap />

          <!-- 2. 事发经过 -->
          <CaseContentSection
            :number="2"
            title="事发经过"
            subtitle="案件发生的具体情况"
            :show="!!caseFile.incidentProcess"
          >
            <div class="text-content-card" v-html="highlightText(caseFile.incidentProcess, searchKeyword)"></div>
          </CaseContentSection>

          <!-- 3. 侦查调查过程及结论 -->
          <CaseContentSection
            :number="3"
            title="侦查调查过程及结论"
            subtitle="案件调查的详细过程和最终结论"
            :show="!!caseFile.investigationProcessAndConclusion"
          >
            <div class="text-content-card" v-html="highlightText(caseFile.investigationProcessAndConclusion, searchKeyword)"></div>
          </CaseContentSection>

          <!-- 4. 原因教训 -->
          <CaseContentSection
            :number="4"
            title="原因教训"
            subtitle="案件反映出的问题和改进建议"
            :show="!!caseFile.causeAndLesson"
          >
            <div class="text-content-card warning" v-html="highlightText(caseFile.causeAndLesson, searchKeyword)"></div>
          </CaseContentSection>
        </div>

        <!-- 右侧：辅助信息 -->
        <div class="main-content-right">
          <!-- 案件时间线 -->
          <CaseTimeline :timeline="caseFile.timeline" />

          <!-- 原始文档 -->
          <CaseDocumentCard
            :file-path="caseFile.filePath"
            :file-size="caseFile.fileSize"
            :file-type="caseFile.fileType"
            :file-id="caseFile.id"
            @preview="showDocumentPreview = true"
            @download="handleDownload"
          />

          <!-- 分类和标签 -->
          <CaseClassificationTags
            :classification-level1="caseFile.classificationLevel1"
            :classification-level2="caseFile.classificationLevel2"
            :classification-level3="caseFile.classificationLevel3"
            :tags="caseFile.tags"
            @tag-click="searchKeyword = $event"
          />

          <!-- OCR识别文本 -->
          <CaseOcrText
            :ocr-text="caseFile.ocrText"
            :highlight-text="(text: string) => highlightText(text, searchKeyword)"
          />
        </div>
      </div>

      <!-- 关联案卷 -->
      <RelatedCasesSection
        :related-cases="relatedCases"
        @view-case="viewRelatedCase"
      />
    </div>

    <!-- 打印预览对话框 -->
    <PrintPreviewDialog
      v-model="showPrintPreview"
      :case-file="caseFile"
    />

    <!-- 文档预览对话框 -->
    <DocumentPreviewDialog
      v-model="showDocumentPreview"
      :file-path="caseFile.filePath"
      :file-type="caseFile.fileType"
      :file-id="caseFile.id"
      @download="handleDownload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { caseFileApi } from '@/api/archive'
import TopActionBar from './components/TopActionBar.vue'
import CaseHeaderCard from './components/CaseHeaderCard.vue'
import CaseStatusGuide from './components/CaseStatusGuide.vue'
import CaseContentSection from './components/CaseContentSection.vue'
import CaseLocationMap from './components/CaseLocationMap.vue'
import CaseTimeline from './components/CaseTimeline.vue'
import CaseDocumentCard from './components/CaseDocumentCard.vue'
import CaseClassificationTags from './components/CaseClassificationTags.vue'
import CaseOcrText from './components/CaseOcrText.vue'
import RelatedCasesSection from './components/RelatedCasesSection.vue'
import PrintPreviewDialog from './components/PrintPreviewDialog.vue'
import DocumentPreviewDialog from './components/DocumentPreviewDialog.vue'
import {
  highlightText,
  formatDateTime,
  formatDate,
  getStatusType,
  getStatusText,
  getFileName
} from './utils'

const route = useRoute()
const router = useRouter()

// 加载状态
const loading = ref(false)

// 档案信息
const caseFile = ref<any>({})

// 快速查询关键词
const searchKeyword = ref('')

// 文档预览（待实现对话框组件）
const showDocumentPreview = ref(false)

// 打印预览
const showPrintPreview = ref(false)

// 关联案卷
const relatedCases = ref<any[]>([])

// 加载关联案卷
const loadRelatedCases = async () => {
  try {
    const related: any[] = []
    
    // 按人员关联
    if (caseFile.value.personName) {
      const response = await caseFileApi.getList({
        keyword: caseFile.value.personName,
        page: 1,
        pageSize: 5
      })
      response.data.forEach((item: any) => {
        if (item.id !== caseFile.value.id) {
          related.push({
            ...item,
            relationReason: `相同人员: ${caseFile.value.personName}`
          })
        }
      })
    }
    
    // 按部门关联
    if (caseFile.value.sourceDepartment) {
      const response = await caseFileApi.getList({
        keyword: caseFile.value.sourceDepartment,
        page: 1,
        pageSize: 5
      })
      response.data.forEach((item: any) => {
        if (item.id !== caseFile.value.id && !related.find(r => r.id === item.id)) {
          related.push({
            ...item,
            relationReason: `相同部门: ${caseFile.value.sourceDepartment}`
          })
        }
      })
    }
    
    // 按罪名关联
    if (caseFile.value.caseType) {
      const response = await caseFileApi.getList({
        caseType: caseFile.value.caseType,
        page: 1,
        pageSize: 5
      })
      response.data.forEach((item: any) => {
        if (item.id !== caseFile.value.id && !related.find(r => r.id === item.id)) {
          related.push({
            ...item,
            relationReason: `相同罪名: ${caseFile.value.caseType}`
          })
        }
      })
    }
    
    relatedCases.value = related.slice(0, 10)
  } catch (error) {
    console.error('加载关联案卷失败:', error)
  }
}

// 查看关联案卷
const viewRelatedCase = (id: number) => {
  router.push(`/case-file/${id}`)
}

// 下载文件
const handleDownload = async () => {
  if (!caseFile.value.filePath) {
    ElMessage.warning('文件路径不存在')
    return
  }
  
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const fileUrl = `${baseUrl}/case-file/file/${caseFile.value.id}`
    const fileName = getFileName(caseFile.value.filePath)
    
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = fileName
    link.style.display = 'none'
    
    if (token) {
      const response = await fetch(fileUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error('下载失败')
      }
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      link.href = url
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('下载成功')
    } else {
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('下载已开始')
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '下载失败')
  }
}

// 按人员查找关联
const searchRelatedByPerson = () => {
  if (caseFile.value.personName) {
    router.push({
      path: '/case-file',
      query: { keyword: caseFile.value.personName }
    })
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const response = await caseFileApi.getDetail(id)
    caseFile.value = response
    // 加载关联案卷
    await loadRelatedCases()
  } catch (error: any) {
    ElMessage.error(error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.archive-detail-view {
  font-family: var(--font-body);
  color: var(--military-text-primary);
}

.main-content-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;
}

.main-content-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-content-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-action-button {
  padding: 6px 12px;
  background: var(--military-bg-input);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.section-action-button:hover {
  background: var(--military-primary);
  color: #ffffff;
  border-color: var(--military-primary);
}

.person-card {
  padding: 20px;
  background: var(--military-bg-input);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
}

.person-name-large {
  font-size: 24px;
  font-weight: 700;
  color: var(--military-primary);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--military-border);
}

.person-info-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.person-detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-label {
  font-size: 14px;
  color: var(--military-text-muted);
  font-weight: 500;
  min-width: 80px;
}

.detail-value {
  font-size: 15px;
  color: var(--military-text-primary);
  font-weight: 600;
}

.text-content-card {
  font-size: 15px;
  line-height: 1.8;
  color: var(--military-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 20px;
  background: var(--military-bg-input);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
}

.text-content-card.warning {
  border-left: 4px solid #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

:deep(.highlight-mark) {
  background: #fef08a;
  color: #854d0e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .main-content-layout {
    grid-template-columns: 1fr;
  }
}
</style>
