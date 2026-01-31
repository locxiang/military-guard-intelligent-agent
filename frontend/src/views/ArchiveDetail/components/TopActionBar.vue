<template>
  <div class="mb-4 flex items-center justify-between">
    <button class="back-nav-button flex items-center gap-2" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      <span>返回案卷列表</span>
    </button>
    <!-- 顶部操作栏 -->
    <div class="flex items-center gap-2 flex-wrap">
      <!-- 快速搜索 -->
      <div class="top-search-box">
        <el-input
          :model-value="searchKeyword"
          placeholder="在本案卷中搜索..."
          clearable
          size="small"
          class="top-search-input"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <!-- 文档操作 -->
      <button 
        class="top-action-button primary" 
        @click="$emit('view-document')" 
        v-if="hasFile"
      >
        <el-icon><View /></el-icon>
        <span>查看原始文档</span>
      </button>
      <button class="top-action-button" @click="$emit('download')" v-if="hasFile">
        <el-icon><Download /></el-icon>
        <span>下载</span>
      </button>
      <button class="top-action-button" @click="$emit('print')">
        <el-icon><DocumentCopy /></el-icon>
        <span>打印</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, Search, View, Download, DocumentCopy } from '@element-plus/icons-vue'

defineProps<{
  searchKeyword: string
  hasFile: boolean
}>()

const emit = defineEmits<{
  'update:searchKeyword': [value: string]
  'view-document': []
  'download': []
  'print': []
}>()

const handleSearch = (value: string) => {
  emit('update:searchKeyword', value)
}
</script>

<style scoped>
.back-nav-button {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.back-nav-button:hover {
  background: var(--military-bg-input);
  border-color: var(--military-primary);
  color: var(--military-primary);
}

.top-search-box {
  min-width: 240px;
}

.top-search-input {
  width: 100%;
}

.top-action-button {
  padding: 8px 16px;
  background: var(--military-bg-input);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  color: var(--military-text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.top-action-button:hover {
  background: var(--military-bg-input-hover);
  border-color: var(--military-primary);
}

.top-action-button.primary {
  background: var(--military-primary);
  color: #ffffff;
  border-color: var(--military-primary);
}

.top-action-button.primary:hover {
  background: var(--military-primary-hover);
}
</style>
