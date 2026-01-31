<template>
  <div class="doc-generate-meeting-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">会议纪要生成</h2>
        <p class="gov-card-subtitle">通过会议录音或文字随记，一键生成标准会议纪要</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">功能说明</span>
        <el-tooltip
          content="支持两种方式：一是现场或会后录入会议要点（文字随记）；二是上传会议录音，系统将转成文字后生成纪要。生成内容仅供参考，请人工审核后使用。"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：录入与生成 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 第一步：选择输入方式 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第一步：选择录入方式</h3>
            <p class="gov-card-subtitle">根据您手头的材料选择一种方式</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              class="input-mode-card"
              :class="{ selected: inputMode === 'text' }"
              @click="inputMode = 'text'"
            >
              <div class="flex items-start gap-3">
                <div class="mode-checkbox">
                  <el-icon v-if="inputMode === 'text'" class="check-icon"><Check /></el-icon>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-icon :size="20" class="mode-icon"><EditPen /></el-icon>
                    <span class="mode-title">文字随记</span>
                  </div>
                  <p class="mode-desc">会后或会中录入的会议要点、讨论内容、决议等文字</p>
                </div>
              </div>
            </div>
            <div
              class="input-mode-card"
              :class="{ selected: inputMode === 'recording' }"
              @click="inputMode = 'recording'"
            >
              <div class="flex items-start gap-3">
                <div class="mode-checkbox">
                  <el-icon v-if="inputMode === 'recording'" class="check-icon"><Check /></el-icon>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-icon :size="20" class="mode-icon"><Microphone /></el-icon>
                    <span class="mode-title">录音</span>
                  </div>
                  <p class="mode-desc">上传会议录音文件，系统转成文字后生成纪要（或粘贴已有转写稿）</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二步：会议基本信息（可选） -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第二步：会议基本信息（可选）</h3>
            <p class="gov-card-subtitle">填写后生成的纪要将更规范</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="gov-input-label">会议主题</label>
              <el-input
                v-model="meetingTitle"
                placeholder="如：第一季度安全工作部署会"
                class="gov-input"
              />
            </div>
            <div>
              <label class="gov-input-label">会议时间</label>
              <el-input
                v-model="meetingTime"
                placeholder="如：2026年1月15日 14:00"
                class="gov-input"
              />
            </div>
          </div>
        </div>

        <!-- 第三步：会议内容 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">
              {{ inputMode === 'text' ? '第三步：填写会议随记' : '第三步：上传录音或粘贴转写稿' }}
            </h3>
            <p class="gov-card-subtitle">
              {{ inputMode === 'text'
                ? '请尽量按议题、讨论要点、决议等分段填写，便于生成规范纪要'
                : '上传会议录音（将自动转写），或直接粘贴已有的转写文字'
              }}
            </p>
          </div>

          <!-- 文字随记 -->
          <template v-if="inputMode === 'text'">
            <el-input
              v-model="meetingNotes"
              type="textarea"
              :rows="12"
              placeholder="请录入会议要点，例如：&#10;&#10;议题一：第一季度安全工作部署&#10;张主任：强调门禁与外来人员登记……&#10;李科长：各科室下周前提交隐患排查表。&#10;&#10;议题二：……&#10;议定：……"
              class="gov-input"
            />
          </template>

          <!-- 录音：上传区 + 转写稿粘贴 -->
          <template v-else>
            <div class="recording-upload-tip">
              <el-icon class="tip-icon"><InfoFilled /></el-icon>
              <span>上传录音后系统将自动转成文字并生成纪要；若您已通过其他方式获得转写稿，可直接粘贴在下方框中。</span>
            </div>
            <div class="mt-4">
              <el-upload
                class="recording-upload gov-upload-area"
                drag
                :auto-upload="false"
                :show-file-list="true"
                :on-change="handleRecordingFileChange"
                accept="audio/*,.mp3,.wav,.m4a"
              >
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">将会议录音文件拖到此处，或<em>点击选择</em></div>
                <template #tip>
                  <div class="upload-tip">支持 mp3、wav、m4a 等常见格式，单文件建议 100MB 以内</div>
                </template>
              </el-upload>
            </div>
            <div class="mt-4">
              <label class="gov-input-label">或直接粘贴转写稿（若已有）</label>
              <el-input
                v-model="meetingTranscript"
                type="textarea"
                :rows="8"
                placeholder="若您已有会议录音的转写文字，可粘贴在此处，然后点击下方「生成会议纪要」。"
                class="gov-input"
              />
            </div>
          </template>
        </div>

        <!-- 生成按钮 -->
        <div class="gov-card">
          <div class="flex flex-wrap items-center gap-4">
            <button
              class="gov-button-primary flex items-center gap-2"
              :disabled="!canGenerate"
              @click="handleGenerate"
            >
              <el-icon><MagicStick /></el-icon>
              <span>生成会议纪要</span>
            </button>
            <button class="gov-button-default flex items-center gap-2" @click="loadDemoData">
              <el-icon><Document /></el-icon>
              <span>使用示例数据</span>
            </button>
            <button class="gov-button-default flex items-center gap-2" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>清空</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：操作指南 -->
      <div class="space-y-6">
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">操作指南</h3>
          </div>
          <div class="space-y-3">
            <div class="guide-step" :class="{ active: currentStep >= 1 }">
              <div class="step-number">1</div>
              <div class="step-content">
                <div class="step-title">选择录入方式</div>
                <div class="step-desc">文字随记或录音（含转写稿粘贴）</div>
              </div>
            </div>
            <div class="guide-step" :class="{ active: currentStep >= 2 }">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-title">填写会议信息</div>
                <div class="step-desc">主题、时间可选，便于生成规范纪要</div>
              </div>
            </div>
            <div class="guide-step" :class="{ active: currentStep >= 3 }">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-title">录入会议内容</div>
                <div class="step-desc">随记或录音/转写稿</div>
              </div>
            </div>
            <div class="guide-step" :class="{ active: currentStep >= 4 }">
              <div class="step-number">4</div>
              <div class="step-content">
                <div class="step-title">生成会议纪要</div>
                <div class="step-desc">AI 将整理成标准会议报告</div>
              </div>
            </div>
          </div>
        </div>

        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">纪要结构说明</h3>
          </div>
          <div class="type-info">
            <div class="type-info-item">
              <div class="type-info-label">包含内容</div>
              <div class="type-info-value">会议基本信息（时间、参会人员、主持）、议题与讨论、议定事项、待办与分工等。</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">使用建议</div>
              <div class="type-info-value">生成内容仅供参考，请根据单位规定模板人工核对、修改后使用。</div>
            </div>
          </div>
        </div>

        <!-- 示例场景快捷加载 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">示例场景</h3>
            <p class="gov-card-subtitle">一键加载演示数据，快速体验</p>
          </div>
          <div class="space-y-2">
            <button
              class="demo-scenario-btn"
              :class="{ active: currentDemoScenario === 'safety' }"
              @click="loadDemoScenario('safety')"
            >
              <span class="demo-title">安全工作部署会</span>
              <span class="demo-desc">第一季度隐患排查、门禁管理等</span>
            </button>
            <button
              class="demo-scenario-btn"
              :class="{ active: currentDemoScenario === 'case' }"
              @click="loadDemoScenario('case')"
            >
              <span class="demo-title">案件研判会</span>
              <span class="demo-desc">线索初查、立案讨论</span>
            </button>
            <button
              class="demo-scenario-btn"
              :class="{ active: currentDemoScenario === 'education' }"
              @click="loadDemoScenario('education')"
            >
              <span class="demo-title">法制教育动员会</span>
              <span class="demo-desc">全员学法、警示教育安排</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Check, EditPen, Microphone, InfoFilled, MagicStick, Refresh, UploadFilled, Document } from '@element-plus/icons-vue'

