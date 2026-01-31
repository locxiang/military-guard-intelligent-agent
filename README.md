# 保卫核心业务智能体

基于AI技术的军队保卫业务智能化系统，实现卷宗管理、公文生成、分析预测等功能。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Tailwind CSS
- **后端**: Python 3.11 + FastAPI + SQLAlchemy
- **数据库**: MySQL 8.0
- **容器化**: Docker + Docker Compose

## 快速开始

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0
- Git

### 环境配置

1. **克隆项目**
```bash
git clone <repository-url>
cd military-guard-intelligent-agent
```

2. **配置环境变量**
```bash
cp .env.example .env
# 根据需要修改 .env 文件中的配置
```

3. **创建数据目录**
```bash
mkdir -p data/{mysql,uploads,logs,backups}
```

### 启动开发环境

1. **启动所有服务**
```bash
docker-compose up -d
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **查看日志**
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### 访问服务

- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **MySQL**: localhost:3306

### 停止服务

```bash
# 停止所有服务（保留数据）
docker-compose stop

# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和数据卷（⚠️ 会删除数据）
docker-compose down -v
```

## 开发指南

### 前端开发

1. **进入前端容器**
```bash
docker-compose exec frontend sh
```

2. **安装新依赖**
```bash
docker-compose exec frontend pnpm add <package-name>
```

3. **代码热更新**
   - 修改 `frontend/src/` 下的代码会自动热更新
   - 浏览器会自动刷新

### 后端开发

1. **进入后端容器**
```bash
docker-compose exec backend bash
```

2. **安装新依赖**
```bash
docker-compose exec backend pip install <package-name>
# 更新 requirements.txt
docker-compose exec backend pip freeze > requirements.txt
```

3. **代码热更新**
   - 修改 `backend/app/` 下的代码会自动重载
   - 无需重启容器

4. **数据库迁移**
```bash
# 创建迁移文件
docker-compose exec backend alembic revision --autogenerate -m "描述"

# 执行迁移
docker-compose exec backend alembic upgrade head
```

### 数据库操作

1. **连接MySQL**
```bash
docker-compose exec mysql mysql -u user -p military_guard
# 密码: password (或 .env 中配置的密码)
```

2. **查看表结构**
```sql
USE military_guard;
SHOW TABLES;
DESCRIBE users;
```

3. **备份数据库**
```bash
docker-compose exec mysql mysqldump -u user -p military_guard > data/backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

## 项目结构

```
military-guard-intelligent-agent/
├── frontend/              # 前端项目
│   ├── src/              # 源代码
│   ├── Dockerfile.dev    # 开发环境Dockerfile
│   └── package.json
├── backend/              # 后端项目
│   ├── app/              # 应用代码
│   ├── scripts/          # 脚本文件
│   ├── Dockerfile.dev    # 开发环境Dockerfile
│   └── requirements.txt  # Python依赖
├── data/                 # 数据存储
│   ├── mysql/           # MySQL数据
│   ├── uploads/         # 上传文件
│   ├── logs/            # 日志文件
│   └── backups/         # 备份文件
├── docker-compose.yml   # Docker Compose配置
├── .env.example         # 环境变量示例
└── README.md
```

## 常见问题

### 1. 端口被占用

修改 `docker-compose.yml` 中的端口映射，或修改 `.env` 文件中的端口配置。

### 2. 权限问题

确保 `data/` 目录有写权限：
```bash
chmod -R 755 data/
```

### 3. 数据库连接失败

检查 MySQL 服务是否正常启动：
```bash
docker-compose ps mysql
docker-compose logs mysql
```

### 4. 前端无法访问后端API

检查 `frontend/vite.config.ts` 中的代理配置，确保指向正确的后端地址。

### 5. 依赖安装失败

尝试重新构建镜像：
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 项目文档

所有项目文档已整理到 `docs/` 目录，请参考 [文档目录](./docs/README.md) 查看详细文档。

### 快速导航

- **[系统功能设计（业务导向版）](./docs/系统功能设计-业务导向版.md)** - 业务人员必读：系统功能和业务流程说明
- **[开发设计文档](./docs/开发设计文档.md)** - 开发人员必读：开发环境、规范、API设计
- **[产品需求文档](./docs/产品需求文档.md)** - 产品需求详细说明
- **[API文档使用说明](./docs/API文档使用说明.md)** - API接口使用说明
- **[数据库初始化说明](./docs/数据库初始化说明.md)** - 数据库初始化机制

更多文档请查看 [docs/README.md](./docs/README.md)

## 开发规范

请参考 [开发设计文档](./docs/开发设计文档.md) 了解详细的开发规范、API设计、数据库设计等内容。

## 许可证

[待定]

## 联系方式

[待定]
