<template>
  <div class="archive-search-chat-view">
    <McLayout class="chat-container">
      <McHeader 
        :title="'案件检索助手'" 
        :logoImg="''"
      >
        <template #operationArea>
          <div class="operations">
            <el-button 
              text 
              type="primary" 
              size="small" 
              @click="newConversation"
              title="新建对话"
            >
              <el-icon><Refresh /></el-icon>
              <span class="ml-1">新建对话</span>
            </el-button>
          </div>
        </template>
      </McHeader>
      
      <!-- 欢迎页面 -->
      <McLayoutContent
        v-if="startPage"
        class="start-page"
      >
        <McIntroduction
          :logoImg="''"
          :title="'案件检索助手'"
          :subTitle="'您好，我是您的案件检索助手'"
          :description="description"
        ></McIntroduction>
        <McPrompt
          :list="introPrompt.list"
          :direction="introPrompt.direction"
          class="intro-prompt"
          @itemClick="onSubmit($event.label)"
        ></McPrompt>
      </McLayoutContent>
      
      <!-- 聊天内容区域 -->
      <McLayoutContent class="content-container" v-else>
        <template v-for="(msg, idx) in messages" :key="idx">
          <!-- 用户消息 -->
          <McBubble
            v-if="msg.from === 'user'"
            :content="msg.content"
            :align="'right'"
            :avatarConfig="{ name: 'user' }"
          >
          </McBubble>
          
          <!-- 助手消息 -->
          <McBubble 
            v-else 
            :content="msg.content" 
            :avatarConfig="{ name: 'assistant' }" 
            :loading="msg.loading"
          >
          </McBubble>
          
          <!-- 案件列表（单独展示） -->
          <div v-if="msg.cases && msg.cases.length > 0 && !msg.loading" class="case-results-wrapper">
            <div 
              v-for="(caseItem, caseIdx) in msg.cases" 
              :key="caseIdx"
              class="case-card"
              @click="handleViewDetail(caseItem)"
            >
              <div class="case-header">
                <h4 class="case-title">{{ caseItem.caseName || caseItem.title }}</h4>
                <el-tag size="small" type="primary">{{ caseItem.caseType }}</el-tag>
              </div>
              <p class="case-subtitle" v-if="caseItem.title && caseItem.caseName">{{ caseItem.title }}</p>
              <div class="case-info">
                <span class="case-meta">案卷编号: {{ caseItem.caseNo }}</span>
                <span class="case-meta" v-if="caseItem.personName">当事人: {{ caseItem.personName }}</span>
                <span class="case-meta">办案单位: {{ caseItem.sourceDepartment }}</span>
                <span class="case-meta">案发日期: {{ formatDate(caseItem.date) }}</span>
              </div>
              <div class="case-tags" v-if="caseItem.tags && caseItem.tags.length > 0">
                <el-tag
                  v-for="tag in caseItem.tags"
                  :key="tag"
                  size="small"
                  :type="tag === '重要' ? 'warning' : 'info'"
                  class="mr-1"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div class="case-actions">
                <el-button size="small" type="primary" @click.stop="handleViewDetail(caseItem)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </template>
      </McLayoutContent>
      
      <!-- 快捷提示 -->
      <div class="shortcut" v-if="!startPage">
        <McPrompt
          :list="simplePrompt"
          :direction="'horizontal'"
          style="flex: 1"
          @itemClick="onSubmit($event.label)"
        ></McPrompt>
      </div>
      
      <!-- 输入框 -->
      <McLayoutSender>
        <McInput 
          :value="inputValue" 
          :maxLength="2000" 
          @change="(e) => (inputValue = e)" 
          @submit="onSubmit"
        >
          <template #extra>
            <div class="input-foot-wrapper">
              <div class="input-foot-left">
                <span class="input-foot-maxlength">{{ inputValue.length }}/2000</span>
              </div>
              <div class="input-foot-right">
                <el-button 
                  text 
                  type="primary" 
                  size="small" 
                  :disabled="!inputValue" 
                  @click="inputValue = ''"
                >
                  清空输入
                </el-button>
              </div>
            </div>
          </template>
        </McInput>
      </McLayoutSender>
    </McLayout>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'

