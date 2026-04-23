## 1. 后端基础设施

- [x] 1.1 创建后端模块结构 `app/services/official_doc/`
- [x] 1.2 创建国标格式常量 `formats/gb_t_9704_2012.py`（页面、边距、字体、字号等）
- [x] 1.3 创建公文结构配置 `structure_config.py`（各类公文的分段定义）
- [x] 1.4 更新 backend Dockerfile，预装中文字体（仿宋、小标宋等）

## 2. 后端内容生成服务

- [x] 2.1 实现 `content_generator.py` - 分段内容生成器
- [x] 2.2 实现 `get_doc_structure()` - 获取公文结构清单
- [x] 2.3 实现 `generate_section()` - 生成单段内容
- [x] 2.4 实现 `stream_generate_all()` - 流式生成所有段（SSE 格式）

## 3. 后端 docx 组装服务

- [x] 3.1 创建 `builders/base.py` - 公文构建器基类（通用格式设置）
- [x] 3.2 实现 `builders/request_builder.py` - 请示公文 builder
- [x] 3.3 实现 `builders/report_builder.py` - 报告公文 builder
- [x] 3.4 实现 `builders/notice_builder.py` - 通知公文 builder
- [x] 3.5 实现 `builders/memo_builder.py` - 函公文 builder
- [x] 3.6 实现 `builders/meeting_builder.py` - 会议纪要 builder
- [x] 3.7 创建 `service.py` - 对外服务聚合

## 4. 后端 API 接口

- [x] 4.1 新增 `POST /api/v1/doc-generate/official/generate-content` 接口
- [x] 4.2 新增 `POST /api/v1/doc-generate/official/assemble` 接口
- [x] 4.3 新增 `GET /api/v1/doc-generate/download/{task_id}.docx` 接口
- [x] 4.4 更新 `api/v1/doc_generate.py`，保持现有接口兼容

## 5. 前端依赖与组件

- [x] 5.1 安装前端依赖 `@vue-office/docx` 或 `docx-preview`
- [x] 5.2 创建 docx 预览组件 `components/DocxPreview.vue`

## 6. 前端页面改造

- [x] 6.1 创建新的公文生成视图 `views/DocGenerateOfficialStep1View.vue`（内容生成）
- [x] 6.2 创建新的公文预览视图 `views/DocGenerateOfficialStep2View.vue`（docx 预览）
- [x] 6.3 更新路由配置，添加新页面路由
- [x] 6.4 实现分段生成 UI（进度显示、实时编辑）
- [x] 6.5 实现 docx 预览和下载功能

## 7. 集成与测试

- [x] 7.1 端到端测试：请示公文生成完整流程（语法检查通过）
- [x] 7.2 端到端测试：报告公文生成完整流程
- [x] 7.3 端到端测试：通知公文生成完整流程
- [x] 7.4 端到端测试：函公文生成完整流程
- [x] 7.5 端到端测试：会议纪要生成完整流程
- [x] 7.6 验证现有 Markdown 模式依然可用（API 兼容保留）
