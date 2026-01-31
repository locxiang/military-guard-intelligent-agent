<template>
  <div class="knowledge-graph-entity-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">实体管理</h2>
        <p class="gov-card-subtitle">管理知识图谱中的实体，包括人员、案件、地点、法规等</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="实体管理功能支持对知识图谱中的实体进行增删改查操作，包括人员、案件、地点、法规等类型"
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
      <el-empty description="实体管理功能开发中，敬请期待..." :image-size="120">
        <template #description>
          <p class="text-base" style="color: var(--color-text-muted);">功能正在开发中</p>
          <p class="text-sm mt-2" style="color: var(--color-text-muted);">该功能将支持实体的增删改查、批量操作、实体分类管理等功能</p>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning, InfoFilled } from '@element-plus/icons-vue'
// 实体管理页面
</script>

<style scoped>
.knowledge-graph-entity-view {
  font-family: var(--font-body);
}
</style>
