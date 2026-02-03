---
name: python-backend-layered-db-sync
description: Guides Python3 backend API development with strong decoupling, layered design, unified API responses, and startup-time database schema sync. Use when designing or refactoring FastAPI/Flask backends, organizing api/services/models/core, or when the user wants automatic table structure sync and default data seeding without manual migrations.
---

# Python3 后端 API：分层设计与启动时数据库同步

强调代码解耦、分层清晰、API 统一；数据库以「启动时检查 + 结构同步」为准，不采用手动迁移；表数据仅按「表是否为空」决定是否填入默认数据。

## 分层与解耦

### 目录与职责

| 层 | 目录 | 职责 |
|----|------|------|
| 路由 | `api/` 或 `api/v1/` | 接收请求、校验参数、调用 service、返回统一响应；**不写业务逻辑** |
| 业务 | `services/` | 业务逻辑、编排、调用外部/模型；**不直接依赖请求对象** |
| 数据 | `models/` | ORM 模型、表定义；**不写业务** |
| 核心 | `core/` | 配置、数据库连接、统一响应封装、鉴权、错误码 |
| 契约 | `schemas/` | 请求/响应结构（Pydantic 等）；可选，也可放在 api 层 |

### 原则

- **路由层**：薄薄一层，只做参数解析、鉴权、调用 service、用 `ResponseModel` 或统一格式返回。
- **服务层**：可被多处路由复用；入参为明确类型（dict、schema、id），不依赖 `request`。
- **模型层**：只定义表结构和关系；需要「与代码一致」时，在**启动时**由 `database_init` 同步，见下文。

## API 统一性

- **响应格式**：所有接口使用同一套结构，例如 `{ errorCode, message, data }` 或 `{ errorCode, message, data, page }`（分页）。
- **错误处理**：在 `core` 中集中定义错误码和异常类；路由层捕获后转成统一 JSON，不散落各接口。
- **分页**：统一字段名（如 `page`, `pageSize`, `total`），由 `core.response` 或等价模块封装。

## 数据库：启动时检查与同步（不做手动迁移）

### 思路

- **不采用**：Alembic 等迁移工具、手写 SQL 迁移脚本。
- **采用**：应用**启动时**执行「表结构检查与同步」+「按表是否为空决定是否填默认数据」。

### 启动流程（推荐顺序）

1. **表存在性**  
   - 用 SQLAlchemy `Base.metadata.create_all` 创建缺失的表。  
   - 按需在**同一或单独事务**内执行必要的 `ALTER`（例如确保主键 `id` 为自增），并提交。

2. **表数据（仅当表为空）**  
   - 对每张需要默认数据的表：`SELECT COUNT(*)` 判断是否为空。  
   - **若为空**：从 JSON/脚本等读取默认数据并 INSERT。  
   - **若不为空**：**不处理**，不覆盖、不清空。

3. **表结构同步（可选但推荐）**  
   - 对比「当前库表结构」与「ORM 模型定义」（列名、类型、可空等）。  
   - 发现不一致时执行 `ALTER TABLE` 补齐或修正列，使**数据库结构与代码一致**。  
   - 若某表不存在，已在步骤 1 创建，此处只做「已有表」的结构对齐。

### 实现要点

- 初始化逻辑放在 `core/database_init.py` 或等价模块，在 `main.py` 或 FastAPI `lifespan` 里**启动时调用一次**。
- 默认数据来源：每张表对应一个 JSON 或脚本；只读、不依赖运行时请求。
- 主键自增：若使用 MySQL，建表或同步后显式 `ALTER TABLE xxx MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT`，避免 1364 错误。

## 何时使用本技能

- 设计或重构 Python3 后端 API（FastAPI/Flask 等）时，需要分层与解耦指导。
- 需要统一响应格式、错误码、分页格式时。
- 讨论或实现「数据库与代码一致」、**不做手动迁移**、**仅对空表填默认数据**时。
- 编写或修改 `database_init`、启动时表结构检查与默认数据逻辑时。
