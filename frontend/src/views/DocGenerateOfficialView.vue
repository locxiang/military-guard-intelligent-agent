<template>
  <div class="doc-generate-official-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">公文助手</h2>
        <p class="gov-card-subtitle">填写公文信息，AI智能辅助生成规范的公文材料</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：表单填写 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 公文类型选择 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第一步：选择公文类型</h3>
            <p class="gov-card-subtitle">选择您需要生成的公文类型</p>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
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

        <!-- 关联案件（可选） -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">第二步：关联案件（可选）</h3>
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
              :label="`${caseItem.caseNo} - ${caseItem.caseName || caseItem.title}`"
              :value="caseItem.id"
            />
          </el-select>

          <!-- 案件信息摘要 -->
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

        <!-- 公文内容填写 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第三步：填写公文内容</h3>
            <p class="gov-card-subtitle">填写公文的核心要素，系统将生成规范的公文格式</p>
          </div>

          <el-form :model="formData" :rules="formRules" ref="formRef" class="gov-form" label-position="top">
            <!-- 根据公文类型显示不同的表单 -->
            <template v-if="selectedType === 'request'">
              <!-- 请示表单 -->
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
              <!-- 汇报表单 -->
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
              <!-- 通知表单 -->
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
              <!-- 函表单 -->
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
              <!-- 默认提示 -->
              <div class="text-center py-8">
                <el-icon :size="48" style="color: var(--military-text-muted);"><Document /></el-icon>
                <p class="mt-4" style="color: var(--military-text-muted);">请先选择公文类型</p>
              </div>
            </template>
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
                <div class="step-title">选择公文类型</div>
                <div class="step-desc">选择需要生成的公文类型</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 2 }">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-title">关联案件（可选）</div>
                <div class="step-desc">可选择相关案件作为参考</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 3 }">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-title">填写公文内容</div>
                <div class="step-desc">填写公文的核心要素</div>
              </div>
            </div>
            <div class="guide-step" :class="{ 'active': currentStep >= 4 }">
              <div class="step-number">4</div>
              <div class="step-content">
                <div class="step-title">AI智能生成</div>
                <div class="step-desc">点击生成，AI将自动生成公文</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前公文类型说明 -->
        <div v-if="selectedType" class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">{{ currentTypeInfo?.label }}说明</h3>
          </div>
          <div class="type-info">
            <div class="type-info-item">
              <div class="type-info-label">适用场景</div>
              <div class="type-info-value">{{ currentTypeInfo?.usage }}</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">格式要点</div>
              <div class="type-info-value">{{ currentTypeInfo?.format }}</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">注意事项</div>
              <div class="type-info-value">{{ currentTypeInfo?.notes }}</div>
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
              <span>关联案件后，系统会自动提取相关信息填入公文</span>
            </div>
            <div class="tip-item">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>填写内容越详细，生成的公文质量越高</span>
            </div>
            <div class="tip-item">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>生成的内容仅供参考，请务必人工审核后使用</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  InfoFilled, Document, Refresh, MagicStick, Check
} from '@element-plus/icons-vue'
import { caseFileApi as archiveApi } from '@/api/archive'

const router = useRouter()

// 表单引用
const formRef = ref<FormInstance>()

// 公文类型
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

// 当前类型信息
const currentTypeInfo = computed(() => {
  return officialTypes.find(t => t.value === selectedType.value)
})

// 关联案件
const caseList = ref<any[]>([])
const selectedCaseId = ref<number | null>(null)
const selectedCase = ref<any>(null)

// 表单数据
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

// 表单验证规则
const formRules: FormRules = {
  recipient: [{ required: true, message: '请填写收文机关', trigger: 'blur' }],
  subject: [{ required: true, message: '请填写公文主题', trigger: 'blur' }],
  content: [{ required: true, message: '请填写公文内容', trigger: 'blur' }],
  situation: [{ required: true, message: '请填写工作情况', trigger: 'blur' }]
}

// 当前步骤
const currentStep = computed(() => {
  if (selectedCaseId.value) return 2
  if (selectedType.value && (formData.recipient || formData.subject)) return 3
  if (selectedType.value) return 1
  return 0
})

// 是否可以生成
const canGenerate = computed(() => {
  if (!selectedType.value) return false
  if (selectedType.value === 'request') {
    return formData.recipient && formData.subject && formData.content
  }
  if (selectedType.value === 'report') {
    return formData.recipient && formData.subject && formData.situation
  }
  if (selectedType.value === 'notice') {
    return formData.recipient && formData.subject && formData.content
  }
  if (selectedType.value === 'memo') {
    return formData.recipient && formData.subject && formData.content
  }
  return false
})

