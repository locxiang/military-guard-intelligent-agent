<template>
  <div class="app-layout min-h-screen relative military-theme">
    <!-- 军事风格背景 -->
    <div class="military-background"></div>

    <!-- 顶部导航栏 - 军事风格，响应式 -->
    <header class="sticky top-0 z-50 w-full">
      <div class="px-4 sm:px-6 py-3 sm:py-4 military-top-bar">
        <div class="flex items-center justify-between w-full">
          <!-- Logo 和标题 -->
          <div class="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
            <div class="flex-shrink-0">
              <h1 class="text-base sm:text-lg lg:text-xl font-title font-semibold truncate military-text-primary">
                <span class="hidden sm:inline">保卫核心业务智能体平台</span>
                <span class="sm:hidden">保卫智能体</span>
              </h1>
            </div>
          </div>

          <!-- 右侧操作区 -->
          <div class="flex items-center space-x-2 sm:space-x-4 flex-shrink-0 ml-auto">
            <!-- 消息通知 -->
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="cursor-pointer">
              <div class="military-button-secondary p-2 rounded-lg">
                <el-icon :size="18" class="sm:w-5 sm:h-5 military-text-primary">
                  <Bell />
                </el-icon>
              </div>
            </el-badge>

            <!-- 用户信息 -->
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="flex items-center space-x-1 sm:space-x-2 cursor-pointer military-button-secondary px-2 sm:px-3 py-2 rounded-lg">
                <el-avatar :size="28" class="sm:w-8 sm:h-8" :src="userAvatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="text-xs sm:text-sm font-medium hidden md:inline military-text-primary">{{ userName }}</span>
                <el-icon class="hidden sm:inline military-text-muted"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    <span class="ml-2">个人中心</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    <span class="ml-2">系统设置</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    <span class="ml-2">退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </header>

    <div class="flex flex-col lg:flex-row pt-4 sm:pt-6 lg:pt-8">
      <!-- 移动端抽屉菜单 -->
      <el-drawer
        v-model="isMobileMenuOpen"
        title="导航菜单"
        direction="ltr"
        size="280px"
        class="lg:hidden"
      >
        <el-menu
          :default-active="activeMenu"
          router
          :unique-opened="true"
          class="border-0 bg-transparent"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/dashboard" class="gov-menu-item">
            <el-icon><Odometer /></el-icon>
            <template #title>工作台</template>
          </el-menu-item>
          <el-sub-menu index="case-file" class="gov-submenu">
            <template #title>
              <el-icon><Files /></el-icon>
              <span>案件档案管理</span>
            </template>
            <el-menu-item index="/case-file" class="gov-menu-item-sub">案件列表</el-menu-item>
            <el-menu-item index="/case-file/import" class="gov-menu-item-sub">案件导入</el-menu-item>
            <el-menu-item index="/case-file/progress" class="gov-menu-item-sub">导入进度管理</el-menu-item>
            <el-menu-item index="/case-file/classification" class="gov-menu-item-sub">案件分类</el-menu-item>
            <el-menu-item index="/case-file/search" class="gov-menu-item-sub">案件检索</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="intelligence" class="gov-submenu">
            <template #title>
              <el-icon><MagicStick /></el-icon>
              <span>智能文档生成</span>
            </template>
            <el-menu-item index="/doc-generate/case" class="gov-menu-item-sub">案件卷宗生成</el-menu-item>
            <el-menu-item index="/doc-generate/official" class="gov-menu-item-sub">公文助手</el-menu-item>
            <el-menu-item index="/doc-generate/report" class="gov-menu-item-sub">报告生成器</el-menu-item>
            <el-menu-item index="/doc-generate/meeting" class="gov-menu-item-sub">会议纪要生成</el-menu-item>
            <el-menu-item index="/template" class="gov-menu-item-sub">模板管理</el-menu-item>
            <el-menu-item index="/content-review" class="gov-menu-item-sub">内容审查</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="knowledge" class="gov-submenu">
            <template #title>
              <el-icon><Connection /></el-icon>
              <span>知识关联分析</span>
            </template>
            <el-menu-item index="/knowledge-graph" class="gov-menu-item-sub">关联查询</el-menu-item>
            <el-menu-item index="/knowledge-graph/entity" class="gov-menu-item-sub">实体管理</el-menu-item>
            <el-menu-item index="/knowledge-graph/relation" class="gov-menu-item-sub">关系管理</el-menu-item>
            <el-menu-item index="/knowledge-graph/extract" class="gov-menu-item-sub">知识提取</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="statistics" class="gov-submenu">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>数据统计分析</span>
            </template>
            <el-menu-item index="/statistics" class="gov-menu-item-sub">数据统计</el-menu-item>
            <el-menu-item index="/statistics/visualization" class="gov-menu-item-sub">可视化分析</el-menu-item>
            <el-menu-item index="/statistics/topic" class="gov-menu-item-sub">专题分析</el-menu-item>
            <el-menu-item index="/statistics/prediction" class="gov-menu-item-sub">预测分析</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="system" class="gov-submenu">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/user" class="gov-menu-item-sub">用户管理</el-menu-item>
            <el-menu-item index="/system/role" class="gov-menu-item-sub">角色权限</el-menu-item>
            <el-menu-item index="/system/config" class="gov-menu-item-sub">系统配置</el-menu-item>
            <el-menu-item index="/system/log" class="gov-menu-item-sub">日志审计</el-menu-item>
            <el-menu-item index="/system/monitor" class="gov-menu-item-sub">系统监控</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-drawer>

      <!-- 侧边栏 - 军事风格，桌面端显示 -->
      <aside
          class="sidebar hidden lg:block lg:ml-4"
          style="width: 256px; min-width: 256px; max-width: 256px;"
      >
        <div class="military-card rounded-xl lg:rounded-2xl p-3 lg:p-4 sticky top-14 lg:top-16">
          <div class="flex flex-col">
            <!-- 导航菜单 - 支持二级菜单 -->
            <el-menu
              :default-active="activeMenu"
              :unique-opened="true"
              router
              class="border-0 bg-transparent"
              @select="handleMenuSelect"
            >
              <!-- 工作台 -->
              <el-menu-item index="/dashboard" class="gov-menu-item">
                <el-icon><Odometer /></el-icon>
                <template #title>工作台</template>
              </el-menu-item>

              <!-- 案件档案管理（业务导向命名） -->
              <el-sub-menu index="case-file" class="gov-submenu">
                <template #title>
                  <el-icon><Files /></el-icon>
                  <span>案件档案管理</span>
                </template>
                <el-menu-item index="/case-file" class="gov-menu-item-sub">
                  <el-icon><DocumentCopy /></el-icon>
                  <template #title>案件列表</template>
                </el-menu-item>
                <el-menu-item index="/case-file/import" class="gov-menu-item-sub">
                  <el-icon><Upload /></el-icon>
                  <template #title>案件导入</template>
                </el-menu-item>
                <el-menu-item index="/case-file/progress" class="gov-menu-item-sub">
                  <el-icon><DataAnalysis /></el-icon>
                  <template #title>导入进度管理</template>
                </el-menu-item>
                <el-menu-item index="/case-file/classification" class="gov-menu-item-sub">
                  <el-icon><Collection /></el-icon>
                  <template #title>案件分类</template>
                </el-menu-item>
                <el-menu-item index="/case-file/search" class="gov-menu-item-sub">
                  <el-icon><Search /></el-icon>
                  <template #title>案件检索</template>
                </el-menu-item>
              </el-sub-menu>

              <!-- 智能文档生成（业务导向命名） -->
              <el-sub-menu index="intelligence" class="gov-submenu">
                <template #title>
                  <el-icon><MagicStick /></el-icon>
                  <span>智能文档生成</span>
                </template>
                <el-menu-item index="/doc-generate/case" class="gov-menu-item-sub">
                  <el-icon><FolderOpened /></el-icon>
                  <template #title>案件卷宗生成</template>
                </el-menu-item>
                <el-menu-item index="/doc-generate/official" class="gov-menu-item-sub">
                  <el-icon><EditPen /></el-icon>
                  <template #title>公文助手</template>
                </el-menu-item>
                <el-menu-item index="/doc-generate/report" class="gov-menu-item-sub">
                  <el-icon><Notebook /></el-icon>
                  <template #title>报告生成器</template>
                </el-menu-item>
                <el-menu-item index="/doc-generate/meeting" class="gov-menu-item-sub">
                  <el-icon><VideoPlay /></el-icon>
                  <template #title>会议纪要生成</template>
                </el-menu-item>
                <el-menu-item index="/template" class="gov-menu-item-sub">
                  <el-icon><Files /></el-icon>
                  <template #title>模板管理</template>
                </el-menu-item>
                <el-menu-item index="/content-review" class="gov-menu-item-sub">
                  <el-icon><View /></el-icon>
                  <template #title>内容审查</template>
                </el-menu-item>
              </el-sub-menu>

              <!-- 知识关联分析（业务导向命名） -->
              <el-sub-menu index="knowledge" class="gov-submenu">
                <template #title>
                  <el-icon><Connection /></el-icon>
                  <span>知识关联分析</span>
                </template>
                <el-menu-item index="/knowledge-graph" class="gov-menu-item-sub">
                  <el-icon><Share /></el-icon>
                  <template #title>关联查询</template>
                </el-menu-item>
                <el-menu-item index="/knowledge-graph/entity" class="gov-menu-item-sub">
                  <el-icon><User /></el-icon>
                  <template #title>实体管理</template>
                </el-menu-item>
                <el-menu-item index="/knowledge-graph/relation" class="gov-menu-item-sub">
                  <el-icon><Link /></el-icon>
                  <template #title>关系管理</template>
                </el-menu-item>
                <el-menu-item index="/knowledge-graph/extract" class="gov-menu-item-sub">
                  <el-icon><Reading /></el-icon>
                  <template #title>知识提取</template>
                </el-menu-item>
              </el-sub-menu>

              <!-- 数据统计分析（业务导向命名） -->
              <el-sub-menu index="statistics" class="gov-submenu">
                <template #title>
                  <el-icon><DataAnalysis /></el-icon>
                  <span>数据统计分析</span>
                </template>
                <el-menu-item index="/statistics" class="gov-menu-item-sub">
                  <el-icon><PieChart /></el-icon>
                  <template #title>数据统计</template>
                </el-menu-item>
                <el-menu-item index="/statistics/visualization" class="gov-menu-item-sub">
                  <el-icon><DataLine /></el-icon>
                  <template #title>可视化分析</template>
                </el-menu-item>
                <el-menu-item index="/statistics/topic" class="gov-menu-item-sub">
                  <el-icon><TrendCharts /></el-icon>
                  <template #title>专题分析</template>
                </el-menu-item>
                <el-menu-item index="/statistics/prediction" class="gov-menu-item-sub">
                  <el-icon><Warning /></el-icon>
                  <template #title>预测分析</template>
                </el-menu-item>
              </el-sub-menu>

              <!-- 系统管理 -->
              <el-sub-menu index="system" class="gov-submenu">
                <template #title>
                  <el-icon><Setting /></el-icon>
                  <span>系统管理</span>
                </template>
                <el-menu-item index="/system/user" class="gov-menu-item-sub">
                  <el-icon><UserFilled /></el-icon>
                  <template #title>用户管理</template>
                </el-menu-item>
                <el-menu-item index="/system/role" class="gov-menu-item-sub">
                  <el-icon><Avatar /></el-icon>
                  <template #title>角色权限</template>
                </el-menu-item>
                <el-menu-item index="/system/config" class="gov-menu-item-sub">
                  <el-icon><Tools /></el-icon>
                  <template #title>系统配置</template>
                </el-menu-item>
                <el-menu-item index="/system/log" class="gov-menu-item-sub">
                  <el-icon><DocumentCopy /></el-icon>
                  <template #title>日志审计</template>
                </el-menu-item>
                <el-menu-item index="/system/monitor" class="gov-menu-item-sub">
                  <el-icon><Monitor /></el-icon>
                  <template #title>系统监控</template>
                </el-menu-item>
              </el-sub-menu>
            </el-menu>
          </div>
        </div>
      </aside>

      <!-- 主内容区 - 响应式 padding -->
      <main class="flex-1 min-h-[calc(100vh-4rem)] lg:min-h-[calc(100vh-5rem)] px-2 sm:px-4 lg:px-6 pb-4 sm:pb-6 w-full max-w-full overflow-x-hidden relative z-10 min-w-0">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authApi } from '@/api/auth'
