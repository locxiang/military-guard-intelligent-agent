<template>
  <div class="statistics-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">统计分析</h2>
        <p class="gov-card-subtitle">多维度统计分析案卷数据，生成可视化报表</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">统计说明</span>
        <el-tooltip
          content="统计分析功能支持多维度数据统计，包括案卷类型、时间趋势、部门分布等，可生成可视化报表"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="gov-card mb-6">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">筛选条件</h3>
        <p class="gov-card-subtitle">设置统计分析的筛选条件</p>
      </div>
      <el-form :model="filterForm" class="gov-form flex flex-wrap gap-4">
        <el-form-item class="gov-form-item">
          <label class="gov-input-label">时间范围</label>
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            class="gov-date-picker"
            style="width: 260px"
            @change="handleFilterChange"
          />
        </el-form-item>

        <el-form-item class="gov-form-item">
          <label class="gov-input-label">案卷类型</label>
          <el-select
            v-model="filterForm.caseType"
            placeholder="请选择案卷类型"
            clearable
            class="gov-select"
            style="width: 160px"
            @change="handleFilterChange"
          >
            <el-option label="全部" value="" />
            <el-option label="案件卷宗" value="案件卷宗" />
            <el-option label="公文材料" value="公文材料" />
            <el-option label="调查报告" value="调查报告" />
          </el-select>
        </el-form-item>

        <el-form-item class="gov-form-item">
          <label class="gov-input-label">来源部门</label>
          <el-select
            v-model="filterForm.department"
            placeholder="请选择部门"
            clearable
            filterable
            class="gov-select"
            style="width: 210px"
            @change="handleFilterChange"
          >
            <el-option label="全部" value="" />
            <el-option label="某试训基地保卫处" value="某试训基地保卫处" />
            <el-option label="其他部门" value="其他部门" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <div class="flex items-center gap-3 mt-7">
            <button class="gov-button-primary flex items-center gap-2" @click="handleRefresh">
              <span>刷新数据</span>
            </button>
            <button class="gov-button-default flex items-center gap-2" @click="handleExport">
              <span>导出报表</span>
            </button>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <span class="gov-help-text-short">操作说明</span>
            <el-tooltip
              content="设置筛选条件后点击刷新可更新统计数据，支持导出Excel和PDF格式报表"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计图表 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- 案卷类型分布 -->
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">案卷类型分布</h3>
        </div>
        <div id="type-chart" class="h-64"></div>
      </div>

      <!-- 时间趋势 -->
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">时间趋势</h3>
        </div>
        <div id="trend-chart" class="h-64"></div>
      </div>

      <!-- 部门统计 -->
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">部门统计</h3>
        </div>
        <div id="department-chart" class="h-64"></div>
      </div>

      <!-- 状态分布 -->
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">状态分布</h3>
        </div>
        <div id="status-chart" class="h-64"></div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="gov-card">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">详细数据</h3>
        <p class="gov-card-subtitle">统计数据的详细列表</p>
      </div>
      <el-table :data="statisticsData" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="dimension" label="维度" />
        <el-table-column prop="value" label="数值" />
        <el-table-column prop="percentage" label="占比">
          <template #default="{ row }">
            <el-progress :percentage="row.percentage" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="趋势">
          <template #default="{ row }">
            <el-tag :type="row.trend > 0 ? 'success' : 'info'" size="small">
              {{ row.trend > 0 ? '↑' : '↓' }} {{ Math.abs(row.trend) }}%
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Warning, InfoFilled } from '@element-plus/icons-vue'

// 加载状态
const loading = ref(false)

// 筛选表单
const filterForm = reactive({
  dateRange: null as [Date, Date] | null,
  caseType: '',
  department: ''
})

// 统计数据
const statisticsData = ref<any[]>([])

// 图表实例（TODO: 使用 ECharts）
const typeChart: any = null
const trendChart: any = null
const departmentChart: any = null
const statusChart: any = null

// 筛选改变
const handleFilterChange = () => {
  loadData()
}

// 刷新
const handleRefresh = () => {
  loadData()
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中...')
  // TODO: 实现导出逻辑
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await statisticsApi.getStatistics(filterForm)
    statisticsData.value = response.data || []

    // TODO: 渲染图表
    // renderCharts()
  } catch (error: any) {
    ElMessage.error(error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  // 销毁图表实例
  // if (typeChart) typeChart.dispose()
  // if (trendChart) trendChart.dispose()
  // if (departmentChart) departmentChart.dispose()
  // if (statusChart) statusChart.dispose()
})
</script>

<style scoped>
.statistics-view {
  font-family: var(--font-body);
}

#type-chart,
#trend-chart,
#department-chart,
#status-chart {
  min-height: 256px;
}
</style>
