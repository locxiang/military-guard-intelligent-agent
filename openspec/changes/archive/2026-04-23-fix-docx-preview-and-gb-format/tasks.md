## 1. DOCX Preview Isolation

- [x] 1.1 重构 DocxPreview.vue 组件，使用 iframe 实现完全样式隔离
- [x] 1.2 实现 iframe 内部 HTML 注入，包含 docx-preview 库和基本样式
- [x] 1.3 实现父组件与 iframe 之间的 postMessage 通信
- [x] 1.4 测试 Blob、ArrayBuffer、URL 三种输入格式
- [x] 1.5 验证预览不受深色主题影响，保持原始样式

## 2. GB/T 9704-2012 Format Fixes

- [x] 2.1 修正红色分隔线实现（使用段落边框替代下划线）
- [x] 2.2 修正发文机关署名位置（右空四字）
- [x] 2.3 修正成文日期位置（右空四字）
- [x] 2.4 添加版记分隔线方法
- [x] 2.5 添加抄送机关方法（左空一字，回行对齐）
- [x] 2.6 添加印发机关和日期方法
- [x] 2.7 添加完整的版记方法，整合以上部分
- [x] 2.8 更新 RequestDocumentBuilder，集成版记功能
- [x] 2.9 生成测试文档，验证所有 GB/T 9704-2012 格式要求
