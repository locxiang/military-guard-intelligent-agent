# BigDataDocAuto Frontend

基于 Vue3 + TypeScript + Pinia + Vite + Tailwind CSS + Element Plus 的开发脚手架

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - JavaScript 的超集，提供静态类型检查
- **Pinia** - Vue 官方状态管理库
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Element Plus** - 基于 Vue 3 的组件库

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 开发

```bash
npm run dev
# 或
yarn dev
# 或
pnpm dev
```

### 构建

```bash
npm run build
# 或
yarn build
# 或
pnpm build
```

### 预览构建结果

```bash
npm run preview
# 或
yarn preview
# 或
pnpm preview
```

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   ├── styles/          # 样式文件
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口文件
├── index.html           # HTML 模板
├── vite.config.ts       # Vite 配置
├── tailwind.config.js   # Tailwind CSS 配置
├── postcss.config.js    # PostCSS 配置
└── tsconfig.json        # TypeScript 配置
```

## 特性

- ✅ Vue 3 Composition API
- ✅ TypeScript 支持
- ✅ Pinia 状态管理
- ✅ Vue Router 路由
- ✅ Tailwind CSS 样式框架
- ✅ Element Plus UI 组件库（按需自动导入）
- ✅ ESLint + Prettier 代码规范
- ✅ 路径别名配置（@ 指向 src）

