<template>
  <div class="system-config-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 页面标题 -->
    <div class="mb-6 military-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <h2 class="text-2xl font-heading font-bold military-text-primary mb-2">系统配置</h2>
          <p class="text-sm military-text-muted">系统参数、敏感词库、数据备份与安全策略配置，修改后仅在本机演示中生效</p>
        </div>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="military-text-muted text-xs">操作说明</span>
        <el-tooltip
          content="配置项用于控制系统行为与安全策略，请按单位要求谨慎修改"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <Warning />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="system-config-tabs">
      <!-- 基础配置 -->
      <el-tab-pane label="基础配置" name="basic">
        <div class="military-card">
          <div class="military-card-header mb-4">
            <h3 class="text-lg font-title font-bold military-text-primary">基础参数</h3>
            <p class="text-sm military-text-muted mt-1">系统名称、登录超时、列表每页条数等</p>
          </div>
          <el-form :model="basicForm" label-width="140px" class="max-w-xl">
            <el-form-item label="系统名称">
              <el-input v-model="basicForm.systemName" placeholder="如：保卫核心业务智能体" class="military-input" />
            </el-form-item>
            <el-form-item label="系统简称">
              <el-input v-model="basicForm.systemShortName" placeholder="用于浏览器标题等" class="military-input w-48" />
            </el-form-item>
            <el-form-item label="登录超时时间">
              <el-input-number v-model="basicForm.loginTimeoutMinutes" :min="30" :max="1440" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">分钟，超时后需重新登录</span>
            </el-form-item>
            <el-form-item label="列表每页条数">
              <el-select v-model="basicForm.pageSize" class="w-40">
                <el-option label="10 条" :value="10" />
                <el-option label="20 条" :value="20" />
                <el-option label="50 条" :value="50" />
                <el-option label="100 条" :value="100" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <button class="military-button" @click="saveBasicConfig">保存基础配置</button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 敏感词库 -->
      <el-tab-pane label="敏感词库" name="sensitive">
        <div class="military-card">
          <div class="military-card-header mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 class="text-lg font-title font-bold military-text-primary">敏感词管理</h3>
              <p class="text-sm military-text-muted mt-1">涉密关键词与敏感表述，内容审查与导出时会据此过滤或提示</p>
            </div>
            <button class="military-button flex items-center gap-2 w-full sm:w-auto" @click="handleAddWord">
              <el-icon><Plus /></el-icon>
              <span>新增敏感词</span>
            </button>
          </div>
          <div class="flex flex-wrap gap-2 mb-4">
            <el-select v-model="sensitiveWordFilter" placeholder="分类筛选" clearable class="w-40">
              <el-option label="涉密关键词" value="secret" />
              <el-option label="个人隐私" value="privacy" />
              <el-option label="不规范表述" value="informal" />
            </el-select>
          </div>
          <div class="overflow-x-auto">
            <el-table
              :data="filteredSensitiveWords"
              stripe
              style="width: 100%; min-width: 560px"
              class="military-table"
              :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)', fontWeight: '600' }"
            >
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="word" label="敏感词" min-width="120" show-overflow-tooltip />
              <el-table-column prop="category" label="分类" width="120">
                <template #default="{ row }">
                  <el-tag :type="categoryTagType(row.category)" size="small">{{ categoryLabel(row.category) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
              <el-table-column label="操作" width="140" fixed="right" align="center">
                <template #default="{ row }">
                  <button
                    class="military-button-secondary military-button-sm mr-1"
                    @click="handleEditWord(row)"
                  >
                    编辑
                  </button>
                  <el-popconfirm title="确定删除该敏感词？" @confirm="handleDeleteWord(row.id)">
                    <template #reference>
                      <button class="military-button-danger military-button-sm">删除</button>
                    </template>
                  </el-popconfirm>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 数据备份 -->
      <el-tab-pane label="数据备份" name="backup">
        <div class="military-card mb-6">
          <div class="military-card-header mb-4">
            <h3 class="text-lg font-title font-bold military-text-primary">备份策略</h3>
            <p class="text-sm military-text-muted mt-1">自动备份时间与保留天数</p>
          </div>
          <el-form :model="backupForm" label-width="140px" class="max-w-xl">
            <el-form-item label="自动备份时间">
              <el-time-picker
                v-model="backupForm.autoBackupTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="每日备份时刻"
                class="w-40"
              />
              <span class="ml-2 military-text-muted text-sm">每日该时刻执行全量备份</span>
            </el-form-item>
            <el-form-item label="备份保留天数">
              <el-input-number v-model="backupForm.retainDays" :min="7" :max="365" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">超期备份将自动归档或清理</span>
            </el-form-item>
            <el-form-item>
              <button class="military-button" @click="saveBackupConfig">保存备份策略</button>
            </el-form-item>
          </el-form>
        </div>
        <div class="military-card">
          <div class="military-card-header mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h3 class="text-lg font-title font-bold military-text-primary">备份记录</h3>
              <p class="text-sm military-text-muted mt-1">最近备份文件，支持下载或恢复</p>
            </div>
            <button class="military-button flex items-center gap-2 w-full sm:w-auto" :loading="backupLoading" @click="handleManualBackup">
              <el-icon><FolderOpened /></el-icon>
              <span>立即备份</span>
            </button>
          </div>
          <el-table
            :data="backupList"
            stripe
            class="military-table"
            :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)', fontWeight: '600' }"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="fileName" label="备份文件" min-width="200" show-overflow-tooltip />
            <el-table-column prop="size" label="大小" width="100" />
            <el-table-column prop="createdAt" label="备份时间" width="170" />
            <el-table-column label="操作" width="180" fixed="right" align="center">
              <template #default="{ row }">
                <button class="military-button-secondary military-button-sm mr-1" @click="handleDownloadBackup(row)">下载</button>
                <button class="military-button-secondary military-button-sm" @click="handleRestoreBackup(row)">恢复</button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 安全与接口 -->
      <el-tab-pane label="安全与接口" name="security">
        <div class="military-card">
          <div class="military-card-header mb-4">
            <h3 class="text-lg font-title font-bold military-text-primary">安全策略</h3>
            <p class="text-sm military-text-muted mt-1">密码策略与登录策略</p>
          </div>
          <el-form :model="securityForm" label-width="160px" class="max-w-xl">
            <el-form-item label="密码最小长度">
              <el-input-number v-model="securityForm.passwordMinLength" :min="6" :max="20" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">位</span>
            </el-form-item>
            <el-form-item label="登录失败锁定次数">
              <el-input-number v-model="securityForm.loginFailLockCount" :min="3" :max="10" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">次失败后锁定账号</span>
            </el-form-item>
            <el-form-item label="锁定时长">
              <el-input-number v-model="securityForm.lockMinutes" :min="5" :max="120" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">分钟</span>
            </el-form-item>
          </el-form>
        </div>
        <div class="military-card mt-6">
          <div class="military-card-header mb-4">
            <h3 class="text-lg font-title font-bold military-text-primary">接口配置</h3>
            <p class="text-sm military-text-muted mt-1">对外接口调用频率限制，用于第三方或外部系统对接</p>
          </div>
          <el-form :model="apiForm" label-width="160px" class="max-w-xl">
            <el-form-item label="单单位调用上限">
              <el-input-number v-model="apiForm.rateLimitPerUnit" :min="1" :max="100" class="w-40" />
              <span class="ml-2 military-text-muted text-sm">次/秒</span>
            </el-form-item>
            <el-form-item label="接口密钥">
              <el-input v-model="apiForm.apiKeyMasked" placeholder="已配置" disabled class="w-80" />
              <span class="ml-2 military-text-muted text-sm">密钥仅创建时展示一次，此处脱敏</span>
            </el-form-item>
            <el-form-item>
              <button class="military-button-secondary" @click="handleRegenerateKey">重新生成密钥</button>
            </el-form-item>
          </el-form>
        </div>
        <el-form class="mt-6">
          <el-form-item>
            <button class="military-button" @click="saveSecurityConfig">保存安全与接口配置</button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <!-- 敏感词 新增/编辑 对话框 -->
    <el-dialog
      v-model="wordDialogVisible"
      :title="wordDialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="wordFormRef" :model="wordForm" :rules="wordFormRules" label-width="80px">
        <el-form-item label="敏感词" prop="word">
          <el-input v-model="wordForm.word" placeholder="请输入敏感词" clearable class="military-input" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="wordForm.category" placeholder="请选择分类" class="w-full">
            <el-option label="涉密关键词" value="secret" />
            <el-option label="个人隐私" value="privacy" />
            <el-option label="不规范表述" value="informal" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="wordForm.remark" type="textarea" :rows="2" placeholder="选填" class="military-input" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="military-button-secondary" @click="wordDialogVisible = false">取消</el-button>
          <el-button class="military-button" type="primary" @click="submitWord" :loading="submitting">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Warning, Plus, FolderOpened } from '@element-plus/icons-vue'