const router = useRouter()

// 录入方式：文字随记 / 录音（上传或粘贴转写稿）
const inputMode = ref<'text' | 'recording'>('text')
const meetingTitle = ref('')
const meetingTime = ref('')
const meetingNotes = ref('')
const meetingTranscript = ref('')
const recordingFile = ref<File | null>(null)
const currentDemoScenario = ref<string | null>(null)

// 拟真示例数据：按场景
const demoScenarios = {
  safety: {
    title: '保卫处2026年第一季度安全工作部署会',
    time: '2026年1月15日 14:30',
    textNotes: `议题一：第一季度安全工作部署

张主任：强调春节前后门禁与外来人员登记必须严格，各科室下周前提交隐患排查表；涉密载体清查已完成，未发现泄密隐患。

李科长：门岗已加装监控，建议各科室明确专人负责保卫联络。

王干事：本周已完成12处重点部位检查，发现3项隐患已整改。

议题二：近期案件情况通报

张主任：受理线索2件，张某某涉嫌盗窃一案已形成立案请示并报批；另一起纠纷类线索正在初查。

议定事项：
1. 各科室1月20日前完成隐患自查并报保卫处
2. 春节前开展一次全员法制教育
3. 建立保卫工作定期联络机制`,
    transcript: `张主任：好，人齐了，咱们开始。今天主要两项议题，一是第一季度安全工作部署，二是近期案件情况通报。先说一下安全工作。

李科长，你先说说门禁这块。李科长：门岗监控已经加上了，现在进出都有记录。建议各科室明确一个保卫联络员，有事好对接。张主任：可以，各科室下周前报一下联络人名单。

王干事，排查情况怎么样？王干事：本周跑了12处重点部位，发现3个隐患都已经整改了。涉密载体清查也做完了，没发现问题。张主任：好，各科室自己也要查一遍，1月20日前把自查表交上来。

第二项，案件情况。最近受理了两件线索，张某某涉嫌盗窃那件已经形成立案请示，等批复。另一件纠纷类的还在初查。大家盯紧一点。

最后议定：各科室20日前完成隐患自查；春节前搞一次法制教育；建立保卫联络机制。散会。`
  },
  case: {
    title: '张某某涉嫌盗窃一案研判会',
    time: '2026年1月12日 10:00',
    textNotes: `议题：张某某涉嫌盗窃一案是否立案

案情概要：2025年12月底，某单位仓库物资丢失，经初查系张某某（本单位职工）所为，涉案金额约8000元。

李科长：初查材料已形成，证据链完整，建议立案。

王干事：已与法制部门沟通，符合立案标准。

张主任：同意立案，按程序报批。注意做好保密和后续调查。`,
    transcript: `张主任：今天开个研判会，讨论张某某涉嫌盗窃那件事，看能不能立案。李科长你先说一下。

李科长：初查做完了，材料都齐了。12月底仓库丢的那批物资，查下来是张某某拿的，金额大概八千左右。证据链是完整的，我建议立案。

王干事：我跟法制那边也沟通过，符合立案标准，可以走程序。

张主任：行，那就定立案。按程序报批，注意保密，后续调查要跟上。散会。`
  },
  education: {
    title: '保卫处2026年度法制教育动员会',
    time: '2026年1月8日 15:00',
    textNotes: `议题：年度法制教育与警示教育安排

张主任：上级要求各单位开展全员学法，结合近期涉法案件，开展警示教育。

李科长：拟安排2月开展专题学习，邀请法律顾问授课；3月组织参观警示教育基地。

王干事：需各科室配合统计参训人员，落实签到。

议定：2月中旬法制讲座，3月警示教育参观，各科室于1月底前上报参训名单。`,
    transcript: `张主任：今天布置一下今年的法制教育工作。上级有要求，全员都要学法，结合最近几起涉法案件，搞警示教育。

李科长：我们计划2月份搞一场法制讲座，请法律顾问来讲。3月份组织去警示教育基地参观。张主任：可以，时间抓紧定。

王干事：需要各科室配合报一下参训人员，到时候要签到。张主任：对，各科室1月底前把名单报上来。那就这么定了，2月中旬讲座，3月参观，散会。`
  }
} as const

