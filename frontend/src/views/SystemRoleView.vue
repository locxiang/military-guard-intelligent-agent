<template>
  <div class="system-role-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 页面标题和操作栏 -->
    <div class="mb-6 military-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <h2 class="text-2xl font-heading font-bold military-text-primary mb-2">角色权限</h2>
          <p class="text-sm military-text-muted">管理角色与可访问功能范围，支持自定义角色与权限分配</p>
        </div>
        <button class="military-button flex items-center gap-2 w-full sm:w-auto" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          <span>新增角色</span>
        </button>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="military-text-muted text-xs">操作说明</span>
        <el-tooltip
          content="角色权限用于控制不同人员能使用哪些功能，请按实际职责分配，避免越权"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <Warning />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="military-card mb-6 max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">搜索筛选</h3>
        <p class="text-sm military-text-muted mt-1">按角色名称、编码或状态筛选</p>
      </div>
      <el-form :model="searchForm" class="flex flex-col sm:flex-row flex-wrap gap-4 max-w-full">
        <el-form-item class="w-full sm:w-auto sm:flex-1 min-w-0">
          <label class="military-input-label">角色名称</label>
          <el-input
            v-model="searchForm.name"
            placeholder="请输入角色名称"
            clearable
            class="military-input w-full sm:max-w-[220px]"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">角色编码</label>
          <el-input
            v-model="searchForm.code"
            placeholder="如 admin、archivist"
            clearable
            class="w-full sm:w-[180px]"
          />
        </el-form-item>
        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">状态</label>
          <el-select
            v-model="searchForm.status"
            placeholder="全部"
            clearable
            class="w-full sm:w-[120px]"
          >
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
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

    <!-- 角色列表 -->
    <div class="military-card relative max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">角色列表</h3>
        <p class="text-sm military-text-muted mt-1">系统内所有角色及权限范围</p>
      </div>
      <div class="overflow-x-auto max-w-full">
        <el-table
          :data="filteredRoleList"
          v-loading="loading"
          stripe
          style="width: 100%; min-width: 900px"
          class="military-table"
          :header-cell-style="{
            background: 'var(--military-bg-card)',
            color: 'var(--military-text-primary)',
            fontWeight: '600'
          }"
        >
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="角色名称" width="140" min-width="140" show-overflow-tooltip />
          <el-table-column prop="code" label="角色编码" width="120" min-width="120" />
          <el-table-column prop="description" label="说明" min-width="180" show-overflow-tooltip />
          <el-table-column label="权限范围" min-width="200">
            <template #default="{ row }">
              <span class="text-sm military-text-muted">{{ getPermissionSummary(row.permissions) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90" min-width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                {{ row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="160" min-width="160">
            <template #default="{ row }">
              <span class="text-xs sm:text-sm">{{ formatDate(row.createdAt) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" min-width="260" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-1 flex-nowrap">
                <button
                  class="military-button-secondary military-button-sm flex items-center gap-1 whitespace-nowrap"
                  @click="handleEdit(row)"
                  title="编辑角色信息"
                >
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </button>
                <button
                  class="military-button-secondary military-button-sm flex items-center gap-1 whitespace-nowrap"
                  @click="handlePermission(row)"
                  title="配置可访问功能"
                >
                  <el-icon><Key /></el-icon>
                  <span>权限配置</span>
                </button>
                <el-popconfirm
                  v-if="row.code !== 'admin'"
                  title="确定要删除该角色吗？已分配该角色的用户将失去对应权限。"
                  confirm-button-text="确认删除"
                  cancel-button-text="取消"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <button
                      class="military-button-danger military-button-sm"
                      title="删除角色"
                    >
                      <el-icon><Delete /></el-icon>
                      <span>删除</span>
                    </button>
                  </template>
                </el-popconfirm>
                <el-tooltip v-else content="系统管理员角色不可删除" placement="top">
                  <span class="inline-block">
                    <button class="military-button-secondary military-button-sm" disabled>
                      <el-icon><Delete /></el-icon>
                      <span>删除</span>
                    </button>
                  </span>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="roleDialogTitle"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleFormRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="roleForm.name"
            placeholder="如：档案管理员"
            clearable
            class="military-input"
          />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input
            v-model="roleForm.code"
            placeholder="英文标识，如 archivist"
            :disabled="isEditRole"
            clearable
            class="military-input"
          />
          <div v-if="!isEditRole" class="text-xs military-text-muted mt-1">编码创建后不可修改，用于系统内部识别</div>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="简要说明该角色的职责与使用场景"
            class="military-input"
          />
        </el-form-item>
        <el-form-item v-if="isEditRole" label="状态" prop="status">
          <el-radio-group v-model="roleForm.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="military-button-secondary" @click="roleDialogVisible = false">取消</el-button>
          <el-button class="military-button" type="primary" @click="handleRoleSubmit" :loading="submitting">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限配置"
      width="560px"
      :close-on-click-modal="false"
    >
      <p class="text-sm military-text-muted mb-4">
        为角色「<strong class="military-text-primary">{{ currentRoleName }}</strong>」勾选可访问的功能菜单，未勾选的功能将不在侧栏显示且无法访问。
      </p>
      <el-tree
        ref="permissionTreeRef"
        :data="permissionTree"
        show-checkbox
        node-key="id"
        :default-expand-all="true"
        :props="{ label: 'name', children: 'children' }"
        class="military-permission-tree"
      />
      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="military-button-secondary" @click="permissionDialogVisible = false">取消</el-button>
          <el-button class="military-button" type="primary" @click="handlePermissionSubmit" :loading="submitting">
            保存权限
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, Key, Warning } from '@element-plus/icons-vue'
import type ElTree from 'element-plus/es/components/tree/src/tree.vue'

// 角色类型（前端 demo 用）
interface Role {
  id: number
  name: string
  code: string
  description: string
  permissions: string[]
  status: 0 | 1
  createdAt: string
}

// 权限树节点
interface PermissionNode {
  id: string
  name: string
  children?: PermissionNode[]
}

// 拟真 demo 角色数据
const demoRoles = ref<Role[]>([
  {
    id: 1,
    name: '系统管理员',
    code: 'admin',
    description: '拥有系统全部功能权限，负责用户、角色、配置与审计管理',
    permissions: ['dashboard', 'case-file', 'doc-generate', 'content-review', 'knowledge-graph', 'statistics', 'system'],
    status: 1,
    createdAt: '2024-01-15 09:00:00'
  },
  {
    id: 2,
    name: '档案管理员',
    code: 'archivist',
    description: '负责案件档案的导入、整理、审核入库与检索',
    permissions: ['dashboard', 'case-file', 'doc-generate/case', 'template'],
    status: 1,
    createdAt: '2024-02-01 10:30:00'
  },
  {
    id: 3,
    name: '卷宗审核员',
    code: 'reviewer',
    description: '对待入库卷宗进行审核与分类',
    permissions: ['dashboard', 'case-file', 'case-file/classification', 'case-file/search'],
    status: 1,
    createdAt: '2024-02-10 14:00:00'
  },
  {
    id: 4,
    name: '普通办案人员',
    code: 'user',
    description: '日常办案人员，可查看案件、检索与使用文档生成等基础功能',
    permissions: ['dashboard', 'case-file', 'case-file/search', 'doc-generate', 'content-review'],
    status: 1,
    createdAt: '2024-03-01 08:00:00'
  }
])

// 权限树结构（按业务模块，便于业务人员理解）
const permissionTreeData: PermissionNode[] = [
  { id: 'dashboard', name: '工作台' },
  {
    id: 'case-file',
    name: '案件档案管理',
    children: [
      { id: 'case-file-list', name: '案件列表' },
      { id: 'case-file-import', name: '案件导入' },
      { id: 'case-file-classification', name: '卷宗审核入库' },
      { id: 'case-file-search', name: '案件检索' },
      { id: 'case-file-progress', name: '导入进度管理' }
    ]
  },
  {
    id: 'doc-generate',
    name: '智能文档生成',
    children: [
      { id: 'doc-generate-case', name: '案件卷宗生成' },
      { id: 'doc-generate-official', name: '公文助手' },
      { id: 'doc-generate-report', name: '报告生成器' },
      { id: 'doc-generate-meeting', name: '会议纪要生成' },
      { id: 'template', name: '模板管理' }
    ]
  },
  { id: 'content-review', name: '内容审查' },
  {
    id: 'knowledge-graph',
    name: '知识关联分析',
    children: [
      { id: 'knowledge-graph-query', name: '关联查询' },
      { id: 'knowledge-graph-entity', name: '实体管理' },
      { id: 'knowledge-graph-relation', name: '关系管理' },
      { id: 'knowledge-graph-extract', name: '知识提取' }
    ]
  },
  {
    id: 'statistics',
    name: '数据统计',
    children: [
      { id: 'statistics-main', name: '数据统计' },
      { id: 'statistics-visualization', name: '可视化分析' },
      { id: 'statistics-topic', name: '专题分析' },
      { id: 'statistics-prediction', name: '预测分析' }
    ]
  },
  {
    id: 'system',
    name: '系统管理',
    children: [
      { id: 'system-user', name: '用户管理' },
      { id: 'system-role', name: '角色权限' },
      { id: 'system-config', name: '系统配置' },
      { id: 'system-log', name: '日志审计' },
      { id: 'system-monitor', name: '系统监控' }
    ]
  }
]

const permissionTree = ref<PermissionNode[]>(JSON.parse(JSON.stringify(permissionTreeData)))

// 扁平化所有权限 id（用于树勾选）
function getAllPermissionIds(nodes: PermissionNode[]): string[] {
  const ids: string[] = []
  function walk(list: PermissionNode[]) {
    list.forEach((n) => {
      ids.push(n.id)
      if (n.children?.length) walk(n.children)
    })
  }
  walk(nodes)
  return ids
}

const allPermissionIds = getAllPermissionIds(permissionTreeData)

// 根据角色 permissions 转成树节点 id（demo 里角色存的是模块简写，这里做映射）
function rolePermissionsToTreeKeys(permissions: string[]): string[] {
  const keys: string[] = []
  permissions.forEach((p) => {
    if (p === 'dashboard') keys.push('dashboard')
    if (p === 'case-file') {
      keys.push('case-file', 'case-file-list', 'case-file-import', 'case-file-classification', 'case-file-search', 'case-file-progress')
    }
    if (p.startsWith('doc-generate')) {
      keys.push('doc-generate', 'doc-generate-case', 'doc-generate-official', 'doc-generate-report', 'doc-generate-meeting', 'template')
    }
    if (p === 'content-review') keys.push('content-review')
    if (p === 'knowledge-graph') {
      keys.push('knowledge-graph', 'knowledge-graph-query', 'knowledge-graph-entity', 'knowledge-graph-relation', 'knowledge-graph-extract')
    }
    if (p === 'statistics') {
      keys.push('statistics', 'statistics-main', 'statistics-visualization', 'statistics-topic', 'statistics-prediction')
    }
    if (p === 'system') {
      keys.push('system', 'system-user', 'system-role', 'system-config', 'system-log', 'system-monitor')
    }
  })
  return [...new Set(keys)]
}

const loading = ref(false)
const submitting = ref(false)
const searchForm = reactive({
  name: '',
  code: '',
  status: undefined as 0 | 1 | undefined
})

const roleList = ref<Role[]>([])
const roleDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEditRole = ref(false)
const currentRoleId = ref<number | null>(null)
const currentRoleName = ref('')
const roleFormRef = ref<FormInstance>()
const permissionTreeRef = ref<InstanceType<typeof ElTree>>()

const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  status: 1 as 0 | 1
})

const roleFormRules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '编码为小写字母开头，仅允许小写字母、数字和下划线', trigger: 'blur' }
  ]
}

