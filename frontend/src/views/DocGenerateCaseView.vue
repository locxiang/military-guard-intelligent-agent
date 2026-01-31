<template>
  <div class="doc-generate-case-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">案件卷宗生成</h2>
        <p class="gov-card-subtitle">填写案件线索信息，AI智能辅助生成标准化的卷宗文书</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：信息填写与生成 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 案件线索信息 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第一步：填写案件线索信息</h3>
            <p class="gov-card-subtitle">请填写案件的基本信息，越详细生成的内容越准确</p>
          </div>

          <el-form :model="caseInfo" ref="formRef" class="gov-form" label-position="top">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <el-form-item label="案发时间" prop="incidentTime" class="gov-form-item">
                <el-date-picker
                  v-model="caseInfo.incidentTime"
                  type="datetime"
                  placeholder="选择案发时间"
                  class="w-full"
                  format="YYYY-MM-DD HH:mm"
                  value-format="YYYY-MM-DD HH:mm"
                />
              </el-form-item>
              <el-form-item label="案件类型" prop="caseType" class="gov-form-item">
                <el-select v-model="caseInfo.caseType" placeholder="选择案件类型" class="w-full gov-select">
                  <el-option label="盗窃案" value="盗窃罪" />
                  <el-option label="诈骗案" value="诈骗罪" />
                  <el-option label="故意伤害案" value="故意伤害罪" />
                  <el-option label="职务侵占案" value="职务侵占罪" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </el-form-item>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <el-form-item label="涉案人员姓名" prop="personName" class="gov-form-item">
                <el-input v-model="caseInfo.personName" placeholder="请输入涉案人员姓名" class="gov-input" />
              </el-form-item>
              <el-form-item label="所属单位" prop="department" class="gov-form-item">
                <el-input v-model="caseInfo.department" placeholder="请输入所属单位" class="gov-input" />
              </el-form-item>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <el-form-item label="性别" class="gov-form-item">
                <el-select v-model="caseInfo.gender" placeholder="选择性别" class="w-full gov-select">
                  <el-option label="男" value="男" />
                  <el-option label="女" value="女" />
                </el-select>
              </el-form-item>
              <el-form-item label="职务/职级" class="gov-form-item">
                <el-input v-model="caseInfo.position" placeholder="如：某连战士" class="gov-input" />
              </el-form-item>
              <el-form-item label="入伍时间" class="gov-form-item">
                <el-date-picker
                  v-model="caseInfo.enlistmentTime"
                  type="date"
                  placeholder="选择入伍时间"
                  class="w-full"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </div>

            <el-form-item label="事发经过" prop="incidentProcess" class="gov-form-item">
              <el-input
                v-model="caseInfo.incidentProcess"
                type="textarea"
                :rows="4"
                placeholder="请详细描述事发经过，包括时间、地点、人物、事件起因、经过、结果等"
                class="gov-input"
              />
            </el-form-item>

            <el-form-item label="初步调查情况" class="gov-form-item">
              <el-input
                v-model="caseInfo.investigation"
                type="textarea"
                :rows="3"
                placeholder="请描述已掌握的调查情况、证据线索等（可选）"
                class="gov-input"
              />
            </el-form-item>
          </el-form>
        </div>

        <!-- 文书类型选择 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第二步：选择要生成的文书</h3>
            <p class="gov-card-subtitle">选择需要AI辅助生成的卷宗文书类型</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="docType in documentTypes"
              :key="docType.value"
              class="doc-type-card"
              :class="{ 'selected': selectedDocType === docType.value }"
              @click="selectedDocType = docType.value"
            >
              <div class="flex items-start gap-3">
                <div class="doc-type-checkbox">
                  <el-icon v-if="selectedDocType === docType.value" class="check-icon"><Check /></el-icon>
                </div>
                <div class="flex-1">
                  <div class="doc-type-title">{{ docType.label }}</div>
                  <div class="doc-type-desc">{{ docType.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 关联卷宗 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">第三步：关联参考卷宗（可选）</h3>
                <p class="gov-card-subtitle">关联已有案件作为参考，提高生成质量</p>
              </div>
            </div>
          </div>

          <el-select
            v-model="relatedCaseIds"
            multiple
            filterable
            placeholder="选择相关案件作为参考（可多选）"
            class="w-full gov-select"
          >
            <el-option
              v-for="caseItem in caseList"
              :key="caseItem.id"
              :label="`${caseItem.caseNo} - ${caseItem.caseName || caseItem.title}`"
              :value="caseItem.id"
            />
          </el-select>

          <div v-if="relatedCaseIds.length > 0" class="mt-4 space-y-2">
            <div
              v-for="caseId in relatedCaseIds"
              :key="caseId"
              class="related-case-tag"
            >
              <span class="case-tag-text">{{ getCaseName(caseId) }}</span>
              <el-icon class="case-tag-remove" @click="removeRelatedCase(caseId)"><Close /></el-icon>
            </div>
          </div>
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

      <!-- 右侧：操作指南与提示 -->
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
                <div class="step-title">填写案件线索</div>
                <div class="step-desc">填写案发时间、涉案人员、事发经过等基本信息</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 2 }">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-title">选择文书类型</div>
                <div class="step-desc">选择需要生成的卷宗文书类型</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 3 }">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-title">关联参考案件</div>
                <div class="step-desc">可选择相似案件作为参考</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 4 }">
              <div class="step-number">4</div>
              <div class="step-content">
                <div class="step-title">AI智能生成</div>
                <div class="step-desc">点击生成，AI将自动生成文书内容</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 填写提示 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">填写提示</h3>
          </div>
          <div class="tips-content">
            <div class="tip-item">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>事发经过描述越详细，生成的文书内容越准确</span>
            </div>
            <div class="tip-item">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>关联相似案件可以帮助AI更好地理解案件背景</span>
            </div>
            <div class="tip-item">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>生成的内容仅供参考，请务必人工审核后使用</span>
            </div>
          </div>
        </div>

        <!-- 最近生成记录 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">最近生成记录</h3>
          </div>
          <div v-if="recentRecords.length > 0" class="space-y-3">
            <div
              v-for="record in recentRecords"
              :key="record.id"
              class="record-item"
            >
              <div class="record-info">
                <div class="record-title">{{ record.docType }}</div>
                <div class="record-case">{{ record.personName }} · {{ record.caseType }}</div>
                <div class="record-time">{{ record.time }}</div>
              </div>
              <el-tag type="success" size="small" class="record-tag">已完成</el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无生成记录" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  InfoFilled, Check, Close,
  MagicStick, Refresh
} from '@element-plus/icons-vue'
import { caseFileApi as archiveApi } from '@/api/archive'