const activeTab = ref('basic')
const submitting = ref(false)
const backupLoading = ref(false)

// ---------- 基础配置 ----------
const basicForm = reactive({
  systemName: '保卫核心业务智能体',
  systemShortName: '保卫智能体',
  loginTimeoutMinutes: 120,
  pageSize: 20
})
function saveBasicConfig() {
  ElMessage.success('基础配置已保存（演示）')
}

// ---------- 敏感词库 ----------
type SensitiveCategory = 'secret' | 'privacy' | 'informal'
interface SensitiveWord {
  id: number
  word: string
  category: SensitiveCategory
  remark: string
}

const demoWords: SensitiveWord[] = [
  { id: 1, word: '绝密', category: 'secret', remark: '涉密等级' },
  { id: 2, word: '机密', category: 'secret', remark: '涉密等级' },
  { id: 3, word: '内部', category: 'secret', remark: '内部资料' },
  { id: 4, word: '身份证号', category: 'privacy', remark: '个人隐私字段' },
  { id: 5, word: '手机号码', category: 'privacy', remark: '个人隐私字段' },
  { id: 6, word: '银行卡号', category: 'privacy', remark: '个人隐私字段' },
  { id: 7, word: '随便', category: 'informal', remark: '不规范表述' },
  { id: 8, word: '搞一下', category: 'informal', remark: '不规范表述' }
]

