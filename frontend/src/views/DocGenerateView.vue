<template>
  <div class="doc-generate-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">文档生成</h2>
        <p class="gov-card-subtitle">基于AI智能生成各类公文、报告、纪要等文档</p>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="gov-help-text-short">生成说明</span>
        <el-tooltip
          content="文档生成基于AI技术，生成的内容需要人工审核和校对，确保符合规范要求"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：生成表单 -->
      <div class="lg:col-span-2">
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <h3 class="gov-card-title">生成文档</h3>
            <p class="gov-card-subtitle">填写文档信息，系统将自动生成文档内容</p>
          </div>

          <el-form :model="generateForm" :rules="formRules" ref="formRef" class="gov-form">
            <el-form-item prop="docType" class="gov-form-item">
              <label class="gov-input-label">文档类型</label>
              <el-select
                v-model="generateForm.docType"
                placeholder="请选择文档类型"
                class="w-full gov-select"
                @change="handleDocTypeChange"
              >
                <el-option label="立案报告" value="立案报告" />
                <el-option label="调查报告" value="调查报告" />
                <el-option label="请示" value="请示" />
                <el-option label="汇报" value="汇报" />
                <el-option label="会议纪要" value="会议纪要" />
                <el-option label="工作总结" value="工作总结" />
              </el-select>
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">文档类型</span>
                <el-tooltip
                  content="选择文档类型后，系统将自动匹配相应的模板和格式要求"
                  placement="top"
                  :show-after="300"
                >
                  <el-icon class="gov-help-icon-tooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </el-form-item>

            <el-form-item prop="templateId" class="gov-form-item">
              <label class="gov-input-label">模板</label>
              <el-select
                v-model="generateForm.templateId"
                placeholder="请选择模板"
                class="w-full gov-select"
                filterable
              >
                <el-option
                  v-for="template in templates"
                  :key="template.id"
                  :label="template.name"
                  :value="template.id"
                />
              </el-select>
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">模板</span>
                <el-tooltip
                  content="模板定义了文档的格式和结构，选择合适的模板可提高生成质量"
                  placement="top"
                  :show-after="300"
                >
                  <el-icon class="gov-help-icon-tooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </el-form-item>

            <el-form-item class="gov-form-item">
              <label class="gov-input-label">核心要素</label>
              <el-input
                v-model="generateForm.coreElements"
                type="textarea"
                :rows="6"
                placeholder="请输入核心要素，例如：案件编号、案由、主送机关、主要内容等，系统将根据这些要素生成文档"
                class="gov-input"
              />
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">核心要素</span>
                <el-tooltip
                  content="核心要素是文档的关键信息，请详细填写，信息越完整生成质量越高"
                  placement="top"
                  :show-after="300"
                >
                  <el-icon class="gov-help-icon-tooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </el-form-item>

            <el-form-item class="gov-form-item">
              <label class="gov-input-label">关联案卷</label>
              <el-select
                v-model="generateForm.attachments"
                multiple
                filterable
                placeholder="选择关联的案卷（可选）"
                class="w-full gov-select"
              >
                <el-option
                  v-for="caseFile in caseFileOptions"
                  :key="caseFile.id"
                  :label="`${caseFile.caseNo} - ${caseFile.title}`"
                  :value="caseFile.id"
                />
              </el-select>
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">关联案卷</span>
                <el-tooltip
                  content="关联案卷可为文档生成提供参考信息，系统将自动提取相关数据"
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
              <div class="flex items-center gap-3">
                <button
                  class="gov-button-primary flex items-center gap-2"
                  :disabled="generating"
                @click="handleGenerate"
                >
                  <span>{{ generating ? '正在生成，请稍候...' : '开始生成文档' }}</span>
                </button>
                <button class="gov-button-default flex items-center gap-2" @click="handleReset">
                  <span>重置表单</span>
                </button>
              </div>
              <div class="flex items-center gap-2 mt-2">
                <span class="gov-help-text-short">生成时间</span>
                <el-tooltip
                  content="生成过程可能需要1-3分钟，请耐心等待，生成完成后可进行编辑和下载"
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

        <!-- 生成结果 -->
        <div v-if="generatedDoc" class="gov-card mt-6">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">生成结果</h3>
                <p class="gov-card-subtitle">文档已生成，可进行编辑、下载等操作</p>
              </div>
              <div class="flex items-center gap-3">
                <button
                  class="gov-button-primary gov-button-sm flex items-center gap-2"
                  @click="handleDownload"
                >
                  <el-icon><Download /></el-icon>
                  <span>下载文档</span>
                </button>
                <button
                  class="gov-button-default gov-button-sm flex items-center gap-2"
                  @click="handleEdit"
                >
                  <el-icon><Edit /></el-icon>
                  <span>编辑内容</span>
                </button>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="gov-help-text-short">审核说明</span>
            <el-tooltip
              content="生成的内容为AI自动生成，请仔细审核和校对，确保符合规范要求后再使用"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="prose max-w-none">
            <div v-html="generatedDoc.content" class="generated-content"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：任务列表 -->
      <div>
        <div class="gov-card">
          <div class="gov-card-header mb-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="gov-card-title">生成任务</h3>
                <p class="gov-card-subtitle">查看历史生成任务记录</p>
              </div>
              <button
                class="gov-button-default gov-button-sm flex items-center gap-2"
                @click="loadTasks"
                :disabled="tasksLoading"
              >
                <el-icon><Refresh /></el-icon>
                <span>刷新</span>
              </button>
            </div>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="gov-help-text-short">任务记录</span>
            <el-tooltip
              content="任务记录保留90天，可查看任务状态和生成结果"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>

          <el-timeline v-loading="tasksLoading" class="gov-timeline">
            <el-timeline-item
              v-for="task in tasks"
              :key="task.id"
              :timestamp="formatDate(task.createdAt)"
              placement="top"
            >
              <div class="gov-card gov-card-interactive" @click="viewTaskDetail(task)">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="text-sm font-semibold" style="color: var(--color-primary-dark); font-family: var(--font-title);">{{ task.docType }}</h4>
                  <el-tag :type="getTaskStatusType(task.status)" size="small" class="gov-tag">
                    {{ getTaskStatusText(task.status) }}
                  </el-tag>
                </div>
                <p class="text-xs" style="color: var(--color-text-muted);">{{ task.taskId }}</p>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Download, Edit, Refresh, Warning, InfoFilled } from '@element-plus/icons-vue'
