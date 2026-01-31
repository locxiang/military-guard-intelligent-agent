<template>
  <div class="doc-generate-meeting-result-view bg-gov-background min-h-full">
    <div class="result-header">
      <div class="header-content">
        <div class="header-left">
          <button class="back-button" @click="handleBack">
            <el-icon><ArrowLeft /></el-icon>
            <span>返回</span>
          </button>
          <div class="header-title-section">
            <h1 class="page-title">
              <el-icon v-if="generating" class="is-loading"><Loading /></el-icon>
              {{ generating ? 'AI正在生成会议纪要...' : '会议纪要' }}
            </h1>
            <p class="page-subtitle">根据您的会议内容整理而成，请核对后使用</p>
          </div>
        </div>
        <div class="header-actions" v-if="!generating">
          <button class="action-button" @click="handleCopy">
            <el-icon><CopyDocument /></el-icon>
            <span>复制</span>
          </button>
          <button class="action-button primary" @click="handleDownload">
            <el-icon><Download /></el-icon>
            <span>导出文档</span>
          </button>
        </div>
      </div>
    </div>

    <div class="result-content-area">
      <div class="template-notice">
        <el-icon class="notice-icon"><Warning /></el-icon>
        <div class="notice-content">
          <strong>模板说明：</strong>当前为通用会议纪要格式，实际使用时请根据单位规定调整。生成内容仅供参考，请务必人工审核后使用。
        </div>
      </div>

      <div class="content-wrapper" ref="contentRef">
        <div class="document-content markdown-body" v-html="renderedContent"></div>
        <span v-if="generating" class="typing-cursor"></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Loading, CopyDocument, Download, Warning } from '@element-plus/icons-vue'
import { Document, Paragraph, TextRun, HeadingLevel, AlignmentType, Packer } from 'docx'
import { saveAs } from 'file-saver'
import { marked } from 'marked'

const router = useRouter()

const generating = ref(true)
const displayContent = ref('')
const contentRef = ref<HTMLElement>()

const renderedContent = computed(() => {
  if (!displayContent.value) return ''
  return marked(displayContent.value, { breaks: true, gfm: true })
})

function handleBack() {
  router.push('/doc-generate/meeting')
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(displayContent.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

async function handleDownload() {
  try {
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            text: '会议纪要',
            heading: HeadingLevel.TITLE,
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 }
          }),
          ...displayContent.value
            .split(/\n+/)
            .filter((line) => line.trim())
            .map((line) => {
              const t = line.trim()
              if (t.startsWith('### ')) {
                return new Paragraph({ text: t.slice(4), heading: HeadingLevel.HEADING_3, spacing: { before: 240, after: 120 } })
              }
              if (t.startsWith('## ')) {
                return new Paragraph({ text: t.slice(3), heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 120 } })
              }
              if (t.startsWith('# ')) {
                return new Paragraph({ text: t.slice(2), heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } })
              }
              return new Paragraph({ children: [new TextRun({ text: t, size: 22 })], spacing: { after: 120 } })
            })
        ]
      }]
    })
    const blob = await Packer.toBlob(doc)
    saveAs(blob, `会议纪要_${new Date().toISOString().slice(0, 10)}.docx`)
    ElMessage.success('DOCX 文档已下载')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}

