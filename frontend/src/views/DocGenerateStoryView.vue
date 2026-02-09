<template>
  <div class="doc-generate-story-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">警示小故事生成</h2>
        <p class="gov-card-subtitle">选择故事类型，AI 生成具有生活感、易记忆的警示小故事，用于宣传教育</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">风格说明</span>
        <el-tooltip
          content="生成的小故事贴近日常、不说教、让人记忆深刻，适合做警示教育素材。"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip"><InfoFilled /></el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：配置与生成 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 第一步：选择故事类型 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第一步：选择故事类型</h3>
            <p class="gov-card-subtitle">选择您需要生成的警示故事类型</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="storyType in storyTypes"
              :key="storyType.value"
              class="story-type-card"
              :class="{ selected: selectedStoryType === storyType.value }"
              @click="selectedStoryType = storyType.value"
            >
              <div class="flex items-start gap-3">
                <div class="story-type-checkbox">
                  <el-icon v-if="selectedStoryType === storyType.value" class="check-icon"><Check /></el-icon>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <el-icon :size="20" class="story-type-icon">
                      <component :is="storyType.icon" />
                    </el-icon>
                    <div class="story-type-title">{{ storyType.label }}</div>
                  </div>
                  <div class="story-type-desc">{{ storyType.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二步：补充关键词（可选） -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">第二步：补充关键词或情节（可选）</h3>
            <p class="gov-card-subtitle">填写后生成的故事会更贴合您的需求</p>
          </div>

          <el-form class="gov-form" label-position="top">
            <el-form-item label="关键词或情节提示" class="gov-form-item">
              <el-input
                v-model="keywords"
                type="textarea"
                :rows="2"
                placeholder="如：网购退款、兼职刷单、冒充领导、小刘、某单位职工、下班途中……"
                class="gov-input"
              />
            </el-form-item>

            <el-form-item label="场景或结构参考" class="gov-form-item">
              <el-input
                v-model="sceneHint"
                placeholder="如：某某做了什么被诈骗、某某因为什么被处分……"
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
              <span>AI 智能生成</span>
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
            <div class="guide-step" :class="{ active: currentStep >= 1 }">
              <div class="step-number">1</div>
              <div class="step-content">
                <div class="step-title">选择故事类型</div>
                <div class="step-desc">诈骗、犯罪、工作失误等</div>
              </div>
            </div>
            <div class="guide-step" :class="{ active: currentStep >= 2 }">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-title">补充关键词（可选）</div>
                <div class="step-desc">让故事更贴近实际场景</div>
              </div>
            </div>
            <div class="guide-step" :class="{ active: currentStep >= 3 }">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-title">AI 智能生成</div>
                <div class="step-desc">点击生成，获得警示小故事</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前类型说明 -->
        <div v-if="selectedStoryType" class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">{{ currentStoryTypeInfo?.label }}说明</h3>
          </div>
          <div class="type-info">
            <div class="type-info-item">
              <div class="type-info-label">适用场景</div>
              <div class="type-info-value">{{ currentStoryTypeInfo?.usage }}</div>
            </div>
            <div class="type-info-item">
              <div class="type-info-label">故事特点</div>
              <div class="type-info-value">{{ currentStoryTypeInfo?.content }}</div>
            </div>
          </div>
        </div>

        <!-- 生成要求 -->
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">生成要求</h3>
          </div>
          <div class="style-hints">
            <div class="style-hint-item">
              <el-icon class="hint-icon"><Check /></el-icon>
              <span>有生活感，像身边真实发生的事</span>
            </div>
            <div class="style-hint-item">
              <el-icon class="hint-icon"><Check /></el-icon>
              <span>不说教、不爹味，让故事本身说话</span>
            </div>
            <div class="style-hint-item">
              <el-icon class="hint-icon"><Check /></el-icon>
              <span>简短精炼，让人记忆深刻</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Check,
  MagicStick,
  Refresh,
  InfoFilled,
  Warning,
  WarningFilled,
  Document,
  Lock,
  School,
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()

// 故事类型
const selectedStoryType = ref('')
const storyTypes = [
  {
    value: '诈骗/被骗',
    label: '诈骗/被骗',
    description: '网络诈骗、电信诈骗等',
    icon: Warning,
    usage: '防骗宣传教育、警示培训',
    content: '贴近日常，如网购退款、兼职刷单、冒充领导等场景'
  },
  {
    value: '犯罪',
    label: '犯罪',
    description: '涉法涉纪犯罪行为',
    icon: WarningFilled,
    usage: '法制教育、案例警示',
    content: '盗窃、伤害等涉法行为，强调后果与教训'
  },
  {
    value: '工作重大失误',
    label: '工作重大失误',
    description: '因疏忽造成的重大后果',
    icon: Document,
    usage: '责任心教育、履职警示',
    content: '因粗心、违规操作等导致的工作事故'
  },
  {
    value: '涉密泄密',
    label: '涉密泄密',
    description: '泄密、违规使用涉密载体',
    icon: Lock,
    usage: '保密教育、警示教育',
    content: '涉密文件、网络、社交等方面的泄密案例'
  },
  {
    value: '违纪违规',
    label: '违纪违规',
    description: '违反纪律规定被处分',
    icon: School,
    usage: '纪律教育、作风警示',
    content: '违反规章制度、作风问题等'
  },
  {
    value: '其他',
    label: '其他',
    description: '其他类型警示故事',
    icon: TrendCharts,
    usage: '根据需求灵活生成',
    content: '可根据关键词自由发挥'
  }
]

// 可选补充
const keywords = ref('')
const sceneHint = ref('')

// 当前故事类型信息
const currentStoryTypeInfo = computed(() => {
  return storyTypes.find((t) => t.value === selectedStoryType.value)
})

// 当前步骤
const currentStep = computed(() => {
  if (selectedStoryType.value && (keywords.value || sceneHint.value)) return 2
  if (selectedStoryType.value) return 1
  return 0
})

// 是否可以生成
const canGenerate = computed(() => !!selectedStoryType.value)

// 生成
function handleGenerate() {
  const storyData = {
    story_type: selectedStoryType.value,
    keywords: keywords.value?.trim() || '',
    scene_hint: sceneHint.value?.trim() || ''
  }
  sessionStorage.setItem('storyData', JSON.stringify(storyData))
  router.push({ path: '/doc-generate/story/result' })
}

// 重置
function handleReset() {
  selectedStoryType.value = ''
  keywords.value = ''
  sceneHint.value = ''
}
</script>

<style scoped>
.doc-generate-story-view {
  font-family: var(--font-body);
}

/* 故事类型卡片 */
.story-type-card {
  background: rgba(10, 22, 40, 0.5);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.story-type-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}

.story-type-card.selected {
  border-color: var(--military-primary);
  background: rgba(59, 130, 246, 0.15);
}

.story-type-checkbox {
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

.story-type-card.selected .story-type-checkbox {
  background: var(--military-primary);
  border-color: var(--military-primary);
}

.check-icon {
  color: #fff;
  font-size: 14px;
}

.story-type-icon {
  color: var(--military-primary);
}

.story-type-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
}

.story-type-desc {
  font-size: 12px;
  color: var(--military-text-secondary);
  line-height: 1.4;
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
.type-info-item {
  padding: 12px;
  background: rgba(10, 22, 40, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
}

.type-info-item:last-child {
  margin-bottom: 0;
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

/* 风格提示 */
.style-hints {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.style-hint-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--military-text-secondary);
}

.hint-icon {
  color: var(--military-primary);
  flex-shrink: 0;
}

/* 表单样式 */
:deep(.el-textarea__inner),
:deep(.el-input__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-textarea__inner:hover),
:deep(.el-input__inner:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
}

:deep(.el-textarea__inner:focus),
:deep(.el-input__inner:focus) {
  border-color: var(--military-primary) !important;
}
</style>
