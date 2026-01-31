<template>
  <div class="knowledge-graph-extract-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">知识提取</h2>
        <p class="gov-card-subtitle">从非结构化文档中提取关键信息，构建知识图谱</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="知识提取功能可从非结构化文档中自动提取实体和关系，用于构建和更新知识图谱"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="gov-card">
      <el-empty description="知识提取功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持从文档中自动提取实体、关系，自动构建知识图谱</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 知识提取页面
</script>

<style scoped>
.knowledge-graph-extract-view {
  font-family: var(--font-body);
}
</style>
