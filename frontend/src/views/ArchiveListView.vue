<template>
  <div class="archive-list-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 页面标题和操作栏 -->
    <div class="mb-6 military-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 max-w-full overflow-x-hidden">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-heading font-bold military-text-primary mb-2">案卷管理</h2>
        <p class="text-sm military-text-muted">管理数字卷宗案卷，支持检索、查看、导出</p>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0 flex-wrap">
      <button
          class="military-button flex items-center gap-2 whitespace-nowrap"
        @click="$router.push('/case-file/import')"
      >
        <el-icon><Upload /></el-icon>
        <span>导入案卷</span>
      </button>
        <div class="hidden sm:flex items-center">
          <el-tooltip
            content="支持 .doc, .pdf, .xls 格式，单个文件最大 500MB，批量导入最多100个文件"
            placement="top"
            :show-after="300"
          >
            <el-icon class="gov-help-icon-tooltip cursor-help">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="military-card mb-6 relative overflow-hidden max-w-full">
      <!-- 装饰条纹 -->
      <div class="absolute top-0 right-0 w-32 h-32 mil-stripe opacity-50 pointer-events-none"></div>

      <div class="flex items-center justify-between mb-4 pb-3 border-b border-military-border relative z-10">
        <div class="flex items-center gap-2">
          <button
            v-if="!showAdvancedSearch"
            class="text-sm military-text-primary hover:text-military-primary-light transition-colors font-medium"
            @click="showAdvancedSearch = true"
          >
            高级检索
          </button>
          <button
            v-else
            class="text-sm military-text-primary hover:text-military-primary-light transition-colors font-medium"
            @click="showAdvancedSearch = false"
          >
            收起检索
          </button>
          <el-dropdown trigger="click" @command="handleFilterTemplate">
            <button class="text-sm military-text-primary flex items-center gap-1 hover:text-military-primary-light transition-colors">
              筛选模板 <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="template in filterTemplates"
                  :key="template.id"
                  :command="template.id"
                >
                  {{ template.name }}
                </el-dropdown-item>
                <el-dropdown-item divided command="save" v-if="hasActiveFilters">
                  保存当前筛选条件
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div v-if="hasActiveFilters" class="flex items-center gap-2">
          <span class="text-sm military-text-muted">当前筛选:</span>
          <el-tag
            v-for="(value, key) in activeFilters"
            :key="key"
            closable
            @close="clearFilter(key)"
            size="small"
            class="gov-tag"
          >
            {{ getFilterLabel(key, value) }}
          </el-tag>
        </div>
      </div>

      <div class="relative z-10 max-w-full">
        <!-- 搜索表单 - 使用网格布局确保对齐 -->
        <el-form :model="searchForm" class="search-form-grid">
          <!-- 关键词搜索 - 占据较大空间 -->
          <el-form-item class="search-form-item search-form-item-keyword">
            <div class="flex items-center gap-2">
              <label class="military-input-label mb-0">关键词</label>
              <el-tooltip
                content="支持模糊搜索和多条件组合搜索，可输入案卷编号、卷宗名、标题或正文内容进行检索，点击搜索按钮执行查询，点击重置可清空所有筛选条件"
                placement="top"
                :show-after="300"
              >
                <el-icon class="gov-help-icon-tooltip cursor-help">
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </div>
            <el-autocomplete
              v-model="searchForm.keyword"
              :fetch-suggestions="searchSuggestions"
              placeholder="请输入案卷编号、卷宗名、标题或内容"
              clearable
              class="w-full military-input"
              @keyup.enter="handleSearch"
              @select="handleSearchSelect"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-autocomplete>
          </el-form-item>

          <!-- 罪名 -->
          <el-form-item class="search-form-item">
            <label class="military-input-label">罪名</label>
            <el-select
              v-model="searchForm.caseType"
              placeholder="请选择..."
              clearable
              class="w-full"
            >
              <el-option label="全部" value="" />
              <el-option label="盗窃罪" value="盗窃罪" />
              <el-option label="诈骗罪" value="诈骗罪" />
              <el-option label="故意伤害罪" value="故意伤害罪" />
              <el-option label="故意杀人罪" value="故意杀人罪" />
              <el-option label="抢劫罪" value="抢劫罪" />
              <el-option label="贪污罪" value="贪污罪" />
              <el-option label="受贿罪" value="受贿罪" />
              <el-option label="滥用职权罪" value="滥用职权罪" />
              <el-option label="玩忽职守罪" value="玩忽职守罪" />
              <el-option label="泄露国家秘密罪" value="泄露国家秘密罪" />
              <el-option label="非法获取国家秘密罪" value="非法获取国家秘密罪" />
              <el-option label="危害国家安全罪" value="危害国家安全罪" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>

          <!-- 状态 -->
          <el-form-item class="search-form-item">
            <label class="military-input-label">状态</label>
            <el-select
              v-model="searchForm.status"
              placeholder="请选择..."
              clearable
              class="w-full"
            >
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>

          <!-- 时间范围 -->
          <el-form-item class="search-form-item search-form-item-date">
            <label class="military-input-label">时间范围</label>
            <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY年MM月DD日"
              value-format="YYYY-MM-DD"
              class="w-full military-date-picker"
            />
          </el-form-item>

          <!-- 操作按钮区域 -->
          <el-form-item class="search-form-item search-form-item-actions">
            <label class="military-input-label invisible">操作</label>
            <div class="flex gap-2">
              <button class="military-button flex-1 flex items-center justify-center gap-2" @click="handleSearch">
                <el-icon><Search /></el-icon>
                <span>执行搜索</span>
              </button>
              <button class="military-button-secondary flex-1 flex items-center justify-center gap-2" @click="handleReset">
                <el-icon><Refresh /></el-icon>
                <span>重置条件</span>
              </button>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 高级搜索 -->
      <el-collapse-transition>
        <div v-show="showAdvancedSearch" class="mt-4 pt-4 border-t border-military-border">
          <el-form :model="advancedSearchForm" label-width="120px" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <el-form-item label="精确匹配">
              <el-switch v-model="advancedSearchForm.exactMatch" active-text="开启" inactive-text="关闭" />
              <div class="flex items-center gap-2 ml-2">
                <span class="military-text-muted text-xs">精确匹配</span>
                <el-tooltip
                  content="开启后将进行完全匹配，关闭则进行模糊匹配"
                  placement="top"
                  :show-after="300"
                >
                  <el-icon class="gov-help-icon-tooltip">
                    <InfoFilled />
                  </el-icon>
                </el-tooltip>
              </div>
            </el-form-item>
            <el-form-item label="排除词">
              <el-input v-model="advancedSearchForm.excludeWords" placeholder="用空格分隔多个排除词" class="military-input" />
            </el-form-item>
            <el-form-item label="来源部门">
              <el-select v-model="advancedSearchForm.department" clearable placeholder="请选择" class="">
                <el-option label="全部" value="" />
                <el-option label="某试训基地保卫处" value="某试训基地保卫处" />
              </el-select>
            </el-form-item>
            <el-form-item label="文件大小">
              <el-input-number v-model="advancedSearchForm.minSize" :min="0" placeholder="最小(KB)" class="" />
              <span class="mx-2 military-text-muted">-</span>
              <el-input-number v-model="advancedSearchForm.maxSize" :min="0" placeholder="最大(KB)" class="" />
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
    </div>

    <!-- 案卷列表 -->
    <div class="military-card relative max-w-full overflow-hidden">
       <!-- 顶部装饰条 -->
      <div class="absolute top-0 left-0 right-0 h-1 bg-military-primary rounded-t-sm"></div>
      
      <div class="military-card-header flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3 sm:gap-0 pb-3 border-b border-military-border mt-2 max-w-full overflow-x-hidden">
        <div class="mil-badge-mark pl-3 flex-shrink-0">
          <span class="text-sm military-text-muted">共找到 </span>
          <span class="text-sm font-semibold text-military-primary font-mono">{{ total }}</span>
          <span class="text-sm military-text-muted"> 条记录</span>
        </div>
        <div class="flex items-center flex-wrap gap-2 min-w-0 w-full sm:w-auto">
          <!-- 视图切换 -->
          <div class="view-mode-switcher flex items-center gap-1 flex-shrink-0">
            <button
              :class="['view-mode-btn', { 'active': viewMode === 'table' }]"
              @click="viewMode = 'table'"
              title="表格视图"
            >
              <el-icon><List /></el-icon>
            </button>
            <button
              :class="['view-mode-btn', { 'active': viewMode === 'card' }]"
              @click="viewMode = 'card'"
              title="卡片视图"
            >
              <el-icon><Grid /></el-icon>
            </button>
          </div>
          
          <!-- 批量操作 -->
          <el-dropdown v-if="selectedRows.length > 0" trigger="click" @command="handleBatchAction" class="flex-shrink-0">
            <button class="military-button military-button-sm flex items-center gap-2 whitespace-nowrap">
              <span>批量操作 ({{ selectedRows.length }})</span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="download">
                  <el-icon><Download /></el-icon>
                  <span class="ml-2">批量下载</span>
                </el-dropdown-item>
                <el-dropdown-item command="delete">
                  <el-icon><Delete /></el-icon>
                  <span class="ml-2">批量删除</span>
                </el-dropdown-item>
                <el-dropdown-item command="update">
                  <el-icon><Edit /></el-icon>
                  <span class="ml-2">批量修改</span>
                </el-dropdown-item>
                <el-dropdown-item command="export">
                  <el-icon><Document /></el-icon>
                  <span class="ml-2">批量导出</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <button class="military-button-secondary military-button-sm flex items-center gap-2 whitespace-nowrap flex-shrink-0" @click="handleExport">
            <el-icon><Download /></el-icon>
            <span class="hidden sm:inline">导出数据</span>
            <span class="sm:hidden">导出</span>
          </button>
          <button class="military-button-secondary military-button-sm flex items-center gap-2 whitespace-nowrap flex-shrink-0" @click="loadData">
            <el-icon><Refresh /></el-icon>
            <span class="hidden sm:inline">刷新列表</span>
            <span class="sm:hidden">刷新</span>
          </button>
          <div class="hidden md:flex items-center gap-2 flex-shrink-0">
            <span class="military-text-muted text-xs">批量操作</span>
            <el-tooltip
              content="批量操作需先选择案卷，导出支持Excel和PDF格式"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <button class="military-button-secondary military-button-sm flex items-center gap-2 whitespace-nowrap flex-shrink-0" @click="showColumnSettings = true">
            <el-icon><Setting /></el-icon>
            <span class="hidden sm:inline">列设置</span>
            <span class="sm:hidden">设置</span>
          </button>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" v-loading="loading" class="overflow-x-auto max-w-full">
        <el-table
          :data="caseFileList"
          stripe
          style="width: 100%; min-width: 800px"
          @row-click="handleRowClick"
          @selection-change="handleSelectionChange"
          class="military-table"
          :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)', fontWeight: '600' }"
          :row-style="{ background: 'transparent' }"
          :cell-style="{ background: 'transparent' }"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="caseNo" label="案卷编号" width="120" min-width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="font-mono text-military-primary font-medium">{{ row.caseNo }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="military-text-primary font-medium">{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="caseType" label="罪名" width="100" min-width="100">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" type="info">{{ row.caseType }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sourceDepartment" label="来源部门" width="130" min-width="130" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="90" min-width="90">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="160" min-width="160">
            <template #default="{ row }">
              <span class="text-xs military-text-muted">{{ formatDate(row.createdAt) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" min-width="240" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-2">
                <button
                  class="military-button-secondary military-button-sm"
                  @click.stop="viewDetail(row.id)"
                  title="查看案卷详情"
                >
                  查看详情
                </button>
                <button
                  class="military-button-secondary military-button-sm"
                  @click.stop="handleDownload(row)"
                  title="下载案卷文件"
                >
                  下载
                </button>
                <el-popconfirm
                  title="确定要删除这条案卷吗？此操作不可恢复，请谨慎操作。"
                  confirm-button-text="确认删除"
                  cancel-button-text="取消"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <button class="military-button-danger military-button-sm" @click.stop title="删除案卷">
                      删除
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 卡片视图 -->
      <div v-else-if="viewMode === 'card'" v-loading="loading" class="case-card-grid">
        <div
          v-for="(item, index) in caseFileList"
          :key="item.id"
          class="case-card-item"
          @click="viewDetail(item.id)"
        >
          <div class="case-card-header">
            <div class="flex items-center justify-between mb-2">
              <span class="case-card-number">{{ item.caseNo }}</span>
              <el-checkbox
                :model-value="selectedRows.some(r => r.id === item.id)"
                @change="toggleCardSelection(item, $event)"
                @click.stop
                class="case-card-checkbox"
              />
            </div>
            <h3 class="case-card-title" :title="item.title">{{ item.title }}</h3>
          </div>
          
          <div class="case-card-body">
            <div class="case-card-info-item">
              <span class="info-label">罪名：</span>
              <el-tag size="small" effect="plain" type="info">{{ item.caseType }}</el-tag>
            </div>
            <div class="case-card-info-item">
              <span class="info-label">来源部门：</span>
              <span class="info-value">{{ item.sourceDepartment || '未知' }}</span>
            </div>
            <div class="case-card-info-item">
              <span class="info-label">状态：</span>
              <el-tag :type="getStatusType(item.status)" size="small" effect="dark">
                {{ getStatusText(item.status) }}
              </el-tag>
            </div>
            <div class="case-card-info-item" v-if="item.personName">
              <span class="info-label">涉案人员：</span>
              <span class="info-value">{{ item.personName }}</span>
            </div>
            <div class="case-card-info-item">
              <span class="info-label">创建时间：</span>
              <span class="info-value text-xs">{{ formatDate(item.createdAt) }}</span>
            </div>
          </div>

          <div class="case-card-footer" @click.stop>
            <button
              class="case-card-action-btn"
              @click.stop="viewDetail(item.id)"
            >
              <el-icon><Document /></el-icon>
              <span>查看详情</span>
            </button>
            <button
              class="case-card-action-btn"
              @click.stop="handleDownload(item)"
            >
              <el-icon><Download /></el-icon>
              <span>下载</span>
            </button>
            <el-popconfirm
              title="确定要删除这条案卷吗？此操作不可恢复，请谨慎操作。"
              confirm-button-text="确认删除"
              cancel-button-text="取消"
              @confirm="handleDelete(item.id)"
            >
              <template #reference>
                <button class="case-card-action-btn danger" @click.stop>
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </button>
              </template>
            </el-popconfirm>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="!loading && caseFileList.length === 0" class="empty-state">
          <el-empty description="暂无案卷数据" />
        </div>
      </div>

      <!-- 分页 -->
      <div class="mt-4 flex flex-col sm:flex-row justify-center sm:justify-end gap-2">
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
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, 
  Refresh, 
  Download, 
  Upload, 
  ArrowDown,
  List,
  Grid,
  Delete,
  Edit,
  Document,
  Setting,
  InfoFilled
} from '@element-plus/icons-vue'
import { caseFileApi } from '@/api/archive'

const router = useRouter()

// 加载状态
const loading = ref(false)

// 视图模式
const viewMode = ref<'table' | 'card'>('table')

// 显示高级搜索
const showAdvancedSearch = ref(false)

// 列设置
const showColumnSettings = ref(false)

// 高级搜索表单
const advancedSearchForm = reactive({
  exactMatch: false,
  excludeWords: '',
  department: '',
  minSize: null as number | null,
  maxSize: null as number | null
})

// 筛选模板
const filterTemplates = ref([
  { id: 1, name: '待处理案卷', filters: { status: 'pending' } },
  { id: 2, name: '本周新增', filters: { dateRange: 'week' } },
  { id: 3, name: '案件卷宗', filters: { caseType: '案件卷宗' } }
])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  caseType: '',
  status: '',
  dateRange: undefined as [Date, Date] | undefined
})

// 选中的行
const selectedRows = ref<any[]>([])

// 计算活跃的筛选条件
const activeFilters = computed(() => {
  const filters: Record<string, any> = {}
  if (searchForm.keyword) filters.keyword = searchForm.keyword
  if (searchForm.caseType) filters.caseType = searchForm.caseType
  if (searchForm.status) filters.status = searchForm.status
  if (searchForm.dateRange) filters.dateRange = searchForm.dateRange
  return filters
})

const hasActiveFilters = computed(() => {
  return Object.keys(activeFilters.value).length > 0
})

// 获取筛选标签
const getFilterLabel = (key: string, value: any) => {
  const labels: Record<string, Record<string, string>> = {
    caseType: {
      '盗窃罪': '盗窃罪',
      '诈骗罪': '诈骗罪',
      '故意伤害罪': '故意伤害罪',
      '故意杀人罪': '故意杀人罪',
      '抢劫罪': '抢劫罪',
      '贪污罪': '贪污罪',
      '受贿罪': '受贿罪',
      '滥用职权罪': '滥用职权罪',
      '玩忽职守罪': '玩忽职守罪',
      '泄露国家秘密罪': '泄露国家秘密罪',
      '非法获取国家秘密罪': '非法获取国家秘密罪',
      '危害国家安全罪': '危害国家安全罪',
      '其他': '其他'
    },
    status: {
      'pending': '待处理',
      'processing': '处理中',
      'completed': '已完成',
      'failed': '失败'
    }
  }
  return labels[key]?.[value] || value
}

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 总数
const total = ref(0)

// 案卷列表
const caseFileList = ref<any[]>([])

// 格式化日期（空值显示为 --，避免渲染报错）
const formatDate = (date: Date | string | null | undefined) => {
  if (date == null) return '--'
  const d = typeof date === 'string' ? new Date(date) : date
  if (Number.isNaN(d.getTime())) return '--'
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.caseType = ''
  searchForm.status = ''
  searchForm.dateRange = undefined
  handleSearch()
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await caseFileApi.getList({
      ...searchForm,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    total.value = response.page.total || 0
    caseFileList.value = response.data || []
  } catch (error: any) {
    ElMessage.error(error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 行点击
const handleRowClick = (row: any, column: any) => {
  // 点击选择框时不触发
  if (column?.property === 'selection') return
  viewDetail(row.id)
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 切换卡片选择
const toggleCardSelection = (item: any, checked: boolean) => {
  if (checked) {
    if (!selectedRows.value.some(r => r.id === item.id)) {
      selectedRows.value.push(item)
    }
  } else {
    selectedRows.value = selectedRows.value.filter(r => r.id !== item.id)
  }
}

// 批量操作
const handleBatchAction = async (command: string) => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要操作的项目')
    return
  }

  const ids = selectedRows.value.map(row => row.id)

  switch (command) {
    case 'download':
      ElMessage.info(`正在批量下载 ${ids.length} 个案卷...`)
      // TODO: 实现批量下载
      break
    case 'delete':
      ElMessageBox.confirm(
        `确定要删除选中的 ${ids.length} 条案卷吗？此操作不可恢复。`,
        '批量删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          // TODO: 调用批量删除API
          ElMessage.success('删除成功')
          selectedRows.value = []
          loadData()
        } catch (error: any) {
          ElMessage.error(error?.message || '删除失败')
        }
      })
      break
    case 'update':
      ElMessage.info(`批量修改 ${ids.length} 个案卷...`)
      // TODO: 打开批量修改对话框
      break
    case 'export':
      ElMessage.info(`正在批量导出 ${ids.length} 个案卷...`)
      // TODO: 实现批量导出
      break
  }
}

// 搜索建议
const searchSuggestions = async (queryString: string, cb: (suggestions: any[]) => void) => {
  if (!queryString) {
    // 显示历史搜索记录
    const history = localStorage.getItem('searchHistory')
    const historyList = history ? JSON.parse(history) : []
    cb(historyList.map((item: string) => ({ value: item })))
    return
  }

  try {
    // TODO: 调用API获取搜索建议
    const suggestions = [
      { value: `${queryString} - 案件卷宗` },
      { value: `${queryString} - 公文材料` }
    ]
    cb(suggestions)
  } catch (error) {
    cb([])
  }
}

// 搜索选择
const handleSearchSelect = (item: any) => {
  searchForm.keyword = item.value
  handleSearch()
}

// 筛选模板
const handleFilterTemplate = (command: string | number) => {
  if (command === 'save') {
    // 保存当前筛选条件
    ElMessageBox.prompt('请输入模板名称', '保存筛选模板', {
      confirmButtonText: '保存',
      cancelButtonText: '取消'
    }).then(({ value }) => {
      filterTemplates.value.push({
        id: Date.now(),
        name: value,
        filters: { ...activeFilters.value } as any
      })
      ElMessage.success('筛选模板已保存')
    })
  } else {
    // 应用筛选模板
    const template = filterTemplates.value.find(t => t.id === command)
    if (template) {
      Object.assign(searchForm, template.filters as any)
      handleSearch()
    }
  }
}

// 清除筛选
const clearFilter = (key: string) => {
  (searchForm as any)[key] = key === 'dateRange' ? undefined : ''
  handleSearch()
}

// 查看详情（延后跳转，避免 el-select 等弹出层在卸载时访问已移除的 parentNode）
const viewDetail = (id: number) => {
  nextTick(() => {
    setTimeout(() => {
      router.push(`/case-file/${id}`)
    }, 0)
  })
}

// 下载
const handleDownload = (row: any) => {
  ElMessage.info(`正在下载: ${row.title}`)
  // TODO: 实现下载逻辑
}

// 导出
const handleExport = () => {
  ElMessage.info('正在导出数据...')
  // TODO: 实现导出逻辑
}

// 删除
const handleDelete = async (id: number) => {
  try {
    await caseFileApi.delete(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.message || '删除失败')
  }
}

// 分页大小改变
const handleSizeChange = () => {
  loadData()
}

// 页码改变
const handlePageChange = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.archive-list-view {
  font-family: var(--font-body);
  color: var(--military-text-primary);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 搜索表单网格布局 */
.search-form-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px 16px;
  align-items: start;
}

.search-form-item {
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}

/* 统一标签样式 */
.search-form-item :deep(.military-input-label) {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--military-text-primary);
  min-height: 20px;
  display: flex;
  align-items: center;
}

.search-form-item-keyword .military-input-label.mb-0 {
  margin-bottom: 0;
}

/* 关键词搜索 - 占据4列 */
.search-form-item-keyword {
  grid-column: span 12;
}

/* 案卷类型和状态 - 占据2列 */
.search-form-item:not(.search-form-item-keyword):not(.search-form-item-date):not(.search-form-item-actions) {
  grid-column: span 12;
}

/* 时间范围 - 占据3列 */
.search-form-item-date {
  grid-column: span 12;
}

/* 操作按钮 - 占据3列 */
.search-form-item-actions {
  grid-column: span 12;
}

/* 关键词标签区域的提示样式 */
.search-form-item-keyword .gov-help-icon-tooltip {
  font-size: 14px;
  color: var(--military-text-muted);
  transition: color 0.2s;
  cursor: help;
}

.search-form-item-keyword .gov-help-icon-tooltip:hover {
  color: var(--military-primary);
}

/* 隐藏标签但保留空间（用于按钮区域对齐） */
.invisible {
  visibility: hidden;
  margin-bottom: 10px;
  min-height: 20px;
}

/* 统一输入框高度 - 所有输入控件统一为 44px */
.search-form-item :deep(.el-input__wrapper),
.search-form-item :deep(.el-select .el-input__wrapper),
.search-form-item :deep(.el-autocomplete .el-input__wrapper) {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
}

/* 日期选择器特殊处理 */
.search-form-item :deep(.el-date-editor) {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
  --el-date-editor-width: 100% !important;
}

.search-form-item :deep(.el-date-editor .el-input__wrapper) {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
  padding: 0 12px !important;
}

.search-form-item :deep(.el-range-editor) {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
  padding: 0 12px !important;
}

.search-form-item :deep(.el-range-editor .el-range-input) {
  font-size: 14px !important;
  color: var(--military-text-primary) !important;
}

.search-form-item :deep(.el-range-editor .el-range-separator) {
  color: var(--military-text-muted) !important;
  line-height: 44px !important;
}

/* 确保下拉框内部元素对齐 */
.search-form-item :deep(.el-select .el-input__inner),
.search-form-item :deep(.el-input__inner) {
  height: 40px !important;
  line-height: 40px !important;
}

/* 响应式布局 - 中等屏幕 (768px+) */
@media (min-width: 768px) {
  .search-form-grid {
    gap: 20px 20px;
  }
  
  .search-form-item-keyword {
    grid-column: span 6;
  }
  
  .search-form-item:not(.search-form-item-keyword):not(.search-form-item-date):not(.search-form-item-actions) {
    grid-column: span 3;
  }
  
  .search-form-item-date {
    grid-column: span 6;
  }
  
  .search-form-item-actions {
    grid-column: span 6;
  }
}

/* 响应式布局 - 大屏幕 (1024px+) */
@media (min-width: 1024px) {
  .search-form-grid {
    gap: 24px 20px;
  }
  
  .search-form-item-keyword {
    grid-column: span 4;
  }
  
  .search-form-item:not(.search-form-item-keyword):not(.search-form-item-date):not(.search-form-item-actions) {
    grid-column: span 2;
  }
  
  .search-form-item-date {
    grid-column: span 2;
  }
  
  .search-form-item-actions {
    grid-column: span 2;
  }
}

/* 响应式布局 - 超大屏幕 (1280px+) */
@media (min-width: 1280px) {
  .search-form-grid {
    gap: 24px 24px;
  }
  
  .search-form-item-keyword {
    grid-column: span 4;
  }
  
  .search-form-item:not(.search-form-item-keyword):not(.search-form-item-date):not(.search-form-item-actions) {
    grid-column: span 2;
  }
  
  .search-form-item-date {
    grid-column: span 2;
  }
  
  .search-form-item-actions {
    grid-column: span 2;
  }
}

/* 覆盖 Element Plus 样式以匹配军事风格 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--military-text-primary);
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper),
:deep(.el-autocomplete .el-input__wrapper) {
  box-shadow: none !important;
  border: 2px solid var(--military-border) !important;
  background-color: var(--military-bg-input) !important;
  color: var(--military-text-primary) !important;
  height: 44px !important;
  min-height: 44px !important;
}

/* 日期范围选择器样式 */
:deep(.el-date-editor),
:deep(.el-range-editor) {
  box-shadow: none !important;
  border: 2px solid var(--military-border) !important;
  background-color: var(--military-bg-input) !important;
  color: var(--military-text-primary) !important;
  height: 44px !important;
  min-height: 44px !important;
  border-radius: var(--military-radius-md) !important;
}

:deep(.el-range-editor .el-input__wrapper) {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select .el-input__wrapper:hover),
:deep(.el-autocomplete .el-input__wrapper:hover) {
  border-color: var(--military-border-hover) !important;
  background-color: var(--military-bg-input-hover) !important;
}

:deep(.el-date-editor:hover),
:deep(.el-range-editor:hover) {
  border-color: var(--military-border-hover) !important;
  background-color: var(--military-bg-input-hover) !important;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select .el-input__wrapper.is-focus),
:deep(.el-autocomplete .el-input__wrapper.is-focus) {
  border-color: var(--military-primary) !important;
  background-color: var(--military-bg-input-focus) !important;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-date-editor.is-active),
:deep(.el-range-editor.is-active) {
  border-color: var(--military-primary) !important;
  background-color: var(--military-bg-input-focus) !important;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-input__inner) {
  color: var(--military-text-primary) !important;
}

:deep(.el-tag) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
  color: var(--military-text-primary) !important;
}