const filteredRoleList = computed(() => {
  let list = roleList.value
  if (searchForm.name?.trim()) {
    const kw = searchForm.name.trim().toLowerCase()
    list = list.filter((r) => r.name.toLowerCase().includes(kw))
  }
  if (searchForm.code?.trim()) {
    const kw = searchForm.code.trim().toLowerCase()
    list = list.filter((r) => r.code.toLowerCase().includes(kw))
  }
  if (searchForm.status !== undefined && searchForm.status !== null) {
    list = list.filter((r) => r.status === searchForm.status)
  }
  return list
})

function formatDate(str: string) {
  if (!str) return '-'
  return str
}

function getPermissionSummary(permissions: string[]) {
  const labels: Record<string, string> = {
    dashboard: '工作台',
    'case-file': '案件档案',
    'doc-generate': '智能文档',
    'content-review': '内容审查',
    'knowledge-graph': '知识关联',
    statistics: '数据统计',
    system: '系统管理'
  }
  const names = permissions.map((p) => labels[p] || p).filter(Boolean)
  return names.length ? names.join('、') : '未配置'
}

function handleSearch() {
  // 筛选由 computed 完成，无需请求
}

function handleReset() {
  searchForm.name = ''
  searchForm.code = ''
  searchForm.status = undefined
}

