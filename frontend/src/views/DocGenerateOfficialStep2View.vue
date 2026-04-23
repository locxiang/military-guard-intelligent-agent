<template>
  <div class="doc-generate-official-step2-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header flex items-center justify-between">
        <div class="flex items-center gap-4">
          <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
          <div>
            <h2 class="gov-card-title">公文助手（国标格式）</h2>
            <p class="gov-card-subtitle">第二步：AI 分段生成内容</p>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto space-y-6">
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">操作进度</h3>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="step-indicator done">
              <el-icon><Check /></el-icon>
            </div>
            <span class="step-label">填写信息</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="generating || Object.keys(generatedSections).length > 0 ? 'bg-primary' : 'bg-gray-300'"></div>
          <div class="flex items-center gap-3">
            <div class="step-indicator" :class="generating || Object.keys(generatedSections).length > 0 ? 'active' : ''">
              <span>2</span>
            </div>
            <span class="step-label">生成内容</span>
          </div>
          <div class="flex-1 h-1 mx-4" :class="canGoToNext ? 'bg-primary' : 'bg-gray-300'"></div>
          <div class="flex items-center gap-3">
            <div class="step-indicator" :class="canGoToNext ? 'active' : ''">
              <span>3</span>
            </div>
            <span class="step-label">预览文档</span>
          </div>
        </div>
      </div>

      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">生成内容（可编辑）</h3>
          <p class="gov-card-subtitle">AI 生成的内容可直接编辑，确认无误后点击「下一步」</p>
        </div>

        <div v-if="!generating && Object.keys(generatedSections).length === 0" class="empty-state">
          <el-icon class="empty-icon"><Document /></el-icon>
          <p>点击「开始生成」让 AI 分段生成内容</p>
          <button class="gov-button-primary mt-4 flex items-center gap-2" @click="handleGenerate">
            <el-icon><MagicStick /></el-icon>
            <span>开始生成</span>
          </button>
        </div>

        <div v-else class="sections-editor">
          <div
            v-for="(section, index) in sectionList"
            :key="section.section_id"
            class="section-item"
            :class="{ 'generating': currentGeneratingSection === section.section_id }"
          >
            <div class="section-header">
              <span class="section-index">{{ index + 1 }}</span>
              <span class="section-name">{{ section.section_name }}</span>
              <el-tag v-if="sectionStatus[section.section_id] === 'done'" size="small" type="success">已完成</el-tag>
              <el-tag v-else-if="sectionStatus[section.section_id] === 'generating'" size="small" type="warning">生成中</el-tag>
              <el-tag v-else size="small" type="info">等待中</el-tag>
            </div>
            <el-input
              v-if="sectionStatus[section.section_id] !== 'pending'"
              v-model="generatedSections[section.section_id]"
              type="textarea"
              :rows="4"
              class="section-textarea"
              @input="handleSectionChange(section.section_id, $event)"
            />
            <div v-else class="section-pending">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>等待生成...</span>
            </div>
          </div>
        </div>
      </div>

      <div class="gov-card">
        <div class="flex items-center justify-between">
          <button class="gov-button-default flex items-center gap-2" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回修改</span>
          </button>
          <div class="flex items-center gap-3">
            <button
              v-if="Object.keys(generatedSections).length > 0 && !generating"
              class="gov-button-default flex items-center gap-2"
              @click="handleRegenerate"
            >
              <el-icon><Refresh /></el-icon>
              <span>重新生成</span>
            </button>
            <button
              v-if="canGoToNext"
              class="gov-button-primary flex items-center gap-2"
              @click="handleNextStep"
            >
              <span>下一步：预览文档</span>
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Refresh, MagicStick, Check, ArrowLeft, ArrowRight, Loading } from '@element-plus/icons-vue'

const router = useRouter()

const generating = ref(false)
const currentGeneratingSection = ref('')
const generatedSections = ref<Record<string, string>>({})
const sectionStatus = ref<Record<string, 'pending' | 'generating' | 'done'>>({})
const sectionList = ref<any[]>([])
const docData = ref<any>(null)

const canGoToNext = computed(() => {
  return Object.keys(generatedSections.value).length > 0 &&
    !generating.value &&
    sectionList.value.every((s: any) => sectionStatus.value[s.section_id] === 'done')
})

