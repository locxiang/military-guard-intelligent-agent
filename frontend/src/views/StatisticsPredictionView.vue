<template>
  <div class="statistics-prediction-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">预测分析</h2>
        <p class="gov-card-subtitle">AI驱动的事件预测引擎，支持风险等级预测、趋势预测</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="预测分析功能基于AI技术，支持风险等级预测、趋势预测等，预测结果仅供参考，需结合实际情况判断"
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
      <el-empty description="预测分析功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持AI驱动的事件预测、风险等级预测、趋势预测等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 预测分析页面
</script>

<style scoped>
.statistics-prediction-view {
  font-family: var(--font-body);
}
</style>
