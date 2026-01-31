<template>
  <div class="doc-generate-report-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">报告生成器</h2>
        <p class="gov-card-subtitle">选择报告类型和时间范围，AI智能辅助生成各类统计分析报告</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：报告配置与生成 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 报告类型选择 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第一步：选择报告类型</h3>
            <p class="gov-card-subtitle">选择您需要生成的报告类型</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="reportType in reportTypes"
              :key="reportType.value"
              class="report-type-card"
              :class="{ 'selected': selectedReportType === reportType.value }"
              @click="selectReportType(reportType.value)"
            >
              <div class="flex items-start gap-3">
                <div class="report-type-checkbox">
                  <el-icon v-if="selectedReportType === reportType.value" class="check-icon"><Check /></el-icon>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-icon :size="20" class="report-type-icon">
                      <component :is="reportType.icon" />
                    </el-icon>
                    <div class="report-type-title">{{ reportType.label }}</div>
                  </div>
                  <div class="report-type-desc">{{ reportType.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 时间范围选择 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第二步：选择统计范围</h3>
            <p class="gov-card-subtitle">设置报告的时间范围和统计维度</p>
          </div>

          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="gov-input-label">报告周期</label>
                <el-select v-model="reportPeriod" placeholder="请选择报告周期" class="w-full gov-select">
                  <el-option label="本周" value="week" />
                  <el-option label="本月" value="month" />
                  <el-option label="本季度" value="quarter" />
                  <el-option label="本年度" value="year" />
                  <el-option label="自定义" value="custom" />
                </el-select>
              </div>
              <div v-if="reportPeriod === 'custom'">
                <label class="gov-input-label">自定义时间</label>
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  class="w-full"
                />
              </div>
            </div>

            <!-- 数据概览 -->
            <div v-if="statisticsLoaded" class="data-overview">
              <div class="overview-title">数据概览（{{ periodLabel }}）</div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div class="overview-item">
                  <div class="overview-value">{{ statistics.totalCases }}</div>
                  <div class="overview-label">案件总数</div>
                </div>
                <div class="overview-item">
                  <div class="overview-value">{{ statistics.completedCases }}</div>
                  <div class="overview-label">已办结</div>
                </div>
                <div class="overview-item">
                  <div class="overview-value">{{ statistics.pendingCases }}</div>
                  <div class="overview-label">待处理</div>
                </div>
                <div class="overview-item">
                  <div class="overview-value">{{ statistics.completionRate }}%</div>
                  <div class="overview-label">办结率</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 补充信息 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第三步：补充报告内容（可选）</h3>
            <p class="gov-card-subtitle">您可以补充一些需要在报告中体现的内容</p>
          </div>

          <el-form :model="formData" class="gov-form" label-position="top">
            <el-form-item label="报告标题" class="gov-form-item">
              <el-input 
                v-model="formData.title" 
                :placeholder="defaultTitle"
                class="gov-input" 
              />
            </el-form-item>

            <el-form-item label="工作亮点" class="gov-form-item">
              <el-input
                v-model="formData.highlights"
                type="textarea"
                :rows="3"
                placeholder="请填写本期工作中的亮点、成效（如有）"
                class="gov-input"
              />
            </el-form-item>

            <el-form-item label="存在问题" class="gov-form-item">
              <el-input
                v-model="formData.problems"
                type="textarea"
                :rows="3"
                placeholder="请填写工作中存在的问题和不足（如有）"
                class="gov-input"
              />
            </el-form-item>

            <el-form-item label="下步计划" class="gov-form-item">
              <el-input
                v-model="formData.plans"
                type="textarea"
                :rows="3"
                placeholder="请填写下一阶段的工作计划（如有）"
                class="gov-input"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 生成按钮 -->
        <div class="gov-card">
          <div class="flex items-center gap-4">
            <button
              class="gov-button-primary flex items-center gap-2"
              :disabled="!canGenerate"
              @click="handleGenerate"
            >
              <el-icon><MagicStick /></el-icon>
              <span>AI智能生成</span>
            </button>
            <button class="gov-button-default flex items-center gap-2" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>重置</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：操作指南与说明 -->
      <div class="space-y-6">
        <!-- 操作指南 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">操作指南</h3>
          </div>
          <div class="space-y-3">
            <div class="guide-step" :class="{ 'active': currentStep >= 1 }">
              <div class="step-number">1</div>
              <div class="step-content">
                <div class="step-title">选择报告类型</div>
                <div class="step-desc">选择需要生成的报告类型</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 2 }">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-title">选择统计范围</div>
                <div class="step-desc">设置报告的时间范围</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 3 }">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-title">补充报告内容</div>
                <div class="step-desc">填写工作亮点、问题等（可选）</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 4 }">
              <div class="step-number">4</div>
              <div class="step-content">
                <div class="step-title">AI智能生成</div>
                <div class="step-desc">点击生成，AI将自动生成报告</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 报告类型说明 -->
        <div v-if="selectedReportType" class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">{{ currentReportTypeInfo?.label }}说明</h3>
          </div>
          <div class="type-info">
            <div class="type-info-item">
              <div class="type-info-label">报告用途</div>
              <div class="type-info-value">{{ currentReportTypeInfo?.usage }}</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">包含内容</div>
              <div class="type-info-value">{{ currentReportTypeInfo?.content }}</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">建议周期</div>
              <div class="type-info-value">{{ currentReportTypeInfo?.period }}</div>
            </div>
          </div>
        </div>

        <!-- 案件类型分布 -->
        <div v-if="statisticsLoaded" class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">案件类型分布</h3>
          </div>
          <div class="space-y-3">
            <div 
              v-for="(item, index) in statistics.caseTypeDistribution" 
              :key="index"
              class="distribution-item"
            >
              <div class="distribution-header">
                <span class="distribution-name">{{ item.name }}</span>
                <span class="distribution-count">{{ item.count }}件</span>
              </div>
              <div class="distribution-bar">
                <div 
                  class="distribution-bar-fill" 
                  :style="{ width: `${item.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史报告 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">历史报告</h3>
          </div>
          <div v-if="historyReports.length > 0" class="space-y-3">
            <div
              v-for="report in historyReports"
              :key="report.id"
              class="history-item"
            >
              <div class="history-info">
                <div class="history-title">{{ report.title }}</div>
                <div class="history-meta">{{ report.period }} · {{ report.date }}</div>
              </div>
              <el-tag size="small" type="success">已生成</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无历史报告" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  InfoFilled, Refresh, MagicStick, Check,
  DataLine, Notebook, TrendCharts
} from '@element-plus/icons-vue'
import { caseFileApi as archiveApi, type CaseFile } from '@/api/archive'