import {
  Bell,
  User,
  ArrowDown,
  Setting,
  SwitchButton,
  Odometer,
  Files,
  Upload,
  Connection,
  DataAnalysis,
  DocumentCopy,
  Collection,
  Search,
  MagicStick,
  FolderOpened,
  EditPen,
  Notebook,
  VideoPlay,
  View,
  Share,
  Link,
  Reading,
  PieChart,
  DataLine,
  TrendCharts,
  Warning,
  UserFilled,
  Avatar,
  Tools,
  Monitor
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 移动端菜单状态
const isMobileMenuOpen = ref(false)

// 用户信息
const getUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr)
      return {
        realName: userInfo.realName || userInfo.username || '管理员',
        username: userInfo.username || '管理员'
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  return {
    realName: '管理员',
    username: '管理员'
  }
}
const userInfo = getUserInfo()
const userName = ref(userInfo.realName)
const userAvatar = ref('')
const unreadCount = ref(3)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
  // 移动端选择菜单后自动关闭
  isMobileMenuOpen.value = false
}

// 用户下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      // 处理登出逻辑
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        )
        
        // 调用登出 API
        try {
          await authApi.logout()
        } catch (error) {
          // 即使 API 调用失败，也要清除本地 token
          console.warn('登出 API 调用失败，但仍将清除本地 token', error)
        }
        
        // 清除本地存储的 token 和用户信息
        localStorage.removeItem('token')
        sessionStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        sessionStorage.removeItem('userInfo')
        
        ElMessage.success('已退出登录')
        
        // 跳转到登录页
        router.push('/login')
      } catch (error) {
        // 用户取消操作，不做任何处理
      }
      break
  }
}
</script>

