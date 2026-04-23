# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于AI技术的军队保卫业务智能化系统，实现卷宗管理、公文生成、分析预测等功能。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Tailwind CSS
- **后端**: Python 3.11 + FastAPI + SQLAlchemy 2.0
- **数据库**: MySQL 8.0
- **AI集成**: 通义千问 (DashScope API)
- **容器化**: Docker + Docker Compose

## 常用命令

### Docker Compose 命令

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose stop
docker-compose down

# 重新构建镜像
docker-compose build --no-cache
```

### 后端开发命令

```bash
# 进入后端容器
docker-compose exec backend bash

# 安装新依赖
pip install <package-name>
pip freeze > requirements.txt

# 运行测试
pytest test_official_doc.py -v

# 代码格式化
black .

# 代码检查
flake8 .
mypy .

# 数据库迁移（虽然项目使用自动初始化）
# alembic revision --autogenerate -m "描述"
# alembic upgrade head
```

### 前端开发命令

```bash
# 进入前端容器
docker-compose exec frontend sh

# 安装新依赖
pnpm add <package-name>

# 代码检查
pnpm lint
```

### 数据库操作

```bash
# 连接MySQL
docker-compose exec mysql mysql -u user -p military_guard

# 备份数据库
docker-compose exec mysql mysqldump -u user -p military_guard > data/backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

## 访问地址

- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **phpMyAdmin**: http://localhost:8080
- **MySQL**: localhost:3306

## 代码架构

### 后端架构 (backend/app/)

```
backend/app/
├── main.py                 # FastAPI 应用入口
├── core/                   # 核心模块
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── database_init.py   # 数据库自动初始化
│   ├── security.py        # 安全工具
│   ├── errors.py          # 错误处理
│   ├── response.py        # 统一响应格式
│   ├── middleware.py      # 中间件（等保2.0）
│   └── audit.py           # 审计日志
├── api/v1/                # API 路由
│   ├── auth.py            # 认证
│   ├── archive.py         # 案卷管理
│   ├── ocr.py             # OCR数字化
│   ├── classification.py  # 智能分类
│   ├── doc_generate.py    # 文档生成（含国标公文API）
│   ├── template.py        # 模板管理
│   ├── content_review.py  # 内容审查
│   ├── knowledge_graph.py # 知识图谱
│   ├── statistics.py      # 统计分析
│   ├── user.py            # 用户管理
│   ├── audit.py           # 审计日志
│   └── dashboard.py       # 工作台
├── models/                # SQLAlchemy 数据模型
├── schemas/               # Pydantic 模式
├── services/              # 业务逻辑层
│   ├── qwen_service.py    # 通义千问AI服务
│   └── official_doc/      # 国标公文生成服务
│       ├── service.py     # 主服务入口
│       ├── structure_config.py  # 公文结构配置
│       ├── content_generator.py # 内容生成器
│       ├── formats/       # 格式标准（GB/T 9704-2012）
│       └── builders/      # 文档构建器（请示/报告/通知/纪要）
└── utils/                 # 工具函数
```

### 前端架构 (frontend/src/)

```
frontend/src/
├── main.ts                # 应用入口
├── router/index.ts        # 路由配置
├── App.vue                # 根组件
├── components/            # 通用组件
│   ├── layout/            # 布局组件
│   └── DocxPreview.vue    # docx 预览组件
├── views/                 # 页面组件
│   ├── LoginView.vue      # 登录页
│   ├── DashboardView.vue  # 工作台
│   ├── ArchiveListView.vue # 案件列表
│   ├── ArchiveImportView.vue # 案件导入
│   ├── ArchiveDetail/     # 案件详情（多组件）
│   ├── ArchiveClassificationView.vue # 卷宗审核
│   ├── DocGenerateCaseView.vue # 案件卷宗生成
│   ├── DocGenerateOfficialView.vue # 公文助手（步骤1-选择类型）
│   ├── DocGenerateOfficialStep1View.vue # 公文助手步骤1
│   ├── DocGenerateOfficialStep2View.vue # 内容生成与编辑
│   ├── DocGenerateOfficialStep3View.vue # 标准公文预览
│   ├── DocGenerateOfficialResultView.vue # 公文生成结果
│   ├── DocGenerateReportView.vue # 报告生成器
│   ├── DocGenerateReportResultView.vue # 报告结果
│   ├── DocGenerateMeetingView.vue # 会议纪要
│   ├── DocGenerateMeetingResultView.vue # 会议纪要结果
│   ├── DocGenerateStoryView.vue # 警示小故事
│   ├── DocGenerateStoryResultView.vue # 小故事结果
│   ├── KnowledgeGraphView.vue # 关联查询
│   ├── StatisticsView.vue # 数据统计
│   ├── TemplateView.vue   # 模板管理
│   ├── ContentReviewView.vue # 内容审查
│   └── System*.vue        # 系统管理页面
├── api/                   # API 调用
│   └── doc-generate.ts  # 文档生成 API
├── stores/                # Pinia 状态管理
├── utils/                 # 工具函数
└── styles/                # 样式文件
```

