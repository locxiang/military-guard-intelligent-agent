<template>
  <div class="doc-generate-official-step1-view bg-gov-background min-h-full p-4 sm:p-6">
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">公文助手（国标格式）</h2>
        <p class="gov-card-subtitle">第一步：填写公文基本信息</p>
      </div>
    </div>

    <div class="max-w-3xl mx-auto space-y-6">
      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">选择公文类型</h3>
          <p class="gov-card-subtitle">选择您需要生成的公文类型</p>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="docType in officialTypes"
            :key="docType.value"
            class="doc-type-card"
            :class="{ 'selected': selectedType === docType.value }"
            @click="selectType(docType.value)"
          >
            <div class="flex items-start gap-3">
              <div class="doc-type-checkbox">
                <el-icon v-if="selectedType === docType.value" class="check-icon"><Check /></el-icon>
              </div>
              <div class="flex-1">
                <div class="doc-type-title">{{ docType.label }}</div>
                <div class="doc-type-desc">{{ docType.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="gov-card-title">关联案件（可选）</h3>
              <p class="gov-card-subtitle">关联案件后，系统将自动提取案件信息填入公文</p>
            </div>
          </div>
        </div>

        <el-select
          v-model="selectedCaseId"
          placeholder="请选择关联的案件（可选）"
          class="w-full gov-select"
          filterable
          clearable
          @change="handleCaseSelect"
        >
          <el-option
            v-for="caseItem in caseList"
            :key="caseItem.id"
            :label="caseItem.caseNo + ' - ' + (caseItem.caseName || caseItem.title)"
            :value="caseItem.id"
          />
        </el-select>

        <div v-if="selectedCase" class="mt-4 case-summary">
          <div class="case-summary-header">
            <span class="case-no">{{ selectedCase.caseNo }}</span>
            <el-tag size="small" type="success">已关联</el-tag>
          </div>
          <div class="case-summary-content">
            <p><strong>案件名称：</strong>{{ selectedCase.caseName || selectedCase.title }}</p>
            <p><strong>当事人：</strong>{{ selectedCase.personName }}</p>
            <p><strong>案件类型：</strong>{{ selectedCase.caseType }}</p>
          </div>
        </div>
      </div>

      <div class="gov-card">
        <div class="gov-card-header mb-4">
          <h3 class="gov-card-title">填写公文内容</h3>
          <p class="gov-card-subtitle">填写公文的核心要素</p>
        </div>

        <el-form :model="formData" :rules="formRules" ref="formRef" class="gov-form" label-position="top">
          <template v-if="selectedType === 'request'">
            <el-form-item label="主送机关" prop="recipient" class="gov-form-item">
              <el-input v-model="formData.recipient" placeholder="如：XX部门" class="gov-input" />
            </el-form-item>
            <el-form-item label="请示事由" prop="subject" class="gov-form-item">
              <el-input v-model="formData.subject" placeholder="如：关于XX事项的请示" class="gov-input" />
            </el-form-item>
            <el-form-item label="请示内容" prop="content" class="gov-form-item">
              <el-input
                v-model="formData.content"
                type="textarea"
                :rows="6"
                placeholder="详细说明请示的事项、理由及建议方案"
                class="gov-input"
              />
            </el-form-item>
            <el-form-item label="附件说明" class="gov-form-item">
              <el-input v-model="formData.attachment" placeholder="如有附件请说明（可选）" class="gov-input" />
            </el-form-item>
          </template>

          <template v-else-if="selectedType === 'report'">
            <el-form-item label="汇报对象" prop="recipient" class="gov-form-item">
              <el-input v-model="formData.recipient" placeholder="如：XX领导" class="gov-input" />
            </el-form-item>
            <el-form-item label="汇报主题" prop="subject" class="gov-form-item">
              <el-input v-model="formData.subject" placeholder="如：关于XX工作情况的汇报" class="gov-input" />
            </el-form-item>
            <el-form-item label="工作情况" prop="situation" class="gov-form-item">
              <el-input
                v-model="formData.situation"
                type="textarea"
                :rows="4"
                placeholder="概述当前工作进展情况"
                class="gov-input"
              />
            </el-form-item>
            <el-form-item label="存在问题" class="gov-form-item">
              <el-input
                v-model="formData.problems"
                type="textarea"
                :rows="3"
                placeholder="说明工作中遇到的问题和困难（可选）"
                class="gov-input"
              />
            </el-form-item>
            <el-form-item label="下步计划" class="gov-form-item">
              <el-input
                v-model="formData.plan"
                type="textarea"
                :rows="3"
                placeholder="说明下一步工作计划和措施（可选）"
                class="gov-input"
              />
            </el-form-item>
          </template>

          <template v-else-if="selectedType === 'notice'">
            <el-form-item label="发文对象" prop="recipient" class="gov-form-item">
              <el-input v-model="formData.recipient" placeholder="如：各部门、各单位" class="gov-input" />
            </el-form-item>
            <el-form-item label="通知主题" prop="subject" class="gov-form-item">
              <el-input v-model="formData.subject" placeholder="如：关于XX事项的通知" class="gov-input" />
            </el-form-item>
            <el-form-item label="通知内容" prop="content" class="gov-form-item">
              <el-input
                v-model="formData.content"
                type="textarea"
                :rows="6"
                placeholder="详细说明通知的内容和要求"
                class="gov-input"
              />
            </el-form-item>
            <el-form-item label="执行要求" class="gov-form-item">
              <el-input
                v-model="formData.requirements"
                type="textarea"
                :rows="3"
                placeholder="说明执行的时间、方式和要求（可选）"
                class="gov-input"
              />
            </el-form-item>
          </template>

          <template v-else-if="selectedType === 'memo'">
            <el-form-item label="收函单位" prop="recipient" class="gov-form-item">
              <el-input v-model="formData.recipient" placeholder="如：XX单位" class="gov-input" />
            </el-form-item>
            <el-form-item label="函件主题" prop="subject" class="gov-form-item">
              <el-input v-model="formData.subject" placeholder="如：关于XX事项的函" class="gov-input" />
            </el-form-item>
            <el-form-item label="函件内容" prop="content" class="gov-form-item">
              <el-input
                v-model="formData.content"
                type="textarea"
                :rows="6"
                placeholder="详细说明函件的内容"
                class="gov-input"
              />
            </el-form-item>
          </template>

          <template v-else>
            <div class="text-center py-8">
              <el-icon :size="48" style="color: var(--military-text-muted);"><Document /></el-icon>
              <p class="mt-4" style="color: var(--military-text-muted);">请先选择公文类型</p>
            </div>
          </template>
        </el-form>
      </div>

      <div class="gov-card">
        <div class="flex items-center justify-between">
          <button class="gov-button-default flex items-center gap-2" @click="handleReset">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </button>
          <button
            class="gov-button-primary flex items-center gap-2"
            :disabled="!canGenerate"
            @click="handleNextStep"
          >
            <span>下一步：AI 生成内容</span>
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Document, Refresh, Check, ArrowRight } from '@element-plus/icons-vue'
import { caseFileApi as archiveApi } from '@/api/archive'

const router = useRouter()

const formRef = ref<FormInstance>()
const selectedType = ref('')
const officialTypes = [
  {
    value: 'request',
    label: '请示',
    description: '向上级请求指示',
    usage: '向上级机关请求指示、批准',
    format: '标题+主送机关+正文+落款',
    notes: '请示一般只写一个主送机关，需要同时报送其他机关的可用抄送'
  },
  {
    value: 'report',
    label: '汇报',
    description: '向上级报告工作',
    usage: '向上级机关汇报工作、反映情况',
    format: '标题+主送机关+正文+落款',
    notes: '汇报应实事求是，重点突出，数据准确'
  },
  {
    value: 'notice',
    label: '通知',
    description: '传达事项通知',
    usage: '传达要求下级办理、知晓的事项',
    format: '标题+主送机关+正文+落款',
    notes: '通知的语气要明确、要求要具体'
  },
  {
    value: 'memo',
    label: '函',
    description: '平行机关往来',
    usage: '不相隶属机关之间商洽工作、询问答复',
    format: '标题+主送机关+正文+落款',
    notes: '函的语气要平和、礼貌'
  }
]

const caseList = ref<any[]>([])
const selectedCaseId = ref<number | null>(null)
const selectedCase = ref<any>(null)

const formData = reactive({
  recipient: '',
  subject: '',
  content: '',
  attachment: '',
  situation: '',
  problems: '',
  plan: '',
  requirements: ''
})

const formRules: FormRules = {
  recipient: [{ required: true, message: '请填写收文机关', trigger: 'blur' }],
  subject: [{ required: true, message: '请填写公文主题', trigger: 'blur' }]
}

const canGenerate = computed(() => {
  if (!selectedType.value) return false
  return formData.recipient && formData.subject
})

const loadDemoDataForType = (type: string) => {
  Object.keys(formData).forEach(key => {
    (formData as any)[key] = ''
  })
  if (type === 'request') {
    formData.recipient = '保卫处'
    formData.subject = '关于对张某某涉嫌盗窃一案拟立案调查的请示'
    formData.content = '我单位在近期工作中发现，战士张某某（某部三营二连，上等兵）存在涉嫌盗窃同宿舍战友财物的行为。\n\n一、简要情况\n2026年1月24日22时30分许，我连发生一起宿舍财物失窃事件。经初步调查，张某某在案发时间段行为异常，且其个人物品中发现与失窃物品相关的线索。目前已完成初步询问和证据固定。\n\n二、请示事项\n为依法依规办理此案，现拟对张某某涉嫌盗窃一案立案调查。妥否，请批示。'
    formData.attachment = '《案件线索登记表》《初步调查情况说明》'
  } else if (type === 'report') {
    formData.recipient = '部领导'
    formData.subject = '关于近期保卫工作情况的汇报'
    formData.situation = '一、工作开展情况\n本月以来，我处围绕营区安全稳定，重点开展了以下工作：一是完成春节前安全隐患排查，共检查重点部位12处，发现并整改隐患3项；二是配合上级完成涉密载体清查，未发现泄密隐患；三是受理并初查线索2件，其中1件已形成立案请示。\n\n二、案件办理进展\n张某某涉嫌盗窃一案：已完成初步调查和证据收集，拟立案材料已按程序报批，待批复后开展讯问及后续处理。'
    formData.problems = '部分单位对保卫工作配合度不够，个别隐患整改存在拖延现象。'
    formData.plan = '一是继续跟进张某某案批复及后续办理；二是开展一次全员法制教育；三是与相关单位建立定期联络机制，强化协同。'
  } else if (type === 'notice') {
    formData.recipient = '各营、直属单位'
    formData.subject = '关于加强营区门禁与外来人员管理的通知'
    formData.content = '近期发现个别单位在门禁管理、外来人员登记方面存在松懈现象。为加强营区安全管控，现就有关事项通知如下：\n\n一、严格落实门岗查验制度，所有进入营区人员必须核验身份、登记事由，车辆须查验通行证。\n\n二、外来办事人员须由对口单位派人接领，并在门岗登记接领人姓名、部门及来访事由。\n\n三、各单位于本周五前开展一次门禁与登记制度自查，发现问题及时整改，并将自查情况报保卫处。\n\n四、本通知自下发之日起执行。'
    formData.requirements = '请各单位于1月31日前将自查情况书面报保卫处；逾期未报的将予以通报。'
  } else if (type === 'memo') {
    formData.recipient = '某某单位保卫科'
    formData.subject = '关于协查张某某有关情况的函'
    formData.content = '我单位正在办理张某某涉嫌盗窃一案。据调查，张某某曾于2025年X月前往贵单位参加培训，期间是否有异常表现或与案件相关情况，需向贵单位核实。\n\n现商请贵单位协助提供以下情况：\n一、张某某在贵单位培训期间的表现及日常交往情况；\n二、是否掌握其经济状况、债务或纠纷等线索；\n三、其他与案件可能相关的情况。\n\n请贵单位在保密前提下予以支持，复函请加盖公章。'
  }
}

const selectType = (type: string) => {
  selectedType.value = type
  loadDemoDataForType(type)
}

const loadCaseList = async () => {
  try {
    const response = await archiveApi.getList({ page: 1, pageSize: 100 })
    const responseData = response as { items?: any[]; data?: { items?: any[] } }
    caseList.value = responseData.data?.items || responseData.items || (Array.isArray(response) ? response : [])
  } catch (error) {
    console.error('加载案件列表失败:', error)
  }
}

const handleCaseSelect = async (caseId: number) => {
  if (!caseId) {
    selectedCase.value = null
    return
  }

  try {
    const response = await archiveApi.getDetail(caseId)
    selectedCase.value = response.data || response
    if (selectedCase.value && selectedType.value) {
      autoFillFromCase()
    }
  } catch (error) {
    ElMessage.error('加载案件详情失败')
  }
}

const autoFillFromCase = () => {
  const caseData = selectedCase.value
  if (!caseData) return

  if (selectedType.value === 'request') {
    formData.subject = '关于' + caseData.personName + caseData.caseType + '案件处理的请示'
    formData.content = '根据' + caseData.caseNo + '号案件调查情况，' + caseData.personName + '涉嫌' + caseData.caseType + '。\n\n' + (caseData.incidentProcess || '') + '\n\n现就该案件处理问题请示如下：...'
  } else if (selectedType.value === 'report') {
    formData.subject = '关于' + caseData.personName + caseData.caseType + '案件办理情况的汇报'
    formData.situation = '案件编号：' + caseData.caseNo + '\n当事人：' + caseData.personName + '\n案件类型：' + caseData.caseType + '\n\n' + (caseData.investigationProcessAndConclusion || '')
    formData.problems = caseData.causeAndLesson || ''
  } else if (selectedType.value === 'memo') {
    formData.subject = '关于协查' + caseData.personName + caseData.caseType + '案件相关情况的函'
    formData.content = '我单位正在办理' + caseData.caseNo + '号案件，当事人' + caseData.personName + '涉嫌' + caseData.caseType + '。\n\n现需协查以下情况：...'
  }
}

const handleNextStep = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (!valid) return

    const officialData = {
      docType: selectedType.value,
      formData: { ...formData },
      selectedCase: selectedCase.value
    }
    sessionStorage.setItem('officialDocData', JSON.stringify(officialData))

    router.push({
      path: '/doc-generate/official/step2',
      query: {
        docType: selectedType.value
      }
    })
  })
}

const handleReset = () => {
  Object.keys(formData).forEach(key => {
    (formData as any)[key] = ''
  })
  selectedType.value = ''
  selectedCase.value = null
  selectedCaseId.value = null
  formRef.value?.resetFields()
}

onMounted(() => {
  loadCaseList()
  const savedData = sessionStorage.getItem('officialDocData')
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      if (data.docType) {
        selectedType.value = data.docType
        Object.assign(formData, data.formData || {})
        if (data.selectedCase) {
          selectedCase.value = data.selectedCase
        }
      }
    } catch (e) {
      console.error('恢复数据失败:', e)
    }
  }
  if (!formData.recipient && !formData.subject && !selectedType.value) {
    selectedType.value = 'request'
    loadDemoDataForType('request')
  }
})
</script>

<style scoped>
.doc-generate-official-step1-view {
  font-family: var(--font-body);
}

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

.case-summary {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 12px;
}

.case-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.case-no {
  font-weight: 600;
  color: var(--military-primary);
}

.case-summary-content p {
  font-size: 13px;
  color: var(--military-text-secondary);
  margin: 4px 0;
}

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
