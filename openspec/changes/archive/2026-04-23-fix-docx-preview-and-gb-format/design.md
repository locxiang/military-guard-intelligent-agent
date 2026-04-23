## Context

当前公文生成系统存在两个主要问题：

1. **DOCX 预览问题**：前端使用深色军事主题，全局 CSS 变量 `--military-text-primary: #FFFFFF` 导致预览继承白色文字，与白色背景融合。当前尝试了多个预览库（docx-preview、@vue-office/docx、@js-preview/docx）都未能彻底解决样式污染问题。

2. **国标格式问题**：后端 GB/T 9704-2012 实现存在多处不符合标准的地方，包括红色分隔线用下划线实现、发文机关署名和日期位置不准确、缺少版记部分等。

## Goals / Non-Goals

**Goals:**
- 使用 iframe 实现 DOCX 预览的完全样式隔离
- 修正红色分隔线实现（使用段落边框）
- 修正发文机关署名和日期位置（右空四字）
- 添加完整的版记部分（抄送机关、印发机关、印发日期）
- 确保所有文档格式符合 GB/T 9704-2012 标准

**Non-Goals:**
- 不修改现有深色主题系统
- 不调整其他模块的样式
- 不改变 DOCX 生成的 API 接口

## Decisions

### 1. DOCX 预览方案选择：iframe 完全隔离

**备选方案：**
- 方案 A：CSS `all: initial` 强隔离（可能仍有继承问题）
- 方案 B：Shadow DOM（兼容性复杂）
- 方案 C：iframe 完全隔离（最彻底）

**决策：选择方案 C（iframe）**

**理由：**
- 完全独立的 DOM 上下文，无任何样式继承
- 可以独立设置 `color-scheme: light`
- 实现简单，兼容性好
- 可以完全控制 iframe 内的样式加载

**实现架构：**
```
DocxPreview.vue (父组件)
  └─ iframe (src="about:blank")
      └─ 内部注入：
          ├─ docx-preview 库
          ├─ 简单的白色背景样式
          └─ 文档渲染容器
```

**通信方式：**
- 父组件通过 `postMessage` 传递 Blob/ArrayBuffer 数据
- iframe 内部监听消息并渲染文档

### 2. 国标格式修改方案

**红色分隔线：**
- 当前：下划线 `"_" * 50`
- 修改：使用段落底部边框，红色粗实线，宽度与版心同宽

**发文机关署名和日期：**
- 当前：简单右对齐
- 修改：右空四字编排（使用缩进或制表符）

**版记部分：**
- 新增：版记分隔线（细实线）
- 新增：抄送机关（左空一字，回行对齐）
- 新增：印发机关和日期（印发机关左空一字，日期右空一字）

## Risks / Trade-offs

### Risk 1：iframe 通信复杂度
→ Mitigation：使用简单的 postMessage 协议，数据类型限制为 Blob/ArrayBuffer

### Risk 2：iframe 加载性能
→ Mitigation：预创建 iframe，仅在需要时注入内容

### Risk 3：国标格式验证
→ Mitigation：生成测试文档，对照 GB/T 9704-2012 标准逐项验证