.military-pagination {
  color: var(--military-text-primary);
}

/* 视图切换按钮样式 */
.view-mode-switcher {
  background: var(--military-bg-input);
  border: 2px solid var(--military-border);
  border-radius: var(--military-radius-md);
  padding: 2px;
}

.view-mode-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--military-text-muted);
  cursor: pointer;
  border-radius: calc(var(--military-radius-md) - 2px);
  transition: all 0.2s;
}

.view-mode-btn:hover {
  background: var(--military-bg-input-hover);
  color: var(--military-text-primary);
}

.view-mode-btn.active {
  background: var(--military-primary);
  color: #ffffff;
}

.view-mode-btn.active:hover {
  background: var(--military-primary-light);
}

/* 卡片视图样式 */
.case-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 4px;
}

.case-card-item {
  background: var(--military-bg-card);
  border: 2px solid var(--military-border);
  border-radius: var(--military-radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.case-card-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--military-primary);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.case-card-item:hover {
  border-color: var(--military-primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.case-card-item:hover::before {
  transform: scaleX(1);
}

.case-card-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--military-border);
}

.case-card-number {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--military-primary);
  letter-spacing: 0.5px;
}

.case-card-checkbox {
  position: absolute;
  top: 20px;
  right: 20px;
}

.case-card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--military-text-primary);
  margin-top: 8px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-card-body {
  margin-bottom: 16px;
}

