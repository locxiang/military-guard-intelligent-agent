<template>
  <div class="system-user-view min-h-full p-3 sm:p-4 max-w-full overflow-x-hidden">
    <!-- 页面标题和操作栏 -->
    <div class="mb-6 military-card">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex-1">
          <h2 class="text-2xl font-heading font-bold military-text-primary mb-2">用户管理</h2>
          <p class="text-sm military-text-muted">管理用户账号，支持用户注册、认证、授权、配置与生命周期管理</p>
        </div>
        <button
          class="military-button flex items-center gap-2 w-full sm:w-auto"
          @click="handleAdd"
        >
          <el-icon><Plus /></el-icon>
          <span>新增用户</span>
        </button>
      </div>
      <div class="flex items-center gap-2 mt-4">
        <span class="military-text-muted text-xs">操作说明</span>
        <el-tooltip
          content="用户管理功能支持用户的增删改查、角色分配、状态管理，请谨慎操作，确保系统安全"
          placement="top"
          :show-after="300"
        >
          <el-icon class="gov-help-icon-tooltip">
            <Warning />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="military-card mb-6 max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">搜索筛选</h3>
        <p class="text-sm military-text-muted mt-1">按条件搜索和筛选用户</p>
      </div>
      <el-form :model="searchForm" class="flex flex-col sm:flex-row flex-wrap gap-4 max-w-full">
        <el-form-item class="w-full sm:w-auto sm:flex-1 min-w-0">
          <label class="military-input-label">关键词</label>
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入用户名、真实姓名或部门"
            clearable
            class="military-input w-full sm:max-w-[300px]"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">角色</label>
          <el-select
            v-model="searchForm.role"
            placeholder="请选择角色"
            clearable
            class="w-full sm:w-[160px]"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item class="w-full sm:w-auto min-w-0">
          <label class="military-input-label">状态</label>
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            class="w-full sm:w-[160px]"
          >
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>

        <el-form-item class="w-full sm:w-auto min-w-0">
          <div class="flex items-center gap-3 mt-7">
            <button class="military-button flex items-center gap-2" @click="handleSearch">
              <el-icon><Search /></el-icon>
              <span>执行搜索</span>
            </button>
            <button class="military-button-secondary flex items-center gap-2" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              <span>重置条件</span>
            </button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 用户列表 -->
    <div class="military-card relative max-w-full overflow-hidden">
      <div class="military-card-header mb-4">
        <h3 class="text-lg font-title font-bold military-text-primary">用户列表</h3>
        <p class="text-sm military-text-muted mt-1">系统所有用户信息列表</p>
      </div>
      <div class="overflow-x-auto max-w-full">
        <el-table
          :data="userList"
          v-loading="loading"
          stripe
          style="width: 100%; min-width: 800px"
          class="military-table"
          :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)', fontWeight: '600' }"
          :row-style="{ background: 'transparent' }"
          :cell-style="{ background: 'transparent' }"
        >
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="username" label="用户名" width="150" min-width="150" />
          <el-table-column prop="realName" label="真实姓名" width="120" min-width="120" />
          <el-table-column prop="department" label="部门" width="150" min-width="150" show-overflow-tooltip />
          <el-table-column prop="role" label="角色" width="100" min-width="100">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                {{ row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
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
          <el-table-column label="操作" width="280" min-width="280" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-1 flex-nowrap">
                <button
                  class="military-button-secondary military-button-sm flex items-center gap-1 whitespace-nowrap"
                  @click="handleEdit(row)"
                  title="编辑用户信息"
                >
                  <el-icon><Edit /></el-icon>
                  <span>编辑</span>
                </button>
                <button
                  :class="row.status === 1 ? 'military-button-secondary military-button-sm' : 'military-button military-button-sm'"
                  class="flex items-center gap-1 whitespace-nowrap"
                  @click="handleToggleStatus(row)"
                  :title="row.status === 1 ? '禁用用户' : '启用用户'"
                >
                  <el-icon v-if="row.status === 1"><Lock /></el-icon>
                  <el-icon v-else><Unlock /></el-icon>
                  <span>{{ row.status === 1 ? '禁用' : '启用' }}</span>
                </button>
                <button
                  class="military-button-secondary military-button-sm flex items-center gap-1 whitespace-nowrap"
                  @click="handleResetPassword(row)"
                  title="重置用户密码"
                >
                  <el-icon><Key /></el-icon>
                  <span>重置密码</span>
                </button>
                <el-popconfirm
                  title="确定要删除该用户吗？此操作不可恢复，请谨慎操作。"
                  confirm-button-text="确认删除"
                  cancel-button-text="取消"
                  @confirm="handleDelete(row.id)"
                >
                  <template #reference>
                    <button
                      class="military-button-danger military-button-sm"
                      title="删除用户"
                    >
                      <el-icon><Delete /></el-icon>
                      <span>删除</span>
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名（3-50个字符）"
            :disabled="isEdit"
            clearable
            class="military-input"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码（至少6个字符）"
            show-password
            clearable
            class="military-input"
          />
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input
            v-model="userForm.realName"
            placeholder="请输入真实姓名"
            clearable
            class="military-input"
          />
        </el-form-item>

        <el-form-item label="部门" prop="department">
          <el-input
            v-model="userForm.department"
            placeholder="请输入部门"
            clearable
            class="military-input"
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select
            v-model="userForm.role"
            placeholder="请选择角色"
            class="w-full"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-radio-group v-model="userForm.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="military-button-secondary" @click="dialogVisible = false">取消</el-button>
          <el-button class="military-button" type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="重置密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordFormRules"
        label-width="100px"
      >
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="passwordForm.password"
            type="password"
            placeholder="请输入新密码（至少6个字符）"
            show-password
            clearable
            class="military-input"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
            class="military-input"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-2">
          <el-button class="military-button-secondary" @click="passwordDialogVisible = false">取消</el-button>
          <el-button class="military-button" type="primary" @click="handlePasswordSubmit" :loading="submitting">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, Key, Lock, Unlock } from '@element-plus/icons-vue'
import { userApi, type User, type UserCreateRequest, type UserUpdateRequest } from '@/api/user'
import { encryptPassword } from '@/utils/rsa'
import { RSA_PUBLIC_KEY } from '@/config/rsaPublicKey'

// 加载状态
const loading = ref(false)
const submitting = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role: '' as '' | 'admin' | 'user',
  status: undefined as 0 | 1 | undefined
})