const router = useRouter()

// 欢迎页面描述
const description = [
  '我可以帮您通过自然语言的方式快速查找案件卷宗信息。',
  '您可以问我："查找盗窃案相关案件"、"找一下张某的案件"等。',
  '我会根据您的描述，为您找到最相关的案件卷宗。'
]

// 欢迎页面的快捷提示
const introPrompt = {
  direction: 'horizontal',
  list: [
    {
      value: 'searchByType',
      label: '查找盗窃案相关案件',
      iconConfig: { name: 'icon-info-o', color: '#0A2463' },
      desc: '按案件类型搜索',
    },
    {
      value: 'searchByPerson',
      label: '查找涉及"张某"的案件',
      iconConfig: { name: 'icon-star', color: '#B8860B' },
      desc: '按当事人姓名搜索',
    },
    {
      value: 'searchByDept',
      label: '查找某试训基地的案件',
      iconConfig: { name: 'icon-priority', color: '#1E7E34' },
      desc: '按办案单位搜索',
    },
  ],
}

// 聊天中的快捷提示
const simplePrompt = [
  {
    value: 'searchByType',
    iconConfig: { name: 'icon-info-o', color: '#0A2463' },
    label: '按案件类型',
  },
  {
    value: 'searchByPerson',
    iconConfig: { name: 'icon-star', color: '#B8860B' },
    label: '按当事人',
  },
  {
    value: 'searchByDept',
    iconConfig: { name: 'icon-priority', color: '#1E7E34' },
    label: '按办案单位',
  },
]

// 页面状态
const startPage = ref(true)
const inputValue = ref('')

// 消息列表
const messages = ref<any[]>([])

