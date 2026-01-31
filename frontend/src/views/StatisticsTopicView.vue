<template>
  <div class="statistics-topic-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">专题分析</h2>
        <p class="gov-card-subtitle">多维度专题分析模型，包括时空分析、成因关联分析、趋势分析</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="专题分析功能支持多维度专题分析，包括时空分析、成因关联分析、趋势分析等高级分析模型"
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
      <el-empty description="专题分析功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持时空分析、成因关联分析、趋势分析等专题分析模型</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 专题分析页面
</script>

<style scoped>
.statistics-topic-view {
  font-family: var(--font-body);
}
</style>
