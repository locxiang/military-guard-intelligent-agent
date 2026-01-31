<template>
  <div class="knowledge-graph-relation-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">关系管理</h2>
        <p class="gov-card-subtitle">管理实体间的关联关系，支持关系查询、编辑、删除</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="关系管理功能支持对实体间的关联关系进行管理，包括关系的创建、编辑、删除和查询"
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
      <el-empty description="关系管理功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持关系的增删改查、关系类型管理、关系权重设置等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 关系管理页面
</script>

<style scoped>
.knowledge-graph-relation-view {
  font-family: var(--font-body);
}
</style>
