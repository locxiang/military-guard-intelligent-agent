<template>
  <div class="content-review-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">内容审查</h2>
        <p class="gov-card-subtitle">上传公文后，系统将自动检查错别字、用词是否妥当、是否符合政府/部队公文写法，并给出修改意见</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="上传 .docx 格式的公文，系统会分析正文中的错别字、用词不当以及不符合公文规范之处，并给出具体修改建议"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="gov-card content-review-card">
      <!-- 上传区域 -->
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title content-review-step-title">第一步：上传待审查的公文</h3>
        <p class="gov-card-subtitle content-review-step-desc">请上传 .docx 格式的公文文件，系统将提取正文并进行审查</p>
      </div>
      <el-upload
        ref="uploadRef"
        class="content-review-upload gov-upload-area"
        drag
        :auto-upload="false"
        :show-file-list="true"
        :limit="1"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        accept=".docx"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">将公文文件拖到此处，或<em>点击选择</em></div>
        <template #tip>
          <div class="upload-tip">仅支持 .docx 格式，单次上传一个文件</div>
        </template>
      </el-upload>

      <!-- 开始审查按钮 -->
      <div class="mt-6 flex flex-wrap items-center gap-4">
        <button
          class="gov-button-primary flex items-center gap-2"
          :disabled="!currentFile || loading"
          @click="handleReview"
        >
          <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
          <el-icon v-else><DocumentChecked /></el-icon>
          <span>{{ loading ? '审查中…' : '开始审查' }}</span>
        </button>
        <button
          class="gov-button-default flex items-center gap-2"
          :disabled="loading"
          @click="handleClear"
        >
          <el-icon><RefreshLeft /></el-icon>
          <span>清空</span>
        </button>
      </div>
    </div>

    <!-- 审查结果（SSE 流式输出，Markdown 渲染） -->
    <div v-if="displayContent !== '' || loading" class="gov-card mt-6">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">审查结果</h3>
        <p class="gov-card-subtitle">以下为系统以 Markdown 格式流式输出的修改意见，供您参考后自行修改公文</p>
      </div>
      <div
        ref="contentRef"
        class="review-result-content markdown-body"
        v-html="renderedContent"
      />
      <div v-if="loading" class="review-streaming-tip">正在输出修改建议…</div>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="errorMsg"
      type="error"
      :title="errorMsg"
      show-icon
      closable
      class="mt-4"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, UploadFilled, DocumentChecked, RefreshLeft, Loading } from '@element-plus/icons-vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import { marked } from 'marked'

const uploadRef = ref<UploadInstance | null>(null)
const currentFile = ref<File | null>(null)
const loading = ref(false)
const displayContent = ref('')
const contentRef = ref<HTMLElement | null>(null)
const errorMsg = ref('')

const renderedContent = computed(() => {
  if (!displayContent.value) return ''
  return marked(displayContent.value, { breaks: true, gfm: true })
})

function handleFileChange(_uploadFile: UploadFile, uploadFiles: UploadFile[]) {
  const raw = uploadFiles[0]?.raw
  currentFile.value = raw ? (raw as File) : null
  if (!currentFile.value) return
  const name = (currentFile.value as File).name
  if (!name.toLowerCase().endsWith('.docx')) {
    ElMessage.warning('请选择 .docx 格式的公文文件')
    currentFile.value = null
    uploadRef.value?.clearFiles()
  }
}

function handleExceed() {
  ElMessage.warning('单次仅支持上传一个文件，请先移除当前文件再选择')
}

async function handleReview() {
  if (!currentFile.value || loading.value) return
  loading.value = true
  displayContent.value = ''
  errorMsg.value = ''
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  const formData = new FormData()
  formData.append('file', currentFile.value)

  try {
    const response = await fetch('/api/v1/content-review/review/stream', {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: formData
    })
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || `请求失败 ${response.status}`)
    }
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) throw new Error('无法读取响应流')
    let buffer = ''
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
            if (data.done) {
              loading.value = false
              ElMessage.success('审查完成')
              return
            }
            if (data.content) {
              displayContent.value += data.content
              nextTick(() => {
                if (contentRef.value) {
                  contentRef.value.scrollTop = contentRef.value.scrollHeight
                }
              })
            }
          } catch (e) {
            if (e instanceof Error && e.message !== '审查完成') {
              console.error('解析 SSE 失败:', e)
            }
          }
        }
      }
    }
    loading.value = false
    ElMessage.success('审查完成')
  } catch (e: any) {
    loading.value = false
    errorMsg.value = e?.message || '审查失败，请稍后重试'
    ElMessage.error(errorMsg.value)
  }
}

function handleClear() {
  currentFile.value = null
  displayContent.value = ''
  errorMsg.value = ''
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.content-review-view {
  font-family: var(--font-body);
}

/* 本页卡片内标题与说明：与系统军事风格一致 */
.content-review-card .content-review-step-title {
  color: var(--military-text-primary);
}

.content-review-card .content-review-step-desc {
  color: var(--military-text-muted);
}

/* 上传区域：与系统军事风格一致（深蓝背景、浅灰内容区、蓝色虚线边框） */
.content-review-upload :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
  border-radius: var(--radius-lg, 8px);
  border: 2px dashed rgba(59, 130, 246, 0.3);
  background-color: rgba(10, 22, 40, 0.6);
  transition: all 0.3s ease;
}

.content-review-upload :deep(.el-upload-dragger:hover) {
  border-color: rgba(59, 130, 246, 0.6);
  background-color: rgba(10, 22, 40, 0.8);
}

.content-review-upload :deep(.el-upload-dragger.is-dragover) {
  border-color: var(--military-primary);
  background-color: rgba(59, 130, 246, 0.1);
}

.content-review-upload .upload-icon {
  font-size: 48px;
  color: var(--military-primary);
  margin-bottom: 12px;
}

.content-review-upload .upload-text {
  margin-top: 8px;
  font-size: 14px;
  color: var(--military-text-secondary);
}

.content-review-upload .upload-text em {
  color: var(--military-primary);
  font-style: normal;
  font-weight: 600;
}

.content-review-upload .upload-tip {
  font-size: 12px;
  color: var(--military-text-muted);
  margin-top: 8px;
}

/* 审查结果区域：流式 Markdown 展示 */
.review-result-content {
  min-height: 120px;
  max-height: 70vh;
  overflow-y: auto;
  padding: 16px;
  background: rgba(10, 22, 40, 0.4);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: var(--military-text-primary);
  font-size: 14px;
  line-height: 1.7;
}

.review-result-content.markdown-body :deep(h2) {
  font-size: 16px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 20px 0 10px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  padding-bottom: 6px;
}

.review-result-content.markdown-body :deep(h3) {
  font-size: 14px;
  font-weight: 600;
  color: var(--military-primary);
  margin: 14px 0 8px;
}

.review-result-content.markdown-body :deep(p),
.review-result-content.markdown-body :deep(li) {
  margin: 6px 0;
  color: var(--military-text-secondary);
}

.review-result-content.markdown-body :deep(ul),
.review-result-content.markdown-body :deep(ol) {
  margin: 8px 0;
  padding-left: 1.5em;
}

.review-result-content.markdown-body :deep(strong) {
  color: var(--military-text-primary);
  font-weight: 600;
}

.review-streaming-tip {
  margin-top: 12px;
  font-size: 13px;
  color: var(--military-text-muted);
}
</style>
