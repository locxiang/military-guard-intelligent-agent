<template>
  <div class="system-role-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">角色权限</h2>
        <p class="gov-card-subtitle">管理角色与权限，支持自定义角色与权限范围</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="角色权限管理功能支持自定义角色和权限范围，请谨慎配置，确保系统安全"
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
      <el-empty description="角色权限功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持角色创建、权限分配、角色管理等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 角色权限页面
</script>

<style scoped>
.system-role-view {
  font-family: var(--font-body);
}
</style>
