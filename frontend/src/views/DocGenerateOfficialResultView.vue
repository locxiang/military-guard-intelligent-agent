<template>
  <div class="doc-generate-official-result-view bg-gov-background min-h-full">
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
              {{ generating ? 'AI正在生成公文...' : 'AI生成结果' }}
            </h1>
            <p class="page-subtitle">{{ currentDocTypeLabel }}</p>
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
          <strong>模板说明：</strong>当前使用的是通用模板格式，实际使用时请根据单位规定的模板进行调整。
          生成的内容仅供参考，请务必人工审核后使用。
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
  // 使用 marked 将 Markdown 转换为 HTML
  return marked(displayContent.value, {
    breaks: true, // 支持换行
    gfm: true // 支持 GitHub Flavored Markdown
  })
})

// 文档类型
const documentTypes: Record<string, string> = {
  request: '请示',
  report: '汇报',
  notice: '通知',
  memo: '函'
}

const currentDocTypeLabel = computed(() => {
  const docType = route.query.docType as string
  return documentTypes[docType] || '公文'
})

// 流式输出效果
const streamOutput = async (content: string) => {
  const chars = content.split('')
  let index = 0
  
  return new Promise<void>((resolve) => {
    const timer = setInterval(() => {
      if (index < chars.length) {
        displayContent.value += chars[index]
        index++
        
        // 自动滚动到底部
        nextTick(() => {
          if (contentRef.value) {
            contentRef.value.scrollTop = contentRef.value.scrollHeight
          }
        })
      } else {
        clearInterval(timer)
        generating.value = false
        resolve()
      }
    }, 12)
  })
}

// 生成文档内容
const generateDocumentContent = (): string => {
  const officialData = JSON.parse(sessionStorage.getItem('officialData') || '{}')
  const docType = route.query.docType as string
  const formData = officialData.formData || {}
  const today = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  switch (docType) {
    case 'request':
      return generateRequest(formData, today)
    case 'report':
      return generateReport(formData, today)
    case 'notice':
      return generateNotice(formData, today)
    case 'memo':
      return generateMemo(formData, today)
    default:
      return ''
  }
}

// 生成请示
const generateRequest = (formData: any, today: string): string => {
  return `<div class="official-document">
<div class="doc-header">
<div class="doc-number">〔2026〕XX号</div>
</div>
<h1 class="doc-title">${formData.subject || '请示'}</h1>
<div class="doc-recipient">${formData.recipient || ''}：</div>
<div class="doc-body">
${(formData.content || '').split('\n').map(p => `<p>${p}</p>`).join('')}
<p>妥否，请批示。</p>
${formData.attachment ? `<p>附件：${formData.attachment}</p>` : ''}
</div>
<div class="doc-footer">
<div class="doc-sender">XX单位</div>
<div class="doc-date">${today}</div>
</div>
</div>`
}

// 生成汇报
const generateReport = (formData: any, today: string): string => {
  return `<div class="official-document">
<div class="doc-header">
<div class="doc-number">〔2026〕XX号</div>
</div>
<h1 class="doc-title">${formData.subject || '汇报'}</h1>
<div class="doc-recipient">${formData.recipient || ''}：</div>
<div class="doc-body">
<p class="section-title">一、基本情况</p>
${(formData.situation || '').split('\n').map(p => `<p>${p}</p>`).join('')}

${formData.problems ? `
<p class="section-title">二、存在问题</p>
${formData.problems.split('\n').map(p => `<p>${p}</p>`).join('')}
` : ''}

${formData.plan ? `
<p class="section-title">三、下步计划</p>
${formData.plan.split('\n').map(p => `<p>${p}</p>`).join('')}
` : ''}

<p>特此汇报。</p>
</div>
<div class="doc-footer">
<div class="doc-sender">XX单位</div>
<div class="doc-date">${today}</div>
</div>
</div>`
}

