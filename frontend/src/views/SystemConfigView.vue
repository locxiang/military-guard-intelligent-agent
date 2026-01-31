<template>
  <div class="system-config-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">系统配置</h2>
        <p class="gov-card-subtitle">系统参数配置，包括敏感词库、数据备份、接口配置等</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="系统配置功能支持系统参数配置，包括敏感词库、数据备份、接口配置等，修改配置需谨慎操作"
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
      <el-empty description="系统配置功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持系统参数配置、敏感词库管理、数据备份设置、接口配置等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 系统配置页面
</script>

<style scoped>
.system-config-view {
  font-family: var(--font-body);
}
</style>
