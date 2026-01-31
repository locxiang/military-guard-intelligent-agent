<template>
  <div class="dashboard-view min-h-full p-3 sm:p-4">
    <!-- 页面标题 -->
    <div class="mb-6 military-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative overflow-hidden">
       <!-- 军事装饰背景 -->
      <div class="absolute right-0 top-0 h-full w-48 mil-stripe opacity-30 pointer-events-none"></div>
      
      <div class="relative z-10">
        <h2 class="text-2xl font-heading font-bold military-text-primary mb-2 flex items-center gap-2">
          <div class="w-2 h-6 bg-military-primary"></div>
          首页 - 仪表盘
        </h2>
        <p class="text-sm military-text-muted flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full bg-military-success"></span>
          系统运行正常 | {{ userName }}，欢迎回来
        </p>
      </div>
      <div class="flex items-center gap-3 relative z-10">
        <button class="military-button-secondary flex items-center gap-2" @click="loadData" :disabled="loading">
          <el-icon :class="{ 'is-loading': loading }"><Refresh /></el-icon>
          <span>{{ loading ? '刷新中...' : '刷新数据' }}</span>
        </button>
        <button class="military-button-secondary flex items-center gap-2" @click="showLayoutSettings = true">
          <el-icon><Setting /></el-icon>
          <span>视图设置</span>
        </button>
        <div class="flex items-center gap-2">
          <span class="military-text-muted text-xs">数据更新</span>
          <el-tooltip
            content="数据每5分钟自动更新，点击刷新可立即获取最新数据"
            placement="top"
            :show-after="300"
          >
            <el-icon class="gov-help-icon-tooltip">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
    </div>

    <!-- 情报广播条 - 系统公告 -->
    <div class="mb-6 notice-broadcast-bar relative overflow-hidden">
      <!-- 左侧装饰 -->
      <div class="absolute left-0 top-0 bottom-0 w-12 flex items-center justify-center bg-military-warning/20 border-r border-military-warning/30 z-10">
        <div class="flex flex-col items-center gap-1">
          <el-icon class="text-military-warning animate-pulse" :size="18"><Bell /></el-icon>
          <span class="text-[10px] text-military-warning font-bold tracking-wider">公告</span>
        </div>
      </div>
      
      <!-- 滚动通知内容 -->
      <div class="ml-12 mr-28 overflow-hidden py-3 px-4">
        <div class="notice-scroll-wrapper flex items-center" :class="{ 'animate-scroll': notices.length > 1 }">
          <div class="notice-scroll-content flex items-center gap-8 whitespace-nowrap">
            <template v-for="(notice, index) in displayNotices" :key="index">
              <div class="inline-flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity" @click="handleNoticeClick(notice)">
                <span 
                  :class="[
                    'inline-flex items-center px-2 py-0.5 rounded-sm text-xs font-bold border',
                    notice.type === 'urgent' ? 'bg-military-error/20 text-military-error border-military-error/30' :
                    notice.type === 'important' ? 'bg-military-warning/20 text-military-warning border-military-warning/30' :
                    'bg-military-primary/20 text-military-primary border-military-primary/30'
                  ]"
                >
                  {{ notice.type === 'urgent' ? '紧急' : notice.type === 'important' ? '重要' : '通知' }}
                </span>
                <span class="text-sm military-text-primary">{{ notice.content }}</span>
                <span class="text-xs military-text-muted">{{ formatNoticeDate(notice.date) }}</span>
                <span class="text-military-border mx-2">|</span>
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <!-- 右侧操作按钮 -->
      <div class="absolute right-0 top-0 bottom-0 w-28 flex items-center justify-center bg-military-bg-card border-l border-military-border z-10">
        <button 
          class="military-button-xs text-xs flex items-center gap-1.5"
          @click="showNoticeDrawer = true"
        >
          <span>全部公告</span>
          <el-badge :value="notices.length" :max="99" class="notice-badge" />
        </button>
      </div>
      
      <!-- 底部装饰线 -->
      <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-military-warning/50 to-transparent"></div>
    </div>

    <!-- 统计卡片 - 军事风格 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6">
      <div 
        class="military-card group relative overflow-hidden cursor-pointer"
        @click="handleCardClick('case-files')"
      >
        <!-- 四角瞄准装饰 -->
        <div class="absolute top-1 left-1 w-2 h-2 border-t-2 border-l-2 border-military-primary opacity-50"></div>
        <div class="absolute top-1 right-1 w-2 h-2 border-t-2 border-r-2 border-military-primary opacity-50"></div>
        <div class="absolute bottom-1 left-1 w-2 h-2 border-b-2 border-l-2 border-military-primary opacity-50"></div>
        <div class="absolute bottom-1 right-1 w-2 h-2 border-b-2 border-r-2 border-military-primary opacity-50"></div>
        
        <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-primary"></div>
        <div class="flex items-center justify-between relative z-10">
          <div class="flex-1 min-w-0 pl-2">
            <p class="text-sm font-medium military-text-muted mb-2">案卷总数</p>
            <div class="flex items-baseline gap-2 mb-3">
              <p class="text-3xl font-bold military-text-primary font-mono">{{ stats.totalCaseFiles }}</p>
              <span v-if="stats.trends?.totalCaseFiles" 
                :class="[
                  'text-xs flex items-center font-medium',
                  stats.trends.totalCaseFiles >= 0 ? 'text-military-success' : 'text-military-error'
                ]">
                <el-icon class="mr-0.5">
                  <ArrowUp v-if="stats.trends.totalCaseFiles >= 0" />
                  <ArrowDown v-else />
                </el-icon>
                {{ Math.abs(stats.trends.totalCaseFiles) }}%
              </span>
            </div>
            <div class="w-full bg-military-border rounded-sm h-1">
              <div class="bg-military-primary h-1 rounded-sm" :style="{ width: '100%' }"></div>
            </div>
          </div>
          <div class="w-12 h-12 rounded-sm bg-military-primary/10 flex items-center justify-center border border-military-primary/20 group-hover:bg-military-primary group-hover:text-white transition-colors duration-300">
            <el-icon :size="24" class="text-military-primary group-hover:text-white transition-colors">
              <Files />
            </el-icon>
          </div>
        </div>
      </div>

      <div 
        class="military-card group relative overflow-hidden cursor-pointer"
        @click="handleCardClick('digitized')"
      >
         <!-- 四角瞄准装饰 -->
        <div class="absolute top-1 left-1 w-2 h-2 border-t-2 border-l-2 border-military-success opacity-50"></div>
        <div class="absolute top-1 right-1 w-2 h-2 border-t-2 border-r-2 border-military-success opacity-50"></div>
        <div class="absolute bottom-1 left-1 w-2 h-2 border-b-2 border-l-2 border-military-success opacity-50"></div>
        <div class="absolute bottom-1 right-1 w-2 h-2 border-b-2 border-r-2 border-military-success opacity-50"></div>

        <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-success"></div>
        <div class="flex items-center justify-between relative z-10">
          <div class="flex-1 min-w-0 pl-2">
            <p class="text-sm font-medium military-text-muted mb-2">已数字化</p>
            <div class="flex items-baseline gap-2 mb-3">
              <p class="text-3xl font-bold military-text-primary font-mono">{{ stats.digitizedCount }}</p>
              <span v-if="stats.trends?.digitizedCount" 
                :class="[
                  'text-xs flex items-center font-medium',
                  stats.trends.digitizedCount >= 0 ? 'text-military-success' : 'text-military-error'
                ]">
                <el-icon class="mr-0.5">
                  <ArrowUp v-if="stats.trends.digitizedCount >= 0" />
                  <ArrowDown v-else />
                </el-icon>
                {{ Math.abs(stats.trends.digitizedCount) }}%
              </span>
            </div>
            <div class="w-full bg-military-border rounded-sm h-1">
              <div 
                class="bg-military-success h-1 rounded-sm transition-all duration-500" 
                :style="{ width: digitizedPercentage + '%' }"
              ></div>
            </div>
            <p class="text-xs military-text-muted mt-1">完成率 {{ digitizedPercentage }}%</p>
          </div>
          <div class="w-12 h-12 rounded-sm bg-military-success/10 flex items-center justify-center border border-military-success/20 group-hover:bg-military-success group-hover:text-white transition-colors duration-300">
            <el-icon :size="24" class="text-military-success group-hover:text-white transition-colors">
              <CircleCheck />
            </el-icon>
          </div>
        </div>
      </div>

      <div 
        class="military-card group relative overflow-hidden cursor-pointer"
        @click="handleCardClick('pending')"
      >
        <!-- 四角瞄准装饰 -->
        <div class="absolute top-1 left-1 w-2 h-2 border-t-2 border-l-2 border-military-warning opacity-50"></div>
        <div class="absolute top-1 right-1 w-2 h-2 border-t-2 border-r-2 border-military-warning opacity-50"></div>
        <div class="absolute bottom-1 left-1 w-2 h-2 border-b-2 border-l-2 border-military-warning opacity-50"></div>
        <div class="absolute bottom-1 right-1 w-2 h-2 border-b-2 border-r-2 border-military-warning opacity-50"></div>

        <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-warning"></div>
        <div class="flex items-center justify-between relative z-10">
          <div class="flex-1 min-w-0 pl-2">
            <p class="text-sm font-medium military-text-muted mb-2">待处理任务</p>
            <div class="flex items-baseline gap-2 mb-3">
              <p class="text-3xl font-bold military-text-primary font-mono">{{ stats.pendingTasks }}</p>
            </div>
            <div class="flex gap-2">
              <span v-if="pendingTasksByPriority.urgent > 0" class="inline-flex items-center px-1.5 py-0.5 rounded-sm text-xs font-medium bg-military-error/10 text-military-error border border-military-error/20">
                紧急 {{ pendingTasksByPriority.urgent }}
              </span>
              <span v-if="pendingTasksByPriority.important > 0" class="inline-flex items-center px-1.5 py-0.5 rounded-sm text-xs font-medium bg-military-warning/10 text-military-warning border border-military-warning/20">
                重要 {{ pendingTasksByPriority.important }}
              </span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-sm bg-military-warning/10 flex items-center justify-center border border-military-warning/20 group-hover:bg-military-warning group-hover:text-white transition-colors duration-300">
            <el-icon :size="24" class="text-military-warning group-hover:text-white transition-colors">
              <Clock />
            </el-icon>
          </div>
        </div>
      </div>

      <div 
        class="military-card group relative overflow-hidden cursor-pointer"
        @click="handleCardClick('today')"
      >
        <!-- 四角瞄准装饰 -->
        <div class="absolute top-1 left-1 w-2 h-2 border-t-2 border-l-2 border-military-primary opacity-50"></div>
        <div class="absolute top-1 right-1 w-2 h-2 border-t-2 border-r-2 border-military-primary opacity-50"></div>
        <div class="absolute bottom-1 left-1 w-2 h-2 border-b-2 border-l-2 border-military-primary opacity-50"></div>
        <div class="absolute bottom-1 right-1 w-2 h-2 border-b-2 border-r-2 border-military-primary opacity-50"></div>

        <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-primary"></div>
        <div class="flex items-center justify-between relative z-10">
          <div class="flex-1 min-w-0 pl-2">
            <p class="text-sm font-medium military-text-muted mb-2">今日新增</p>
            <div class="flex items-baseline gap-2 mb-3">
              <p class="text-3xl font-bold military-text-primary font-mono">{{ stats.todayAdded }}</p>
              <span v-if="stats.trends?.todayAdded" 
                :class="[
                  'text-xs flex items-center font-medium',
                  stats.trends.todayAdded >= 0 ? 'text-military-success' : 'text-military-error'
                ]">
                <el-icon class="mr-0.5">
                  <ArrowUp v-if="stats.trends.todayAdded >= 0" />
                  <ArrowDown v-else />
                </el-icon>
                {{ Math.abs(stats.trends.todayAdded) }}%
              </span>
            </div>
            <p class="text-xs military-text-muted mt-1">较昨日{{ stats.trends?.todayAdded >= 0 ? '↑' : '↓' }}</p>
          </div>
          <div class="w-12 h-12 rounded-sm bg-military-primary/10 flex items-center justify-center border border-military-primary/20 group-hover:bg-military-primary group-hover:text-white transition-colors duration-300">
            <el-icon :size="24" class="text-military-primary group-hover:text-white transition-colors">
              <TrendCharts />
            </el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据可视化区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6">
      <!-- 案卷类型分布 -->
      <div class="military-card">
        <div class="military-card-header flex items-center justify-between mb-4 pb-3 border-b border-military-border">
          <div class="flex items-center gap-2 flex-1 min-w-0 pr-4">
            <div class="w-1 h-4 bg-military-primary rounded-sm flex-shrink-0"></div>
            <h3 class="text-lg font-title font-bold military-text-primary whitespace-nowrap">案卷类型分布</h3>
          </div>
          <el-select v-model="chartTimeRange" size="small" class="!w-16 flex-shrink-0" @change="loadChartData" style="width: 64px;">
            <el-option label="今日" value="today" />
            <el-option label="本周" value="week" />
            <el-option label="本月" value="month" />
            <el-option label="本年" value="year" />
          </el-select>
        </div>
        <div ref="typeChartRef" class="w-full h-72"></div>
      </div>

      <!-- 时间趋势 -->
      <div class="military-card">
        <div class="military-card-header flex items-center justify-between mb-4 pb-3 border-b border-military-border">
          <div class="flex items-center gap-2 flex-1 min-w-0 pr-4">
            <div class="w-1 h-4 bg-military-primary rounded-sm flex-shrink-0"></div>
            <h3 class="text-lg font-title font-bold military-text-primary whitespace-nowrap">时间趋势</h3>
          </div>
          <el-select v-model="trendTimeRange" size="small" class="!w-20 flex-shrink-0" @change="loadChartData" style="width: 80px;">
            <el-option label="近7天" value="7days" />
            <el-option label="近30天" value="30days" />
            <el-option label="近90天" value="90days" />
          </el-select>
        </div>
        <div ref="trendChartRef" class="w-full h-72"></div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- 左侧：待办事项 + 最近访问 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 待办事项专区 -->
        <div class="military-card">
          <div class="military-card-header flex items-center justify-between mb-4 pb-3 border-b border-military-border">
            <div class="flex items-center gap-2">
              <div class="w-1 h-4 bg-military-warning rounded-sm"></div>
              <h3 class="text-lg font-title font-bold military-text-primary">待办事项</h3>
            </div>
            <div class="flex items-center gap-3">
              <el-badge :value="todoTasks.length" :hidden="todoTasks.length === 0">
                <button class="military-button-xs font-medium" @click="handleViewAllTodos">
                  查看全部
                </button>
              </el-badge>
              <button class="military-button-icon" @click="loadTodoTasks" title="刷新待办事项">
                <el-icon><Refresh /></el-icon>
              </button>
            </div>
          </div>
          <div v-if="todoTasks.length > 0" class="space-y-5">
            <!-- 紧急事项 -->
            <div v-if="groupedTodoTasks.urgent.length > 0" class="todo-priority-group">
              <!-- 优先级分组标题 -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-2">
                  <div class="w-1 h-6 bg-military-error rounded-full"></div>
                  <h4 class="text-base font-bold text-military-error">紧急</h4>
                </div>
              </div>
              <!-- 任务列表 -->
              <div class="space-y-2.5">
                <div
                  v-for="task in groupedTodoTasks.urgent"
                  :key="task.id"
                  class="group relative flex items-start gap-4 p-4 rounded-lg bg-military-bg-card border border-military-border hover:border-military-error/50 hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden"
                  @click="handleTodoClick(task)"
                >
                  <!-- 左侧彩色指示条 -->
                  <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-error"></div>
                  
                  <!-- 主要内容区 -->
                  <div class="flex-1 min-w-0 pl-3">
                    <!-- 类型标签和标题行 -->
                    <div class="flex items-start justify-between gap-3 mb-2">
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1.5">
                          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-military-error/10 text-military-error border border-military-error/20">
                            {{ task.type }}
                          </span>
                        </div>
                        <p class="text-sm font-semibold military-text-primary leading-relaxed group-hover:text-military-error transition-colors">
                          {{ task.title }}
                        </p>
                      </div>
                      <!-- 操作按钮 -->
                      <button
                        class="flex-shrink-0 military-button military-button-sm opacity-60 group-hover:opacity-100 transition-opacity"
                        @click.stop="handleTodoAction(task)"
                      >
                        处理
                      </button>
                    </div>
                    
                    <!-- 时间信息 -->
                    <div class="flex items-center gap-3 text-xs">
                      <span class="military-text-muted flex items-center gap-1">
                        <el-icon :size="12"><Clock /></el-icon>
                        {{ formatDate(task.createdAt) }}
                      </span>
                      <span v-if="task.timeout" class="text-military-error flex items-center gap-1 font-medium">
                        <el-icon :size="12"><Warning /></el-icon>
                        {{ task.timeout }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 重要事项 -->
            <div v-if="groupedTodoTasks.important.length > 0" class="todo-priority-group">
              <!-- 分割线 -->
              <div v-if="groupedTodoTasks.urgent.length > 0" class="h-px bg-gradient-to-r from-transparent via-military-border/50 to-transparent mb-5 mt-1"></div>
              
              <!-- 优先级分组标题 -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-2">
                  <div class="w-1 h-6 bg-military-warning rounded-full"></div>
                  <h4 class="text-base font-bold text-military-warning">重要</h4>
                </div>
              </div>
              <!-- 任务列表 -->
              <div class="space-y-2.5">
                <div
                  v-for="task in groupedTodoTasks.important"
                  :key="task.id"
                  class="group relative flex items-start gap-4 p-4 rounded-lg bg-military-bg-card border border-military-border hover:border-military-warning/50 hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden"
                  @click="handleTodoClick(task)"
                >
                  <!-- 左侧彩色指示条 -->
                  <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-warning"></div>
                  
                  <!-- 主要内容区 -->
                  <div class="flex-1 min-w-0 pl-3">
                    <!-- 类型标签和标题行 -->
                    <div class="flex items-start justify-between gap-3 mb-2">
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1.5">
                          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-military-warning/10 text-military-warning border border-military-warning/20">
                            {{ task.type }}
                          </span>
                        </div>
                        <p class="text-sm font-semibold military-text-primary leading-relaxed group-hover:text-military-warning transition-colors">
                          {{ task.title }}
                        </p>
                      </div>
                      <!-- 操作按钮 -->
                      <button
                        class="flex-shrink-0 military-button military-button-sm opacity-60 group-hover:opacity-100 transition-opacity"
                        @click.stop="handleTodoAction(task)"
                      >
                        处理
                      </button>
                    </div>
                    
                    <!-- 时间信息 -->
                    <div class="flex items-center gap-3 text-xs">
                      <span class="military-text-muted flex items-center gap-1">
                        <el-icon :size="12"><Clock /></el-icon>
                        {{ formatDate(task.createdAt) }}
                      </span>
                      <span v-if="task.timeout" class="text-military-error flex items-center gap-1 font-medium">
                        <el-icon :size="12"><Warning /></el-icon>
                        {{ task.timeout }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 一般事项 -->
            <div v-if="groupedTodoTasks.normal.length > 0" class="todo-priority-group">
              <!-- 分割线 -->
              <div v-if="groupedTodoTasks.urgent.length > 0 || groupedTodoTasks.important.length > 0" class="h-px bg-gradient-to-r from-transparent via-military-border/50 to-transparent mb-5 mt-1"></div>
              
              <!-- 优先级分组标题 -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center gap-2">
                  <div class="w-1 h-6 bg-military-primary rounded-full"></div>
                  <h4 class="text-base font-bold text-military-primary">一般</h4>
                </div>
              </div>
              <!-- 任务列表 -->
              <div class="space-y-2.5">
                <div
                  v-for="task in groupedTodoTasks.normal"
                  :key="task.id"
                  class="group relative flex items-start gap-4 p-4 rounded-lg bg-military-bg-card border border-military-border hover:border-military-primary/50 hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden"
                  @click="handleTodoClick(task)"
                >
                  <!-- 左侧彩色指示条 -->
                  <div class="absolute left-0 top-0 bottom-0 w-1 bg-military-primary"></div>
                  
                  <!-- 主要内容区 -->
                  <div class="flex-1 min-w-0 pl-3">
                    <!-- 类型标签和标题行 -->
                    <div class="flex items-start justify-between gap-3 mb-2">
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1.5">
                          <span class="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-military-primary/10 text-military-primary border border-military-primary/20">
                            {{ task.type }}
                          </span>
                        </div>
                        <p class="text-sm font-semibold military-text-primary leading-relaxed group-hover:text-military-primary transition-colors">
                          {{ task.title }}
                        </p>
                      </div>
                      <!-- 操作按钮 -->
                      <button
                        class="flex-shrink-0 military-button military-button-sm opacity-60 group-hover:opacity-100 transition-opacity"
                        @click.stop="handleTodoAction(task)"
                      >
                        处理
                      </button>
                    </div>
                    
                    <!-- 时间信息 -->
                    <div class="flex items-center gap-3 text-xs">
                      <span class="military-text-muted flex items-center gap-1">
                        <el-icon :size="12"><Clock /></el-icon>
                        {{ formatDate(task.createdAt) }}
                      </span>
                      <span v-if="task.timeout" class="text-military-error flex items-center gap-1 font-medium">
                        <el-icon :size="12"><Warning /></el-icon>
                        {{ task.timeout }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无待办事项" :image-size="80" />
        </div>

        <!-- 最近访问 -->
        <div class="military-card">
          <div class="military-card-header flex items-center justify-between mb-4 pb-3 border-b border-military-border">
            <div class="flex items-center gap-2">
              <div class="w-1 h-4 bg-military-primary rounded-sm"></div>
              <h3 class="text-lg font-title font-bold military-text-primary">最近访问</h3>
            </div>
            <button class="military-button-secondary military-button-sm" @click="$router.push('/case-file')">
              进入案卷库
            </button>
            <div class="flex items-center gap-2 mt-3">
              <span class="military-text-muted text-xs">访问记录</span>
              <el-tooltip
                content="最近访问记录保留30天，点击可快速查看案卷详情"
                placement="top"
                :show-after="300"
              >
                <el-icon class="gov-help-icon-tooltip">
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </div>
          <el-table :data="recentCaseFiles" style="width: 100%" class="military-table" :header-cell-style="{ background: 'var(--military-bg-card)', color: 'var(--military-text-primary)' }">
            <el-table-column prop="caseNo" label="案卷编号" width="150">
              <template #default="{ row }">
                <span class="font-mono text-military-primary">{{ row.caseNo }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="caseType" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" type="info">{{ row.caseType }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updatedAt" label="更新时间" width="180">
              <template #default="{ row }">
                <span class="military-text-muted text-xs">{{ formatDate(row.updatedAt) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <button class="military-button-secondary military-button-sm" @click="viewDetail(row.id)">
                  查看详情
                </button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 右侧：快捷操作 + 工作概览 + 系统公告 -->
      <div class="space-y-6">
        <!-- 快捷操作 -->
        <div class="military-card">
          <div class="military-card-header mb-4 pb-3 border-b border-military-border">
            <h3 class="text-lg font-title font-bold military-text-primary">快捷操作</h3>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="military-text-muted text-xs">快捷操作</span>
            <el-tooltip
              content="点击快捷操作可快速进入常用功能模块，提高工作效率"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <button
              class="flex flex-col items-center justify-center p-4 rounded-lg border border-military-border hover:border-military-primary hover:bg-military-bg-card-hover transition-all duration-200 group"
              @click="$router.push('/case-file/import')"
            >
              <div class="w-10 h-10 rounded-full bg-military-primary/10 flex items-center justify-center mb-2 group-hover:bg-military-primary group-hover:text-white transition-colors">
                <el-icon :size="20" class="text-military-primary group-hover:text-white"><Upload /></el-icon>
              </div>
              <span class="text-sm font-medium military-text-primary">导入案卷</span>
            </button>
            <button
              class="flex flex-col items-center justify-center p-4 rounded-lg border border-military-border hover:border-military-primary hover:bg-military-bg-card-hover transition-all duration-200 group"
              @click="$router.push('/doc-generate')"
            >
              <div class="w-10 h-10 rounded-full bg-military-primary/10 flex items-center justify-center mb-2 group-hover:bg-military-primary group-hover:text-white transition-colors">
                <el-icon :size="20" class="text-military-primary group-hover:text-white"><Document /></el-icon>
              </div>
              <span class="text-sm font-medium military-text-primary">生成文档</span>
            </button>
            <button
              class="flex flex-col items-center justify-center p-4 rounded-lg border border-military-border hover:border-military-primary hover:bg-military-bg-card-hover transition-all duration-200 group"
              @click="$router.push('/knowledge-graph')"
            >
              <div class="w-10 h-10 rounded-full bg-military-primary/10 flex items-center justify-center mb-2 group-hover:bg-military-primary group-hover:text-white transition-colors">
                <el-icon :size="20" class="text-military-primary group-hover:text-white"><Connection /></el-icon>
              </div>
              <span class="text-sm font-medium military-text-primary">知识图谱</span>
            </button>
            <button
              class="flex flex-col items-center justify-center p-4 rounded-lg border border-military-border hover:border-military-primary hover:bg-military-bg-card-hover transition-all duration-200 group"
              @click="$router.push('/statistics')"
            >
              <div class="w-10 h-10 rounded-full bg-military-primary/10 flex items-center justify-center mb-2 group-hover:bg-military-primary group-hover:text-white transition-colors">
                <el-icon :size="20" class="text-military-primary group-hover:text-white"><DataAnalysis /></el-icon>
              </div>
              <span class="text-sm font-medium military-text-primary">统计分析</span>
            </button>
          </div>
        </div>

        <!-- 工作概览 -->
        <div class="military-card">
          <div class="military-card-header mb-4 pb-3 border-b border-military-border">
            <h3 class="text-lg font-title font-bold military-text-primary">工作月报</h3>
          </div>
          <div class="flex items-center gap-2 mb-4">
            <span class="military-text-muted text-xs">工作月报</span>
            <el-tooltip
              content="统计数据实时更新，反映本周工作完成情况"
              placement="top"
              :show-after="300"
            >
              <el-icon class="gov-help-icon-tooltip">
                <InfoFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="space-y-4">
            <div class="flex items-center justify-between p-3 bg-military-bg-card rounded-lg border border-military-border">
              <span class="text-sm military-text-muted">本周处理案卷</span>
              <span class="text-lg font-bold text-military-primary font-mono">{{ workStats.weekCaseFiles }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-military-bg-card rounded-lg border border-military-border">
              <span class="text-sm military-text-muted">生成文档数</span>
              <span class="text-lg font-bold text-military-primary font-mono">{{ workStats.docGenerated }}</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-military-bg-card rounded-lg border border-military-border">
              <span class="text-sm military-text-muted">审查通过率</span>
              <span class="text-lg font-bold text-military-success font-mono">{{ workStats.reviewPassRate }}%</span>
            </div>
            <button class="military-button-secondary w-full" @click="$router.push('/statistics')">
              查看详细统计
            </button>
            <div class="flex items-center gap-2">
              <span class="military-text-muted text-xs">统计说明</span>
              <el-tooltip
                content="统计数据实时更新，支持导出Excel和PDF格式报表"
                placement="top"
                :show-after="300"
              >
                <el-icon class="gov-help-icon-tooltip">
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 公告详情抽屉 -->
    <el-drawer
      v-model="showNoticeDrawer"
      title=""
      direction="rtl"
      size="400px"
      :with-header="false"
      class="notice-drawer"
    >
      <div class="h-full flex flex-col bg-military-bg">
        <!-- 抽屉头部 -->
        <div class="p-4 border-b border-military-border bg-military-bg-card">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-sm bg-military-warning/20 flex items-center justify-center border border-military-warning/30">
                <el-icon class="text-military-warning" :size="20"><Bell /></el-icon>
              </div>
              <div>
                <h3 class="text-lg font-title font-bold military-text-primary">情报中心</h3>
                <p class="text-xs military-text-muted">系统公告与重要通知</p>
              </div>
            </div>
            <button class="military-button-icon" @click="showNoticeDrawer = false">
              <el-icon :size="18"><Close /></el-icon>
            </button>
          </div>
        </div>
        
        <!-- 公告筛选 -->
        <div class="p-3 border-b border-military-border flex items-center gap-2 bg-military-bg-card/50">
          <button 
            v-for="filter in noticeFilters" 
            :key="filter.value"
            :class="[
              'px-3 py-1.5 text-xs rounded-sm border transition-all',
              activeNoticeFilter === filter.value 
                ? 'bg-military-primary text-white border-military-primary' 
                : 'bg-transparent military-text-muted border-military-border hover:border-military-primary'
            ]"
            @click="activeNoticeFilter = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>
        
        <!-- 公告列表 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div 
            v-for="(notice, index) in filteredNotices" 
            :key="index"
            class="p-4 rounded-lg border border-military-border bg-military-bg-card hover:border-military-primary transition-colors cursor-pointer group"
            @click="handleNoticeDetail(notice)"
          >
            <div class="flex items-start gap-3">
              <div 
                :class="[
                  'w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0 border',
                  notice.type === 'urgent' ? 'bg-military-error/20 border-military-error/30' :
                  notice.type === 'important' ? 'bg-military-warning/20 border-military-warning/30' :
                  'bg-military-primary/20 border-military-primary/30'
                ]"
              >
                <el-icon 
                  :class="[
                    notice.type === 'urgent' ? 'text-military-error' :
                    notice.type === 'important' ? 'text-military-warning' :
                    'text-military-primary'
                  ]"
                  :size="16"
                >
                  <WarningFilled v-if="notice.type === 'urgent'" />
                  <InfoFilled v-else-if="notice.type === 'important'" />
                  <ChatDotRound v-else />
                </el-icon>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span 
                    :class="[
                      'inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] font-bold border',
                      notice.type === 'urgent' ? 'bg-military-error/20 text-military-error border-military-error/30' :
                      notice.type === 'important' ? 'bg-military-warning/20 text-military-warning border-military-warning/30' :
                      'bg-military-primary/20 text-military-primary border-military-primary/30'
                    ]"
                  >
                    {{ notice.type === 'urgent' ? '紧急' : notice.type === 'important' ? '重要' : '通知' }}
                  </span>
                  <span v-if="!notice.read" class="w-2 h-2 rounded-full bg-military-error"></span>
                </div>
                <p class="text-sm military-text-primary mb-2 line-clamp-2 group-hover:text-military-primary transition-colors">{{ notice.content }}</p>
                <div class="flex items-center justify-between">
                  <span class="text-xs military-text-muted">{{ formatDate(notice.date) }}</span>
                  <el-icon class="text-military-muted opacity-0 group-hover:opacity-100 transition-opacity"><ArrowRight /></el-icon>
                </div>
              </div>
            </div>
          </div>
          
          <el-empty v-if="filteredNotices.length === 0" description="暂无公告" :image-size="80" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// @ts-ignore
import * as echarts from 'echarts'
import {
  Files,
  CircleCheck,
  Clock,
  TrendCharts,
  Upload,
  Document,
  Connection,
  DataAnalysis,
  Refresh,
  Setting,
  ArrowUp,
  ArrowDown,
  Warning,
  InfoFilled,
  Bell,
  Close,
  ArrowRight,
  WarningFilled,
  ChatDotRound
} from '@element-plus/icons-vue'
import { dashboardApi } from '@/api/dashboard'

const router = useRouter()

// 用户信息
const getUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr)
      return userInfo.realName || userInfo.username || '管理员'
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
  return '管理员'
}
const userName = ref(getUserInfo())

// 加载状态
const loading = ref(false)

// 布局设置
const showLayoutSettings = ref(false)

// 统计数据
const stats = ref({
  totalCaseFiles: 0,
  digitizedCount: 0,
  pendingTasks: 0,
  todayAdded: 0,
  trends: {
    totalCaseFiles: 5.2,
    digitizedCount: 12.5,
    todayAdded: -3.1
  }
})

// 图表相关
const typeChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let typeChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
const chartTimeRange = ref('month')
const trendTimeRange = ref('30days')

// 待办事项
const todoTasks = ref<any[]>([])

// 工作统计
const workStats = ref({
  weekCaseFiles: 0,
  docGenerated: 0,
  reviewPassRate: 0
})

// 计算属性
const digitizedPercentage = computed(() => {
  if (stats.value.totalCaseFiles === 0) return 0
  return Math.round((stats.value.digitizedCount / stats.value.totalCaseFiles) * 100)
})

const pendingTasksByPriority = computed(() => {
  return {
    urgent: todoTasks.value.filter(t => t.priority === 'urgent').length,
    important: todoTasks.value.filter(t => t.priority === 'important').length,
    normal: todoTasks.value.filter(t => t.priority === 'normal').length
  }
})

// 按优先级分组的待办事项
const groupedTodoTasks = computed(() => {
  const groups = {
    urgent: todoTasks.value.filter(t => t.priority === 'urgent'),
    important: todoTasks.value.filter(t => t.priority === 'important'),
    normal: todoTasks.value.filter(t => t.priority === 'normal')
  }
  return groups
})

// 最近访问的案卷
const recentCaseFiles = ref<any[]>([])

// 系统公告
const showNoticeDrawer = ref(false)
const activeNoticeFilter = ref('all')
const noticeFilters = [
  { label: '全部', value: 'all' },
  { label: '紧急', value: 'urgent' },
  { label: '重要', value: 'important' },
  { label: '通知', value: 'normal' }
]

interface Notice {
  id: number
  content: string
  date: Date
  type: 'urgent' | 'important' | 'normal'
  read: boolean
}

const notices = ref<Notice[]>([
  { id: 1, content: '【紧急】系统安全更新：请所有用户今日内完成密码更换', date: new Date(), type: 'urgent', read: false },
  { id: 2, content: '系统维护通知：系统将于今晚22:00-24:00进行例行维护，届时将无法访问', date: new Date(Date.now() - 3600000), type: 'important', read: false },
  { id: 3, content: '新功能上线：知识图谱智能查询功能已正式上线，欢迎使用', date: new Date(Date.now() - 86400000), type: 'normal', read: true },
  { id: 4, content: '培训通知：案卷数字化操作培训将于本周五下午2点举行', date: new Date(Date.now() - 172800000), type: 'normal', read: true }
])

// 用于无缝滚动的双倍公告列表
const displayNotices = computed(() => {
  return [...notices.value, ...notices.value]
})

// 筛选后的公告
const filteredNotices = computed(() => {
  if (activeNoticeFilter.value === 'all') return notices.value
  return notices.value.filter(n => n.type === activeNoticeFilter.value)
})

// 格式化公告日期（简短版本）
const formatNoticeDate = (date: Date | string) => {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 公告点击处理
const handleNoticeClick = (_notice: Notice) => {
  showNoticeDrawer.value = true
}

// 查看公告详情
const handleNoticeDetail = (notice: Notice) => {
  notice.read = true
  ElMessage.info(`查看公告: ${notice.content}`)
  // TODO: 可以跳转到公告详情页或展开详情
}

// 格式化日期
const formatDate = (date: Date | string) => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    urgent: 'danger',
    important: 'warning',
    normal: 'info'
  }
  return map[priority] || 'info'
}