// 生成通知
const generateNotice = (formData: any, today: string): string => {
  return `<div class="official-document">
<div class="doc-header">
<div class="doc-number">〔2026〕XX号</div>
</div>
<h1 class="doc-title">${formData.subject || '通知'}</h1>
<div class="doc-recipient">${formData.recipient || ''}：</div>
<div class="doc-body">
${(formData.content || '').split('\n').map(p => `<p>${p}</p>`).join('')}

${formData.requirements ? `
<p class="section-title">具体要求：</p>
${formData.requirements.split('\n').map(p => `<p>${p}</p>`).join('')}
` : ''}

<p>特此通知。</p>
</div>
<div class="doc-footer">
<div class="doc-sender">XX单位</div>
<div class="doc-date">${today}</div>
</div>
</div>`
}

// 生成函
const generateMemo = (formData: any, today: string): string => {
  return `<div class="official-document">
<div class="doc-header">
<div class="doc-number">〔2026〕XX号</div>
</div>
<h1 class="doc-title">${formData.subject || '函'}</h1>
<div class="doc-recipient">${formData.recipient || ''}：</div>
<div class="doc-body">
${(formData.content || '').split('\n').map(p => `<p>${p}</p>`).join('')}
<p>请予以协助，函复为盼。</p>
</div>
<div class="doc-footer">
<div class="doc-sender">XX单位</div>
<div class="doc-date">${today}</div>
</div>
</div>`
}

// 返回
const handleBack = () => {
  router.back()
}