const currentStep = computed(() => {
  const hasContent = inputMode.value === 'text'
    ? !!meetingNotes.value?.trim()
    : !!meetingTranscript.value?.trim() || !!recordingFile.value
  if (hasContent && (meetingTitle.value || meetingTime.value)) return 3
  if (hasContent) return 2
  if (inputMode.value) return 1
  return 0
})

const canGenerate = computed(() => {
  if (inputMode.value === 'text') return !!meetingNotes.value?.trim()
  return !!meetingTranscript.value?.trim()
})

function handleRecordingFileChange(file: { raw?: File }) {
  if (file?.raw) {
    recordingFile.value = file.raw
  }
}

// 加载示例场景（文字随记 / 录音转写稿 共用）
function loadDemoScenario(scenario: keyof typeof demoScenarios) {
  currentDemoScenario.value = scenario
  const d = demoScenarios[scenario]
  meetingTitle.value = d.title
  meetingTime.value = d.time
  if (inputMode.value === 'text') {
    meetingNotes.value = d.textNotes
    meetingTranscript.value = ''
  } else {
    meetingTranscript.value = d.transcript
    meetingNotes.value = ''
  }
}

// 加载当前录入方式的示例数据（通用示例）
function loadDemoData() {
  currentDemoScenario.value = null
  const d = demoScenarios.safety
  meetingTitle.value = d.title
  meetingTime.value = d.time
  if (inputMode.value === 'text') {
    meetingNotes.value = d.textNotes
    meetingTranscript.value = ''
  } else {
    meetingTranscript.value = d.transcript
    meetingNotes.value = ''
  }
}