const roleDialogTitle = computed(() => (isEditRole.value ? '编辑角色' : '新增角色'))

function handleAdd() {
  isEditRole.value = false
  currentRoleId.value = null
  roleForm.name = ''
  roleForm.code = ''
  roleForm.description = ''
  roleForm.status = 1
  roleDialogVisible.value = true
}

function handleEdit(row: Role) {
  isEditRole.value = true
  currentRoleId.value = row.id
  roleForm.name = row.name
  roleForm.code = row.code
  roleForm.description = row.description
  roleForm.status = row.status
  roleDialogVisible.value = true
}

function handleRoleSubmit() {
  roleFormRef.value?.validate((valid) => {
    if (!valid) return
    submitting.value = true
    setTimeout(() => {
      if (isEditRole.value && currentRoleId.value) {
        const r = roleList.value.find((x) => x.id === currentRoleId.value)
        if (r) {
          r.name = roleForm.name
          r.description = roleForm.description
          r.status = roleForm.status
        }
        ElMessage.success('角色信息已更新')
      } else {
        const codeExists = roleList.value.some((x) => x.code === roleForm.code)
        if (codeExists) {
          ElMessage.warning('该角色编码已存在')
          submitting.value = false
          return
        }
        const newId = Math.max(...roleList.value.map((x) => x.id), 0) + 1
        roleList.value.push({
          id: newId,
          name: roleForm.name,
          code: roleForm.code,
          description: roleForm.description,
          permissions: ['dashboard'],
          status: 1,
          createdAt: new Date().toLocaleString('sv-SE').replace('T', ' ').slice(0, 19)
        })
        ElMessage.success('角色已新增，请为其配置权限')
      }
      submitting.value = false
      roleDialogVisible.value = false
    }, 400)
  })
}

