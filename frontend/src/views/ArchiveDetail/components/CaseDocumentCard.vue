<template>
  <div class="sidebar-card military-card" v-if="filePath">
    <div class="sidebar-header">
      <el-icon class="sidebar-icon"><Document /></el-icon>
      <h3 class="sidebar-title">原始文档</h3>
    </div>
    <div class="sidebar-body">
      <div 
        class="document-card" 
        @click="$emit('preview')"
      >
        <div class="document-icon-wrapper">
          <!-- 图片文件显示缩略图 -->
          <div v-if="isImageFile(fileType)" class="document-icon-image">
            <el-image
              :src="fileUrl"
              fit="cover"
              class="document-thumbnail"
              :preview-src-list="[fileUrl]"
              @click.stop="$emit('preview')"
            />
          </div>
          <!-- PDF文件图标 -->
          <div v-else-if="isPdfFile(fileType)" class="document-icon-pdf">
            <el-icon class="document-type-icon"><Document /></el-icon>
            <span class="document-type-label">PDF</span>
          </div>
          <!-- Word文件图标 -->
          <div v-else-if="isWordFile(fileType)" class="document-icon-word">
            <el-icon class="document-type-icon"><DocumentCopy /></el-icon>
            <span class="document-type-label">DOC</span>
          </div>
          <!-- Excel文件图标 -->
          <div v-else-if="isExcelFile(fileType)" class="document-icon-excel">
            <el-icon class="document-type-icon"><DocumentCopy /></el-icon>
            <span class="document-type-label">XLS</span>
          </div>
          <!-- 其他文件类型 -->
          <div v-else class="document-icon-default">
            <el-icon class="document-type-icon"><DocumentCopy /></el-icon>
            <span class="document-type-label">{{ fileType?.toUpperCase() || 'FILE' }}</span>
          </div>
        </div>
        <div class="document-info">
          <div class="document-name" :title="fileName">
            {{ fileName }}
          </div>
          <div class="document-meta">
            <span>{{ formatFileSize(fileSize) }}</span>
            <span>·</span>
            <span>{{ fileType?.toUpperCase() || '未知' }}</span>
          </div>
        </div>
        <div class="document-actions">
          <button class="document-action-btn" @click.stop="$emit('preview')" title="预览">
            <el-icon><View /></el-icon>
          </button>
          <button class="document-action-btn" @click.stop="$emit('download')" title="下载">
            <el-icon><Download /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, DocumentCopy, View, Download } from '@element-plus/icons-vue'
import { formatFileSize, isPdfFile, isImageFile, isWordFile, isExcelFile, getFileName } from '../utils'

const props = defineProps<{
  filePath?: string
  fileSize?: number
  fileType?: string
  fileId?: number
}>()

const emit = defineEmits<{
  preview: []
  download: []
}>()

const fileName = computed(() => getFileName(props.filePath || ''))

const fileUrl = computed(() => {
  if (!props.filePath) return ''
  if (props.filePath.startsWith('http://') || props.filePath.startsWith('https://')) {
    return props.filePath
  }
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  return `${baseUrl}/case-file/file/${props.fileId}`
})
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

.sidebar-body {
  padding-top: 8px;
}

.document-card {
  padding: 16px;
  background: var(--military-bg-input);
  border: 2px solid var(--military-border);
  border-radius: var(--military-radius-md);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.document-card:hover {
  border-color: var(--military-primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.document-icon-wrapper {
  width: 100%;
  height: 120px;
  margin-bottom: 12px;
  border-radius: var(--military-radius-md);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.document-icon-image {
  width: 100%;
  height: 100%;
}

.document-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.document-icon-pdf,
.document-icon-word,
.document-icon-excel,
.document-icon-default {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.document-icon-pdf {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.document-icon-word {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.document-icon-excel {
  background: linear-gradient(135deg, #10b981, #059669);
}

.document-icon-default {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.document-type-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.document-type-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
}

.document-info {
  margin-bottom: 12px;
}

.document-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--military-text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-meta {
  font-size: 12px;
  color: var(--military-text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.document-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.document-action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-sm);
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.document-action-btn:hover {
  background: var(--military-primary);
  color: #ffffff;
  border-color: var(--military-primary);
}
</style>