// 用户列表
const userList = ref<User[]>([])
const total = ref(0)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20
})

// 对话框
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const isEdit = ref(false)
const currentUserId = ref<number | null>(null)

// 表单引用
const userFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 用户表单
const userForm = reactive<UserCreateRequest & { status?: 0 | 1 }>({
  username: '',
  password: '',
  realName: '',
  department: '',
  role: 'user',
  status: 1
})

// 密码表单
const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const userFormRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度为 6 到 100 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 密码表单验证规则
const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== passwordForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordFormRules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度为 6 到 100 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 计算对话框标题
const dialogTitle = computed(() => isEdit.value ? '编辑用户' : '新增用户')

// 加载用户列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchForm.keyword || undefined,
      role: searchForm.role || undefined,
      status: searchForm.status,
      page: pagination.page,
      pageSize: pagination.pageSize
    }
    
    const response = await userApi.getList(params)
    userList.value = response.data
    total.value = response.page.total
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.role = ''
  searchForm.status = undefined
  pagination.page = 1
  loadData()
}

// 分页变化
const handleSizeChange = () => {
  loadData()
}

const handlePageChange = () => {
  loadData()
}

// 新增用户
const handleAdd = () => {
  isEdit.value = false
  currentUserId.value = null
  Object.assign(userForm, {
    username: '',
    password: '',
    realName: '',
    department: '',
    role: 'user',
    status: 1
  })
  dialogVisible.value = true
  nextTick(() => {
    userFormRef.value?.clearValidate()
  })
}

// 编辑用户
const handleEdit = async (row: User) => {
  isEdit.value = true
  currentUserId.value = row.id
  try {
    const user = await userApi.getDetail(row.id)
    Object.assign(userForm, {
      username: user.username,
      realName: user.realName || '',
      department: user.department || '',
      role: user.role,
      status: user.status
    })
    dialogVisible.value = true
    nextTick(() => {
      userFormRef.value?.clearValidate()
    })
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '获取用户详情失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value && currentUserId.value) {
          // 更新用户
          const updateData: UserUpdateRequest = {
            realName: userForm.realName || undefined,
            department: userForm.department || undefined,
            role: userForm.role,
            status: userForm.status
          }
          await userApi.update(currentUserId.value, updateData)
          ElMessage.success('更新用户成功')
        } else {
          // 创建用户
          const createData: UserCreateRequest = {
            username: userForm.username,
            password: userForm.password,
            realName: userForm.realName || undefined,
            department: userForm.department || undefined,
            role: userForm.role || 'user'
          }
          // 加密密码
          createData.password = encryptPassword(createData.password, RSA_PUBLIC_KEY)
          await userApi.create({ ...createData, encrypted: true } as any)
          ElMessage.success('创建用户成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 删除用户
const handleDelete = async (id: number) => {
  try {
    await userApi.delete(id)
    ElMessage.success('删除用户成功')
    loadData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '删除用户失败')
  }
}

// 启用/禁用用户
const handleToggleStatus = async (row: User) => {
  const newStatus = row.status === 1 ? 0 : 1
  const statusText = newStatus === 1 ? '启用' : '禁用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${statusText}该用户吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await userApi.updateStatus(row.id, newStatus)
    ElMessage.success(`${statusText}用户成功`)
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || `${statusText}用户失败`)
    }
  }
}

// 重置密码
const handleResetPassword = (row: User) => {
  currentUserId.value = row.id
  passwordForm.password = ''
  passwordForm.confirmPassword = ''
  passwordDialogVisible.value = true
  nextTick(() => {
    passwordFormRef.value?.clearValidate()
  })
}

// 提交密码重置
const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value || !currentUserId.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // 加密密码
        const encryptedPassword = encryptPassword(passwordForm.password, RSA_PUBLIC_KEY)
        await userApi.resetPassword(currentUserId.value!, encryptedPassword, true)
        ElMessage.success('重置密码成功')
        passwordDialogVisible.value = false
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.message || '重置密码失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 格式化日期
const formatDate = (date: Date | string) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.system-user-view {
  font-family: var(--font-body);
}
</style>