onMounted(async () => {
  try {
    const meetingDataStr = sessionStorage.getItem('meetingData')
    if (!meetingDataStr) {
      ElMessage.warning('未找到会议数据，请返回重新填写')
      router.push('/doc-generate/meeting')
      return
    }

    const meetingData = JSON.parse(meetingDataStr)
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')

    const response = await fetch('/api/v1/doc-generate/meeting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        input_type: meetingData.input_type || 'text',
        meeting_notes: meetingData.meeting_notes,
        meeting_transcript: meetingData.meeting_transcript,
        meeting_title: meetingData.meeting_title,
        meeting_time: meetingData.meeting_time
      })
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error((err as any).detail || `请求失败 ${response.status}`)
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
        if (!line.startsWith('data: ')) continue
        try {
          const data = JSON.parse(line.slice(6))
          if (data.error) throw new Error(data.error)
          if (data.done) {
            generating.value = false
            ElMessage.success('会议纪要生成完成')
            return
          }
          if (data.content) {
            displayContent.value += data.content
            nextTick(() => {
              if (contentRef.value) contentRef.value.scrollTop = contentRef.value.scrollHeight
            })
          }
        } catch (e) {
          if (e instanceof Error && e.message !== 'Unexpected end of JSON input') console.error(e)
        }
      }
    }

    generating.value = false
    ElMessage.success('会议纪要生成完成')
  } catch (error: any) {
    console.error('生成失败:', error)
    ElMessage.error(error?.message || '生成失败，请重试')
    generating.value = false
    if (!sessionStorage.getItem('meetingData')) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => router.push('/doc-generate/meeting'), 2000)
    }
  }
})
</script>

<style scoped>
.doc-generate-meeting-result-view {
  font-family: var(--font-body);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.result-header {
  background: rgba(10, 22, 40, 0.9);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.back-button:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--military-text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.page-subtitle {
  font-size: 13px;
  color: var(--military-text-secondary);
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(10, 22, 40, 0.5);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.action-button:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.5);
}

.action-button.primary {
  background: var(--military-primary);
  border-color: var(--military-primary);
  color: #fff;
}

.result-content-area {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
}

.template-notice {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  margin-bottom: 24px;
}

.notice-icon {
  color: #f59e0b;
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.notice-content {
  font-size: 14px;
  color: var(--military-text-secondary);
  line-height: 1.6;
}

.notice-content strong {
  color: #f59e0b;
  font-weight: 600;
}

/* 内容区域 - 白底区域需强制深色文字，避免继承军事主题的白色 */
.content-wrapper {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  min-height: 600px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  color: #333 !important;
}

.content-wrapper :deep(.document-content),
.content-wrapper :deep(.document-content *) {
  color: inherit;
}

.document-content {
  color: #1a1a2e;
  font-family: SimSun, serif;
  line-height: 1.8;
}

.document-content.markdown-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
}

.document-content.markdown-body :deep(h1) {
  text-align: center;
  font-size: 28px;
  font-weight: bold;
  margin: 32px 0;
  letter-spacing: 8px;
  color: #1a1a2e;
  border-bottom: none;
  padding-bottom: 0;
}

.document-content.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a2e;
  margin: 24px 0 12px;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

.document-content.markdown-body :deep(h3) {
  font-size: 17px;
  font-weight: bold;
  color: #1a1a2e;
  margin: 20px 0 10px;
}

.document-content.markdown-body :deep(p) {
  text-indent: 2em;
  line-height: 2.2;
  margin: 12px 0;
  font-size: 15px;
  color: #333;
}

.document-content.markdown-body :deep(ul),
.document-content.markdown-body :deep(ol) {
  margin: 12px 0;
  padding-left: 2em;
}

.document-content.markdown-body :deep(li) {
  margin: 8px 0;
  line-height: 2;
  color: #333;
}

.document-content.markdown-body :deep(strong),
.document-content.markdown-body :deep(b) {
  font-weight: bold;
  color: #1a1a2e;
}

.document-content.markdown-body :deep(em),
.document-content.markdown-body :deep(i) {
  font-style: italic;
}

.document-content.markdown-body :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  font-style: italic;
}

.document-content.markdown-body :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #1a1a2e;
}

.document-content.markdown-body :deep(pre) {
  background: #f3f4f6;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.document-content.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}

.document-content.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 14px;
  color: #333;
}

.document-content.markdown-body :deep(table th),
.document-content.markdown-body :deep(table td) {
  border: 1px solid #333;
  padding: 8px;
  text-align: center;
  color: #1a1a2e;
}

.document-content.markdown-body :deep(table th) {
  background: #f0f0f0;
  font-weight: bold;
}

.typing-cursor {
  display: inline-block;
  width: 3px;
  height: 22px;
  background: var(--military-primary);
  margin-left: 2px;
  animation: blink 0.8s infinite;
  vertical-align: middle;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>