.case-card-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 14px;
}

.case-card-info-item:last-child {
  margin-bottom: 0;
}

.case-card-info-item .info-label {
  color: var(--military-text-muted);
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.case-card-info-item .info-value {
  color: var(--military-text-primary);
  flex: 1;
}

.case-card-footer {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--military-border);
}

.case-card-action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--military-border);
  background: var(--military-bg-input);
  color: var(--military-text-primary);
  border-radius: var(--military-radius-md);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.case-card-action-btn:hover {
  background: var(--military-bg-input-hover);
  border-color: var(--military-primary);
  color: var(--military-primary);
}

.case-card-action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px 20px;
}

/* 响应式：卡片视图 */
@media (max-width: 768px) {
  .case-card-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .case-card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .case-card-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1440px) {
  .case-card-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 日期选择器样式 - 中文显示和军事风格 */
:deep(.military-date-picker .el-date-editor) {
  width: 100%;
}

/* 日期选择器下拉面板样式 */
:deep(.el-picker__popper) {
  background: var(--military-bg-card) !important;
  border: 2px solid var(--military-border) !important;
  border-radius: var(--military-radius-md) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

/* 日期选择器面板头部 */
:deep(.el-picker__popper .el-picker-panel__header) {
  background: var(--military-bg-card) !important;
  border-bottom: 1px solid var(--military-border) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-picker-panel__header button) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-picker-panel__header button:hover) {
  color: var(--military-primary) !important;
  background: var(--military-bg-input-hover) !important;
}

:deep(.el-picker__popper .el-picker-panel__header .el-picker-panel__icon-btn) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-picker-panel__header .el-picker-panel__icon-btn:hover) {
  color: var(--military-primary) !important;
}

