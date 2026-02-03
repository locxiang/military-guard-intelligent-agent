<template>
  <div class="system-log-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 页面标题与说明 -->
    <div class="mb-6 military-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <h2 class="text-2xl font-heading font-bold military-text-primary mb-2">日志审计</h2>
          <p class="text-sm military-text-muted">查看系统操作记录，用于安全审计与问题追溯</p>
        </div>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="military-text-muted text-xs">功能说明</span>
        <el-tooltip
          content="日志审计记录谁在何时执行了哪些操作、结果是否成功，便于事后排查与合规审计"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="military-card mb-6 max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">查询条件</h3>
        <p class="text-sm military-text-muted mt-1">按时间、操作类型、操作人筛选记录</p>
      </div>
      <el-form :model="searchForm" class="flex flex-col sm:flex-row flex-wrap gap-4 max-w-full">
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">开始日期</label>
          <el-date-picker
            v-model="searchForm.startDate"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
            clearable
            class="w-full sm:w-[160px]"
          />
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">结束日期</label>
          <el-date-picker
            v-model="searchForm.endDate"
            type="date"
            placeholder="选择结束日期"
            value-format="YYYY-MM-DD"
            clearable
            class="w-full sm:w-[160px]"
          />
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">操作类型</label>
          <el-select
            v-model="searchForm.action"
            placeholder="全部类型"
            clearable
            class="w-full sm:w-[140px]"
          >
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="新增" value="create" />
            <el-option label="修改" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="查询" value="query" />
            <el-option label="导出" value="export" />
          </el-select>
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">操作人</label>
          <el-input
            v-model="searchForm.username"
            placeholder="用户名（模糊）"
            clearable
            class="military-input w-full sm:w-[140px]"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">结果状态</label>
          <el-select
            v-model="searchForm.status"
            placeholder="全部"
            clearable
            class="w-full sm:w-[120px]"
          >
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failure" />
          </el-select>
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <div class="flex items-center gap-3 mt-7">
            <button class="military-button flex items-center gap-2" @click="handleSearch">
              <el-icon><Search /></el-icon>
              <span>查询</span>
            </button>
            <button class="military-button-secondary flex items-center gap-2" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>重置</span>
            </button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作日志列表 -->
    <div class="military-card relative max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">操作记录</h3>
        <p class="text-sm military-text-muted mt-1">按时间倒序显示，最近操作在前</p>
      </div>
      <div class="overflow-x-auto max-w-full">
        <el-table
          :data="logList"
          v-loading="loading"
          stripe
          style="width: 100%; min-width: 900px"
          class="military-table"
          :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)', fontWeight: '600' }"
          :row-style="{ background: 'transparent' }"
          :cell-style="{ background: 'transparent' }"
        >
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="createdAt" label="操作时间" width="170" min-width="170">
            <template #default="{ row }">
              <span class="text-xs sm:text-sm">{{ formatDateTime(row.createdAt) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="操作人" width="110" min-width="110">
            <template #default="{ row }">
              {{ row.username || '—' }}
            </template>
          </el-table-column>
          <el-table-column prop="actionLabel" label="操作类型" width="90" min-width="90">
            <template #default="{ row }">
              <el-tag size="small" :type="getActionTagType(row.action)">
                {{ row.actionLabel || row.action || '—' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="操作描述" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.description || '—' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="结果" width="80" min-width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="clientIp" label="IP 地址" width="120" min-width="120">
            <template #default="{ row }">
              {{ row.clientIp || '—' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && logList.length === 0"
        description="暂无操作记录"
        :image-size="80"
        class="py-8"
      />

      <!-- 分页 -->
      <div v-if="total > 0" class="mt-4 flex flex-col sm:flex-row justify-center sm:justify-end gap-2">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          class="military-pagination"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, InfoFilled } from '@element-plus/icons-vue'
import { auditApi, type AuditLogItem } from '@/api/audit'

const loading = ref(false)
const logList = ref<AuditLogItem[]>([])
const total = ref(0)

const searchForm = reactive({
  startDate: '' as string,
  endDate: '' as string,
  action: '' as string,
  username: '' as string,
  status: '' as string
})

const pagination = reactive({
  page: 1,
  pageSize: 20
})

function formatDateTime(iso: string | null): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch {
    return iso
  }
}

function getActionTagType(action: string): string {
  const map: Record<string, string> = {
    login: 'success',
    logout: 'info',
    create: 'primary',
    update: 'warning',
    delete: 'danger',
    query: 'info',
    export: 'primary'
  }
  return map[action] || 'info'
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      startDate: searchForm.startDate || undefined,
      endDate: searchForm.endDate || undefined,
      action: searchForm.action || undefined,
      username: searchForm.username || undefined,
      status: searchForm.status || undefined,
      page: pagination.page,
      pageSize: pagination.pageSize
    }
    const response = await auditApi.getList(params)
    logList.value = response.data
    total.value = response.page.total
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '获取操作记录失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  searchForm.startDate = ''
  searchForm.endDate = ''
  searchForm.action = ''
  searchForm.username = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

function handleSizeChange() {
  loadData()
}

function handlePageChange() {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.system-log-view {
  font-family: var(--font-body);
}
</style>
