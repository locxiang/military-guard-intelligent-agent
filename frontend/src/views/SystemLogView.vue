<template>
  <div class="system-log-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">日志审计</h2>
        <p class="gov-card-subtitle">记录系统操作日志，生成全生命周期审计轨迹</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="日志审计功能记录系统所有操作日志，生成全生命周期审计轨迹，用于安全审计和问题追溯"
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
      <el-empty description="日志审计功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持操作日志记录、日志查询、审计轨迹生成等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 日志审计页面
</script>

<style scoped>
.system-log-view {
  font-family: var(--font-body);
}
</style>
