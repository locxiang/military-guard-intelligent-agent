<template>
  <div class="system-monitor-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">系统监控</h2>
        <p class="gov-card-subtitle">监控系统运行状态，包括响应速度、CPU使用率、接口调用成功率等</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="系统监控功能实时监控系统运行状态，包括响应速度、CPU使用率、接口调用成功率等关键指标"
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
      <el-empty description="系统监控功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持系统运行状态监控、性能指标展示、告警通知等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 系统监控页面
</script>

<style scoped>
.system-monitor-view {
  font-family: var(--font-body);
}
</style>
