<template>
  <div class="doc-generate-story-result-view bg-gov-background min-h-full">
    <!-- 页面头部 -->
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
              {{ generating ? 'AI 正在生成警示小故事...' : 'AI 生成结果' }}
            </h1>
            <p class="page-subtitle">{{ currentStoryTypeLabel }}</p>
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

    <!-- 页面内容 -->
    <div class="result-content-area">
      <!-- 模板提示 -->
      <div class="template-notice">
        <el-icon class="notice-icon"><Warning /></el-icon>
        <div class="notice-content">
          <strong>使用说明：</strong>生成内容仅供参考，用于警示宣传教育。请根据实际需要修改后使用。
        </div>
      </div>

      <!-- 生成内容区域 -->
      <div class="content-wrapper" ref="contentRef">
        <div class="document-content markdown-body" v-html="renderedContent"></div>
        <span v-if="generating" class="typing-cursor"></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Loading, CopyDocument, Download, Warning } from '@element-plus/icons-vue'
import { Document, Paragraph, TextRun, HeadingLevel, AlignmentType, Packer } from 'docx'
import { saveAs } from 'file-saver'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

// 生成状态
const generating = ref(true)
const displayContent = ref('')
const contentRef = ref<HTMLElement>()

// 渲染后的 Markdown 内容
const renderedContent = computed(() => {
  if (!displayContent.value) return ''
  return marked(displayContent.value, {
    breaks: true,
    gfm: true
  })
})

// 当前故事类型标签
const currentStoryTypeLabel = computed(() => {
  const storyData = JSON.parse(sessionStorage.getItem('storyData') || '{}')
  return storyData.story_type || '警示小故事'
})

// 返回
const handleBack = () => {
  router.back()
}

// 复制内容
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(displayContent.value)
    ElMessage.success('内容已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 解析 Markdown 为 DOCX 段落
const parseMarkdownToDocx = (markdown: string) => {
  const html = marked(markdown, { breaks: true, gfm: true })
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const paragraphs: Paragraph[] = []
  const body = doc.body

  if (!body) return paragraphs

  Array.from(body.children).forEach((element) => {
    const tagName = element.tagName.toLowerCase()
    const text = element.textContent?.trim() || ''

    if (tagName === 'h1') {
      paragraphs.push(
        new Paragraph({
          text,
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 }
        })
      )
    } else if (tagName === 'h2') {
      paragraphs.push(
        new Paragraph({
          text,
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 }
        })
      )
    } else if (tagName === 'h3') {
      paragraphs.push(
        new Paragraph({
          text,
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 150 }
        })
      )
    } else if (tagName === 'p') {
      if (text) {
        paragraphs.push(
          new Paragraph({
            children: [new TextRun({ text })],
            indent: { firstLine: 720 },
            spacing: { after: 200 }
          })
        )
      }
    } else if (tagName === 'ul' || tagName === 'ol') {
      element.querySelectorAll('li').forEach((li) => {
        const liText = li.textContent?.trim() || ''
        if (liText) {
          paragraphs.push(
            new Paragraph({
              text: liText,
              indent: { left: 720 },
              spacing: { after: 150 }
            })
          )
        }
      })
    }
  })

  return paragraphs
}

// 下载文档
const handleDownload = async () => {
  if (!displayContent.value) return

  try {
    const storyData = JSON.parse(sessionStorage.getItem('storyData') || '{}')
    const storyType = storyData.story_type || '警示小故事'
    const fileName = `警示小故事_${storyType}_${Date.now()}.docx`

    const docParagraphs = parseMarkdownToDocx(displayContent.value)

    const doc = new Document({
      sections: [
        {
          properties: {
            page: {
              margin: {
                top: 1440,
                right: 1440,
                bottom: 1440,
                left: 1440
              }
            }
          },
          children: docParagraphs
        }
      ],
      styles: {
        default: {
          document: {
            run: {
              font: 'SimSun',
              size: 24,
              color: '000000'
            },
            paragraph: {
              spacing: { line: 360, lineRule: 'auto' }
            }
          }
        }
      }
    })

    const blob = await Packer.toBlob(doc)
    saveAs(blob, fileName)

    ElMessage.success('DOCX 文档已下载')
  } catch (error) {
    console.error('导出 DOCX 失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}

onMounted(async () => {
  try {
    const storyData = JSON.parse(sessionStorage.getItem('storyData') || '{}')

    if (!storyData.story_type) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => router.push('/doc-generate/story'), 2000)
      generating.value = false
      return
    }

    const token = localStorage.getItem('token') || sessionStorage.getItem('token')

    const response = await fetch('/api/v1/doc-generate/story', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        story_type: storyData.story_type,
        keywords: storyData.keywords || '',
        scene_hint: storyData.scene_hint || ''
      })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error((errorData as { detail?: string })?.detail || `HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

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

            if (data.error) {
              throw new Error(data.error)
            }

            if (data.done) {
              generating.value = false
              ElMessage.success('警示小故事生成完成')
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
            if ((e as Error).message && (e as Error).message !== 'Unexpected end of JSON input') {
              throw e
            }
          }
        }
      }
    }

    generating.value = false
    ElMessage.success('警示小故事生成完成')
  } catch (error: unknown) {
    const err = error as Error
    console.error('生成失败:', err)
    ElMessage.error(err?.message || '生成失败，请重试')
    generating.value = false

    if (!sessionStorage.getItem('storyData')) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => router.push('/doc-generate/story'), 2000)
    }
  }
})
</script>

<style scoped>
.doc-generate-story-result-view {
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

.action-button.primary:hover {
  background: rgba(59, 130, 246, 0.8);
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
  color: #1a1a2e;
}

.document-content.markdown-body :deep(h2) {
  font-size: 20px;
  font-weight: bold;
  color: #1a1a2e;
  margin: 24px 0 12px;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

.document-content.markdown-body :deep(p) {
  text-indent: 2em;
  line-height: 2.2;
  margin: 12px 0;
  font-size: 15px;
  color: #333;
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
