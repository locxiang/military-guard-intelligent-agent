<template>
  <div class="statistics-visualization-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">可视化分析</h2>
        <p class="gov-card-subtitle">多维度数据可视化展示，支持图表交互、数据钻取</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="可视化分析功能支持多维度数据可视化展示，支持图表交互、数据钻取等高级分析功能"
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
      <el-empty description="可视化分析功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持多维度数据可视化、图表交互、数据钻取等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 可视化分析页面
</script>

<style scoped>
.statistics-visualization-view {
  font-family: var(--font-body);
}
</style>
