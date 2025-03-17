# CFLP_RAG

这是一个基于 FastAPI 的 AI-RAG（Retrieval-Augmented Generation）系统，结合 OpenAI 的语言模型和向量检索，旨在提供智能对话服务。

# 🚀 快速开始
## 环境要求
- Docker & Docker Compose v2.0+
## 安装步骤
1. 克隆项目到本地：
    ```bash
    git clone https://github.com/dthghjc/CFLP_RAG.git
    ```
2. 进入项目目录：
    ```bash
    cd CFLP_RAG
    ```
3. 配置环境变量
    ```bash
    cp .env.example .env
    ```
    在 `.env` 文件中，你需要配置以下变量：
    - `FASTAPI_SERVER_URL` - FastAPI 服务的 URL
    - `SECRET_KEY` - 密钥，用于签名令牌。建议使用长度为32的随机字符。
4. 启动服务：
    ```bash
    docker compose up -d
    ```
# 验证安装
服务启动后，可通过以下地址访问 Swagger UI 。
- http://localhost:8000/docs

# 🏗️ 技术架构
- 🐍 Python FastAPI: 高性能异步 Web 框架
- 🗄️ MySQL: 数据库
- 🔒 JWT + OAuth2: 身份认证