function handlePermission(row: Role) {
  currentRoleId.value = row.id
  currentRoleName.value = row.name
  permissionTree.value = JSON.parse(JSON.stringify(permissionTreeData))
  permissionDialogVisible.value = true
  nextTick(() => {
    const keys = rolePermissionsToTreeKeys(row.permissions)
    permissionTreeRef.value?.setCheckedKeys(keys)
  })
}

function handlePermissionSubmit() {
  const tree = permissionTreeRef.value
  if (!tree) return
  submitting.value = true
  setTimeout(() => {
    const checked = tree.getCheckedKeys() as string[]
    const half = tree.getHalfCheckedKeys() as string[]
    const keys = [...checked, ...half]
    const role = roleList.value.find((r) => r.id === currentRoleId.value)
    if (role) {
      // 简化存储为模块级（与 demo 一致）
      const mods = new Set<string>()
      if (keys.includes('dashboard')) mods.add('dashboard')
      if (keys.some((k) => k.startsWith('case-file'))) mods.add('case-file')
      if (keys.some((k) => k.startsWith('doc-generate') || k === 'template')) mods.add('doc-generate')
      if (keys.includes('content-review')) mods.add('content-review')
      if (keys.some((k) => k.startsWith('knowledge-graph'))) mods.add('knowledge-graph')
      if (keys.some((k) => k.startsWith('statistics'))) mods.add('statistics')
      if (keys.some((k) => k.startsWith('system'))) mods.add('system')
      role.permissions = Array.from(mods)
    }
    submitting.value = false
    permissionDialogVisible.value = false
    ElMessage.success('权限已保存')
  }, 300)
}

function handleDelete(id: number) {
  roleList.value = roleList.value.filter((r) => r.id !== id)
  ElMessage.success('角色已删除')
}

onMounted(() => {
  roleList.value = JSON.parse(JSON.stringify(demoRoles.value))
})
</script>

<style scoped>
.system-role-view {
  font-family: var(--font-body);
}
.military-permission-tree {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px 0;
}
:deep(.el-tree-node__label) {
  font-size: 14px;
}
</style>
