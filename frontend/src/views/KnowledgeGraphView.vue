<template>
  <div class="knowledge-graph-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">知识图谱</h2>
        <p class="gov-card-subtitle">查询实体关联关系，可视化展示知识网络</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">图谱说明</span>
        <el-tooltip
          content="知识图谱可查询实体间的关联关系，通过可视化方式展示知识网络，支持多跳查询和关系分析"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 左侧：查询面板 -->
      <div class="lg:col-span-1">
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">查询条件</h3>
            <p class="gov-card-subtitle">设置查询参数，查找实体关联关系</p>
          </div>

          <el-form :model="queryForm" label-width="0" class="gov-form">
            <el-form-item class="gov-form-item">
              <label class="gov-input-label">实体类型</label>
              <el-select
                v-model="queryForm.entityType"
                placeholder="请选择实体类型"
                class="w-full gov-select"
              >
                <el-option label="案件" value="case" />
                <el-option label="人员" value="person" />
                <el-option label="法规" value="law" />
                <el-option label="地点" value="location" />
              </el-select>
            </el-form-item>

            <el-form-item class="gov-form-item">
              <label class="gov-input-label">实体ID</label>
              <el-input
                v-model="queryForm.entityId"
                placeholder="请输入实体ID"
                clearable
                class="gov-input"
              />
            </el-form-item>

            <el-form-item class="gov-form-item">
              <label class="gov-input-label">关联类型</label>
              <el-select
                v-model="queryForm.relationType"
                placeholder="请选择关联类型（可选）"
                clearable
                class="w-full gov-select"
              >
                <el-option label="相关人员" value="related_person" />
                <el-option label="相关案件" value="related_case" />
                <el-option label="引用法规" value="cited_law" />
                <el-option label="发生地点" value="location" />
              </el-select>
            </el-form-item>

            <el-form-item class="gov-form-item">
              <label class="gov-input-label">查询跳数</label>
              <el-input-number
                v-model="queryForm.hopCount"
                :min="1"
                :max="5"
                placeholder="查询跳数"
                class="w-full gov-input-number"
              />
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">查询跳数</span>
                <el-tooltip
                  content="查询跳数表示查询的深度，范围1-5，跳数越大查询范围越广"
                  placement="top"
                  :show-after="300"
                >
                  <el-icon class="gov-help-icon-tooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </el-form-item>

            <el-form-item>
              <button
                class="gov-button-primary w-full"
                :disabled="querying"
                @click="handleQuery"
              >
                <span>{{ querying ? '正在查询，请稍候...' : '执行查询' }}</span>
              </button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 查询结果列表 -->
        <div v-if="queryResult" class="gov-card mt-6">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">查询结果</h3>
            <p class="gov-card-subtitle">查询到的实体关联关系列表</p>
          </div>
          <div class="space-y-2">
            <div
              v-for="(relation, index) in queryResult.relations"
              :key="index"
              class="p-3 bg-gray-50 rounded cursor-pointer hover:bg-gray-100 transition-colors"
              @click="handleRelationClick(relation)"
            >
              <p class="text-sm font-semibold">{{ relation.targetEntity.name }}</p>
              <p class="text-xs text-gray-600">{{ relation.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：图谱可视化 -->
      <div class="lg:col-span-3">
        <div class="gov-card h-[600px]">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">知识图谱可视化</h3>
                <p class="gov-card-subtitle">图形化展示实体间的关联关系</p>
              </div>
              <div class="flex items-center gap-3">
                <button class="gov-button-default gov-button-sm flex items-center gap-2" @click="handleRefresh">
                  <el-icon><Refresh /></el-icon>
                  <span>刷新</span>
                </button>
                <button class="gov-button-primary gov-button-sm flex items-center gap-2" @click="handleExport">
                  <el-icon><Download /></el-icon>
                  <span>导出图谱</span>
                </button>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="gov-help-text-short">可视化说明</span>
            <el-tooltip
              content="图谱可视化支持交互操作，可拖拽、缩放、点击查看详情，支持导出为图片或JSON格式"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div id="graph-container" class="w-full h-full bg-gray-50 rounded">
            <div class="flex items-center justify-center h-full text-gray-400">
              <div class="text-center">
                <el-icon :size="48" class="mb-4"><Connection /></el-icon>
                <p>请在上方输入查询条件进行查询</p>
                <p class="text-sm mt-2">或点击关系节点查看详细信息</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, Connection, Warning, InfoFilled } from '@element-plus/icons-vue'
import { knowledgeGraphApi } from '@/api/knowledge-graph'

// 查询状态
const querying = ref(false)

// 查询表单
const queryForm = reactive({
  entityType: 'case',
  entityId: '',
  relationType: '',
  hopCount: 2
})

// 查询结果
const queryResult = ref<any>(null)

// 查询
const handleQuery = async () => {
  if (!queryForm.entityId) {
    ElMessage.warning('请输入实体ID')
    return
  }

  querying.value = true
  try {
    const response = await knowledgeGraphApi.query(queryForm)
    queryResult.value = response

    // TODO: 渲染图谱可视化
    // renderGraph(queryResult.value)

    ElMessage.success('查询成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '查询失败')
  } finally {
    querying.value = false
  }
}

// 关系点击
const handleRelationClick = (relation: any) => {
  ElMessage.info(`查看实体: ${relation.targetEntity.name}`)
  // TODO: 实现关系详情查看
}

// 刷新
const handleRefresh = () => {
  if (queryResult.value) {
    handleQuery()
  }
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中...')
  // TODO: 实现导出逻辑
}
</script>

<style scoped>
.knowledge-graph-view {
  font-family: var(--font-body);
}

#graph-container {
  min-height: 500px;
}
</style>