const router = useRouter()

// 表单引用
const formRef = ref()

// 案件线索信息
const caseInfo = reactive({
  incidentTime: '',
  caseType: '',
  personName: '',
  department: '',
  gender: '',
  position: '',
  enlistmentTime: '',
  incidentProcess: '',
  investigation: ''
})

// 文书类型
const selectedDocType = ref('')
const documentTypes = [
  {
    value: 'case_report',
    label: '立案报告',
    description: '用于案件立案时的正式报告文书'
  },
  {
    value: 'investigation_report',
    label: '调查报告',
    description: '案件调查结束后的调查结论报告'
  },
  {
    value: 'interrogation_outline',
    label: '讯问笔录提纲',
    description: '用于讯问嫌疑人时的问题提纲'
  },
  {
    value: 'case_summary',
    label: '案件处理意见',
    description: '案件处理的建议和意见文书'
  }
]

// 关联卷宗
const caseList = ref<any[]>([])
const relatedCaseIds = ref<number[]>([])

// 最近记录
const recentRecords = ref<any[]>([])

// 当前步骤
const currentStep = computed(() => {
  if (relatedCaseIds.value.length > 0) return 3
  if (selectedDocType.value) return 2
  if (caseInfo.personName || caseInfo.incidentProcess) return 1
  return 0
})

// 是否可以生成
const canGenerate = computed(() => {
  return caseInfo.personName && 
         caseInfo.incidentProcess && 
         selectedDocType.value
})

// 加载案件列表
const loadCaseList = async () => {
  try {
    const response = await archiveApi.getList({ page: 1, pageSize: 100 })
    // 处理不同的返回格式
    const responseData = response as { items?: any[]; data?: { items?: any[] } }
    caseList.value = responseData.data?.items || responseData.items || (Array.isArray(response) ? response : [])
  } catch (error: any) {
    console.error('加载案件列表失败:', error)
    // 不显示错误消息，避免干扰用户操作
    // 如果确实需要，可以显示一个警告
    if (error?.response?.status === 500) {
      console.warn('案件列表加载失败，可能是数据库连接问题')
    }
  }
}

// 获取案件名称
const getCaseName = (caseId: number) => {
  const caseItem = caseList.value.find(c => c.id === caseId)
  return caseItem ? `${caseItem.caseNo} - ${caseItem.caseName || caseItem.title}` : ''
}

// 移除关联案件
const removeRelatedCase = (caseId: number) => {
  relatedCaseIds.value = relatedCaseIds.value.filter(id => id !== caseId)
}

// AI生成文书
const handleGenerate = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请填写必要的案件信息')
    return
  }

  // 保存案件信息到 sessionStorage
  sessionStorage.setItem('caseInfo', JSON.stringify(caseInfo))
  
  // 添加到记录
  addToRecentRecords()
  
  // 跳转到生成结果页面
  router.push({
    path: '/doc-generate/case/result',
    query: {
      docType: selectedDocType.value
    }
  })
}