// 按公文类型加载演示数据（方便演示，避免录入）
const loadDemoDataForType = (type: string) => {
  Object.keys(formData).forEach(key => {
    (formData as any)[key] = ''
  })
  if (type === 'request') {
    // 请示
    formData.recipient = '保卫处'
    formData.subject = '关于对张某某涉嫌盗窃一案拟立案调查的请示'
    formData.content = `我单位在近期工作中发现，战士张某某（某部三营二连，上等兵）存在涉嫌盗窃同宿舍战友财物的行为。

一、简要情况
2026年1月24日22时30分许，我连发生一起宿舍财物失窃事件。经初步调查，张某某在案发时间段行为异常，且其个人物品中发现与失窃物品相关的线索。目前已完成初步询问和证据固定。

二、请示事项
为依法依规办理此案，现拟对张某某涉嫌盗窃一案立案调查。妥否，请批示。`
    formData.attachment = '《案件线索登记表》《初步调查情况说明》'
  } else if (type === 'report') {
    // 汇报
    formData.recipient = '部领导'
    formData.subject = '关于近期保卫工作情况的汇报'
    formData.situation = `一、工作开展情况
本月以来，我处围绕营区安全稳定，重点开展了以下工作：一是完成春节前安全隐患排查，共检查重点部位12处，发现并整改隐患3项；二是配合上级完成涉密载体清查，未发现泄密隐患；三是受理并初查线索2件，其中1件已形成立案请示。

二、案件办理进展
张某某涉嫌盗窃一案：已完成初步调查和证据收集，拟立案材料已按程序报批，待批复后开展讯问及后续处理。`
    formData.problems = '部分单位对保卫工作配合度不够，个别隐患整改存在拖延现象。'
    formData.plan = '一是继续跟进张某某案批复及后续办理；二是开展一次全员法制教育；三是与相关单位建立定期联络机制，强化协同。'
  } else if (type === 'notice') {
    // 通知
    formData.recipient = '各营、直属单位'
    formData.subject = '关于加强营区门禁与外来人员管理的通知'
    formData.content = `近期发现个别单位在门禁管理、外来人员登记方面存在松懈现象。为加强营区安全管控，现就有关事项通知如下：

一、严格落实门岗查验制度，所有进入营区人员必须核验身份、登记事由，车辆须查验通行证。

二、外来办事人员须由对口单位派人接领，并在门岗登记接领人姓名、部门及来访事由。

三、各单位于本周五前开展一次门禁与登记制度自查，发现问题及时整改，并将自查情况报保卫处。

四、本通知自下发之日起执行。`
    formData.requirements = '请各单位于1月31日前将自查情况书面报保卫处；逾期未报的将予以通报。'
  } else if (type === 'memo') {
    // 函
    formData.recipient = '某某单位保卫科'
    formData.subject = '关于协查张某某有关情况的函'
    formData.content = `我单位正在办理张某某涉嫌盗窃一案。据调查，张某某曾于2025年X月前往贵单位参加培训，期间是否有异常表现或与案件相关情况，需向贵单位核实。

现商请贵单位协助提供以下情况：
一、张某某在贵单位培训期间的表现及日常交往情况；
二、是否掌握其经济状况、债务或纠纷等线索；
三、其他与案件可能相关的情况。

请贵单位在保密前提下予以支持，复函请加盖公章。`
  }
}

// 选择公文类型
const selectType = (type: string) => {
  selectedType.value = type
  // 重置后加载该类型的演示数据，方便演示
  loadDemoDataForType(type)
}

// 加载案件列表
const loadCaseList = async () => {
  try {
    const response = await archiveApi.getList({ page: 1, pageSize: 100 })
    const responseData = response as { items?: any[]; data?: { items?: any[] } }
    caseList.value = responseData.data?.items || responseData.items || (Array.isArray(response) ? response : [])
  } catch (error) {
    console.error('加载案件列表失败:', error)
  }
}

// 选择案件
const handleCaseSelect = async (caseId: number) => {
  if (!caseId) {
    selectedCase.value = null
    return
  }
  
  try {
    const response = await archiveApi.getDetail(caseId)
    selectedCase.value = response.data || response
    // 自动填充相关信息
    if (selectedCase.value && selectedType.value) {
      autoFillFromCase()
    }
  } catch (error) {
    ElMessage.error('加载案件详情失败')
  }
}

// 从案件自动填充
const autoFillFromCase = () => {
  const caseData = selectedCase.value
  if (!caseData) return

  if (selectedType.value === 'request') {
    formData.subject = `关于${caseData.personName}${caseData.caseType}案件处理的请示`
    formData.content = `根据${caseData.caseNo}号案件调查情况，${caseData.personName}涉嫌${caseData.caseType}。\n\n${caseData.incidentProcess || ''}\n\n现就该案件处理问题请示如下：...`
  } else if (selectedType.value === 'report') {
    formData.subject = `关于${caseData.personName}${caseData.caseType}案件办理情况的汇报`
    formData.situation = `案件编号：${caseData.caseNo}\n当事人：${caseData.personName}\n案件类型：${caseData.caseType}\n\n${caseData.investigationProcessAndConclusion || ''}`
    formData.problems = caseData.causeAndLesson || ''
  } else if (selectedType.value === 'memo') {
    formData.subject = `关于协查${caseData.personName}${caseData.caseType}案件相关情况的函`
    formData.content = `我单位正在办理${caseData.caseNo}号案件，当事人${caseData.personName}涉嫌${caseData.caseType}。\n\n现需协查以下情况：...`
  }
}

// 生成公文
const handleGenerate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // 保存表单数据到 sessionStorage
      const officialData = {
        type: selectedType.value,
        formData: { ...formData },
        selectedCase: selectedCase.value
      }
      sessionStorage.setItem('officialData', JSON.stringify(officialData))
      
      // 跳转到生成结果页面
      router.push({
        path: '/doc-generate/official/result',
        query: {
          docType: selectedType.value
        }
      })
    }
  })
}

// 重置表单
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
  // 若尚未填写任何内容，则默认选中「请示」并加载该类型演示数据，方便演示
  if (!formData.recipient && !formData.subject) {
    selectedType.value = 'request'
    loadDemoDataForType('request')
  }
})
</script>

<style scoped>
.doc-generate-official-view {
  font-family: var(--font-body);
}

/* 公文类型卡片 */
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

/* 案件摘要 */
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