// 复制内容
const handleCopy = async () => {
  try {
    // 复制原始 Markdown 内容
    await navigator.clipboard.writeText(displayContent.value)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 解析 Markdown 内容为 DOCX 段落
const parseMarkdownToDocx = (markdown: string): Paragraph[] => {
  // 先将 Markdown 转换为 HTML
  const html = marked(markdown, { breaks: true, gfm: true })
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const paragraphs: Paragraph[] = []
  
  // 获取 body 中的所有元素
  const body = doc.body
  if (!body) {
    return paragraphs
  }
  
  // 遍历所有子元素
  Array.from(body.children).forEach((element) => {
    const tagName = element.tagName.toLowerCase()
    
    if (tagName === 'h1') {
      // 一级标题（文档标题）
      paragraphs.push(
        new Paragraph({
          text: element.textContent?.trim() || '',
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 }
        })
      )
    } else if (tagName === 'h2') {
      // 二级标题（章节标题）
      paragraphs.push(
        new Paragraph({
          text: element.textContent?.trim() || '',
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 }
        })
      )
    } else if (tagName === 'h3') {
      // 三级标题
      paragraphs.push(
        new Paragraph({
          text: element.textContent?.trim() || '',
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 150 }
        })
      )
    } else if (tagName === 'p') {
      // 段落
      const pText = element.textContent || ''
      
      if (pText.trim()) {
        // 处理包含格式的文本（如加粗、斜体）
        const textRuns: TextRun[] = []
        const strongElements = element.querySelectorAll('strong, b')
        const emElements = element.querySelectorAll('em, i')
        
        if (strongElements.length > 0 || emElements.length > 0) {
          // 有格式文本，需要分段处理
          let lastIndex = 0
          const fullText = element.textContent || ''
          const formatMap = new Map<number, { bold?: boolean; italic?: boolean }>()
          
          // 标记加粗位置
          strongElements.forEach((strong) => {
            const strongText = strong.textContent || ''
            const strongIndex = fullText.indexOf(strongText, lastIndex)
            for (let i = strongIndex; i < strongIndex + strongText.length; i++) {
              formatMap.set(i, { ...formatMap.get(i), bold: true })
            }
          })
          
          // 标记斜体位置
          emElements.forEach((em) => {
            const emText = em.textContent || ''
            const emIndex = fullText.indexOf(emText, lastIndex)
            for (let i = emIndex; i < emIndex + emText.length; i++) {
              formatMap.set(i, { ...formatMap.get(i), italic: true })
            }
          })
          
          // 分段处理文本
          let currentFormat: { bold?: boolean; italic?: boolean } | null = null
          let currentText = ''
          
          for (let i = 0; i < fullText.length; i++) {
            const format = formatMap.get(i) || {}
            const formatKey = JSON.stringify(format)
            const currentFormatKey = JSON.stringify(currentFormat)
            
            if (formatKey !== currentFormatKey) {
              // 格式变化，保存当前文本段
              if (currentText && currentFormat) {
                textRuns.push(
                  new TextRun({
                    text: currentText,
                    bold: currentFormat.bold,
                    italics: currentFormat.italic
                  })
                )
              }
              currentText = fullText[i]
              currentFormat = format
            } else {
              currentText += fullText[i]
            }
          }
          
          // 添加最后一段
          if (currentText && currentFormat) {
            textRuns.push(
              new TextRun({
                text: currentText,
                bold: currentFormat.bold,
                italics: currentFormat.italic
              })
            )
          }
        } else {
          // 普通文本
          textRuns.push(new TextRun({ text: pText.trim() }))
        }
        
        paragraphs.push(
          new Paragraph({
            children: textRuns,
            indent: { firstLine: 720 },
            spacing: { after: 200 }
          })
        )
      }
    } else if (tagName === 'ul' || tagName === 'ol') {
      // 列表
      const listItems = element.querySelectorAll('li')
      listItems.forEach((li) => {
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
    } else if (tagName === 'blockquote') {
      // 引用块
      const quoteText = element.textContent?.trim() || ''
      if (quoteText) {
        paragraphs.push(
          new Paragraph({
            text: quoteText,
            indent: { left: 720 },
            spacing: { before: 200, after: 200 }
          })
        )
      }
    }
  })
  
  return paragraphs
}

// 下载文档
const handleDownload = async () => {
  if (!displayContent.value) return
  
  try {
    const officialData = JSON.parse(sessionStorage.getItem('officialData') || '{}')
    const formData = officialData.formData || {}
    const docTypeLabel = currentDocTypeLabel.value
    const fileName = `${formData.subject || docTypeLabel}_${Date.now()}.docx`
    
    // 解析 Markdown 内容为 DOCX 段落
    const paragraphs = parseMarkdownToDocx(displayContent.value)
    
    // 创建 DOCX 文档
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
          children: paragraphs
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
              spacing: {
                line: 360,
                lineRule: 'auto'
              }
            }
          }
        }
      }
    })
    
    // 生成并下载 DOCX 文件
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
    // 获取公文数据
    const officialData = JSON.parse(sessionStorage.getItem('officialData') || '{}')
    const docType = route.query.docType as string
    
    // 文档类型映射
    const docTypeMap: Record<string, string> = {
      request: '请示',
      report: '汇报',
      notice: '通知',
      memo: '函'
    }
    
    // 获取 token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    
    // 使用 SSE 流式接收数据
    const response = await fetch('/api/v1/doc-generate/official', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        doc_type: docTypeMap[docType] || docType,
        form_data: officialData.formData || {},
        selected_case: officialData.selectedCase
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    // 读取 SSE 流
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (!reader) {
      throw new Error('无法读取响应流')
    }
    
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      // 解码数据
      buffer += decoder.decode(value, { stream: true })
      
      // 处理完整的 SSE 消息
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留不完整的行
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.error) {
              throw new Error(data.error)
            }
            
            if (data.done) {
              generating.value = false
              ElMessage.success('公文生成完成')
              return
            }
            
            if (data.content) {
              // 实时追加内容
              displayContent.value += data.content
              
              // 自动滚动到底部
              nextTick(() => {
                if (contentRef.value) {
                  contentRef.value.scrollTop = contentRef.value.scrollHeight
                }
              })
            }
          } catch (e) {
            console.error('解析 SSE 数据失败:', e)
          }
        }
      }
    }
    
    generating.value = false
    ElMessage.success('公文生成完成')
  } catch (error: any) {
    console.error('生成失败:', error)
    const errorMessage = error?.message || '生成失败，请重试'
    ElMessage.error(errorMessage)
    generating.value = false
    // 如果 sessionStorage 中没有数据，可能是页面刷新导致的
    if (!sessionStorage.getItem('officialData')) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => {
        router.push('/doc-generate/official')
      }, 2000)
    }
  }
})
</script>

<style scoped>
.doc-generate-official-result-view {
  font-family: var(--font-body);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 页面头部 */
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

/* 页面内容区域 */
.result-content-area {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
}

/* 模板提示 */
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

/* 内容区域 */
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

/* Markdown 样式 */
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

/* 打字机光标 */
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