const router = useRouter()

// 报告类型
const selectedReportType = ref('')
const reportTypes = [
  {
    value: 'work_summary',
    label: '工作总结',
    description: '汇总工作情况和成效',
    icon: Notebook,
    usage: '向上级汇报工作开展情况，总结经验教训',
    content: '工作概况、主要成效、存在问题、下步计划',
    period: '月度/季度/年度'
  },
  {
    value: 'statistics_report',
    label: '统计分析报告',
    description: '案件数据统计分析',
    icon: DataLine,
    usage: '分析案件数据，为决策提供数据支撑',
    content: '案件数量统计、类型分布、趋势分析、对比分析',
    period: '月度/季度'
  },
  {
    value: 'trend_analysis',
    label: '形势分析报告',
    description: '分析案件发展趋势',
    icon: TrendCharts,
    usage: '分析案件发展态势，预判风险隐患',
    content: '案件态势、特点分析、原因剖析、对策建议',
    period: '季度/年度'
  }
]

// 当前报告类型信息
const currentReportTypeInfo = computed(() => {
  return reportTypes.find(t => t.value === selectedReportType.value)
})

// 时间范围
const reportPeriod = ref('month')
const dateRange = ref<[Date, Date] | null>(null)

// 周期标签
const periodLabel = computed(() => {
  const labels: Record<string, string> = {
    week: '本周',
    month: '本月',
    quarter: '本季度',
    year: '本年度',
    custom: '自定义'
  }
  return labels[reportPeriod.value] || ''
})