<style scoped>
.app-layout {
  font-family: var(--font-body);
  color: var(--military-text-primary);
}

/* 顶部栏样式 */
.military-top-bar {
  background: rgba(10, 22, 40, 0.7);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  min-height: 56px; /* 固定最小高度，便于计算间距 */
  display: flex;
  align-items: center;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Element Plus 菜单样式覆盖 - 军事风格 */
:deep(.el-menu) {
  border-right: none;
  background: transparent;
  width: 100% !important;
}

/* 侧边栏固定宽度 */
.sidebar {
  flex-shrink: 0;
}

.sidebar .military-card {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

:deep(.el-menu-item) {
  cursor: pointer;
  border-radius: var(--military-radius-md);
  margin-bottom: 0.5rem;
  transition: all var(--military-transition);
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  color: var(--military-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-menu-item span),
:deep(.el-menu-item .el-menu-item__title) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  display: inline-block;
}

:deep(.el-menu-item:hover) {
  background: var(--military-bg-card-hover);
  border-color: var(--military-border-hover);
  transform: translateX(4px);
}

:deep(.el-menu-item.is-active) {
  background: rgba(59, 130, 246, 0.2);
  border-color: var(--military-primary);
  color: var(--military-primary);
  font-weight: 600;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: var(--military-primary);
}

/* 二级菜单样式 */
:deep(.el-sub-menu) {
  margin-bottom: 0.5rem;
}

:deep(.el-sub-menu__title) {
  border-radius: var(--military-radius-md);
  margin-bottom: 0.25rem;
  transition: all var(--military-transition);
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  cursor: pointer;
  color: var(--military-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-sub-menu__title span) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  display: inline-block;
}

:deep(.el-sub-menu__title:hover) {
  background: var(--military-bg-card-hover);
  border-color: var(--military-border-hover);
}

:deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
  background: rgba(59, 130, 246, 0.2);
  border-color: var(--military-primary);
  color: var(--military-primary);
}

:deep(.el-sub-menu.is-opened > .el-sub-menu__title .el-icon) {
  color: var(--military-primary);
}

:deep(.el-menu-item.gov-menu-item-sub) {
  margin-left: 0.5rem;
  margin-bottom: 0.25rem;
  padding-left: 2.5rem !important;
  border-radius: var(--military-radius-sm);
  background: var(--military-bg-card);
  border: 1px solid var(--military-border);
  color: var(--military-text-secondary);
}

:deep(.el-menu-item.gov-menu-item-sub:hover) {
  background: var(--military-bg-card-hover);
  border-color: var(--military-border-hover);
}

:deep(.el-menu-item.gov-menu-item-sub.is-active) {
  background: rgba(59, 130, 246, 0.25);
  border-color: var(--military-primary);
  color: var(--military-primary);
  font-weight: 500;
}

/* Element Plus 按钮样式覆盖 - 军事风格 */
:deep(.el-button) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-button:hover) {
  background: var(--military-bg-card-hover) !important;
  border-color: var(--military-border-hover) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-button.is-circle) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-button.is-circle:hover) {
  background: var(--military-bg-card-hover) !important;
  border-color: var(--military-border-hover) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-button .el-icon) {
  color: var(--military-text-primary) !important;
}