const sensitiveWordList = ref<SensitiveWord[]>(JSON.parse(JSON.stringify(demoWords)))
const sensitiveWordFilter = ref<SensitiveCategory | ''>('')
const filteredSensitiveWords = computed(() => {
  if (!sensitiveWordFilter.value) return sensitiveWordList.value
  return sensitiveWordList.value.filter((w) => w.category === sensitiveWordFilter.value)
})

function categoryLabel(c: SensitiveCategory) {
  const map = { secret: '涉密关键词', privacy: '个人隐私', informal: '不规范表述' }
  return map[c] || c
}
function categoryTagType(c: SensitiveCategory) {
  const map = { secret: 'danger', privacy: 'warning', informal: 'info' } as const
  return map[c] || 'info'
}

const wordDialogVisible = ref(false)
const wordDialogTitle = computed(() => (editingWordId.value ? '编辑敏感词' : '新增敏感词'))
const editingWordId = ref<number | null>(null)
const wordFormRef = ref<FormInstance>()
const wordForm = reactive({ word: '', category: 'secret' as SensitiveCategory, remark: '' })
const wordFormRules: FormRules = {
  word: [{ required: true, message: '请输入敏感词', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

function handleAddWord() {
  editingWordId.value = null
  wordForm.word = ''
  wordForm.category = 'secret'
  wordForm.remark = ''
  wordDialogVisible.value = true
}
function handleEditWord(row: SensitiveWord) {
  editingWordId.value = row.id
  wordForm.word = row.word
  wordForm.category = row.category
  wordForm.remark = row.remark
  wordDialogVisible.value = true
}
function submitWord() {
  wordFormRef.value?.validate((valid) => {
    if (!valid) return
    submitting.value = true
    setTimeout(() => {
      if (editingWordId.value) {
        const item = sensitiveWordList.value.find((w) => w.id === editingWordId.value)
        if (item) {
          item.word = wordForm.word
          item.category = wordForm.category
          item.remark = wordForm.remark
        }
        ElMessage.success('敏感词已更新')
      } else {
        const newId = Math.max(0, ...sensitiveWordList.value.map((w) => w.id)) + 1
        sensitiveWordList.value.push({
          id: newId,
          word: wordForm.word,
          category: wordForm.category,
          remark: wordForm.remark
        })
        ElMessage.success('敏感词已添加')
      }
      submitting.value = false
      wordDialogVisible.value = false
    }, 300)
  })
}
function handleDeleteWord(id: number) {
  sensitiveWordList.value = sensitiveWordList.value.filter((w) => w.id !== id)
  ElMessage.success('已删除')
}

// ---------- 数据备份 ----------
const backupForm = reactive({
  autoBackupTime: '02:00',
  retainDays: 365
})
const backupList = ref([
  { id: 1, fileName: 'backup_20250203_020001.sql', size: '128 MB', createdAt: '2025-02-03 02:00:01' },
  { id: 2, fileName: 'backup_20250202_020001.sql', size: '127 MB', createdAt: '2025-02-02 02:00:01' },
  { id: 3, fileName: 'backup_20250201_020001.sql', size: '126 MB', createdAt: '2025-02-01 02:00:01' }
])

function saveBackupConfig() {
  ElMessage.success('备份策略已保存（演示）')
}
function handleManualBackup() {
  backupLoading.value = true
  setTimeout(() => {
    const now = new Date()
    const name = `backup_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}.sql`
    backupList.value.unshift({ id: Date.now(), fileName: name, size: '—', createdAt: now.toLocaleString('sv-SE').replace('T', ' ').slice(0, 19) })
    backupLoading.value = false
    ElMessage.success('备份任务已创建（演示）')
  }, 800)
}
function handleDownloadBackup(row: { fileName: string }) {
  ElMessage.info(`下载备份：${row.fileName}（演示）`)
}
function handleRestoreBackup(row: { fileName: string }) {
  ElMessage.warning(`恢复将用该备份覆盖当前数据，请确认后再执行。当前为演示，未实际执行。`)
}

// ---------- 安全与接口 ----------
const securityForm = reactive({
  passwordMinLength: 8,
  loginFailLockCount: 5,
  lockMinutes: 30
})
const apiForm = reactive({
  rateLimitPerUnit: 5,
  apiKeyMasked: 'sk_****************' + String(Date.now()).slice(-4)
})
function saveSecurityConfig() {
  ElMessage.success('安全与接口配置已保存（演示）')
}
function handleRegenerateKey() {
  apiForm.apiKeyMasked = 'sk_****************' + String(Date.now()).slice(-4)
  ElMessage.warning('新密钥已生成（演示），实际环境请妥善保管并更新调用方')
}
</script>

<style scoped>
.system-config-view {
  font-family: var(--font-body);
}
/* Tab 文字颜色：未选中为白色，选中保持主题色 */
.system-config-tabs :deep(.el-tabs__header) {
  margin-bottom: 1rem;
}
.system-config-tabs :deep(.el-tabs__item) {
  font-weight: 500;
  color: var(--military-text-primary);
}
.system-config-tabs :deep(.el-tabs__item.is-active) {
  color: var(--military-primary-light);
}
.system-config-tabs :deep(.el-tabs__item:hover) {
  color: var(--military-text-primary);
}
.system-config-tabs :deep(.el-tabs__content) {
  overflow: visible;
}
/* 数字输入框与深色主题一致，避免白底 */
.system-config-view :deep(.el-input-number) {
  --el-fill-color-blank: var(--military-bg-input);
}
.system-config-view :deep(.el-input-number .el-input__wrapper) {
  background: var(--military-bg-input);
  border: 2px solid var(--military-border);
  box-shadow: none;
}
.system-config-view :deep(.el-input-number .el-input__wrapper:hover) {
  background: var(--military-bg-input-hover);
  border-color: var(--military-border-hover);
}
.system-config-view :deep(.el-input-number .el-input__wrapper.is-focus) {
  background: var(--military-bg-input-focus);
  border-color: var(--military-border-focus);
}
.system-config-view :deep(.el-input-number .el-input__inner),
.system-config-view :deep(.el-input-number .el-input .el-input__inner) {
  color: var(--military-text-primary);
}
.system-config-view :deep(.el-input-number .el-input-number__decrease),
.system-config-view :deep(.el-input-number .el-input-number__increase) {
  background: var(--military-bg-input);
  border-color: var(--military-border);
  color: var(--military-text-primary);
}
.system-config-view :deep(.el-input-number .el-input-number__decrease:hover),
.system-config-view :deep(.el-input-number .el-input-number__increase:hover) {
  background: var(--military-bg-input-hover);
  color: var(--military-primary-light);
}
</style>