/* 日期选择器面板内容 */
:deep(.el-picker__popper .el-picker-panel__body) {
  background: var(--military-bg-card) !important;
  color: var(--military-text-primary) !important;
}

/* 日期选择器星期标题 */
:deep(.el-picker__popper .el-date-table th) {
  color: var(--military-text-muted) !important;
  font-weight: 600 !important;
  border-bottom: 1px solid var(--military-border) !important;
}

/* 日期选择器日期单元格 */
:deep(.el-picker__popper .el-date-table td) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-date-table td .available) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-date-table td .available:hover) {
  background: var(--military-bg-input-hover) !important;
  color: var(--military-primary) !important;
}

/* 当前日期 */
:deep(.el-picker__popper .el-date-table td.today .el-date-table__cell) {
  color: var(--military-primary) !important;
  font-weight: 600 !important;
}

/* 选中的日期 */
:deep(.el-picker__popper .el-date-table td.current:not(.disabled) .el-date-table__cell) {
  background: var(--military-primary) !important;
  color: #ffffff !important;
}

/* 日期范围选中区域 */
:deep(.el-picker__popper .el-date-table td.in-range .el-date-table__cell) {
  background: rgba(59, 130, 246, 0.1) !important;
}

:deep(.el-picker__popper .el-date-table td.start-date .el-date-table__cell),
:deep(.el-picker__popper .el-date-table td.end-date .el-date-table__cell) {
  background: var(--military-primary) !important;
  color: #ffffff !important;
}

