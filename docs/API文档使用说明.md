# API 文档使用说明

## Swagger UI 文档

FastAPI 自动生成了交互式 API 文档，可以通过以下方式访问：

### 访问地址

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 在 Docker 中访问

如果使用 Docker Compose 运行，访问地址为：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 功能特性

### 1. 交互式 API 测试

Swagger UI 提供了完整的交互式界面，可以：
- 查看所有 API 接口
- 查看请求参数和响应格式
- 直接在浏览器中测试 API
- 查看请求示例和响应示例

### 2. 认证测试

在 Swagger UI 中测试需要认证的接口：

1. 点击右上角的 **"Authorize"** 按钮
2. 在弹出的对话框中输入：
   - **Value**: `Bearer <your_token>`
   - 例如：`Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. 点击 **"Authorize"** 确认
4. 之后所有需要认证的接口都会自动携带 Token

### 3. 接口分组

API 文档按功能模块分组：
- **认证**: 登录、登出、Token刷新
- **档案管理**: 档案导入、查询、检索
- **文档生成**: 文档生成、模板管理
- **知识图谱**: 实体查询、关系查询

### 4. 请求/响应模型

每个接口都包含：
- 详细的参数说明
- 请求体模型
- 响应模型
- 示例数据

## 使用示例

### 测试登录接口

1. 打开 http://localhost:8000/docs
2. 找到 **"认证"** 模块
3. 点击 **POST /api/v1/auth/login**
4. 点击 **"Try it out"**
5. 输入测试数据：
```json
{
  "username": "admin",
  "password": "admin123"
}
```
6. 点击 **"Execute"**
7. 查看响应结果，复制返回的 `token`

### 测试需要认证的接口

1. 先完成登录，获取 Token
2. 点击右上角 **"Authorize"** 按钮
3. 输入 `Bearer <token>`
4. 现在可以测试其他需要认证的接口了

## API 接口列表

### 认证模块 (`/api/v1/auth`)

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新Token
- `GET /api/v1/auth/me` - 获取当前用户信息

### 档案管理模块 (`/api/v1/archive`)

- `POST /api/v1/archive/import` - 批量导入档案
- `GET /api/v1/archive/list` - 获取档案列表
- `GET /api/v1/archive/detail/{archive_id}` - 获取档案详情
- `POST /api/v1/archive/search` - 全文检索

### 文档生成模块 (`/api/v1/doc-generate`)

- `POST /api/v1/doc-generate/generate` - 生成文档
- `GET /api/v1/doc-generate/templates` - 获取模板列表
- `GET /api/v1/doc-generate/status/{task_id}` - 查询生成状态

### 知识图谱模块 (`/api/v1/knowledge-graph`)

- `GET /api/v1/knowledge-graph/query` - 查询知识图谱
- `POST /api/v1/knowledge-graph/entity` - 创建实体
- `GET /api/v1/knowledge-graph/relations` - 获取关联关系

## 响应格式

所有 API 响应统一使用以下格式：

```json
{
  "errorCode": 0,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 错误码说明

- `0`: 成功
- `400`: 请求参数错误
- `401`: 未授权（Token无效或过期）
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 注意事项

1. **开发环境**: Swagger UI 默认在开发环境可用
2. **生产环境**: 建议在生产环境禁用或限制访问 Swagger UI
3. **认证**: 大部分接口需要 JWT Token 认证
4. **CORS**: 已配置 CORS，支持跨域请求

## 导出 API 文档

### 导出 OpenAPI JSON

访问 http://localhost:8000/openapi.json 可以获取完整的 OpenAPI 规范 JSON，可以：
- 导入到 Postman
- 导入到其他 API 测试工具
- 生成客户端 SDK
- 生成 API 文档

### 导出为其他格式

可以使用工具将 OpenAPI JSON 转换为其他格式：
- HTML 文档
- Markdown 文档
- PDF 文档

## 常见问题

### Q: 如何禁用 Swagger UI？

在 `app/main.py` 中设置：
```python
app = FastAPI(
    docs_url=None,  # 禁用 Swagger UI
    redoc_url=None,  # 禁用 ReDoc
)
```

### Q: 如何自定义 Swagger UI 样式？

可以通过修改 FastAPI 的 OpenAPI 配置来自定义文档样式和内容。

### Q: 如何添加更多接口文档？

只需在路由函数上添加详细的 docstring 和参数说明，FastAPI 会自动生成文档。