import { docGenerateApi } from '@/api/doc-generate'

const formRef = ref<FormInstance>()

// 生成状态
const generating = ref(false)

// 生成表单
const generateForm = reactive({
  docType: '',
  templateId: '',
  coreElements: '',
  attachments: [] as number[]
})

// 表单验证规则
const formRules: FormRules = {
  docType: [{ required: true, message: '请选择文档类型', trigger: 'change' }],
  templateId: [{ required: true, message: '请选择模板', trigger: 'change' }]
}

// 模板列表
const templates = ref<any[]>([])

// 案卷选项
const caseFileOptions = ref<any[]>([])

// 生成结果
const generatedDoc = ref<any>(null)

// 任务列表
const tasks = ref<any[]>([])
const tasksLoading = ref(false)

// 格式化日期
const formatDate = (date: Date | string) => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取任务状态类型
const getTaskStatusType = (status: string) => {
  const map: Record<string, string> = {
    generating: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    generating: '生成中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 文档类型改变
const handleDocTypeChange = () => {
  // 根据文档类型加载对应模板
  loadTemplates()
}

// 生成文档
const handleGenerate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      generating.value = true
      try {
        const response = await docGenerateApi.generate(generateForm)
        generatedDoc.value = {
          id: response.task_id,
          content: '',
          filePath: ''
        }
        ElMessage.success('文档生成任务已提交')
        loadTasks()
      } catch (error: any) {
        ElMessage.error(error?.message || '文档生成失败')
      } finally {
        generating.value = false
      }
    }
  })
}

// 重置
const handleReset = () => {
  generateForm.docType = ''
  generateForm.templateId = ''
  generateForm.coreElements = ''
  generateForm.attachments = []
  generatedDoc.value = null
  formRef.value?.resetFields()
}

// 下载
const handleDownload = () => {
  ElMessage.info('正在下载...')
  // TODO: 实现下载逻辑
}

// 编辑
const handleEdit = () => {
  ElMessage.info('编辑功能开发中...')
  // TODO: 实现编辑逻辑
}

// 查看任务详情
const viewTaskDetail = (task: any) => {
  ElMessage.info(`查看任务: ${task.taskId}`)
  // TODO: 实现任务详情查看
}

// 加载模板
const loadTemplates = async () => {
  try {
    const response = await docGenerateApi.getTemplates(generateForm.docType)
    templates.value = response.templates || []
  } catch (error: any) {
    ElMessage.error(error?.message || '加载模板失败')
  }
}

// 加载任务列表
const loadTasks = async () => {
  tasksLoading.value = true
  try {
    const response = await docGenerateApi.getTasks()
    tasks.value = response
  } catch (error: any) {
    ElMessage.error(error?.message || '加载任务列表失败')
  } finally {
    tasksLoading.value = false
  }
}

onMounted(() => {
  loadTemplates()
  loadTasks()
})
</script>

<style scoped>
.doc-generate-view {
  font-family: var(--font-body);
}

.generated-content {
  line-height: 1.8;
  color: var(--color-text);
}
</style>
