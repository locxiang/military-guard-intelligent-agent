<template>
  <div class="doc-generate-report-result-view bg-gov-background min-h-full">
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
              {{ generating ? 'AI正在生成报告...' : 'AI生成结果' }}
            </h1>
            <p class="page-subtitle">{{ currentReportTypeLabel }}</p>
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
import { Document, Paragraph, TextRun, HeadingLevel, AlignmentType, Packer, Table, TableRow, TableCell, WidthType } from 'docx'
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

// 报告类型
const reportTypes: Record<string, string> = {
  work_summary: '工作总结',
  statistics_report: '统计分析报告',
  trend_analysis: '形势分析报告'
}

const currentReportTypeLabel = computed(() => {
  const reportType = route.query.reportType as string
  return reportTypes[reportType] || '报告'
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
  const reportData = JSON.parse(sessionStorage.getItem('reportData') || '{}')
  const reportType = route.query.reportType as string
  const formData = reportData.formData || {}
  const statistics = reportData.statistics || {}
  const periodLabel = reportData.reportPeriod === 'week' ? '本周' :
                      reportData.reportPeriod === 'month' ? '本月' :
                      reportData.reportPeriod === 'quarter' ? '本季度' :
                      reportData.reportPeriod === 'year' ? '本年度' : '自定义'
  const today = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  switch (reportType) {
    case 'work_summary':
      return generateWorkSummary(formData, statistics, periodLabel, today)
    case 'statistics_report':
      return generateStatisticsReport(formData, statistics, periodLabel, today)
    case 'trend_analysis':
      return generateTrendAnalysis(formData, statistics, periodLabel, today)
    default:
      return ''
  }
}

// 生成工作总结
const generateWorkSummary = (formData: any, statistics: any, periodLabel: string, today: string): string => {
  const title = formData.title || `${periodLabel}工作总结`
  return `<div class="report-document">
<h1 class="report-title">${title}</h1>

<div class="report-section">
<h2 class="section-title">一、工作概况</h2>
<p>${periodLabel}，我单位共受理各类案件 <strong>${statistics.totalCases || 0}</strong> 件，已办结 <strong>${statistics.completedCases || 0}</strong> 件，办结率达到 <strong>${statistics.completionRate || 0}%</strong>。</p>
<p>案件类型分布如下：</p>
<ul>
${(statistics.caseTypeDistribution || []).map((item: any) => `<li>${item.name}：${item.count}件，占比${item.percentage}%</li>`).join('')}
</ul>
</div>

<div class="report-section">
<h2 class="section-title">二、主要成效</h2>
${formData.highlights 
  ? formData.highlights.split('\n').map(p => `<p>${p}</p>`).join('')
  : `<p>1. 案件办理效率稳步提升，办结率保持在较高水平；</p>
     <p>2. 卷宗审核入库管理更加规范，档案质量持续改善；</p>
     <p>3. 信息化手段应用更加深入，工作效率明显提高。</p>`
}
</div>

<div class="report-section">
<h2 class="section-title">三、存在问题</h2>
${formData.problems
  ? formData.problems.split('\n').map(p => `<p>${p}</p>`).join('')
  : `<p>1. 部分案件办理周期较长，需要进一步优化流程；</p>
     <p>2. 个别类型案件有上升趋势，需要加强防范；</p>
     <p>3. 基层业务人员培训仍需加强。</p>`
}
</div>

<div class="report-section">
<h2 class="section-title">四、下步计划</h2>
${formData.plans
  ? formData.plans.split('\n').map(p => `<p>${p}</p>`).join('')
  : `<p>1. 进一步优化案件办理流程，提高工作效率；</p>
     <p>2. 加强重点类型案件的预防和打击力度；</p>
     <p>3. 组织开展业务培训，提升队伍专业能力。</p>`
}
</div>

<div class="report-footer">
<p>XX单位</p>
<p>${today}</p>
</div>
</div>`
}

// 生成统计分析报告
const generateStatisticsReport = (formData: any, statistics: any, periodLabel: string, today: string): string => {
  const title = formData.title || `${periodLabel}统计分析报告`
  return `<div class="report-document">
<h1 class="report-title">${title}</h1>

<div class="report-section">
<h2 class="section-title">一、总体情况</h2>
<p>${periodLabel}，共受理案件 <strong>${statistics.totalCases || 0}</strong> 件，其中：</p>
<ul>
<li>已办结：${statistics.completedCases || 0}件</li>
<li>待处理：${statistics.pendingCases || 0}件</li>
<li>办结率：${statistics.completionRate || 0}%</li>
</ul>
</div>

<div class="report-section">
<h2 class="section-title">二、案件类型分布</h2>
<table class="data-table">
<thead>
<tr>
<th>序号</th>
<th>案件类型</th>
<th>数量（件）</th>
<th>占比</th>
</tr>
</thead>
<tbody>
${(statistics.caseTypeDistribution || []).map((item: any, index: number) => `
<tr>
<td>${index + 1}</td>
<td>${item.name}</td>
<td>${item.count}</td>
<td>${item.percentage}%</td>
</tr>
`).join('')}
</tbody>
</table>
</div>

<div class="report-section">
<h2 class="section-title">三、数据分析</h2>
<p>从案件类型分布来看：</p>
<p>1. ${statistics.caseTypeDistribution?.[0]?.name || '盗窃类'}案件占比最高，达到${statistics.caseTypeDistribution?.[0]?.percentage || 0}%，是当前需要重点关注的类型；</p>
<p>2. 办结率为${statistics.completionRate || 0}%，${(statistics.completionRate || 0) >= 80 ? '保持在较高水平' : '有待进一步提高'}；</p>
<p>3. 待处理案件${statistics.pendingCases || 0}件，需要持续跟进。</p>
</div>

<div class="report-section">
<h2 class="section-title">四、工作建议</h2>
<p>1. 加强${statistics.caseTypeDistribution?.[0]?.name || '重点类型'}案件的预防和处置工作；</p>
<p>2. 优化案件办理流程，进一步提高办结率；</p>
<p>3. 加强数据分析应用，为决策提供依据。</p>
</div>

<div class="report-footer">
<p>XX单位</p>
<p>${today}</p>
</div>
</div>`
}

// 生成形势分析报告
const generateTrendAnalysis = (formData: any, statistics: any, periodLabel: string, today: string): string => {
  const title = formData.title || `${periodLabel}形势分析报告`
  return `<div class="report-document">
<h1 class="report-title">${title}</h1>

<div class="report-section">
<h2 class="section-title">一、基本态势</h2>
<p>${periodLabel}，共发生各类案件 <strong>${statistics.totalCases || 0}</strong> 件。从总体态势看，案件数量${(statistics.totalCases || 0) > 10 ? '保持在一定水平' : '相对平稳'}，需要持续关注。</p>
</div>

<div class="report-section">
<h2 class="section-title">二、主要特点</h2>
<p><strong>（一）从案件类型看</strong></p>
<p>${statistics.caseTypeDistribution?.[0]?.name || '盗窃类'}案件${statistics.caseTypeDistribution?.[0]?.count || 0}件，占比${statistics.caseTypeDistribution?.[0]?.percentage || 0}%，是最主要的案件类型。</p>

<p><strong>（二）从办理情况看</strong></p>
<p>已办结${statistics.completedCases || 0}件，办结率${statistics.completionRate || 0}%，${(statistics.completionRate || 0) >= 80 ? '办理效率较高' : '仍需进一步提升'}。</p>

<p><strong>（三）从发展趋势看</strong></p>
<p>需要持续关注${statistics.caseTypeDistribution?.[0]?.name || '重点类型'}案件的发展态势，防止出现上升趋势。</p>
</div>

<div class="report-section">
<h2 class="section-title">三、原因分析</h2>
${formData.problems
  ? formData.problems.split('\n').map(p => `<p>${p}</p>`).join('')
  : `<p>1. 部分人员法纪观念淡薄，需要加强教育引导；</p>
     <p>2. 日常管理存在薄弱环节，有待进一步完善；</p>
     <p>3. 监督检查力度有待加强。</p>`
}
</div>

<div class="report-section">
<h2 class="section-title">四、对策建议</h2>
${formData.plans
  ? formData.plans.split('\n').map(p => `<p>${p}</p>`).join('')
  : `<p>1. 加强法纪教育，提高人员守法意识；</p>
     <p>2. 完善管理制度，堵塞管理漏洞；</p>
     <p>3. 强化监督检查，确保制度落实；</p>
     <p>4. 做好风险防控，防止问题发生。</p>`
}
</div>

<div class="report-footer">
<p>XX单位</p>
<p>${today}</p>
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

// 解析 Markdown 内容为 DOCX 段落（支持表格）
const parseMarkdownToDocx = (markdown: string): (Paragraph | Table)[] => {
  // 先将 Markdown 转换为 HTML
  const html = marked(markdown, { breaks: true, gfm: true })
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const paragraphs: (Paragraph | Table)[] = []
  
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
    } else if (tagName === 'table') {
      // 处理表格
      const rows = element.querySelectorAll('tr')
      const tableRows: TableRow[] = []
      
      rows.forEach((row) => {
        const cells = row.querySelectorAll('th, td')
        const tableCells = Array.from(cells).map((cell) => {
          return new TableCell({
            children: [
              new Paragraph({
                text: cell.textContent?.trim() || '',
                alignment: AlignmentType.CENTER
              })
            ]
          })
        })
        
        tableRows.push(new TableRow({ children: tableCells }))
      })
      
      if (tableRows.length > 0) {
        paragraphs.push(
          new Table({
            rows: tableRows,
            width: { size: 100, type: WidthType.PERCENTAGE }
          })
        )
      }
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
    const reportData = JSON.parse(sessionStorage.getItem('reportData') || '{}')
    const formData = reportData.formData || {}
    const reportTypeLabel = currentReportTypeLabel.value
    const fileName = `${formData.title || reportTypeLabel}_${Date.now()}.docx`
    
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
    // 获取报告数据
    const reportData = JSON.parse(sessionStorage.getItem('reportData') || '{}')
    const reportType = route.query.reportType as string
    
    // 报告类型映射
    const reportTypeMap: Record<string, string> = {
      work_summary: '工作总结',
      statistics_report: '统计分析报告',
      trend_analysis: '形势分析报告'
    }
    
    // 获取 token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    
    // 使用 SSE 流式接收数据
    const response = await fetch('/api/v1/doc-generate/report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        report_type: reportTypeMap[reportType] || reportType,
        form_data: reportData.formData || {},
        statistics: reportData.statistics || {},
        report_period: reportData.reportPeriod
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
              ElMessage.success('报告生成完成')
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
    ElMessage.success('报告生成完成')
  } catch (error: any) {
    console.error('生成失败:', error)
    const errorMessage = error?.message || '生成失败，请重试'
    ElMessage.error(errorMessage)
    generating.value = false
    // 如果 sessionStorage 中没有数据，可能是页面刷新导致的
    if (!sessionStorage.getItem('reportData')) {
      ElMessage.warning('页面数据已丢失，请返回重新填写')
      setTimeout(() => {
        router.push('/doc-generate/report')
      }, 2000)
    }
  }
})
</script>

<style scoped>
.doc-generate-report-result-view {
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

.document-content.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 14px;
}

.document-content.markdown-body :deep(table th),
.document-content.markdown-body :deep(table td) {
  border: 1px solid #333;
  padding: 8px;
  text-align: center;
}

.document-content.markdown-body :deep(table th) {
  background: #f0f0f0;
  font-weight: bold;
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
