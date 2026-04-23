## Why

当前公文生成使用 Markdown 格式，无法精确符合 GB/T 9704-2012 党政机关公文格式标准，且前端预览与最终导出格式不一致。需要支持标准公文格式的 docx 生成，提供 1:1 的预览效果。

## What Changes

- 新增两步式公文生成流程：先分段流式生成内容（可编辑），再一键生成标准 docx
- 后端使用 python-docx 代码直接生成符合国标的 docx 文件（红头、版头、主体、版记等格式）
- 前端集成 Vue3 docx 预览组件，实现 1:1 文档预览
- 保留现有 Markdown 生成能力作为可选模式
- **BREAKING**: 文档生成 API 接口调整，新增内容生成和 docx 组装两个独立接口

## Capabilities

### New Capabilities
- `gb-official-docx-generation`: 国家标准公文格式 docx 生成与预览
- `sectioned-content-generation`: 分段流式内容生成，支持实时预览和编辑

### Modified Capabilities
- `doc-generation`: 现有文档生成能力扩展，支持新的两步式流程

## Impact

- **后端**: 新增 `app/services/official_doc/` 模块，修改 `api/v1/doc_generate.py`
- **前端**: 修改文档生成相关视图，新增 docx 预览组件
- **依赖**: 后端新增 `python-docx`（已有），前端新增 `@vue-office/docx` 或 `docx-preview`
