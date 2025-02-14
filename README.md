# CFLP_RAG

这是一个基于 FastAPI 的 AI-RAG（Retrieval-Augmented Generation）系统，结合 OpenAI 的语言模型和向量检索，旨在提供智能对话服务。

## 项目结构

```
CFLP_RAG/
│
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI 启动文件
│   ├── config.py                 # 配置文件（如数据库连接等）
│   ├── db/                       # 数据库操作相关的文件
│   │   ├── __init__.py
│   │   ├── conversation_manager.py # 用于管理对话数据的操作
│   │   ├── milvus.py              # 与 Milvus 数据库交互的操作
│   │   └── mysql.py               # 与 MySQL 数据库交互的操作
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── conversation.py       # 对话历史相关模型
│   │   └── knowledge_base.py     # 知识库模型
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── knowledge_retrieval.py # 知识检索相关逻辑
│   │   ├── openai_client.py      # OpenAI 客户端交互
│   │   ├── rag_process.py        # RAG 流程控制
│   │   ├── response_generation.py # 生成最终回复的逻辑
│   ├── api/                      # FastAPI 路由
│   │   ├── __init__.py
│   │   ├── v1/                   # API 版本 1 路由
│   │   │   ├── __init__.py
│   │   │   └── conversation.py   # 处理用户对话相关的路由
│   ├── templates/                # 存放模板文件
│   │   └── prompt_template.txt   # 存放 prompt 模板
│   ├── tests/                    # 测试文件夹
│   │   └── history.json          # 测试用的对话历史数据
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── embedding.py          # 嵌入生成相关逻辑
│       └── logger.py             # 日志相关工具
│
├── .gitignore                    # 忽略不需要上传到 Git 的文件
├── Dockerfile                    # Docker 配置文件
├── requirements.txt              # 项目依赖包
└── README.md                     # 项目说明文档

```