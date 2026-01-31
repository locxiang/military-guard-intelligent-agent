<template>
  <div class="case-status-guide military-card" v-if="caseFile.caseFiling || caseFile.judgment">
    <div class="status-guide-header">
      <el-icon class="status-guide-icon"><Flag /></el-icon>
      <h3 class="status-guide-title">案件处理状态</h3>
    </div>
    <div class="status-guide-content">
      <div class="status-step" v-if="caseFile.caseFiling">
        <div class="step-indicator completed">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="step-content">
          <div class="step-title">已立案</div>
          <div class="step-desc" v-html="highlightText(caseFile.caseFiling)"></div>
        </div>
      </div>
      <div class="status-step" v-if="caseFile.judgment">
        <div class="step-indicator completed">
          <el-icon><Finished /></el-icon>
        </div>
        <div class="step-content">
          <div class="step-title">已判决/处理</div>
          <div class="step-desc highlight-text" v-html="highlightText(caseFile.judgment)"></div>
        </div>
      </div>
      <div class="status-step" v-if="!caseFile.caseFiling && !caseFile.judgment">
        <div class="step-indicator pending">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="step-content">
          <div class="step-title">待处理</div>
          <div class="step-desc">案件尚未立案，请及时处理</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Flag, CircleCheck, Finished, Timer } from '@element-plus/icons-vue'

defineProps<{
  caseFile: any
  highlightText: (text: string) => string
}>()
</script>

<style scoped>
.case-status-guide {
  padding: 20px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.02) 100%);
  border-left: 4px solid #10b981;
}

.status-guide-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.status-guide-icon {
  font-size: 24px;
  color: #10b981;
}

.status-guide-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0;
}

.status-guide-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.step-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
  color: #ffffff;
}

.step-indicator.completed {
  background: linear-gradient(135deg, #10b981, #059669);
}

.step-indicator.pending {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin-bottom: 8px;
}

.step-desc {
  font-size: 14px;
  color: var(--military-text-muted);
  line-height: 1.6;
}

.step-desc.highlight-text {
  color: var(--military-primary);
  font-weight: 600;
}

:deep(.highlight-mark) {
  background: #fef08a;
  color: #854d0e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}
</style>