// 固定话术响应映射
const getResponse = (userInput: string): { content: string; cases?: any[] } => {
  const input = userInput.toLowerCase()
  
  // 盗窃案/案件类型搜索
  if (input.includes('盗窃') || input.includes('类型')) {
    return {
      content: '好的，我为您找到了以下盗窃案相关的案件卷宗，共 2 条记录：',
      cases: [
        {
          id: 1,
          title: '关于张某盗窃战友财物案件的调查报告',
          caseNo: 'AJ2025-001',
          caseName: '2025年1月-某试训基地-战士张某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某试训基地保卫处',
          personName: '张某',
          date: '2025-01-15',
          tags: ['盗窃', '内部案件', '战士']
        },
        {
          id: 2,
          title: '关于李某盗窃公共财物案件的处理报告',
          caseNo: 'AJ2025-002',
          caseName: '2025年1月-某通信旅-班长李某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某通信旅保卫科',
          personName: '李某',
          date: '2025-01-08',
          tags: ['盗窃', '公共财物', '班长']
        }
      ]
    }
  }
  
  // 当事人搜索
  if (input.includes('张某') || input.includes('当事人')) {
    return {
      content: '我为您找到了涉及"张某"的案件卷宗，共 1 条记录：',
      cases: [
        {
          id: 1,
          title: '关于张某盗窃战友财物案件的调查报告',
          caseNo: 'AJ2025-001',
          caseName: '2025年1月-某试训基地-战士张某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某试训基地保卫处',
          personName: '张某',
          date: '2025-01-15',
          tags: ['盗窃', '内部案件', '战士']
        }
      ]
    }
  }
  
  // 办案单位搜索
  if (input.includes('试训基地') || input.includes('办案单位') || input.includes('保卫处')) {
    return {
      content: '我为您找到了某试训基地保卫处的案件卷宗，共 1 条记录：',
      cases: [
        {
          id: 1,
          title: '关于张某盗窃战友财物案件的调查报告',
          caseNo: 'AJ2025-001',
          caseName: '2025年1月-某试训基地-战士张某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某试训基地保卫处',
          personName: '张某',
          date: '2025-01-15',
          tags: ['盗窃', '内部案件', '战士']
        }
      ]
    }
  }
  
  // 2025年/时间搜索
  if (input.includes('2025') || input.includes('今年') || input.includes('最近')) {
    return {
      content: '我为您找到了 2025 年的案件卷宗，共 2 条记录：',
      cases: [
        {
          id: 1,
          title: '关于张某盗窃战友财物案件的调查报告',
          caseNo: 'AJ2025-001',
          caseName: '2025年1月-某试训基地-战士张某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某试训基地保卫处',
          personName: '张某',
          date: '2025-01-15',
          tags: ['盗窃', '内部案件', '战士']
        },
        {
          id: 2,
          title: '关于李某盗窃公共财物案件的处理报告',
          caseNo: 'AJ2025-002',
          caseName: '2025年1月-某通信旅-班长李某盗窃案',
          caseType: '盗窃罪',
          sourceDepartment: '某通信旅保卫科',
          personName: '李某',
          date: '2025-01-08',
          tags: ['盗窃', '公共财物', '班长']
        }
      ]
    }
  }
  
  // 默认响应 - 显示所有案件
  return {
    content: '好的，我为您查询了系统中的案件卷宗，以下是相关记录：',
    cases: [
      {
        id: 1,
        title: '关于张某盗窃战友财物案件的调查报告',
        caseNo: 'AJ2025-001',
        caseName: '2025年1月-某试训基地-战士张某盗窃案',
        caseType: '盗窃罪',
        sourceDepartment: '某试训基地保卫处',
        personName: '张某',
        date: '2025-01-15',
        tags: ['盗窃', '内部案件', '战士']
      },
      {
        id: 2,
        title: '关于李某盗窃公共财物案件的处理报告',
        caseNo: 'AJ2025-002',
        caseName: '2025年1月-某通信旅-班长李某盗窃案',
        caseType: '盗窃罪',
        sourceDepartment: '某通信旅保卫科',
        personName: '李某',
        date: '2025-01-08',
        tags: ['盗窃', '公共财物', '班长']
      }
    ]
  }
}

// 新建对话
const newConversation = () => {
  startPage.value = true
  messages.value = []
  inputValue.value = ''
}

// 提交消息
const onSubmit = (evt: string | Event) => {
  const userInput = typeof evt === 'string' ? evt : inputValue.value
  if (!userInput.trim()) {
    return
  }
  
  inputValue.value = ''
  startPage.value = false
  
  // 添加用户消息
  messages.value.push({
    from: 'user',
    content: userInput,
  })
  
  // 模拟助手思考
  messages.value.push({
    from: 'model',
    content: '',
    loading: true,
  })
  
  // 延迟响应（模拟API调用）
  setTimeout(() => {
    const response = getResponse(userInput)
    // 移除loading消息，添加实际响应
    messages.value.pop()
    messages.value.push({
      from: 'model',
      content: response.content,
      cases: response.cases || [],
      loading: false,
    })
    
    // 滚动到底部
    setTimeout(() => {
      const container = document.querySelector('.content-container')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }, 100)
  }, 800)
}

// 格式化日期
const formatDate = (date: Date | string) => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('zh-CN')
}

// 查看详情
const handleViewDetail = (caseItem: any) => {
  router.push(`/case-file/${caseItem.id}`)
}
</script>

<style lang="scss" scoped>
// 政务色彩变量（与全局主题保持一致）
$gov-primary: #0A2463;
$gov-primary-dark: #001F3F;
$gov-primary-lighter: #E8EDF5;
$gov-accent: #B8860B;
$gov-bg: #F8F9FA;
$gov-bg-light: #F5F5F5;
$gov-white: #FFFFFF;
$gov-text: #1A202C;
$gov-text-muted: #6C757D;
$gov-border: #E2E8F0;
$gov-border-dark: #CBD5E0;
$gov-shadow: rgba(10, 36, 99, 0.12);
$gov-shadow-lg: rgba(10, 36, 99, 0.16);