// 默认标题
const defaultTitle = computed(() => {
  const typeLabel = currentReportTypeInfo.value?.label || '报告'
  return `${periodLabel.value}${typeLabel}`
})

// 表单数据
const formData = reactive({
  title: '',
  highlights: '',
  problems: '',
  plans: ''
})

// 统计数据
const statisticsLoaded = ref(false)
const statistics = reactive({
  totalCases: 0,
  completedCases: 0,
  pendingCases: 0,
  completionRate: 0,
  caseTypeDistribution: [] as Array<{ name: string; count: number; percentage: number }>
})

// 历史报告
const historyReports = ref<any[]>([])

// 当前步骤
const currentStep = computed(() => {
  if (selectedReportType.value && statisticsLoaded.value && (formData.title || formData.highlights || formData.problems || formData.plans)) return 3
  if (selectedReportType.value && statisticsLoaded.value) return 2
  if (selectedReportType.value) return 1
  return 0
})

// 是否可以生成
const canGenerate = computed(() => {
  return selectedReportType.value && statisticsLoaded.value
})

// 按报告类型加载演示数据（方便演示，避免录入）
const loadDemoDataForType = (type: string) => {
  formData.title = ''
  formData.highlights = ''
  formData.problems = ''
  formData.plans = ''
  if (type === 'work_summary') {
    formData.title = '保卫处2026年1月份工作总结'
    formData.highlights = `一、完成春节前安全隐患排查，共检查重点部位12处，发现并整改隐患3项。
二、配合上级完成涉密载体清查，未发现泄密隐患。
三、受理并初查线索2件，其中张某某涉嫌盗窃一案已形成立案请示并报批。`
    formData.problems = '部分单位对保卫工作配合度不够，个别隐患整改存在拖延现象；门禁与外来人员登记仍有松懈。'
    formData.plans = '一是继续跟进在办案件批复及后续办理；二是开展一次全员法制教育；三是与相关单位建立定期联络机制，强化协同。'
  } else if (type === 'statistics_report') {
    formData.title = '保卫工作案件统计分析报告（2026年1月）'
    formData.highlights = '本月案件总数与上月基本持平，办结率较上月提升；盗窃类、诈骗类案件占比仍居前列，已针对性加强宣教与防控。'
    formData.problems = '待办案件中有2件因需跨单位协查，进度偏慢；部分案件证据固定不够及时。'
    formData.plans = '下月将重点推动跨单位协查机制落地，并加强办案时限督导与证据固定培训。'
  } else if (type === 'trend_analysis') {
    formData.title = '保卫工作形势分析报告（2026年第一季度）'
    formData.highlights = '本季度案件态势总体可控，盗窃、诈骗类案件仍为主要类型；春节前后未发生重大案事件，节前排查与值班备勤成效明显。'
    formData.problems = '个别单位对保卫工作重视不够，存在“重业务轻安全”倾向；新兵入营后涉法涉纪风险需持续关注。'
    formData.plans = '下一阶段将加强形势研判与风险预警，开展新兵专题法制教育，并推动各单位落实保卫工作责任制。'
  }
}

