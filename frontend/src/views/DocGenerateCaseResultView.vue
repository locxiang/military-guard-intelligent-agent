<template>
  <div class="doc-generate-result-view bg-gov-background min-h-full">
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
              {{ generating ? 'AI正在生成文书...' : 'AI生成结果' }}
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
import { ref, computed, onMounted, nextTick, watch } from 'vue'
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
  case_report: '立案报告',
  investigation_report: '调查报告',
  interrogation_outline: '讯问笔录提纲',
  case_summary: '案件处理意见'
}

const currentDocTypeLabel = computed(() => {
  const docType = route.query.docType as string
  return documentTypes[docType] || '文书'
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
    }, 12) // 每12ms输出一个字符
  })
}

// 生成文档内容
const generateDocumentContent = (): string => {
  const caseInfo = JSON.parse(sessionStorage.getItem('caseInfo') || '{}')
  const docType = route.query.docType as string
  
  const personDesc = [
    caseInfo.gender,
    caseInfo.position,
    caseInfo.enlistmentTime ? `${caseInfo.enlistmentTime}入伍` : ''
  ].filter(Boolean).join('，')

  switch (docType) {
    case 'case_report':
      return generateCaseReport(personDesc, caseInfo)
    case 'investigation_report':
      return generateInvestigationReport(personDesc, caseInfo)
    case 'interrogation_outline':
      return generateInterrogationOutline(personDesc, caseInfo)
    case 'case_summary':
      return generateCaseSummary(personDesc, caseInfo)
    default:
      return ''
  }
}

// 生成立案报告
const generateCaseReport = (personDesc: string, caseInfo: any): string => {
  return `<div class="document-content">
<h1 class="doc-title">立 案 报 告</h1>

<div class="doc-section">
<h2 class="section-title">一、案件基本情况</h2>
<p><strong>案发时间：</strong>${caseInfo.incidentTime || '待补充'}</p>
<p><strong>案件类型：</strong>${caseInfo.caseType || '待补充'}</p>
<p><strong>来源部门：</strong>${caseInfo.department || '待补充'}</p>
</div>

<div class="doc-section">
<h2 class="section-title">二、涉案人员情况</h2>
<p><strong>当事人：</strong>${caseInfo.personName}</p>
<p><strong>基本情况：</strong>${personDesc || '待补充'}</p>
</div>

<div class="doc-section">
<h2 class="section-title">三、事发经过</h2>
<p>${caseInfo.incidentProcess}</p>
</div>

<div class="doc-section">
<h2 class="section-title">四、立案依据</h2>
<p>根据相关规定，${caseInfo.personName}的上述行为涉嫌${caseInfo.caseType || '违纪违法'}，符合立案条件，现依法立案侦查。</p>
${caseInfo.investigation ? `<p><strong>初步调查情况：</strong>${caseInfo.investigation}</p>` : ''}
</div>

<div class="doc-section">
<h2 class="section-title">五、承办意见</h2>
<p>建议依法立案侦查，查清案件事实，依规依纪处理。</p>
</div>

<div class="doc-footer">
<p>承办人：______________</p>
<p>审批人：______________</p>
<p>日  期：______________</p>
</div>
</div>`
}

// 生成调查报告
const generateInvestigationReport = (personDesc: string, caseInfo: any): string => {
  return `<div class="document-content">
<h1 class="doc-title">调 查 报 告</h1>

<div class="doc-section">
<h2 class="section-title">一、案件概述</h2>
<p><strong>案发时间：</strong>${caseInfo.incidentTime || '待补充'}</p>
<p><strong>案件类型：</strong>${caseInfo.caseType || '待补充'}</p>
<p><strong>当事人：</strong>${caseInfo.personName}（${personDesc || '基本情况待补充'}）</p>
</div>

<div class="doc-section">
<h2 class="section-title">二、事发经过</h2>
<p>${caseInfo.incidentProcess}</p>
</div>

<div class="doc-section">
<h2 class="section-title">三、调查过程及结论</h2>
${caseInfo.investigation ? `<p>${caseInfo.investigation}</p>` : '<p>经调查核实，现将调查过程及结论报告如下：</p><p>1. 调查方式：通过询问当事人、调取相关证据、走访知情人等方式进行调查；</p><p>2. 调查结论：经查，' + caseInfo.personName + '的行为事实清楚，证据确凿。</p>'}
</div>

<div class="doc-section">
<h2 class="section-title">四、原因分析及教训</h2>
<p>该案反映出以下问题：</p>
<p>1. 当事人法纪观念淡薄，需要加强教育引导；</p>
<p>2. 日常管理存在薄弱环节，有待进一步完善；</p>
<p>3. 建议举一反三，加强类似问题的防范。</p>
</div>

<div class="doc-section">
<h2 class="section-title">五、处理建议</h2>
<p>根据案件事实和相关规定，建议对${caseInfo.personName}作出相应处理。</p>
</div>

<div class="doc-footer">
<p>调查人员：______________</p>
<p>审核人员：______________</p>
<p>报告日期：______________</p>
</div>
</div>`
}

