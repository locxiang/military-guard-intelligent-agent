<template>
  <div class="sidebar-card military-card" v-if="classificationLevel1 || (tags && tags.length > 0)">
    <div class="sidebar-header">
      <el-icon class="sidebar-icon"><Collection /></el-icon>
      <h3 class="sidebar-title">分类与标签</h3>
    </div>
    <div class="sidebar-body">
      <div class="classification-section" v-if="classificationLevel1">
        <div class="classification-label">分类</div>
        <div class="classification-tags-list">
          <el-tag class="classification-tag-item" effect="dark" type="primary" size="small">
            {{ classificationLevel1 }}
          </el-tag>
          <el-tag class="classification-tag-item" effect="plain" type="info" size="small" v-if="classificationLevel2">
            {{ classificationLevel2 }}
          </el-tag>
          <el-tag class="classification-tag-item" effect="plain" type="info" size="small" v-if="classificationLevel3">
            {{ classificationLevel3 }}
          </el-tag>
        </div>
      </div>
      <div class="tags-section" v-if="tags && tags.length > 0">
        <div class="tags-label">标签</div>
        <div class="tags-list">
          <el-tag
            v-for="tag in tags"
            :key="tag"
            size="small"
            class="tag-item"
            @click="$emit('tag-click', tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Collection } from '@element-plus/icons-vue'

defineProps<{
  classificationLevel1?: string
  classificationLevel2?: string
  classificationLevel3?: string
  tags?: string[]
}>()

defineEmits<{
  'tag-click': [tag: string]
}>()
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

.classification-section,
.tags-section {
  margin-bottom: 16px;
}

.classification-section:last-child,
.tags-section:last-child {
  margin-bottom: 0;
}

.classification-label,
.tags-label {
  font-size: 13px;
  color: var(--military-text-muted);
  font-weight: 500;
  margin-bottom: 8px;
}

.classification-tags-list,
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.classification-tag-item,
.tag-item {
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  transform: scale(1.05);
}
</style>