// 选择报告类型
const selectReportType = (type: string) => {
  selectedReportType.value = type
  loadDemoDataForType(type)
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    // 获取案件列表
    const response = await archiveApi.getList({ page: 1, pageSize: 1000 })
    // 处理不同的返回格式
    const responseData = response as { items?: CaseFile[]; data?: { items?: CaseFile[] } }
    const cases: CaseFile[] = responseData.data?.items || responseData.items || (Array.isArray(response) ? response : [])
    
    // 计算统计数据
    statistics.totalCases = cases.length
    statistics.completedCases = cases.filter((c) => c.status === 'completed').length
    statistics.pendingCases = cases.filter((c) => c.status !== 'completed').length
    statistics.completionRate = statistics.totalCases > 0 
      ? Math.round((statistics.completedCases / statistics.totalCases) * 100)
      : 0
    
    // 计算类型分布
    const typeCount: Record<string, number> = {}
    cases.forEach((c) => {
      const type = c.caseType || '未分类'
      typeCount[type] = (typeCount[type] || 0) + 1
    })
    
    const total = cases.length || 1
    statistics.caseTypeDistribution = Object.entries(typeCount)
      .map(([name, count]) => ({
        name,
        count,
        percentage: Math.round((count / total) * 100)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
    
    statisticsLoaded.value = true
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据
    statistics.totalCases = 15
    statistics.completedCases = 12
    statistics.pendingCases = 3
    statistics.completionRate = 80
    statistics.caseTypeDistribution = [
      { name: '盗窃罪', count: 6, percentage: 40 },
      { name: '诈骗罪', count: 4, percentage: 27 },
      { name: '故意伤害', count: 3, percentage: 20 },
      { name: '其他', count: 2, percentage: 13 }
    ]
    statisticsLoaded.value = true
  }
}

// 生成报告
const handleGenerate = async () => {
  // 保存报告数据到 sessionStorage
  const reportData = {
    reportType: selectedReportType.value,
    reportPeriod: reportPeriod.value,
    dateRange: dateRange.value,
    formData: { ...formData },
    statistics: { ...statistics }
  }
  sessionStorage.setItem('reportData', JSON.stringify(reportData))
  
  // 添加到历史记录
  addToHistory()
  
  // 跳转到生成结果页面
  router.push({
    path: '/doc-generate/report/result',
    query: {
      reportType: selectedReportType.value
    }
  })
}

// 添加到历史记录
const addToHistory = () => {
  historyReports.value.unshift({
    id: Date.now(),
    title: formData.title || defaultTitle.value,
    period: periodLabel.value,
    date: new Date().toLocaleDateString('zh-CN')
  })
  if (historyReports.value.length > 5) {
    historyReports.value = historyReports.value.slice(0, 5)
  }
}

// 重置
const handleReset = () => {
  formData.title = ''
  formData.highlights = ''
  formData.problems = ''
  formData.plans = ''
}

// 监听周期变化
watch(reportPeriod, () => {
  loadStatistics()
})

onMounted(() => {
  loadStatistics()
  // 若尚未填写任何内容，则默认选中「工作总结」并加载该类型演示数据，方便演示
  if (!formData.title && !formData.highlights && !formData.problems && !formData.plans) {
    selectedReportType.value = 'work_summary'
    loadDemoDataForType('work_summary')
  }
})
</script>

<style scoped>
.doc-generate-report-view {
  font-family: var(--font-body);
}

/* 报告类型卡片 */
.report-type-card {
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.report-type-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.report-type-card.selected {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.15);
}

.report-type-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(59, 130, 246, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.report-type-card.selected .report-type-checkbox {
  background: var(--military-primary);
  border-color: var(--military-primary);
}

.check-icon {
  color: #fff;
  font-size: 14px;
}

.report-type-icon {
  color: var(--military-primary);
}

.report-type-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.report-type-desc {
  font-size: 12px;
  color: var(--military-text-secondary);
  line-height: 1.4;
}

/* 数据概览 */
.data-overview {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 16px;
}

.overview-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--military-primary);
}

.overview-item {
  background: rgba(10, 22, 40, 0.3);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--military-primary);
}

.overview-label {
  font-size: 12px;
  color: var(--military-text-muted);
  margin-top: 4px;
}

/* 生成内容 */
.generated-content-wrapper {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  max-height: 600px;
  overflow-y: auto;
}