// 添加到最近记录
const addToRecentRecords = () => {
  const docTypeLabel = documentTypes.find(d => d.value === selectedDocType.value)?.label || ''
  recentRecords.value.unshift({
    id: Date.now(),
    docType: docTypeLabel,
    personName: caseInfo.personName,
    caseType: caseInfo.caseType,
    time: new Date().toLocaleString('zh-CN')
  })
  if (recentRecords.value.length > 5) {
    recentRecords.value = recentRecords.value.slice(0, 5)
  }
}

// 加载演示数据
const loadDemoData = () => {
  // 检查是否已经填写过数据，如果已填写则不加载演示数据
  if (caseInfo.personName || caseInfo.incidentProcess) {
    return
  }
  
  // 设置拟真的演示数据
  const now = new Date()
  // 案发时间：7天前的晚上22:30
  const incidentDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  incidentDate.setHours(22, 30, 0, 0)
  // 入伍时间：3年前的1月1日
  const enlistmentDate = new Date(now.getFullYear() - 3, 0, 1)
  
  // 格式化日期时间
  const formatDateTime = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }
  
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  Object.assign(caseInfo, {
    incidentTime: formatDateTime(incidentDate),
    caseType: '盗窃罪',
    personName: '张某某',
    department: '某部三营二连',
    gender: '男',
    position: '上等兵',
    enlistmentTime: formatDate(enlistmentDate),
    incidentProcess: `2026年1月24日晚上22时30分许，我单位接到报案，称营区宿舍内发生财物失窃事件。

经初步了解，案发地点位于三营二连宿舍楼3楼305房间。失窃物品包括：现金人民币800元、一部华为手机（价值约2000元）、一条金项链（价值约3000元）。

据同宿舍战士反映，案发时间段（22:00-22:30）内，张某某曾独自在宿舍内，且行为异常。经调取监控录像发现，张某某在22:15分左右离开宿舍，手中持有可疑物品。

案发后，张某某情绪紧张，对失窃事件表现出异常关注，多次询问案件调查进展。`,
    investigation: `1. 已调取案发时间段宿舍楼监控录像，发现张某某在案发时间段有异常行为。

2. 对张某某个人物品进行检查，在其储物柜中发现与失窃手机型号相同的手机包装盒。

3. 询问同宿舍其他战士，均反映张某某近期经济状况紧张，曾向多人借钱未还。

4. 对案发现场进行勘验，发现305房间门锁完好，无撬动痕迹，初步判断为内部人员作案。

5. 已对张某某进行初步询问，其否认参与盗窃，但无法合理解释案发时间段的行为。`
  })
}

// 重置
const handleReset = () => {
  Object.keys(caseInfo).forEach(key => {
    (caseInfo as any)[key] = ''
  })
  selectedDocType.value = ''
  relatedCaseIds.value = []
}

onMounted(() => {
  loadCaseList()
  // 加载演示数据
  loadDemoData()
})
</script>

<style scoped>
.doc-generate-case-view {
  font-family: var(--font-body);
}

/* 文书类型卡片 */
.doc-type-card {
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.doc-type-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.doc-type-card.selected {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.15);
}

.doc-type-checkbox {
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

.doc-type-card.selected .doc-type-checkbox {
  background: var(--military-primary);
  border-color: var(--military-primary);
}

.check-icon {
  color: #fff;
  font-size: 14px;
}

.doc-type-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
  margin-bottom: 4px;
}

.doc-type-desc {
  font-size: 12px;
  color: var(--military-text-secondary);
  line-height: 1.4;
}

/* 关联案件标签 */
.related-case-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  padding: 6px 12px;
  margin-right: 8px;
}

.case-tag-text {
  font-size: 13px;
  color: var(--military-text-primary);
}

.case-tag-remove {
  cursor: pointer;
  color: var(--military-text-secondary);
  transition: color 0.2s;
}

.case-tag-remove:hover {
  color: #ef4444;
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

/* 提示内容 */
.tips-content {
  space-y: 12px;
}

.tip-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 10px 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  margin-bottom: 8px;
}

.tip-icon {
  color: var(--military-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.tip-item span {
  font-size: 13px;
  color: var(--military-text-secondary);
  line-height: 1.5;
}

/* 记录项 */
.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(10, 22, 40, 0.3);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 8px;
}

.record-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--military-text-primary);
}

.record-case {
  font-size: 12px;
  color: var(--military-text-secondary);
  margin-top: 2px;
}

.record-time {
  font-size: 11px;
  color: var(--military-text-muted);
  margin-top: 4px;
}

.record-tag {
  flex-shrink: 0;
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

/* 输入框标签样式 */
:deep(.gov-input-label) {
  color: var(--military-text-primary);
  font-weight: 500;
  margin-bottom: 8px;
  display: block;
}
</style>
