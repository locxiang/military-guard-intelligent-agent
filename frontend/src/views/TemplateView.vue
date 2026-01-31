<template>
  <div class="template-view bg-gov-background min-h-full p-4 sm:p-6">
    <!-- 页面标题 -->
    <div class="mb-6 gov-card">
      <div class="gov-card-header">
        <h2 class="gov-card-title">模板管理</h2>
        <p class="gov-card-subtitle">管理公文模板库，以 .docx 公文文件作为模板，供 AI 生成时参考格式</p>
      </div>
      <div class="flex items-center justify-between mt-4">
        <div class="flex items-center gap-2">
          <span class="gov-help-text-short">功能说明</span>
          <el-tooltip
            content="上传以往公文 .docx 文件作为模板，AI 生成时将参考其格式与结构。停用后该模板将不会在文档生成中展示。"
            placement="top"
            :show-after="300"
          >
            <el-icon class="gov-help-icon-tooltip"><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <button class="gov-button-primary flex items-center gap-2" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          <span>新建模板</span>
        </button>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="gov-card mb-6">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">搜索筛选</h3>
        <p class="gov-card-subtitle">按文档类型、关键词、状态筛选模板</p>
      </div>
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="gov-input-label">关键词</label>
          <el-input
            v-model="searchForm.keyword"
            placeholder="模板名称、说明"
            clearable
            class="gov-input w-full"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="w-[180px]">
          <label class="gov-input-label">文档类型</label>
          <el-select
            v-model="searchForm.doc_type"
            placeholder="全部类型"
            clearable
            class="gov-select w-full"
          >
            <el-option
              v-for="opt in docTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </div>
        <div class="w-[140px]">
          <label class="gov-input-label">状态</label>
          <el-select
            v-model="searchForm.status"
            placeholder="全部"
            clearable
            class="gov-select w-full"
          >
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </div>
        <div class="flex items-end gap-2">
          <button class="gov-button-primary flex items-center gap-2" @click="handleSearch">
            <el-icon><Search /></el-icon>
            <span>搜索</span>
          </button>
          <button class="gov-button-default flex items-center gap-2" @click="handleReset">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 模板列表 -->
    <div class="gov-card">
      <div class="gov-card-header mb-4">
        <h3 class="gov-card-title">模板列表</h3>
        <p class="gov-card-subtitle">共 {{ total }} 个模板</p>
      </div>
      <el-table
        :data="templateList"
        v-loading="loading"
        stripe
        class="gov-table"
        :header-cell-style="{ background: 'var(--color-background-light)', color: 'var(--military-text-primary)', fontWeight: '600' }"
      >
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="模板名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="doc_type" label="文档类型" width="140" />
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column label="模板文件" width="120">
          <template #default="{ row }">
            <span v-if="row.file_path" class="text-[var(--military-primary)]">已上传</span>
            <span v-else class="text-[var(--military-text-muted)]">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-2 flex-wrap">
              <button
                class="gov-button-default gov-button-sm flex items-center gap-1"
                @click="handleView(row)"
                title="查看详情"
              >
                <el-icon><View /></el-icon>
                <span>查看</span>
              </button>
              <button
                class="gov-button-default gov-button-sm flex items-center gap-1"
                @click="handleEdit(row)"
                title="编辑模板"
              >
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </button>
              <button
                :class="row.status === 1 ? 'gov-button-default gov-button-sm' : 'gov-button-primary gov-button-sm'"
                class="flex items-center gap-1"
                @click="handleToggleStatus(row)"
                :title="row.status === 1 ? '停用' : '启用'"
              >
                <el-icon v-if="row.status === 1"><CircleClose /></el-icon>
                <el-icon v-else><CircleCheck /></el-icon>
                <span>{{ row.status === 1 ? '停用' : '启用' }}</span>
              </button>
              <el-popconfirm
                title="确定要删除该模板吗？删除后不可恢复。"
                confirm-button-text="确认删除"
                cancel-button-text="取消"
                @confirm="handleDelete(row.id)"
              >
                <template #reference>
                  <button class="gov-button-danger gov-button-sm" title="删除">
                    <el-icon><Delete /></el-icon>
                    <span>删除</span>
                  </button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="mt-4 flex justify-end">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 新建/编辑 对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模板' : '新建模板'"
      width="560px"
      :close-on-click-modal="false"
      class="template-dialog"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
        class="gov-form"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="如：立案报告模板"
            class="gov-input"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="文档类型" prop="doc_type">
          <el-select
            v-model="form.doc_type"
            placeholder="请选择文档类型"
            class="gov-select w-full"
          >
            <el-option
              v-for="opt in docTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模板说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="简要说明该模板的用途"
            class="gov-input"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item :label="isEdit ? '更换模板文件' : '模板文件'" prop="file" :required="!isEdit">
          <div class="w-full">
            <div v-if="isEdit && currentTemplate?.file_path" class="mb-2 text-sm text-[var(--military-text-muted)]">
              当前：{{ (currentTemplate.file_path || '').split('/').pop() || '—' }}
            </div>
            <el-upload
              ref="uploadRef"
              class="gov-upload-area"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".docx"
              :on-change="handleFileChange"
              :on-exceed="handleFileExceed"
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">
                {{ isEdit ? '拖拽或点击选择新文件替换' : '拖拽或点击上传 .docx 公文文件' }}
              </div>
              <template #tip>
                <div class="upload-tip">以往公文作为模板，供 AI 生成时参考格式</div>
              </template>
            </el-upload>
            <div v-if="form.file" class="mt-2 text-sm text-[var(--military-text-muted)]">
              {{ isEdit ? '将替换为' : '已选' }}：{{ form.file.name }}
            </div>
          </div>
        </el-form-item>
        <el-form-item v-if="isEdit" label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="gov-button-default" @click="dialogVisible = false">取消</el-button>
          <el-button class="gov-button-primary" :loading="submitting" @click="handleSubmit">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看详情 对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="模板详情"
      width="560px"
      class="template-dialog"
    >
      <div v-if="currentTemplate" class="template-detail">
        <div class="detail-row">
          <span class="detail-label">模板名称</span>
          <span class="detail-value">{{ currentTemplate.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">文档类型</span>
          <span class="detail-value">{{ currentTemplate.doc_type }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">模板说明</span>
          <span class="detail-value">{{ currentTemplate.description || '—' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">版本</span>
          <span class="detail-value">v{{ currentTemplate.version }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">状态</span>
          <el-tag :type="currentTemplate.status === 1 ? 'success' : 'info'" size="small">
            {{ currentTemplate.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </div>
        <div class="detail-row full">
          <span class="detail-label">模板文件</span>
          <span class="detail-value">{{ currentTemplate.file_path ? (currentTemplate.file_path.split('/').pop() || '—') : '—' }}</span>
        </div>
      </div>
      <template #footer>
        <el-button class="gov-button-primary" @click="viewDialogVisible = false">关闭</el-button>
        <el-button class="gov-button-default" @click="handleEdit(currentTemplate); viewDialogVisible = false">
          编辑
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, View, InfoFilled, CircleCheck, CircleClose, UploadFilled } from '@element-plus/icons-vue'
import { templateApi, type DocTemplate, type TemplateCreateForm, type TemplateUpdateRequest } from '@/api/template'

const loading = ref(false)
const submitting = ref(false)

const searchForm = reactive({
  keyword: '',
  doc_type: '',
  status: undefined as 0 | 1 | undefined
})

const templateList = ref<DocTemplate[]>([])
const total = ref(0)
const pagination = reactive({ page: 1, pageSize: 20 })

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)
const currentTemplate = ref<DocTemplate | null>(null)

const docTypeOptions = ref<Array<{ value: string; label: string }>>([])
const formRef = ref<FormInstance>()
const uploadRef = ref()

const form = reactive<{
  name: string
  doc_type: string
  description: string
  status?: 0 | 1
  file?: File | null
}>({
  name: '',
  doc_type: '',
  description: '',
  status: 1,
  file: null
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }, { max: 100, message: '最多100字', trigger: 'blur' }],
  doc_type: [{ required: true, message: '请选择文档类型', trigger: 'change' }]
}

function formatDate(val: string | undefined) {
  if (!val) return '—'
  try {
    const d = new Date(val)
    return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return val
  }
}

async function loadData() {
  loading.value = true
  try {
    const res = await templateApi.getList({
      keyword: searchForm.keyword || undefined,
      doc_type: searchForm.doc_type || undefined,
      status: searchForm.status,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    templateList.value = res.data
    total.value = res.page?.total ?? 0
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '获取模板列表失败')
  } finally {
    loading.value = false
  }
}

async function loadDocTypeOptions() {
  try {
    docTypeOptions.value = await templateApi.getDocTypeOptions()
  } catch {
    docTypeOptions.value = []
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.doc_type = ''
  searchForm.status = undefined
  pagination.page = 1
  loadData()
}

function handleAdd() {
  isEdit.value = false
  currentId.value = null
  currentTemplate.value = null
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row: DocTemplate) {
  isEdit.value = true
  currentId.value = row.id
  currentTemplate.value = row
  form.name = row.name
  form.doc_type = row.doc_type
  form.description = row.description ?? ''
  form.status = row.status ?? 1
  form.file = null
  uploadRef.value?.clearFiles?.()
  dialogVisible.value = true
}

function handleView(row: DocTemplate) {
  currentTemplate.value = row
  viewDialogVisible.value = true
}

function handleFileChange(file: { raw?: File }) {
  form.file = file.raw ?? null
}

function handleFileExceed() {
  ElMessage.warning('最多上传 1 个文件')
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  if (!isEdit.value && !form.file) {
    ElMessage.warning('请上传 .docx 公文模板文件')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value && currentId.value) {
      const updateData: TemplateUpdateRequest = {
        name: form.name,
        doc_type: form.doc_type,
        description: form.description || undefined,
        status: form.status
      }
      await templateApi.update(currentId.value, updateData)
      if (form.file) {
        await templateApi.updateFile(currentId.value, form.file)
      }
      ElMessage.success('模板已更新')
    } else {
      await templateApi.create({
        name: form.name,
        doc_type: form.doc_type,
        description: form.description || undefined,
        file: form.file!
      })
      ElMessage.success('模板已创建')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleToggleStatus(row: DocTemplate) {
  const newStatus = row.status === 1 ? 0 : 1
  try {
    await templateApi.update(row.id, { status: newStatus })
    ElMessage.success(newStatus === 1 ? '已启用' : '已停用')
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

async function handleDelete(id: number) {
  try {
    await templateApi.delete(id)
    ElMessage.success('模板已删除')
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '删除失败')
  }
}

function resetForm() {
  form.name = ''
  form.doc_type = ''
  form.description = ''
  form.status = 1
  form.file = null
  uploadRef.value?.clearFiles?.()
}

onMounted(() => {
  loadDocTypeOptions()
  loadData()
})
</script>

<style scoped>
.template-view {
  font-family: var(--font-body);
}

/* 弹框与表单：与系统军事主题一致 */
.template-dialog :deep(.el-dialog__body) {
  padding-top: 12px;
}

.template-dialog :deep(.el-form-item__label) {
  color: var(--military-text-primary) !important;
}

/* 单行输入、选择框 */
.template-dialog :deep(.el-input__wrapper) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border: 2px solid rgba(59, 130, 246, 0.3) !important;
  box-shadow: none !important;
  transition: all 0.3s ease;
}

.template-dialog :deep(.el-input__wrapper:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
  background-color: rgba(10, 22, 40, 0.7) !important;
}

.template-dialog :deep(.el-input__wrapper.is-focus) {
  border-color: var(--military-primary) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

.template-dialog :deep(.el-input__inner),
.template-dialog :deep(.el-input__inner::placeholder) {
  color: var(--military-text-primary) !important;
}

.template-dialog :deep(.el-input__inner::placeholder) {
  opacity: 0.7;
}

/* 多行文本框 */
.template-dialog :deep(.el-textarea__inner) {
  background-color: rgba(10, 22, 40, 0.6) !important;
  border: 2px solid rgba(59, 130, 246, 0.3) !important;
  color: var(--military-text-primary) !important;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.template-dialog :deep(.el-textarea__inner:hover) {
  border-color: rgba(59, 130, 246, 0.5) !important;
  background-color: rgba(10, 22, 40, 0.7) !important;
}

.template-dialog :deep(.el-textarea__inner:focus) {
  border-color: var(--military-primary) !important;
  background-color: rgba(10, 22, 40, 0.8) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

.template-dialog :deep(.el-textarea__inner::placeholder) {
  color: var(--military-text-muted) !important;
  opacity: 0.8;
}

/* 字数统计 */
.template-dialog :deep(.el-input__count) {
  background: transparent !important;
  color: var(--military-text-muted) !important;
}

/* 单选组 */
.template-dialog :deep(.el-radio__label) {
  color: var(--military-text-primary) !important;
}

/* 上传区域 */
.template-dialog .gov-upload-area :deep(.el-upload-dragger) {
  background-color: rgba(10, 22, 40, 0.4) !important;
  border-color: rgba(59, 130, 246, 0.3) !important;
}
.template-dialog .upload-icon {
  font-size: 48px;
  color: var(--military-primary);
}
.template-dialog .upload-text {
  color: var(--military-text-primary);
  margin-top: 8px;
}
.template-dialog .upload-tip {
  color: var(--military-text-muted);
  font-size: 12px;
  margin-top: 8px;
}

.template-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-row.full {
  flex-direction: column;
}

.detail-label {
  flex-shrink: 0;
  width: 90px;
  font-weight: 600;
  color: var(--military-text-secondary);
}

.detail-value {
  flex: 1;
  color: var(--military-text-primary);
}

.detail-content {
  margin: 0;
  padding: 12px;
  background: rgba(10, 22, 40, 0.5);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--military-text-primary);
  max-height: 240px;
  overflow-y: auto;
}
</style>

<!-- 弹框被 teleport 到 body，需非 scoped 样式才能生效 -->
<style lang="scss">
.el-dialog.template-dialog {
  .el-textarea__inner {
    background-color: rgba(10, 22, 40, 0.6) !important;
    border: 2px solid rgba(59, 130, 246, 0.3) !important;
    color: var(--military-text-primary) !important;
    transition: all 0.3s ease;
    border-radius: 8px;

    &:hover {
      border-color: rgba(59, 130, 246, 0.5) !important;
      background-color: rgba(10, 22, 40, 0.7) !important;
    }

    &:focus {
      border-color: var(--military-primary) !important;
      background-color: rgba(10, 22, 40, 0.8) !important;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
    }

    &::placeholder {
      color: var(--military-text-muted) !important;
      opacity: 0.8;
    }
  }

  .el-input__wrapper {
    background-color: rgba(10, 22, 40, 0.6) !important;
    border: 2px solid rgba(59, 130, 246, 0.3) !important;
    box-shadow: none !important;

    &:hover {
      border-color: rgba(59, 130, 246, 0.5) !important;
      background-color: rgba(10, 22, 40, 0.7) !important;
    }

    &.is-focus {
      border-color: var(--military-primary) !important;
      background-color: rgba(10, 22, 40, 0.8) !important;
    }
  }

  /* 右侧后缀区域：字数统计、下拉箭头，去除白色背景 */
  .el-input__suffix,
  .el-input__suffix-inner,
  .el-input .el-input__suffix,
  .el-input .el-input__suffix-inner {
    background: transparent !important;
    background-color: transparent !important;
  }

  /* Element Plus 字数统计及内层有白色背景，必须覆盖 */
  .el-input__count,
  .el-input .el-input__count,
  .el-textarea .el-input__count,
  .el-input__count .el-input__count-inner,
  .el-input .el-input__count .el-input__count-inner {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--military-text-muted) !important;
  }

  /* 选择框：确保内部 input 及其后缀无白底 */
  .el-select .el-input__wrapper,
  .el-select .el-input .el-input__wrapper {
    background-color: rgba(10, 22, 40, 0.6) !important;
  }

  .el-select .el-input__suffix .el-icon,
  .el-select .el-input .el-input__suffix .el-icon {
    color: var(--military-text-primary) !important;
  }
}
</style>
