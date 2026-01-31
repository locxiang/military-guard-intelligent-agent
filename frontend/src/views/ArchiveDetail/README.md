# ArchiveDetail 组件结构说明

## 已完成的工作

### 1. 文件夹结构
```
ArchiveDetail/
├── index.vue                    # 主文件
├── utils.ts                     # 工具函数
├── components/                  # 组件文件夹
│   ├── TopActionBar.vue         # 顶部操作栏 ✅
│   ├── CaseHeaderCard.vue       # 案件核心信息卡片 ✅
│   ├── CaseStatusGuide.vue      # 案件状态引导 ✅
│   ├── CaseContentSection.vue   # 内容区块（可复用）✅
│   ├── CaseTimeline.vue         # 案件时间线 ✅
│   ├── CaseDocumentCard.vue     # 原始文档卡片 ✅
│   ├── CaseClassificationTags.vue # 分类和标签 ✅
│   ├── CaseOcrText.vue          # OCR文本 ✅
│   ├── RelatedCasesSection.vue  # 关联案卷 ✅
│   ├── PrintPreviewDialog.vue   # 打印预览对话框 ✅
│   └── DocumentPreviewDialog.vue # 文档预览对话框 ✅
└── README.md                    # 说明文档
```

### 2. 已创建的组件

#### TopActionBar.vue
- 顶部导航和操作栏
- 包含返回按钮、搜索框、文档操作按钮

#### CaseHeaderCard.vue
- 案件核心信息展示
- 案件编号、状态、标题、摘要信息

#### CaseStatusGuide.vue
- 案件处理状态引导
- 显示立案、判决等状态

#### CaseContentSection.vue
- 可复用的内容区块组件
- 支持编号、标题、副标题、操作按钮插槽

#### utils.ts
- 工具函数集合
- 包含格式化、高亮、文件类型判断等函数

### 3. 主文件重构
- 已将主文件拆分为 `index.vue`
- 使用组件化方式组织代码
- 路由已更新指向新文件

## 已完成的组件（全部完成）

### 1. CaseTimeline.vue ✅
- 案件时间线展示
- 支持不同类型的时间节点显示

### 2. CaseDocumentCard.vue ✅
- 原始文档卡片
- 支持PDF、图片、Word、Excel等文件类型预览

### 3. CaseClassificationTags.vue ✅
- 分类和标签展示
- 支持点击标签搜索

### 4. CaseOcrText.vue ✅
- OCR文本展示（可选）
- 支持展开/收起长文本

### 5. RelatedCasesSection.vue ✅
- 关联案卷区域
- 支持按人员/部门/罪名/时间筛选

### 6. PrintPreviewDialog.vue ✅
- 打印预览对话框
- 符合部队公文格式的打印样式

### 7. DocumentPreviewDialog.vue ✅
- 文档预览对话框
- 支持PDF、图片预览和全屏模式

## 使用说明

### 导入组件
```vue
import TopActionBar from './components/TopActionBar.vue'
import CaseHeaderCard from './components/CaseHeaderCard.vue'
// ... 其他组件
```

### 使用工具函数
```typescript
import { highlightText, formatDateTime, getStatusType } from './utils'
```

## 后续工作

1. 完成剩余组件的创建
2. 将样式从主文件拆分到各组件
3. 完善组件的 props 和 emits 定义
4. 添加组件的 TypeScript 类型定义
5. 测试所有组件的功能

## 备份文件

原文件已备份为：`ArchiveDetailView.vue.backup`