const loadStoredData = () => {
  const savedData = sessionStorage.getItem('officialDocData')
  if (!savedData) {
    ElMessage.error('未找到公文数据，请先填写表单')
    router.push('/doc-generate/official/step1')
    return
  }
  try {
    docData.value = JSON.parse(savedData)
  } catch (e) {
    ElMessage.error('数据解析失败')
    router.push('/doc-generate/official/step1')
  }
}

const handleGenerate = async () => {
  if (!docData.value) return

  generating.value = true
  generatedSections.value = {}
  sectionStatus.value = {}

  try {
    const structureResponse = await fetch('/api/v1/doc-generate/structure/' + docData.value.docType, {
      headers: {
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || sessionStorage.getItem('token'))
      }
    })

    if (!structureResponse.ok) throw new Error('获取结构失败')
    const structureData = await structureResponse.json()
    sectionList.value = structureData.data.sections || []

    sectionList.value.forEach((section: any) => {
      sectionStatus.value[section.section_id] = 'pending'
    })

    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const response = await fetch('/api/v1/doc-generate/official/generate-content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({
        doc_type: docData.value.docType,
        form_data: docData.value.formData || {}
      })
    })

    if (!response.ok) throw new Error('生成失败')

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) throw new Error('无法读取响应流')

    let buffer = ''
    let currentSectionId = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.error) throw new Error(data.error)

            if (data.type === 'section_start') {
              currentSectionId = data.section_id
              currentGeneratingSection.value = currentSectionId
              sectionStatus.value[currentSectionId] = 'generating'
              generatedSections.value[currentSectionId] = ''
            } else if (data.type === 'content' && data.section_id) {
              generatedSections.value[data.section_id] = (generatedSections.value[data.section_id] || '') + data.content
            } else if (data.type === 'section_complete') {
              sectionStatus.value[data.section_id] = 'done'
              if (currentGeneratingSection.value === data.section_id) {
                currentGeneratingSection.value = ''
              }
            } else if (data.type === 'all_complete') {
              ElMessage.success('内容生成完成')
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e)
          }
        }
      }
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '生成失败，请重试')
  } finally {
    generating.value = false
    currentGeneratingSection.value = ''
  }
}

const handleSectionChange = (sectionId: string, value: any) => {
  generatedSections.value[sectionId] = value
}

const handleRegenerate = () => {
  handleGenerate()
}

const handleNextStep = () => {
  const updatedData = {
    ...docData.value,
    sections: { ...generatedSections.value }
  }
  sessionStorage.setItem('officialDocData', JSON.stringify(updatedData))

  router.push({
    path: '/doc-generate/official/step3',
    query: {
      docType: docData.value.docType
    }
  })
}

const goBack = () => {
  router.push('/doc-generate/official')
}

onMounted(() => {
  loadStoredData()
})
</script>

<style scoped>
.doc-generate-official-step2-view {
  font-family: var(--font-body);
}

.step-indicator {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--military-text-secondary);
  font-weight: 600;
  transition: all 0.3s ease;
}

.step-indicator.active {
  background: var(--military-primary);
  border-color: var(--military-primary);
  color: #fff;
}

.step-indicator.done {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}

.step-label {
  font-size: 14px;
  color: var(--military-text-secondary);
}

.bg-primary {
  background: var(--military-primary);
}

.bg-gray-300 {
  background: rgba(10, 22, 40, 0.3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--military-text-muted);
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.sections-editor {
  space-y: 16px;
}

.section-item {
  background: rgba(10, 22, 40, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.section-item.generating {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.section-index {
  width: 28px;
  height: 28px;
  background: rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  color: var(--military-text-primary);
  flex-shrink: 0;
}

.section-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.section-textarea {
  width: 100%;
}

.section-pending {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--military-text-muted);
  padding: 16px 0;
}

:deep(.el-textarea__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
  color: var(--military-text-primary) !important;
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-textarea__inner:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
  background-color: rgba(10, 22, 40, 0.7) !important;
}

:deep(.el-textarea__inner:focus) {
  border-color: var(--military-primary) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-textarea__inner::placeholder) {
  color: var(--military-text-muted) !important;
  opacity: 0.7;
}
</style>
