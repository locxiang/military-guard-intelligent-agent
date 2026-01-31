import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '工作台' }
      },
      // 案件档案管理模块（业务导向命名）
      {
        path: 'case-file',
        name: 'case-file',
        component: () => import('@/views/ArchiveListView.vue'),
        meta: { title: '案件列表' }
      },
      {
        path: 'case-file/import',
        name: 'case-file-import',
        component: () => import('@/views/ArchiveImportView.vue'),
        meta: { title: '案件导入' }
      },
      {
        path: 'case-file/:id',
        name: 'case-file-detail',
        component: () => import('@/views/ArchiveDetail/index.vue'),
        meta: { title: '案件详情' }
      },
      {
        // OCR数字化页面已合并到案件导入页面，保留路由重定向以兼容旧链接
        path: 'case-file/ocr',
        name: 'case-file-ocr',
        redirect: '/case-file/import',
        meta: { title: '案件导入' }
      },
      {
        path: 'case-file/classification',
        name: 'case-file-classification',
        component: () => import('@/views/ArchiveClassificationView.vue'),
        meta: { title: '案件分类' }
      },
      {
        path: 'case-file/search',
        name: 'case-file-search',
        component: () => import('@/views/ArchiveSearchView.vue'),
        meta: { title: '案件检索' }
      },
      {
        path: 'case-file/progress',
        name: 'case-file-progress',
        component: () => import('@/views/ArchiveProgressView.vue'),
        meta: { title: '导入进度管理' }
      },
      {
        path: 'case-file/progress/:id',
        name: 'case-file-progress-detail',
        component: () => import('@/views/ArchiveProgressDetailView.vue'),
        meta: { title: '任务详情' }
      },
      // 智能文档生成模块（业务导向命名）
      // /doc-generate 重定向到案件卷宗生成（默认子功能）
      {
        path: 'doc-generate',
        redirect: '/doc-generate/case'
      },
      {
        path: 'doc-generate/case',
        name: 'doc-generate-case',
        component: () => import('@/views/DocGenerateCaseView.vue'),
        meta: { title: '案件卷宗生成' }
      },
      {
        path: 'doc-generate/case/result',
        name: 'doc-generate-case-result',
        component: () => import('@/views/DocGenerateCaseResultView.vue'),
        meta: { title: 'AI生成结果' }
      },
      {
        path: 'doc-generate/official',
        name: 'doc-generate-official',
        component: () => import('@/views/DocGenerateOfficialView.vue'),
        meta: { title: '公文助手' }
      },
      {
        path: 'doc-generate/official/result',
        name: 'doc-generate-official-result',
        component: () => import('@/views/DocGenerateOfficialResultView.vue'),
        meta: { title: 'AI生成结果' }
      },
      {
        path: 'doc-generate/report',
        name: 'doc-generate-report',
        component: () => import('@/views/DocGenerateReportView.vue'),
        meta: { title: '报告生成器' }
      },
      {
        path: 'doc-generate/report/result',
        name: 'doc-generate-report-result',
        component: () => import('@/views/DocGenerateReportResultView.vue'),
        meta: { title: 'AI生成结果' }
      },
      {
        path: 'doc-generate/meeting',
        name: 'doc-generate-meeting',
        component: () => import('@/views/DocGenerateMeetingView.vue'),
        meta: { title: '会议纪要生成' }
      },
      {
        path: 'doc-generate/meeting/result',
        name: 'doc-generate-meeting-result',
        component: () => import('@/views/DocGenerateMeetingResultView.vue'),
        meta: { title: '会议纪要' }
      },
      {
        path: 'template',
        name: 'template',
        component: () => import('@/views/TemplateView.vue'),
        meta: { title: '模板管理' }
      },
      {
        path: 'content-review',
        name: 'content-review',
        component: () => import('@/views/ContentReviewView.vue'),
        meta: { title: '内容审查' }
      },
      // 知识关联分析模块（业务导向命名）
      {
        path: 'knowledge-graph',
        name: 'knowledge-graph',
        component: () => import('@/views/KnowledgeGraphView.vue'),
        meta: { title: '关联查询' }
      },
      {
        path: 'knowledge-graph/entity',
        name: 'knowledge-graph-entity',
        component: () => import('@/views/KnowledgeGraphEntityView.vue'),
        meta: { title: '实体管理' }
      },
      {
        path: 'knowledge-graph/relation',
        name: 'knowledge-graph-relation',
        component: () => import('@/views/KnowledgeGraphRelationView.vue'),
        meta: { title: '关系管理' }
      },
      {
        path: 'knowledge-graph/extract',
        name: 'knowledge-graph-extract',
        component: () => import('@/views/KnowledgeGraphExtractView.vue'),
        meta: { title: '知识提取' }
      },
      // 数据统计分析模块（业务导向命名）
      {
        path: 'statistics',
        name: 'statistics',
        component: () => import('@/views/StatisticsView.vue'),
        meta: { title: '数据统计' }
      },
      {
        path: 'statistics/visualization',
        name: 'statistics-visualization',
        component: () => import('@/views/StatisticsVisualizationView.vue'),
        meta: { title: '可视化分析' }
      },
      {
        path: 'statistics/topic',
        name: 'statistics-topic',
        component: () => import('@/views/StatisticsTopicView.vue'),
        meta: { title: '专题分析' }
      },
      {
        path: 'statistics/prediction',
        name: 'statistics-prediction',
        component: () => import('@/views/StatisticsPredictionView.vue'),
        meta: { title: '预测分析' }
      },
      // 系统管理模块
      {
        path: 'system/user',
        name: 'system-user',
        component: () => import('@/views/SystemUserView.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'system/role',
        name: 'system-role',
        component: () => import('@/views/SystemRoleView.vue'),
        meta: { title: '角色权限' }
      },
      {
        path: 'system/config',
        name: 'system-config',
        component: () => import('@/views/SystemConfigView.vue'),
        meta: { title: '系统配置' }
      },
      {
        path: 'system/log',
        name: 'system-log',
        component: () => import('@/views/SystemLogView.vue'),
        meta: { title: '日志审计' }
      },
      {
        path: 'system/monitor',
        name: 'system-monitor',
        component: () => import('@/views/SystemMonitorView.vue'),
        meta: { title: '系统监控' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 保卫核心业务智能体`
  }

  // 检查登录状态
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (to.path === '/login') {
    if (token) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    if (!token) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