/* 下拉菜单军事风格 - 全局样式 */
:deep(.el-dropdown-menu) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
  box-shadow: var(--military-shadow-xl) !important;
  border-radius: var(--military-radius-lg) !important;
  padding: 0.5rem !important;
  backdrop-filter: blur(20px) !important;
  min-width: 160px !important;
}

:deep(.el-dropdown-menu__item) {
  border-radius: var(--military-radius-sm) !important;
  margin-bottom: 0.25rem !important;
  transition: all var(--military-transition) !important;
  color: var(--military-text-primary) !important;
  background: transparent !important;
  padding: 8px 12px !important;
}

:deep(.el-dropdown-menu__item:last-child) {
  margin-bottom: 0 !important;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(59, 130, 246, 0.2) !important;
  color: var(--military-primary) !important;
}

:deep(.el-dropdown-menu__item .el-icon) {
  color: var(--military-text-primary) !important;
  margin-right: 8px !important;
}

:deep(.el-dropdown-menu__item:hover .el-icon) {
  color: var(--military-primary) !important;
}

:deep(.el-dropdown-menu__item span) {
  color: var(--military-text-primary) !important;
}

:deep(.el-dropdown-menu__item:hover span) {
  color: var(--military-primary) !important;
}

:deep(.el-dropdown-menu__item.is-divided) {
  border-top: 1px solid var(--military-border) !important;
  margin-top: 0.5rem !important;
  padding-top: 0.5rem !important;
}

/* Avatar 样式 */
:deep(.el-avatar) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
}

:deep(.el-avatar .el-icon) {
  color: var(--military-text-primary) !important;
}

/* Element Plus MessageBox 样式已移至全局样式文件 design-system.css */
/* 因为 MessageBox 是动态创建并挂载到 body 的，需要全局样式才能生效 */
</style>
