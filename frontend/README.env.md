# 环境变量配置说明

## 环境变量文件

本项目使用 Vite 的环境变量系统，支持以下环境变量文件：

### 文件说明

- **`.env`** - 所有环境的默认配置（会被 git 忽略，需要手动创建）
- **`.env.local`** - 本地开发环境的本地配置（会被 git 忽略，优先级最高）
- **`.env.development`** - 开发环境配置（运行 `npm run dev` 时自动加载）
- **`.env.production`** - 生产环境配置（运行 `npm run build` 时自动加载）
- **`.env.example`** - 环境变量示例文件（可以提交到 git，作为模板）

### 优先级

环境变量的加载优先级（从高到低）：
1. `.env.local`（所有环境）
2. `.env.[mode].local`（如 `.env.development.local`）
3. `.env.[mode]`（如 `.env.development`）
4. `.env`

### 使用方法

#### 1. 首次使用

```bash
# 复制示例文件创建本地配置
cp .env.example .env
```

#### 2. 本地开发

创建 `.env` 或 `.env.local` 文件，配置如下：

```env
# API 基础地址
VITE_API_BASE_URL=/api/v1

# 应用标题
VITE_APP_TITLE=保卫核心业务智能体
```

#### 3. Docker 环境

在 Docker 环境中，环境变量通过 `docker-compose.yml` 配置，无需创建 `.env` 文件。

### 环境变量说明

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `VITE_API_BASE_URL` | API 基础地址 | `/api/v1` | `/api/v1` 或 `http://localhost:8000/api/v1` |
| `VITE_APP_TITLE` | 应用标题 | `保卫核心业务智能体` | - |
| `DOCKER_ENV` | Docker 环境标识 | - | `true`（Docker 中自动设置） |

### 注意事项

1. **必须以 `VITE_` 开头**：只有以 `VITE_` 开头的环境变量才会暴露给客户端代码
2. **敏感信息**：不要在 `.env` 文件中存储敏感信息，使用 `.env.local` 并确保它被 git 忽略
3. **重启服务**：修改环境变量后需要重启开发服务器才能生效

### 在代码中使用

```typescript
// 获取环境变量
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
const appTitle = import.meta.env.VITE_APP_TITLE

// 判断环境
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
const isDocker = import.meta.env.DOCKER_ENV === 'true'
```
