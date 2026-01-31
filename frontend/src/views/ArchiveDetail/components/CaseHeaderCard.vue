<template>
  <div class="case-header-card military-card">
    <!-- 案件编号和状态行 -->
    <div class="case-header-top">
      <div class="case-number-section">
        <span class="case-number-label">案件编号</span>
        <span class="case-number-value">{{ caseFile.caseNo || '未编号' }}</span>
      </div>
      <div class="case-status-section">
        <el-tag :type="getStatusType(caseFile.status)" size="default" effect="dark" class="status-tag">
          {{ getStatusText(caseFile.status) }}
        </el-tag>
        <el-tag size="default" effect="plain" type="info" v-if="caseFile.caseType" class="type-tag">
          {{ caseFile.caseType }}
        </el-tag>
      </div>
    </div>
    
    <!-- 案件标题 -->
    <h1 class="case-title" v-html="highlightText(caseFile.caseName || caseFile.title || '案卷详情')"></h1>
    <p class="case-title-sub" v-if="caseFile.title && caseFile.title !== caseFile.caseName" v-html="highlightText(caseFile.title)"></p>
    
    <!-- 核心信息摘要 -->
    <div class="case-summary-grid">
      <div class="summary-item highlight" v-if="caseFile.personName">
        <div class="summary-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">涉案人员</div>
          <div class="summary-value" v-html="highlightText(caseFile.personName)"></div>
        </div>
      </div>
      <div class="summary-item" v-if="caseFile.incidentTime">
        <div class="summary-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">发生时间</div>
          <div class="summary-value">{{ formatDateTime(caseFile.incidentTime) }}</div>
        </div>
      </div>
      <div class="summary-item" v-if="caseFile.sourceDepartment">
        <div class="summary-icon">
          <el-icon><Files /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">来源部门</div>
          <div class="summary-value">{{ caseFile.sourceDepartment }}</div>
        </div>
      </div>
      <div class="summary-item" v-if="caseFile.classificationLevel1">
        <div class="summary-icon">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">案件分类</div>
          <div class="summary-value">{{ caseFile.classificationLevel1 }}{{ caseFile.classificationLevel2 ? ' / ' + caseFile.classificationLevel2 : '' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Clock, Files, Collection } from '@element-plus/icons-vue'

defineProps<{
  caseFile: any
  highlightText: (text: string) => string
  formatDateTime: (date: string | Date) => string
  getStatusType: (status: string) => string
  getStatusText: (status: string) => string
}>()
</script>

<style scoped>
.case-header-card {
  padding: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(59, 130, 246, 0.02) 100%);
  border: 2px solid var(--military-primary);
  border-radius: var(--military-radius-lg);
}

.case-header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.case-number-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.case-number-label {
  font-size: 12px;
  color: var(--military-text-muted);
  font-weight: 500;
}

.case-number-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--military-primary);
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

.case-status-section {
  display: flex;
  gap: 8px;
  align-items: center;
}

.status-tag,
.type-tag {
  font-size: 14px;
  padding: 6px 12px;
}

.case-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--military-text-primary);
  line-height: 1.4;
  margin: 0 0 8px 0;
}

.case-title-sub {
  font-size: 16px;
  color: var(--military-text-muted);
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.case-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid var(--military-border);
}

.summary-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  transition: all 0.2s;
}

.summary-item:hover {
  border-color: var(--military-primary);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.summary-item.highlight {
  background: rgba(59, 130, 246, 0.08);
  border-color: var(--military-primary);
}

.summary-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--military-primary);
  color: #ffffff;
  border-radius: var(--military-radius-md);
  flex-shrink: 0;
  font-size: 20px;
}

.summary-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--military-text-muted);
  font-weight: 500;
}

.summary-value {
  font-size: 16px;
  color: var(--military-text-primary);
  font-weight: 600;
  line-height: 1.4;
}

:deep(.highlight-mark) {
  background: #fef08a;
  color: #854d0e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}
</style>
