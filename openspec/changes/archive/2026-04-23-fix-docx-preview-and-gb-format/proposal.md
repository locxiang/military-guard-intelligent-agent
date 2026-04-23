## Why

当前公文生成功能存在两个关键问题：1) DOCX 预览受全局深色主题影响，文字变为白色且丢失原有样式；2) 生成的 DOCX 文档格式不完全符合 GB/T 9704-2012 国家标准。这两个问题严重影响了公文生成和预览的用户体验及文档的正式性。

## What Changes

- **修复 DOCX 预览问题**：使用 iframe 完全隔离预览容器，避免全局深色主题样式污染，确保文档原始样式正确显示
- **完善 GB/T 9704-2012 国标格式**：修正红色分隔线、发文机关署名和日期位置、添加版记部分等
- **保持 DOCX 原始样式**：预览时不添加任何自定义样式修改，完全保留文档的字体、颜色、间距等属性

## Capabilities

### New Capabilities

- `docx-preview-isolation`: 使用 iframe 实现 DOCX 预览的完全样式隔离

### Modified Capabilities

- `official-doc-generation`: 更新国标公文生成，完善 GB/T 9704-2012 格式实现

## Impact

- 前端：`frontend/src/components/DocxPreview.vue` 组件需要重构
- 后端：`backend/app/services/official_doc/` 模块需要更新
- 依赖：无需新增依赖，使用现有技术栈