.archive-search-chat-view {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $gov-bg;
  font-family: 'Noto Sans SC', 'Microsoft YaHei', '微软雅黑', sans-serif;
}

.chat-container {
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
  height: calc(100vh - 40px);
  padding: 0;
  gap: 0;
  background: $gov-white;
  border-radius: 8px;
  box-shadow: 0 4px 12px $gov-shadow-lg;
  border: 1px solid $gov-border-dark;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.start-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  min-height: 500px;
  padding: 40px 20px;
  background: $gov-white;
  color: $gov-text;
  
  // 确保 MateChat 组件内文字颜色正确
  :deep(.mc-introduction) {
    color: $gov-text;
  }
  
  :deep(.mc-introduction-title) {
    color: $gov-primary;
  }
  
  :deep(.mc-introduction-sub-title) {
    color: $gov-text !important;
  }
  
  :deep(.mc-introduction-description) {
    color: $gov-text-muted !important;
    
    > div {
      color: $gov-text-muted !important;
    }
  }
  
  :deep(.mc-prompt-item) {
    background: $gov-white;
    border: 1.5px solid $gov-border-dark;
    color: $gov-text;
    
    &:hover {
      border-color: $gov-primary;
      background: $gov-primary-lighter;
    }
  }
  
  :deep(.mc-prompt-item-label) {
    color: $gov-text !important;
    font-weight: 600;
  }
  
  :deep(.mc-prompt-item-description) {
    color: $gov-text-muted !important;
  }
}

.intro-prompt {
  margin-top: 32px;
  width: 100%;
  max-width: 800px;
  
  :deep(.mc-prompt) {
    justify-content: center;
    gap: 16px;
  }
  
  :deep(.mc-prompt-item) {
    background: $gov-white !important;
    border: 1.5px solid $gov-border-dark !important;
    border-radius: 8px !important;
    padding: 16px 24px !important;
    box-shadow: 0 2px 4px $gov-shadow !important;
    transition: all 0.2s ease !important;
    
    &:hover {
      border-color: $gov-primary !important;
      background: $gov-primary-lighter !important;
      box-shadow: 0 4px 12px $gov-shadow-lg !important;
      transform: translateY(-2px) !important;
    }
  }
  
  :deep(.mc-prompt-item-content) {
    color: $gov-text !important;
  }
  
  :deep(.mc-prompt-item-label) {
    color: $gov-text !important;
    font-weight: 600 !important;
    font-size: 14px !important;
  }
  
  :deep(.mc-prompt-item-description) {
    color: $gov-text-muted !important;
    font-size: 12px !important;
  }
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  padding: 24px;
  background: $gov-bg;
  
  // 滚动条样式
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: $gov-bg-light;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: $gov-border-dark;
    border-radius: 4px;
    
    &:hover {
      background: $gov-primary;
    }
  }
}

// 快捷提示区域
.shortcut {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: $gov-bg-light;
  border-top: 1px solid $gov-border;
}

// 输入框底部
.input-foot-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 0;
}

.input-foot-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-foot-maxlength {
  font-size: 13px;
  color: $gov-text-muted;
}

.input-foot-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.operations {
  display: flex;
  align-items: center;
  gap: 8px;
  
  :deep(.el-button) {
    color: $gov-white !important;
    font-weight: 600;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.2) !important;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .chat-container {
    margin: 10px;
    height: calc(100vh - 20px);
    border-radius: 8px;
  }
  
  .start-page {
    min-height: 400px;
    padding: 24px 16px;
  }
  
  .content-container {
    padding: 16px;
  }
  
  .shortcut {
    padding: 12px 16px;
  }
}
</style>