/* 禁用日期 */
:deep(.el-picker__popper .el-date-table td.disabled .el-date-table__cell) {
  color: var(--military-text-muted) !important;
  opacity: 0.5 !important;
}

/* 月份选择器 */
:deep(.el-picker__popper .el-month-table td .cell) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-month-table td .cell:hover) {
  background: var(--military-bg-input-hover) !important;
  color: var(--military-primary) !important;
}

:deep(.el-picker__popper .el-month-table td.current .cell) {
  color: var(--military-primary) !important;
  font-weight: 600 !important;
}

/* 年份选择器 */
:deep(.el-picker__popper .el-year-table td .cell) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-year-table td .cell:hover) {
  background: var(--military-bg-input-hover) !important;
  color: var(--military-primary) !important;
}

:deep(.el-picker__popper .el-year-table td.current .cell) {
  color: var(--military-primary) !important;
  font-weight: 600 !important;
}

/* 日期选择器底部按钮 */
:deep(.el-picker__popper .el-picker-panel__footer) {
  background: var(--military-bg-card) !important;
  border-top: 1px solid var(--military-border) !important;
}

:deep(.el-picker__popper .el-picker-panel__footer button) {
  color: var(--military-text-primary) !important;
}

:deep(.el-picker__popper .el-picker-panel__footer button:hover) {
  color: var(--military-primary) !important;
  background: var(--military-bg-input-hover) !important;
}
</style>