// 获取优先级文本
const getPriorityText = (priority: string) => {
  const map: Record<string, string> = {
    urgent: '紧急',
    important: '重要',
    normal: '一般'
  }
  return map[priority] || priority
}

// 卡片点击
const handleCardClick = (type: string) => {
  switch (type) {
    case 'case-files':
      router.push({ path: '/case-file' })
      break
    case 'digitized':
      router.push({ path: '/case-file', query: { status: 'completed' } })
      break
    case 'pending':
      handleViewAllTodos()
      break
    case 'today':
      router.push({ path: '/case-file', query: { dateRange: 'today' } })
      break
  }
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/case-file/${id}`)
}

// 加载待办事项
const loadTodoTasks = async () => {
  try {
    // 模拟数据，实际应从API获取
    todoTasks.value = [
      {
        id: 1,
        type: '待审核分类',
        title: '案件卷宗2024001需要确认分类',
        description: '系统自动分类为"刑事案件"，请审核确认',
        priority: 'urgent',
        createdAt: new Date(Date.now() - 3600000),
        timeout: '1小时前'
      },
      {
        id: 2,
        type: '待确认OCR',
        title: 'OCR识别结果需人工校对',
        description: '文件"调查报告-2024-01.pdf"识别准确率85%，建议人工校对',
        priority: 'important',
        createdAt: new Date(Date.now() - 7200000)
      },
      {
        id: 3,
        type: '待审查文档',
        title: '文档生成完成，等待审查',
        description: '"立案报告-2024002"已生成，请进行内容审查',
        priority: 'normal',
        createdAt: new Date(Date.now() - 10800000)
      }
    ]
  } catch (error: any) {
    console.error('加载待办事项失败', error)
  }
}

// 待办事项点击
const handleTodoClick = (task: any) => {
  ElMessage.info(`查看待办: ${task.title}`)
  // TODO: 跳转到对应页面
}

// 待办事项操作
const handleTodoAction = (task: any) => {
  ElMessage.info(`处理待办: ${task.title}`)
  // TODO: 打开处理对话框
}

// 查看全部待办
const handleViewAllTodos = () => {
  router.push({ path: '/dashboard', query: { tab: 'todos' } })
  // TODO: 实现待办列表页面
}

// 初始化类型分布图表
const initTypeChart = () => {
  if (!typeChartRef.value) return
  
  typeChart = echarts.init(typeChartRef.value, 'dark')
  const option = {
    backgroundColor: 'transparent',
    color: ['#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6'],
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(59, 130, 246, 0.5)',
      borderWidth: 1,
      textStyle: { color: '#FFFFFF', fontSize: 13 },
      padding: [10, 15]
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: { 
        color: 'rgba(255, 255, 255, 0.9)',
        fontSize: 13,
        fontWeight: 500
      },
      itemGap: 12,
      itemWidth: 14,
      itemHeight: 14
    },
    series: [
      {
        name: '案卷类型',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: '#FFFFFF'
          },
          itemStyle: {
            shadowBlur: 15,
            shadowOffsetX: 0,
            shadowColor: 'rgba(59, 130, 246, 0.5)'
          }
        },
        data: [
          { value: 320, name: '案件卷宗' },
          { value: 180, name: '公文材料' },
          { value: 150, name: '调查报告' },
          { value: 100, name: '其他' }
        ]
      }
    ]
  }
  typeChart.setOption(option)
}

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value, 'dark')
  const dates = []
  const values = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }))
    values.push(Math.floor(Math.random() * 50) + 100)
  }
  
  const option = {
    backgroundColor: 'transparent',
    color: ['#3B82F6'],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(59, 130, 246, 0.5)',
      borderWidth: 1,
      textStyle: { color: '#FFFFFF', fontSize: 13 },
      padding: [10, 15]
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { 
        lineStyle: { 
          color: 'rgba(59, 130, 246, 0.3)',
          width: 1
        } 
      },
      axisLabel: { 
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 12
      },
      axisTick: {
        lineStyle: { color: 'rgba(59, 130, 246, 0.3)' }
      }
    },
    yAxis: {
      type: 'value',
      splitLine: { 
        lineStyle: { 
          type: 'dashed', 
          color: 'rgba(59, 130, 246, 0.2)',
          width: 1
        } 
      },
      axisLine: {
        lineStyle: { color: 'rgba(59, 130, 246, 0.3)' }
      },
      axisLabel: { 
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 12
      }
    },
    series: [
      {
        name: '新增案卷',
        type: 'line',
        smooth: true,
        showSymbol: false,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ])
        },
        lineStyle: { 
          width: 3,
          color: '#3B82F6'
        },
        itemStyle: { 
          color: '#3B82F6',
          borderColor: '#FFFFFF',
          borderWidth: 2
        },
        emphasis: {
          lineStyle: {
            width: 4
          },
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(59, 130, 246, 0.8)'
          }
        },
        data: values
      }
    ]
  }
  trendChart.setOption(option)
}

// 加载图表数据
const loadChartData = () => {
  nextTick(() => {
    if (typeChart) {
      // TODO: 根据时间范围加载数据
      typeChart.resize()
    }
    if (trendChart) {
      // TODO: 根据时间范围加载数据
      trendChart.resize()
    }
  })
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await dashboardApi.getDashboardData()
    stats.value = { ...stats.value, ...response.stats } as any
    recentCaseFiles.value = response.recentCaseFiles || []
    
    // 加载工作统计
    workStats.value = {
      weekCaseFiles: 45,
      docGenerated: 12,
      reviewPassRate: 92
    }
    
    // 加载待办事项
    await loadTodoTasks()
    
    // 初始化图表
    await nextTick()
    initTypeChart()
    initTrendChart()
  } catch (error: any) {
    ElMessage.error(error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

// 窗口大小改变时调整图表
const handleResize = () => {
  if (typeChart) typeChart.resize()
  if (trendChart) trendChart.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (typeChart) typeChart.dispose()
  if (trendChart) trendChart.dispose()
})
</script>

<style scoped>
.dashboard-view {
  font-family: var(--font-body);
  color: var(--military-text-primary);
}

/* 覆盖 Element Plus 组件样式以匹配军事风格 */
:deep(.el-select .el-input__wrapper) {
  box-shadow: none !important;
  border: 2px solid var(--military-border) !important;
  background-color: var(--military-bg-input) !important;
  color: var(--military-text-primary) !important;
}

:deep(.el-select .el-input__wrapper:hover) {
  border-color: var(--military-border-hover) !important;
  background-color: var(--military-bg-input-hover) !important;
}

:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: var(--military-primary) !important;
  background-color: var(--military-bg-input-focus) !important;
}

:deep(.el-select .el-input__inner) {
  color: var(--military-text-primary) !important;
}

:deep(.el-tag) {
  background: var(--military-bg-card) !important;
  border: 1px solid var(--military-border) !important;
  color: var(--military-text-primary) !important;
}

/* 情报广播条样式 */
.notice-broadcast-bar {
  background: linear-gradient(135deg, 
    rgba(245, 158, 11, 0.05) 0%, 
    var(--military-bg-card) 30%, 
    var(--military-bg-card) 70%, 
    rgba(245, 158, 11, 0.05) 100%
  );
  border: 1px solid var(--military-border);
  border-left: 3px solid var(--military-warning);
  border-radius: 0.25rem;
}

/* 滚动动画 */
.notice-scroll-wrapper {
  display: flex;
  width: max-content;
}

.notice-scroll-content {
  display: flex;
  animation: none;
}

.animate-scroll .notice-scroll-content {
  animation: scrollNotice 30s linear infinite;
}

@keyframes scrollNotice {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* 悬停时暂停滚动 */
.notice-broadcast-bar:hover .notice-scroll-content {
  animation-play-state: paused;
}

/* 公告徽章样式 */
.notice-badge :deep(.el-badge__content) {
  background-color: var(--military-error) !important;
  border: none !important;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 5px;
}

/* 抽屉样式覆盖 */
:deep(.el-drawer) {
  background: var(--military-bg) !important;
}

:deep(.el-drawer__body) {
  padding: 0 !important;
}

/* 文字截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 待办事项优先级分组样式 */
.todo-priority-group {
  position: relative;
}
</style>
