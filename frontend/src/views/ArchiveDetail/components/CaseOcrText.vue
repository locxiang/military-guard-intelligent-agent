<template>
  <div class="sidebar-card military-card" v-if="ocrText">
    <div class="sidebar-header">
      <el-icon class="sidebar-icon"><DocumentCopy /></el-icon>
      <h3 class="sidebar-title">OCR识别文本</h3>
      <el-tooltip
        content="OCR识别文本由系统自动提取，准确率约85-95%，建议人工校对关键信息"
        placement="top"
        :show-after="300"
      >
        <el-icon class="help-icon">
          <InfoFilled />
        </el-icon>
      </el-tooltip>
    </div>
    <div class="sidebar-body">
      <div class="ocr-text-preview">
        <pre class="ocr-text-content" v-html="highlightText((ocrText || '').substring(0, 500))"></pre>
        <button class="ocr-expand-btn" @click="showFull = !showFull" v-if="ocrText && ocrText.length > 500">
          {{ showFull ? '收起' : '展开全部' }}
        </button>
        <pre v-if="showFull && ocrText" class="ocr-text-content" v-html="highlightText(ocrText.substring(500))"></pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { DocumentCopy, InfoFilled } from '@element-plus/icons-vue'

defineProps<{
  ocrText?: string
  highlightText: (text: string) => string
}>()

const showFull = ref(false)
</script>

<style scoped>
.sidebar-card {
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--military-border);
}

.sidebar-icon {
  font-size: 20px;
  color: var(--military-primary);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0;
  flex: 1;
}

.help-icon {
  font-size: 16px;
  color: var(--military-text-muted);
  cursor: help;
}

.sidebar-body {
  padding-top: 8px;
}

.ocr-text-preview {
  max-height: 300px;
  overflow-y: auto;
  background: var(--military-bg-input);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  padding: 12px;
}

.ocr-text-content {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: var(--military-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.ocr-expand-btn {
  margin-top: 8px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-sm);
  color: var(--military-primary);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.ocr-expand-btn:hover {
  background: var(--military-primary);
  color: #ffffff;
}

:deep(.highlight-mark) {
  background: #fef08a;
  color: #854d0e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}
</style>