function handleGenerate() {
  const sourceText = inputMode.value === 'text' ? meetingNotes.value?.trim() : meetingTranscript.value?.trim()
  if (!sourceText) return

  const meetingData = {
    input_type: inputMode.value,
    meeting_notes: inputMode.value === 'text' ? sourceText : undefined,
    meeting_transcript: inputMode.value === 'recording' ? sourceText : undefined,
    meeting_title: meetingTitle.value?.trim() || undefined,
    meeting_time: meetingTime.value?.trim() || undefined
  }
  sessionStorage.setItem('meetingData', JSON.stringify(meetingData))
  router.push({ path: '/doc-generate/meeting/result' })
}

function handleReset() {
  meetingTitle.value = ''
  meetingTime.value = ''
  meetingNotes.value = ''
  meetingTranscript.value = ''
  recordingFile.value = null
  currentDemoScenario.value = null
}

// 切换录入方式时，若有已选示例，同步另一形式内容
watch(inputMode, (mode) => {
  if (currentDemoScenario.value) {
    const d = demoScenarios[currentDemoScenario.value as keyof typeof demoScenarios]
    if (mode === 'text') {
      meetingNotes.value = d.textNotes
      meetingTranscript.value = ''
    } else {
      meetingTranscript.value = d.transcript
      meetingNotes.value = ''
    }
  }
})

onMounted(() => {
  if (!meetingNotes.value && !meetingTranscript.value) {
    loadDemoScenario('safety')
  }
})
</script>

<style scoped>
.doc-generate-meeting-view {
  font-family: var(--font-body);
}

.input-mode-card {
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.input-mode-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.input-mode-card.selected {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.15);
}

.mode-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(59, 130, 246, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.input-mode-card.selected .mode-checkbox {
  background: var(--military-primary);
  border-color: var(--military-primary);
}

.check-icon {
  color: #fff;
  font-size: 14px;
}

.mode-icon {
  color: var(--military-primary);
}

.mode-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.mode-desc {
  font-size: 12px;
  color: var(--military-text-secondary);
  line-height: 1.4;
}

.recording-upload-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: var(--military-text-secondary);
}

.tip-icon {
  color: var(--military-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.recording-upload :deep(.el-upload-dragger) {
  width: 100%;
  background-color: rgba(10, 22, 40, 0.6) !important;
  border: 2px dashed rgba(59, 130, 246, 0.3) !important;
  transition: all 0.3s ease;
}

.recording-upload :deep(.el-upload-dragger:hover) {
  border-color: rgba(59, 130, 246, 0.6) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
}

.recording-upload :deep(.el-upload-dragger.is-dragover) {
  border-color: var(--military-primary) !important;
  background-color: rgba(59, 130, 246, 0.1) !important;
}

.upload-icon {
  font-size: 48px;
  color: var(--military-primary);
}

.upload-text {
  margin-top: 8px;
  font-size: 14px;
  color: var(--military-text-secondary);
}

.upload-text em {
  color: var(--military-primary);
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: var(--military-text-muted);
  margin-top: 8px;
}

/* 文本框样式：与系统军事主题一致 */
:deep(.el-textarea__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border: 2px solid rgba(59, 130, 246, 0.3) !important;
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
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

:deep(.el-textarea__inner::placeholder) {
  color: var(--military-text-muted) !important;
  opacity: 0.8;
}

.guide-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  opacity: 0.7;
}

.guide-step.active {
  opacity: 1;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.2);
  color: var(--military-primary);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.guide-step.active .step-number {
  background: var(--military-primary);
  color: #fff;
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

.type-info-item {
  margin-bottom: 12px;
}

.type-info-item:last-child {
  margin-bottom: 0;
}

.type-info-label {
  font-size: 12px;
  color: var(--military-text-muted);
  margin-bottom: 4px;
}

.type-info-value {
  font-size: 13px;
  color: var(--military-text-secondary);
  line-height: 1.5;
}

/* 示例场景按钮 */
.demo-scenario-btn {
  width: 100%;
  text-align: left;
  padding: 12px 16px;
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: block;
}

.demo-scenario-btn:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.demo-scenario-btn.active {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.15);
}

.demo-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.demo-desc {
  display: block;
  font-size: 12px;
  color: var(--military-text-muted);
  margin-top: 4px;
}
</style>
