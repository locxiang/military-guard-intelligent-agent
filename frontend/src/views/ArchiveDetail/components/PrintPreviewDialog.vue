<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="打印预览"
    width="90%"
    class="print-preview-dialog"
    :close-on-click-modal="false"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <el-icon><DocumentCopy /></el-icon>
          <span>打印预览 - {{ caseFile.caseNo || '案卷详情' }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="print-preview-btn secondary" @click="$emit('update:modelValue', false)">
            <el-icon><CircleClose /></el-icon>
            <span>取消</span>
          </button>
          <button class="print-preview-btn primary" @click="doPrint">
            <el-icon><DocumentCopy /></el-icon>
            <span>打印</span>
          </button>
        </div>
      </div>
    </template>
    <div class="print-preview-content">
      <div class="print-document" id="print-content">
        <!-- 页眉 -->
        <div class="print-header">
          <div class="print-header-left">{{ caseFile.sourceDepartment || '保卫处' }}</div>
          <div class="print-header-center">案卷详情</div>
          <div class="print-header-right">{{ formatDate(new Date().toISOString()) }}</div>
        </div>
        
        <!-- 标题 -->
        <div class="print-title">
          <h1 class="print-title-main">{{ caseFile.caseName || caseFile.title || '案卷详情' }}</h1>
          <div class="print-title-meta">
            <span class="print-case-no">案件编号：{{ caseFile.caseNo || '未编号' }}</span>
          </div>
        </div>
        
        <!-- 基本信息 -->
        <div class="print-section">
          <h2 class="print-section-title">一、基本信息</h2>
          <table class="print-info-table">
            <tr v-if="caseFile.incidentTime">
              <td class="print-label">发生时间：</td>
              <td class="print-value">{{ formatDateTime(caseFile.incidentTime) }}</td>
            </tr>
            <tr v-if="caseFile.caseType">
              <td class="print-label">案件类型：</td>
              <td class="print-value">{{ caseFile.caseType }}</td>
            </tr>
            <tr v-if="caseFile.sourceDepartment">
              <td class="print-label">来源部门：</td>
              <td class="print-value">{{ caseFile.sourceDepartment }}</td>
            </tr>
            <tr v-if="caseFile.classificationLevel1">
              <td class="print-label">案件分类：</td>
              <td class="print-value">
                {{ caseFile.classificationLevel1 }}
                <span v-if="caseFile.classificationLevel2"> / {{ caseFile.classificationLevel2 }}</span>
                <span v-if="caseFile.classificationLevel3"> / {{ caseFile.classificationLevel3 }}</span>
              </td>
            </tr>
            <tr v-if="caseFile.status">
              <td class="print-label">处理状态：</td>
              <td class="print-value">{{ getStatusText(caseFile.status) }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 涉案人员 -->
        <div class="print-section" v-if="caseFile.personName || caseFile.personInfo">
          <h2 class="print-section-title">二、涉案人员</h2>
          <div class="print-person-name">{{ caseFile.personName || '未知' }}</div>
          <table class="print-info-table" v-if="caseFile.personInfo && Object.keys(caseFile.personInfo).length > 0">
            <tr v-if="caseFile.personInfo.gender">
              <td class="print-label">性别：</td>
              <td class="print-value">{{ caseFile.personInfo.gender }}</td>
            </tr>
            <tr v-if="caseFile.personInfo.nationality">
              <td class="print-label">民族：</td>
              <td class="print-value">{{ caseFile.personInfo.nationality }}</td>
            </tr>
            <tr v-if="caseFile.personInfo.birthPlace">
              <td class="print-label">出生地：</td>
              <td class="print-value">{{ caseFile.personInfo.birthPlace }}</td>
            </tr>
            <tr v-if="caseFile.personInfo.enlistmentTime">
              <td class="print-label">入伍时间：</td>
              <td class="print-value">{{ formatDate(caseFile.personInfo.enlistmentTime) }}</td>
            </tr>
            <tr v-if="caseFile.personInfo.position">
              <td class="print-label">部职别：</td>
              <td class="print-value">{{ caseFile.personInfo.position }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 事发经过 -->
        <div class="print-section" v-if="caseFile.incidentProcess">
          <h2 class="print-section-title">三、事发经过</h2>
          <div class="print-content">{{ caseFile.incidentProcess }}</div>
        </div>
        
        <!-- 侦查调查过程及结论 -->
        <div class="print-section" v-if="caseFile.investigationProcessAndConclusion">
          <h2 class="print-section-title">四、侦查调查过程及结论</h2>
          <div class="print-content">{{ caseFile.investigationProcessAndConclusion }}</div>
        </div>
        
        <!-- 原因教训 -->
        <div class="print-section" v-if="caseFile.causeAndLesson">
          <h2 class="print-section-title">五、原因教训</h2>
          <div class="print-content">{{ caseFile.causeAndLesson }}</div>
        </div>
        
        <!-- 立案情况 -->
        <div class="print-section" v-if="caseFile.caseFiling">
          <h2 class="print-section-title">六、立案情况</h2>
          <div class="print-content">{{ caseFile.caseFiling }}</div>
        </div>
        
        <!-- 判决情况 -->
        <div class="print-section" v-if="caseFile.judgment">
          <h2 class="print-section-title">七、判决情况</h2>
          <div class="print-content highlight">{{ caseFile.judgment }}</div>
        </div>
        
        <!-- 案件时间线 -->
        <div class="print-section" v-if="caseFile.timeline && caseFile.timeline.length > 0">
          <h2 class="print-section-title">八、案件时间线</h2>
          <div class="print-timeline">
            <div 
              v-for="(item, index) in caseFile.timeline" 
              :key="index"
              class="print-timeline-item"
            >
              <div class="print-timeline-time">{{ formatDateTime(item.time) }}</div>
              <div class="print-timeline-event">{{ item.event }}</div>
              <div class="print-timeline-desc" v-if="item.description">{{ item.description }}</div>
            </div>
          </div>
        </div>
        
        <!-- 页脚 -->
        <div class="print-footer">
          <div class="print-footer-left">打印时间：{{ formatDateTime(new Date().toISOString()) }}</div>
          <div class="print-footer-right">第 <span class="print-page-number"></span> 页</div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { DocumentCopy, CircleClose } from '@element-plus/icons-vue'
import { formatDateTime, formatDate, getStatusText } from '../utils'

defineProps<{
  modelValue: boolean
  caseFile: any
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const doPrint = () => {
  const printContent = document.getElementById('print-content')
  if (!printContent) {
    ElMessage.error('打印内容不存在')
    return
  }
  
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    ElMessage.error('无法打开打印窗口，请检查浏览器弹窗设置')
    return
  }
  
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>打印</title>
      <style>
        @page {
          size: A4;
          margin: 3.7cm 2.8cm 3.5cm 2.8cm;
        }
        
        /* 确保打印时所有文字都是黑色 */
        html, body {
          color: #000000 !important;
          background: #ffffff !important;
        }
        * { 
          margin: 0; 
          padding: 0; 
          box-sizing: border-box;
          color: #000000 !important;
        }
        body {
          font-family: "SimSun", "宋体", "FangSong", "仿宋", serif !important;
          font-size: 16pt;
          line-height: 1.8;
          color: #000000 !important;
          background: #ffffff !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div, td, th, li {
          color: #000000 !important;
        }
        .print-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-bottom: 8pt;
          border-bottom: 2pt solid #000000;
          margin-bottom: 25pt;
          font-size: 14pt;
          color: #000000 !important;
        }
        .print-header-left,
        .print-header-right {
          color: #000000 !important;
          font-weight: normal;
        }
        .print-header-center {
          font-size: 18pt;
          font-weight: bold;
          letter-spacing: 2pt;
          color: #000000 !important;
        }
        .print-title {
          text-align: center;
          margin-bottom: 35pt;
          color: #000000 !important;
        }
        .print-title-main {
          font-size: 22pt;
          font-weight: bold;
          margin-bottom: 12pt;
          letter-spacing: 1pt;
          color: #000000 !important;
        }
        .print-title-meta {
          font-size: 14pt;
          color: #000000 !important;
        }
        .print-case-no {
          color: #000000 !important;
          font-weight: normal;
        }
        .print-section {
          margin-bottom: 25pt;
          page-break-inside: avoid;
          color: #000000 !important;
        }
        .print-section-title {
          font-size: 18pt;
          font-weight: bold;
          margin-bottom: 12pt;
          padding-bottom: 6pt;
          border-bottom: 1pt solid #000000;
          color: #000000 !important;
        }
        .print-info-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 12pt;
        }
        .print-info-table tr {
          border-bottom: 1pt solid #e0e0e0;
        }
        .print-info-table tr:last-child {
          border-bottom: none;
        }
        .print-info-table td {
          color: #000000 !important;
        }
        .print-label {
          width: 120pt;
          padding: 6pt 8pt;
          font-weight: bold;
          vertical-align: top;
          color: #000000 !important;
        }
        .print-value {
          padding: 6pt 8pt;
          vertical-align: top;
          color: #000000 !important;
        }
        .print-person-name {
          font-size: 18pt;
          font-weight: bold;
          margin-bottom: 12pt;
          padding: 8pt;
          background: #f5f5f5 !important;
          border-left: 4pt solid #000000;
          color: #000000 !important;
        }
        .print-content {
          text-align: justify;
          text-indent: 2em;
          line-height: 2;
          margin-bottom: 8pt;
          color: #000000 !important;
        }
        .print-content.highlight {
          font-weight: bold;
          background: #f9f9f9 !important;
          padding: 12pt;
          border-left: 4pt solid #000000;
          color: #000000 !important;
        }
        .print-timeline {
          margin-left: 18pt;
        }
        .print-timeline-item {
          margin-bottom: 18pt;
          padding-left: 28pt;
          position: relative;
        }
        .print-timeline-item::before {
          content: '●';
          position: absolute;
          left: 0;
          color: #000000;
          font-size: 12pt;
        }
        .print-timeline-time {
          font-weight: bold;
          margin-bottom: 4pt;
          font-size: 14pt;
          color: #000000 !important;
        }
        .print-timeline-event {
          font-weight: bold;
          margin-bottom: 4pt;
          color: #000000 !important;
        }
        .print-timeline-desc {
          text-indent: 2em;
          color: #000000 !important;
        }
        .print-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 35pt;
          padding-top: 12pt;
          border-top: 1pt solid #000000;
          font-size: 12pt;
          color: #666666 !important;
        }
        .print-footer-left,
        .print-footer-right {
          color: #666666 !important;
        }
        @media print {
          * {
            color: #000000 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          body {
            print-color-adjust: exact !important;
            -webkit-print-color-adjust: exact !important;
            color: #000000 !important;
            background: #ffffff !important;
          }
          h1, h2, h3, h4, h5, h6, p, span, div, td, th, li {
            color: #000000 !important;
          }
          .print-section {
            page-break-inside: avoid;
          }
          .print-content {
            orphans: 3;
            widows: 3;
          }
          .print-timeline-item {
            page-break-inside: avoid;
          }
        }
      </style>
    </head>
    <body>
      ${printContent.innerHTML}
    </body>
    </html>
  `)
  
  printWindow.document.close()
  
  printWindow.onload = () => {
    setTimeout(() => {
      printWindow.print()
      printWindow.onafterprint = () => {
        printWindow.close()
        emit('update:modelValue', false)
      }
    }, 250)
  }
}
</script>

<style scoped>
:deep(.print-preview-dialog) {
  --el-dialog-bg-color: var(--military-bg-card);
  --el-dialog-border-color: var(--military-border);
}

:deep(.print-preview-dialog .el-dialog__header) {
  background: var(--military-bg-card);
  border-bottom: 1px solid var(--military-border);
  padding: 16px 20px;
}

:deep(.print-preview-dialog .el-dialog__body) {
  background: #f5f5f5;
  padding: 20px;
}

.print-preview-content {
  background: #e5e5e5;
  border-radius: 4px;
  padding: 20px;
  overflow: auto;
  max-height: calc(100vh - 200px);
  display: flex;
  justify-content: center;
}

.print-document {
  width: 210mm;
  min-height: 297mm;
  margin: 0;
  padding: 25mm 20mm;
  background: #ffffff !important;
  font-family: "SimSun", "宋体", "FangSong", "仿宋", serif !important;
  font-size: 16px;
  line-height: 1.8;
  color: #000000 !important;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  transform: scale(0.9);
  transform-origin: top center;
  /* 确保不被全局样式覆盖 */
  isolation: isolate;
}

/* 确保所有文字都是黑色 - 强制重置 */
.print-document {
  color: #000000 !important;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}

.print-document * {
  color: #000000 !important;
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
}

.print-document *::before,
.print-document *::after {
  color: #000000 !important;
}

/* 重置可能的白色文字 */
.print-document h1,
.print-document h2,
.print-document h3,
.print-document h4,
.print-document h5,
.print-document h6 {
  color: #000000 !important;
}

.print-document p,
.print-document span,
.print-document div,
.print-document td,
.print-document th,
.print-document li {
  color: #000000 !important;
}

.print-document .print-header,
.print-document .print-header-left,
.print-document .print-header-right,
.print-document .print-header-center {
  color: #000000 !important;
}

.print-document .print-title,
.print-document .print-title-main,
.print-document .print-title-meta,
.print-document .print-case-no {
  color: #000000 !important;
}

.print-document .print-section-title {
  color: #000000 !important;
}

.print-document .print-label,
.print-document .print-value {
  color: #000000 !important;
}

.print-document .print-person-name {
  color: #000000 !important;
}

.print-document .print-content {
  color: #000000 !important;
}

.print-document .print-content.highlight {
  color: #000000 !important;
}

.print-document .print-timeline-time,
.print-document .print-timeline-event,
.print-document .print-timeline-desc {
  color: #000000 !important;
}

.print-document .print-footer,
.print-document .print-footer-left,
.print-document .print-footer-right {
  color: #666666 !important;
}

/* 预览区域所有元素的样式 */
.print-document h1,
.print-document h2,
.print-document h3,
.print-document h4,
.print-document h5,
.print-document h6 {
  color: #000000 !important;
  font-weight: bold !important;
}

.print-document p,
.print-document span,
.print-document div,
.print-document td,
.print-document th {
  color: #000000 !important;
}

.print-document table {
  border-collapse: collapse;
  width: 100%;
}

.print-document .print-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 2px solid #000000;
  margin-bottom: 30px;
  font-size: 14px;
}

.print-document .print-header-left,
.print-document .print-header-right {
  color: #000000 !important;
  font-weight: normal;
}

.print-document .print-header-center {
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 2px;
  color: #000000 !important;
}

.print-document .print-title {
  text-align: center;
  margin-bottom: 40px;
}

.print-document .print-title-main {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 15px;
  letter-spacing: 1px;
  color: #000000 !important;
}

.print-document .print-title-meta {
  font-size: 14px;
  color: #000000 !important;
}

.print-document .print-case-no {
  color: #000000 !important;
  font-weight: normal;
}

.print-document .print-section {
  margin-bottom: 30px;
}

.print-document .print-section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #000000;
  color: #000000 !important;
}

.print-document .print-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.print-document .print-info-table tr {
  border-bottom: 1px solid #e0e0e0;
}

.print-document .print-info-table tr:last-child {
  border-bottom: none;
}

.print-document .print-label {
  width: 120px;
  padding: 8px 10px;
  font-weight: bold;
  vertical-align: top;
  color: #000000 !important;
}

.print-document .print-value {
  padding: 8px 10px;
  vertical-align: top;
  color: #000000 !important;
}

.print-document .print-person-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f5f5 !important;
  border-left: 4px solid #000000;
  color: #000000 !important;
}

.print-document .print-content {
  text-align: justify;
  text-indent: 2em;
  line-height: 1.8;
  margin-bottom: 10px;
  color: #000000 !important;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.print-document .print-content.highlight {
  font-weight: bold;
  background: #f9f9f9 !important;
  padding: 15px;
  border-left: 4px solid #000000;
  color: #000000 !important;
}

.print-document .print-timeline {
  margin-left: 20px;
}

.print-document .print-timeline-item {
  margin-bottom: 20px;
  padding-left: 30px;
  position: relative;
}

.print-document .print-timeline-item::before {
  content: '●';
  position: absolute;
  left: 0;
  color: #000000 !important;
  font-size: 12px;
}

.print-document .print-timeline-time {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 14px;
  color: #000000 !important;
}

.print-document .print-timeline-event {
  font-weight: bold;
  margin-bottom: 5px;
  color: #000000 !important;
}

.print-document .print-timeline-desc {
  text-indent: 2em;
  color: #000000 !important;
}

.print-document .print-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
  padding-top: 15px;
  border-top: 1px solid #000000;
  font-size: 12px;
  color: #666666 !important;
}

.print-preview-btn {
  padding: 8px 16px;
  border-radius: var(--military-radius-md);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--military-border);
}

.print-preview-btn.secondary {
  background: var(--military-bg-input);
  color: var(--military-text-primary);
}

.print-preview-btn.secondary:hover {
  background: var(--military-bg-input-hover);
  border-color: var(--military-primary);
}

.print-preview-btn.primary {
  background: var(--military-primary);
  color: #ffffff;
  border-color: var(--military-primary);
}

.print-preview-btn.primary:hover {
  background: var(--military-primary-hover);
}

@media (max-width: 1200px) {
  .print-document {
    transform: scale(0.8);
  }
}

@media (max-width: 768px) {
  .print-document {
    transform: scale(0.6);
    width: 100%;
  }
}
</style>
