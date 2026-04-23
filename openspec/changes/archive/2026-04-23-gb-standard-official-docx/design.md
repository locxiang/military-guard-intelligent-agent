## Context

当前系统文档生成使用通义千问 AI 生成 Markdown 内容，前端通过 marked 渲染 HTML 预览，再用 docx 库简单转换为 docx 下载。这种方式存在以下问题：
- Markdown 表达能力有限，无法精确控制公文格式（红头、版头、行距、缩进等）
- 前端 HTML 预览与最终 docx 格式不一致
- 不符合 GB/T 9704-2012 党政机关公文格式标准

现有技术栈：
- 后端：Python 3.11 + FastAPI + python-docx 1.1.0
- 前端：Vue 3 + TypeScript + docx 8.6.0

## Goals / Non-Goals

**Goals:**
- 实现符合 GB/T 9704-2012 标准的公文格式
- 提供两步式生成流程：内容生成 → docx 组装
- 分段流式生成内容，提升用户体验
- 1:1 docx 预览（使用 Vue3 docx 组件）
- 支持请示、报告、通知、函、会议纪要等公文类型

**Non-Goals:**
- 不使用 docx 模板文件，全部通过代码生成
- 不使用 PDF 预览，直接预览 docx
- 不修改其他文档类型（案件卷宗、警示小故事等）的生成逻辑

## Decisions

### 1. 两步式生成流程
**决策**: 采用「内容生成 → docx 组装」的两步流程

**替代方案**:
- 方案 A: 一步生成（直接生成带格式的 docx）- 用户等待时间长，无法编辑
- 方案 B: 全前端生成 - 格式控制能力有限，AI 提示词复杂

**理由**: 两步式既保证用户体验（实时生成、可编辑），又保证格式精度（后端精确控制）

### 2. 后端使用 python-docx 代码生成
**决策**: 使用 python-docx 代码直接构建 docx，不使用模板文件

**替代方案**:
- 方案 A: docx 模板文件 + 占位符替换 - 模板管理复杂，版本控制困难
- 方案 B: 使用 LibreOffice 转换 - 依赖重，容器化复杂

**理由**: 代码生成更灵活，便于调整格式，无需管理模板文件

### 3. 前端使用 @vue-office/docx 预览
**决策**: 使用 @vue-office/docx 组件进行 docx 预览

**替代方案**:
- 方案 A: docx-preview - 功能相对简单
- 方案 B: OnlyOffice / 微软 Office Online - 依赖外部服务

**理由**: @vue-office/docx 专为 Vue3 设计，纯前端无依赖，效果良好

### 4. API 设计
**决策**: 新增两个独立接口
- `POST /api/v1/doc-generate/official/generate-content` - 分段流式生成内容
- `POST /api/v1/doc-generate/official/assemble` - 组装 docx

**替代方案**:
- 保留现有接口，增加参数控制 - 接口职责不清晰

**理由**: 接口职责分离，便于维护和扩展

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| 中文字体在容器中缺失 | docx 格式不正确 | Dockerfile 预装仿宋、小标宋等字体 |
| @vue-office/docx 预览与实际 docx 有细微差异 | 用户体验受影响 | 文档说明，并提供下载后确认 |
| 两步式流程增加用户操作步骤 | 流程变长 | 优化 UI，提供「一键生成」快捷选项 |
| python-docx 对某些复杂格式支持有限 | 格式不完美 | 逐步迭代，必要时结合其他库 |

## Migration Plan

1. 新增后端模块 `app/services/official_doc/`
2. 新增 API 接口（兼容现有接口）
3. 前端新建文档生成视图（保留旧视图作为备选）
4. 灰度测试，逐步迁移
5. 确认稳定后 deprecate 旧接口

Rollback: 保留旧代码和接口，可随时切换回原流程

## Open Questions

1. 是否需要支持用户自定义公文格式参数（如页边距、字号）？
   - 暂定：v1.0 只支持标准 GB/T 9704-2012 格式，后续版本可考虑自定义
2. 是否需要支持红头文件的自定义抬头（如不同单位名称）？
   - 暂定：通过系统配置支持