.generated-content {
  color: #333;
  font-family: SimSun, serif;
}

.generated-content :deep(.report-title) {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 24px;
}

.generated-content :deep(.section-title) {
  font-size: 15px;
  font-weight: bold;
  margin: 20px 0 10px;
}

.generated-content :deep(.report-section) {
  margin-bottom: 16px;
}

.generated-content :deep(.report-section p) {
  text-indent: 2em;
  line-height: 1.8;
  margin: 6px 0;
  font-size: 14px;
}

.generated-content :deep(.report-section ul) {
  margin: 8px 0;
  padding-left: 3em;
}

.generated-content :deep(.report-section li) {
  line-height: 1.8;
  font-size: 14px;
}

.generated-content :deep(.data-table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 13px;
}

.generated-content :deep(.data-table th),
.generated-content :deep(.data-table td) {
  border: 1px solid #333;
  padding: 8px;
  text-align: center;
}

.generated-content :deep(.data-table th) {
  background: #f0f0f0;
}

.generated-content :deep(.report-footer) {
  margin-top: 32px;
  text-align: right;
}

/* 操作指南 */
.guide-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.guide-step.active {
  opacity: 1;
}

.step-number {
  width: 24px;
  height: 24px;
  background: rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: var(--military-text-secondary);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.guide-step.active .step-number {
  background: var(--military-primary);
  color: #fff;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.step-desc {
  font-size: 12px;
  color: var(--military-text-secondary);
  margin-top: 2px;
}

/* 类型说明 */
.type-info {
  space-y: 12px;
}

.type-info-item {
  padding: 12px;
  background: rgba(10, 22, 40, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
}

.type-info-label {
  font-size: 12px;
  color: var(--military-primary);
  font-weight: 500;
  margin-bottom: 4px;
}

.type-info-value {
  font-size: 13px;
  color: var(--military-text-secondary);
  line-height: 1.5;
}

/* 分布条 */
.distribution-item {
  padding: 10px 12px;
  background: rgba(10, 22, 40, 0.3);
  border-radius: 8px;
}

.distribution-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.distribution-name {
  font-size: 13px;
  color: var(--military-text-primary);
}

.distribution-count {
  font-size: 12px;
  color: var(--military-text-muted);
}

.distribution-bar {
  height: 6px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.distribution-bar-fill {
  height: 100%;
  background: var(--military-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* 历史记录 */
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(10, 22, 40, 0.3);
  border-radius: 8px;
}

.history-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--military-text-primary);
}

.history-meta {
  font-size: 11px;
  color: var(--military-text-muted);
  margin-top: 2px;
}

/* 表单样式优化 */
:deep(.el-date-editor) {
  --el-fill-color-blank: rgba(10, 22, 40, 0.5);
  --el-text-color-regular: var(--military-text-primary);
  --el-border-color: rgba(59, 130, 246, 0.3);
}

:deep(.el-date-editor:hover) {
  --el-border-color: rgba(59, 130, 246, 0.5);
}

:deep(.el-date-editor.is-focus) {
  --el-border-color: var(--military-primary);
}

/* 多行输入框样式优化 */
:deep(.el-textarea__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
  color: var(--military-text-primary) !important;
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-textarea__inner:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
  background-color: rgba(10, 22, 40, 0.7) !important;
}

:deep(.el-textarea__inner:focus) {
  border-color: var(--military-primary) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-textarea__inner::placeholder) {
  color: var(--military-text-muted) !important;
  opacity: 0.7;
}

/* 单行输入框样式优化 */
:deep(.el-input__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
  color: var(--military-text-primary) !important;
  transition: all 0.3s ease;
}

:deep(.el-input__inner:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
  background-color: rgba(10, 22, 40, 0.7) !important;
}

:deep(.el-input__inner:focus) {
  border-color: var(--military-primary) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-input__inner::placeholder) {
  color: var(--military-text-muted) !important;
  opacity: 0.7;
}
</style>