// 生成讯问笔录提纲
const generateInterrogationOutline = (personDesc: string, caseInfo: any): string => {
  return `<div class="document-content">
<h1 class="doc-title">讯问笔录提纲</h1>

<div class="doc-section">
<h2 class="section-title">一、被讯问人基本情况核实</h2>
<p>1. 请说明你的姓名、性别、民族、籍贯、出生年月、入伍时间、现任职务等基本情况。</p>
<p class="note">（核实信息：${caseInfo.personName}，${personDesc || '详细情况待核实'}）</p>
</div>

<div class="doc-section">
<h2 class="section-title">二、事件经过询问</h2>
<p>2. ${caseInfo.incidentTime ? `${caseInfo.incidentTime}` : '案发当天'}发生了什么事情？请你详细说明。</p>
<p>3. 事发时你在什么地方？在做什么？</p>
<p>4. 事发时还有哪些人在场？他们分别是谁？</p>
<p>5. 请从头到尾详细描述事情的起因、经过和结果。</p>
<p class="note">（参考：${caseInfo.incidentProcess ? caseInfo.incidentProcess.substring(0, 100) + '...' : '待核实'}）</p>
</div>

<div class="doc-section">
<h2 class="section-title">三、动机和目的</h2>
<p>6. 你为什么要这样做？当时是怎么想的？</p>
<p>7. 事前有没有预谋？如果有，是怎样计划的？</p>
<p>8. 有没有其他人参与或事先知情？</p>
</div>

<div class="doc-section">
<h2 class="section-title">四、证据和物证</h2>
<p>9. 有没有相关的物证可以证明你说的情况？</p>
<p>10. 有没有其他证人可以证明？</p>
<p>11. 事后有没有采取什么补救措施？</p>
</div>

<div class="doc-section">
<h2 class="section-title">五、认识和态度</h2>
<p>12. 你现在如何看待自己的行为？</p>
<p>13. 你认为自己的行为造成了什么后果？</p>
<p>14. 有什么想说的或者需要补充的？</p>
</div>

<div class="doc-footer">
<p>提纲拟定人：______________</p>
<p>拟定日期：______________</p>
</div>
</div>`
}