## 主要功能模块

### 1. 案卷管理 (Archive)
- 案件导入（支持PDF解析）
- 案件列表与检索
- 案件详情查看
- OCR数字化
- 智能分类与审核入库

### 2. 文档生成 (Doc Generate)
- 案件卷宗生成
- 公文助手（支持 GB/T 9704-2012 国家标准公文格式）
  - 两步式生成流程：分段内容生成 → 标准 docx 组装
  - 支持请示、报告、通知、纪要、函等公文类型
  - 1:1 docx 预览与导出
- 报告生成器
- 会议纪要生成（支持文字随记和录音转写稿）
- 警示小故事生成

### 3. 知识图谱 (Knowledge Graph)
- 实体管理
- 关系管理
- 知识提取
- 关联查询

### 4. 统计分析 (Statistics)
- 数据统计
- 可视化分析
- 专题分析
- 预测分析

### 5. 系统管理
- 用户管理
- 角色权限
- 系统配置
- 日志审计
- 系统监控

## 关键技术点

### 后端
- **数据库自动初始化**: `database_init.py` 会在启动时检查表是否存在，自动创建和同步
- **统一响应格式**: `ResponseModel` 封装所有API响应
- **等保2.0中间件**: 安全头部、访问日志、速率限制、输入清理
- **审计日志**: 记录用户操作
- **JWT认证**: 无状态认证
- **国标公文生成**: `services/official_doc/` 模块实现 GB/T 9704-2012 标准公文格式
- **流式API**: SSE 流式输出用于文档生成
- **OpenSpec**: 特性开发使用 OpenSpec 工作流（`openspec/` 目录）

### 前端
- **路由守卫**: 自动检查登录状态
- **Element Plus**: UI组件库（中文）
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **MateChat**: AI聊天组件
- **Docx 预览**: `@vue-office/docx` + `docx-preview` 实现 1:1 文档预览
- **两步式公文生成**: 分段内容生成 → 标准 docx 组装流程

## 环境变量

参考 `.env.example` 配置环境变量，关键配置：
- `DASHSCOPE_API_KEY`: 通义千问API密钥（必需用于AI功能）
- `MYSQL_*`: 数据库配置
- `SECRET_KEY` / `JWT_SECRET_KEY`: 安全密钥（生产环境必须修改）

## 开发注意事项

1. **代码热重载**: 后端和前端都支持热重载，修改代码后自动刷新
2. **数据库初始化**: 应用启动时自动检查和初始化数据库表
3. **AI功能**: 需要配置 `DASHSCOPE_API_KEY` 才能使用文档生成等AI功能
4. **文件上传**: 上传的文件存储在 `data/uploads/` 目录
5. **日志**: 应用日志存储在 `data/logs/` 目录
6. **OpenSpec 工作流**: 新功能开发使用 OpenSpec 特性工作流
   - `/openspec-explore`: 探索模式，思考问题和需求
   - `/openspec-propose`: 提案模式，创建设计和任务
   - `/openspec-apply-change`: 实施任务
   - `/openspec-archive-change`: 归档完成的变更
7. **公文生成测试**: 使用 `test_official_doc.py` 测试国标公文生成功能
8. **Docx 预览**: 前端使用独立的 `docx-preview.html` 页面避免 iframe 沙箱问题
