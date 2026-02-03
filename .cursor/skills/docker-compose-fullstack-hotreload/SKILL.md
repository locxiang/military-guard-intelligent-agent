---
name: docker-compose-fullstack-hotreload
description: Configures docker-compose for Vue3 + Python3 + MySQL full-stack development with hot reload. Use when setting up or modifying dev environments with docker-compose, pnpm dev, Vite, uvicorn --reload, or when the user wants to edit code without local build or dependency install.
---

# Docker Compose 全栈热更新开发

在容器内安装依赖、运行 dev 服务，宿主机只挂载源码；改代码即热更新，无需本机安装 Node/pnpm 或 Python/pip。

## 核心思路

| 角色 | 宿主机 | 容器内 |
|------|--------|--------|
| 代码 | 用 IDE 编辑（不装依赖） | 通过 volume 挂载进容器 |
| 依赖 | 不安装 | 在 Dockerfile / 启动命令里安装 |
| 进程 | 不跑 dev 服务 | 跑 pnpm dev / uvicorn --reload |

## docker-compose 配置要点

### 前端 (Vue3 + Vite / pnpm)

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
  volumes:
    - ./frontend:/app           # 源码挂载，改即生效
    - /app/node_modules         # 匿名卷：node_modules 只在容器内，不覆盖宿主机
    - /app/.vite                # 可选：Vite 缓存放容器，避免权限问题
  ports:
    - "5173:5173"
  command: sh -c "pnpm install && pnpm dev --host 0.0.0.0 --port 5173"
```

- **必须**使用匿名卷 `/app/node_modules`，否则宿主机没有 node_modules 时会把空目录挂进去，导致依赖丢失。
- `command` 里先 `pnpm install` 再 `pnpm dev`，保证新增依赖后重启容器即可，无需本机执行 pnpm。

### 后端 (Python3 / FastAPI)

```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile.dev
  volumes:
    - ./backend:/app
    - ./data/uploads:/app/uploads   # 按需：上传目录
  ports:
    - "8000:8000"
  command: sh -c "pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
```

- `uvicorn ... --reload` 监听文件变化，改 Python 代码即热重载。
- `command` 里先 `pip install -r requirements.txt` 再启动，方便在 requirements.txt 增加依赖后重启容器即可。

### MySQL

- 仅数据持久化：`volumes: - ./data/mysql:/var/lib/mysql`，不挂载代码。

## Dockerfile.dev 建议

- **只** COPY 依赖声明（`package.json`+lock / `requirements.txt`），在镜像里安装依赖；**不要** COPY 整份业务源码，否则和运行时 volume 挂载混在一起容易混淆。
- CMD 用 dev 命令（pnpm dev / uvicorn --reload）；若 docker-compose 里用 `command` 覆盖，以 `command` 为准。

**前端 Dockerfile.dev 示例：**

```dockerfile
FROM node:20-alpine
RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install
EXPOSE 5173
CMD ["sh", "-c", "pnpm install && pnpm dev --host 0.0.0.0 --port 5173"]
```

**后端 Dockerfile.dev 示例：**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

## 日常流程

1. **启动**：`docker-compose up -d`（或 `docker-compose up` 看日志）。
2. **改代码**：直接改宿主机上的 `frontend/`、`backend/`；Vite 与 uvicorn --reload 会自动热更新。
3. **加依赖**：
   - 前端：改 `package.json` 或 `pnpm add xxx` 在本机只改文件，然后 `docker-compose restart frontend`。
   - 后端：改 `requirements.txt`，然后 `docker-compose restart backend`。
4. **不**在本机执行 `pnpm install` / `pip install`（可选：本机也装一份用于 IDE 补全，但运行以容器为准）。

## 常见问题

- **前端白屏/依赖报错**：确认有匿名卷 `- /app/node_modules`，并重启 frontend 让容器内重新 `pnpm install`。
- **后端 500 / 模块找不到**：确认 `command` 里包含 `pip install -r requirements.txt`，并重启 backend。
- **热更新不生效**：Linux 下若 inotify 限制导致监听不到，可增加 volume 的 `:cached` 或检查 Vite/uvicorn 的 watch 配置。

## 何时使用本技能

- 用 docker-compose 跑 Vue3 + Python3 + MySQL 全栈、且希望本机不装 Node/Python 依赖时。
- 配置或排查「改代码不热更新」「依赖在容器里才对」一类问题时。
- 需要写或改 Dockerfile.dev、docker-compose 的 volumes/command 时。