// 生成案件处理意见
const generateCaseSummary = (personDesc: string, caseInfo: any): string => {
  return `<div class="document-content">
<h1 class="doc-title">案件处理意见书</h1>

<div class="doc-section">
<h2 class="section-title">一、案件基本情况</h2>
<p><strong>案发时间：</strong>${caseInfo.incidentTime || '待补充'}</p>
<p><strong>当事人：</strong>${caseInfo.personName}</p>
<p><strong>基本情况：</strong>${personDesc || '详情见案卷'}</p>
<p><strong>涉案性质：</strong>${caseInfo.caseType || '待定'}</p>
<p><strong>所属单位：</strong>${caseInfo.department || '待补充'}</p>
</div>

<div class="doc-section">
<h2 class="section-title">二、事实认定</h2>
<p><strong>事发经过：</strong>${caseInfo.incidentProcess}</p>
${caseInfo.investigation ? `<p><strong>调查情况：</strong>${caseInfo.investigation}</p>` : ''}
</div>

<div class="doc-section">
<h2 class="section-title">三、处理依据</h2>
<p>根据相关法律法规和规章制度，${caseInfo.personName}的行为违反了相关规定，应当依法依规进行处理。</p>
</div>

<div class="doc-section">
<h2 class="section-title">四、处理意见</h2>
<p>综合考虑案件事实、情节轻重、认错态度等因素，提出以下处理意见：</p>
<p>1. 对${caseInfo.personName}的行为性质进行认定；</p>
<p>2. 根据相关规定提出处分建议；</p>
<p>3. 责令当事人作出深刻检查。</p>
</div>

<div class="doc-section">
<h2 class="section-title">五、整改建议</h2>
<p>针对本案暴露出的问题，建议采取以下措施：</p>
<p>1. 加强法纪教育，提高人员守法意识；</p>
<p>2. 完善管理制度，堵塞管理漏洞；</p>
<p>3. 举一反三，防止类似问题再次发生。</p>
</div>

<div class="doc-footer">
<p>承办人意见：______________</p>
<p>承办日期：______________</p>
<p>审批人意见：______________</p>
<p>审批日期：______________</p>
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
    
    if (tagName === 'h1' && element.classList.contains('doc-title')) {
      // 文档标题
      paragraphs.push(
        new Paragraph({
          text: element.textContent?.trim() || '',
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 }
        })
      )
    } else if (tagName === 'h2' && element.classList.contains('section-title')) {
      // 章节标题
      paragraphs.push(
        new Paragraph({
          text: element.textContent?.trim() || '',
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 }
        })
      )
    } else if (tagName === 'div' && element.classList.contains('doc-section')) {
      // 段落容器
      const isFooter = element.classList.contains('doc-footer')
      const sectionParagraphs = element.querySelectorAll('p')
      
      sectionParagraphs.forEach((p) => {
        const pText = p.textContent || ''
        const isNote = p.classList.contains('note')
        
        if (pText.trim()) {
          // 处理包含格式的文本（如加粗）
          const textRuns: TextRun[] = []
          const strongElements = p.querySelectorAll('strong')
          
          if (strongElements.length > 0) {
            // 有加粗文本，需要分段处理
            let lastIndex = 0
            const fullText = p.textContent || ''
            
            strongElements.forEach((strong) => {
              const strongText = strong.textContent || ''
              const strongIndex = fullText.indexOf(strongText, lastIndex)
              
              // 添加加粗前的文本
              if (strongIndex > lastIndex) {
                const beforeText = fullText.substring(lastIndex, strongIndex)
                if (beforeText.trim()) {
                  textRuns.push(
                    new TextRun({
                      text: beforeText,
                      italics: isNote,
                      size: isNote ? 20 : 24,
                      color: isNote ? '666666' : '000000'
                    })
                  )
                }
              }
              
              // 添加加粗文本
              textRuns.push(
                new TextRun({
                  text: strongText,
                  bold: true,
                  italics: isNote,
                  size: isNote ? 20 : 24,
                  color: isNote ? '666666' : '000000'
                })
              )
              
              lastIndex = strongIndex + strongText.length
            })
            
            // 添加剩余文本
            if (lastIndex < fullText.length) {
              const afterText = fullText.substring(lastIndex)
              if (afterText.trim()) {
                textRuns.push(
                  new TextRun({
                    text: afterText,
                    italics: isNote,
                    size: isNote ? 20 : 24,
                    color: isNote ? '666666' : '000000'
                  })
                )
              }
            }
          } else {
            // 普通文本
            textRuns.push(
              new TextRun({
                text: pText.trim(),
                italics: isNote,
                size: isNote ? 20 : 24,
                color: isNote ? '666666' : '000000'
              })
            )
          }
          
          paragraphs.push(
            new Paragraph({
              children: textRuns,
              indent: { firstLine: isFooter ? 0 : 720 },
              alignment: isFooter ? AlignmentType.RIGHT : AlignmentType.LEFT,
              spacing: { after: 200 }
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
    const caseInfo = JSON.parse(sessionStorage.getItem('caseInfo') || '{}')
    const docTypeLabel = currentDocTypeLabel.value
    const fileName = `${caseInfo.personName || '案件'}_${docTypeLabel}_${Date.now()}.docx`
    
    // 解析 Markdown 内容为 DOCX 段落
    const paragraphs = parseMarkdownToDocx(displayContent.value)
    
    // 创建 DOCX 文档
    const doc = new Document({
      sections: [
        {
          properties: {
            page: {
              margin: {
                top: 1440,    // 2.54cm (1 inch)
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
              size: 24, // 12pt
              color: '000000'
            },
            paragraph: {
              spacing: {
                line: 360, // 1.5倍行距
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
    // 获取案件信息
    const caseInfo = JSON.parse(sessionStorage.getItem('caseInfo') || '{}')
    const docType = route.query.docType as string
    
    // 文档类型映射
    const docTypeMap: Record<string, string> = {
      case_report: '立案报告',
      investigation_report: '调查报告',
      interrogation_outline: '讯问笔录提纲',
      case_summary: '案件处理意见'
    }
    
    // 获取关联案件
    const relatedCases = JSON.parse(sessionStorage.getItem('relatedCases') || '[]')
    
    // 获取 token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    
    // 使用 SSE 流式接收数据
    const response = await fetch('/api/v1/doc-generate/case', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        doc_type: docTypeMap[docType] || docType,
        case_info: caseInfo,
        related_cases: relatedCases
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
              ElMessage.success('文书生成完成')
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
    ElMessage.success('文书生成完成')
  } catch (error: any) {
    console.error('生成失败:', error)
    const errorMessage = error?.message || '生成失败，请重试'
    ElMessage.error(errorMessage)
    generating.value = false
    // 如果 sessionStorage 中没有数据，可能是页面刷新导致的
    if (!sessionStorage.getItem('caseInfo')) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => {
        router.push('/doc-generate/case')
      }, 2000)
    }
  }
})
</script>

<style scoped>
.doc-generate-result-view {
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
