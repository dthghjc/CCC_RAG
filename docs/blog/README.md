# 1. 整体架构
这个应用是一个 RESTful API，使用 FastAPI 框架构建，主要分为以下几个模块：

- `main.py`: 应用程序的入口，定义 FastAPI 实例并启动服务。
- `api.py`: API 路由的总入口，组织各个子模块的路由（如认证和聊天）。
- `auth.py`: 处理用户认证相关功能（注册、登录、Token验证）。
- `chat.py`: 处理聊天相关功能（创建对话、获取对话、发送消息等）。
# 2. 文件功能详解
## `main.py` - 应用程序入口
- 作用: 初始化 FastAPI 应用并启动服务。
- 关键代码:
    - `app = FastAPI(...)`: 创建 FastAPI 实例，设置标题、版本、描述等元信息。
    - `app.include_router(api_router)`: 将 API 路由（来自 `api.py`）挂载到应用中。
    - `uvicorn.run(...)`: 使用 Uvicorn 运行服务，监听 `0.0.0.0`（所有网络接口）上的指定端口，`reload=True` 表示开发模式下代码修改后自动重启。
- 根路由 (`/v1`): 返回欢迎信息，用于测试服务是否正常运行。
## `api.py` - 路由组织
- 作用: 定义一个 `APIRouter` 对象，统一管理所有子路由。
- 关键代码:
    - `api_router.include_router(auth.router, ...)`: 挂载认证相关路由，前缀为 `/v1/auth`，标签为 `auth`。
    - `api_router.include_router(chat.router, ...)`: 挂载聊天相关路由，前缀为 `/v1/chats`，标签为 `chats`。
- 功能: 将认证和聊天的功能模块化，便于管理和扩展。
## `auth.py` - 用户认证
- 作用: 提供用户注册、登录和 Token 验证功能。
- 核心功能:
    1. 用户注册 (`/register`):
        - 输入: 用户信息（邮箱、用户名、密码）。
        - 流程: 检查邮箱和用户名是否重复，若无重复则创建用户，密码经过哈希处理后存储。
        - 输出: 返回用户信息。
    2. 获取 Token (`/token`):
        - 输入: 用户名和密码（通过表单提交）。
        - 流程: 验证用户名和密码，若正确则生成 JWT（JSON Web Token），包含用户名和过期时间。
        - 输出: 返回包含 `access_token` 和 `token_type` 的响应。
    3. 验证 Token (`/test_token`):
        - 输入: JWT Token（通过 `Authorization: Bearer <token>` 头传递）。
        - 流程: 解码 Token，验证有效性，返回当前用户信息。
- 依赖注入: 使用 `Depends` 获取数据库会话 (`get_db`) 和当前用户 (`get_current_user`)。
- 安全性: 使用 OAuth2 和 JWT 进行认证，密码哈希存储。
## `chat.py` - 聊天功能
- 作用: 提供创建、获取、删除对话以及发送消息的功能。
- 核心功能:
    1. 创建对话 (`POST /`):
        - 输入: 对话标题。
        - 流程: 为当前用户创建新对话，存储到数据库。
        - 输出: 返回新对话信息。
    2. 获取所有对话 (`GET /`):
        - 输入: 可选的 `skip` 和 `limit` 参数（分页）。
        - 流程: 查询当前用户的所有对话。
        - 输出: 返回对话列表。
    3.  获取指定对话 (`GET /{chat_id}`):
        - 输入: 对话 ID。
        - 流程: 查询指定对话，若不存在则返回 404。
        - 输出: 返回对话信息。
    4. 删除对话 (`DELETE /{chat_id}`):
        - 输入: 对话 ID。
        - 流程: 删除指定对话，若不存在则返回 404。
        - 输出: 返回成功状态。
    5. 发送消息 (`POST /message`):
        - 输入: 对话 ID、消息内容、角色（`system`、`user` 或 `assistant`）等。
        - 流程: 验证对话存在性和角色合法性，保存消息到数据库。
        - 输出: 返回消息详情。
- 依赖: 使用 `get_current_user` 确保操作限于当前登录用户。
# 3. 工作流程
## 启动流程
1. 运行 `python main.py`，Uvicorn 启动服务。
2. FastAPI 初始化，加载路由（`auth` 和 `chat`）。
3. 服务监听指定端口，等待请求。
## 用户认证流程
1. 用户通过 `/v1/auth/register` 注册，创建账户。
2. 用户通过 `/v1/auth/token` 提交用户名和密码，获取 JWT Token。
3. 用户在后续请求中携带 Token（放在 HTTP 头 `Authorization: Bearer <token>` 中）。
4. 服务器通过 `get_current_user` 验证 Token，确认用户身份。
## 聊天功能流程
1. 用户登录后，通过 `/v1/chats/` 创建新对话。
2. 通过 `/v1/chats/{chat_id}/message` 发送消息到指定对话。
3. 通过 `/v1/chats/` 获取所有对话，或通过 `/v1/chats/{chat_id}` 获取特定对话。
4. 可通过 `/v1/chats/{chat_id}` 删除对话。
# 4. 技术亮点
- FastAPI: 高性能异步框架，支持自动生成 OpenAPI 文档。
- 依赖注入: 通过 `Depends` 优雅地管理数据库会话和用户认证。
- 安全性: JWT 用于认证，密码哈希存储，防止泄露。
- 数据库操作: 使用 SQLAlchemy ORM 与数据库交互，支持事务管理。
- 模块化: 路由分层设计，便于维护和扩展。

# 5. 示例请求
## 注册用户
```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "username": "user1", "password": "password123"}'
```

## 获取 Token
```bash
curl -X POST "http://localhost:8000/v1/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=user1&password=password123"
```

## 创建对话
```bash
curl -X POST "http://localhost:8000/v1/chats/" \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{"title": "My Chat"}'
```

## 上传对话历史
```bash
curl -X POST "http://localhost:8000/v1/chats/message?chat_id=1" \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{"role": "user", "content": "Hello!"}'
```