<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="原始文档预览"
    width="90%"
    :fullscreen="isFullscreen"
    class="document-preview-dialog"
    @close="isFullscreen = false"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-2">
          <el-icon><Document /></el-icon>
          <span>原始文档预览 - {{ fileName }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="military-button-secondary military-button-sm" @click="isFullscreen = !isFullscreen">
            <el-icon><FullScreen /></el-icon>
            <span>{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
          </button>
          <button class="military-button military-button-sm" @click="$emit('download')">
            <el-icon><Download /></el-icon>
            <span>下载</span>
          </button>
        </div>
      </div>
    </template>
    
    <div class="document-preview-container">
      <!-- PDF预览 -->
      <div v-if="isPdfFile(fileType)" class="pdf-preview-wrapper">
        <iframe
          :src="fileUrl"
          class="pdf-preview-iframe"
          frameborder="0"
        ></iframe>
      </div>
      
      <!-- 图片预览 -->
      <div v-else-if="isImageFile(fileType)" class="image-preview-wrapper">
        <el-image
          :src="fileUrl"
          fit="contain"
          :preview-src-list="[fileUrl]"
          class="preview-image"
        />
      </div>
      
      <!-- 其他文件类型 -->
      <div v-else class="unsupported-preview">
        <el-icon class="unsupported-icon"><DocumentCopy /></el-icon>
        <p class="unsupported-text">当前文件类型不支持在线预览</p>
        <p class="unsupported-hint">文件类型: {{ fileType?.toUpperCase() || '未知' }}</p>
        <button class="military-button mt-4" @click="$emit('download')">
          <el-icon><Download /></el-icon>
          <span>下载文件查看</span>
        </button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Document, DocumentCopy, Download, FullScreen } from '@element-plus/icons-vue'
import { isPdfFile, isImageFile, getFileName } from '../utils'

const props = defineProps<{
  modelValue: boolean
  filePath?: string
  fileType?: string
  fileId?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'download': []
}>()

const isFullscreen = ref(false)

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
:deep(.document-preview-dialog) {
  --el-dialog-bg-color: var(--military-bg-card);
  --el-dialog-border-color: var(--military-border);
}

:deep(.document-preview-dialog .el-dialog__header) {
  background: var(--military-bg-card);
  border-bottom: 1px solid var(--military-border);
  padding: 16px 20px;
}

:deep(.document-preview-dialog .el-dialog__body) {
  background: var(--military-bg-card);
  padding: 0;
}

.document-preview-container {
  width: 100%;
  height: calc(100vh - 200px);
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--military-bg-input);
}

.pdf-preview-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdf-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.image-preview-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: var(--military-radius-md);
}

.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  text-align: center;
}

.unsupported-icon {
  font-size: 64px;
  color: var(--military-text-muted);
}

.unsupported-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.unsupported-hint {
  font-size: 14px;
  color: var(--military-text-muted);
}
</style>
