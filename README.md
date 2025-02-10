 # AI-RAG 项目

这是一个基于 FastAPI 的 AI-RAG（Retrieval-Augmented Generation）系统，结合 OpenAI 的语言模型和向量检索，旨在提供智能对话服务。

## 项目结构

```html
ai-rag-project/
├── app/
│   ├── __init__.py                # FastAPI应用初始化
│   ├── main.py                    # FastAPI主应用文件，包含接口路由
│   ├── api/                       # API路由
│   │   ├── __init__.py
│   │   └── v1/                    # v1版本API接口
│   │       ├── __init__.py
│   │       └── conversation.py    # 对话相关API接口
│   ├── services/                  # 业务逻辑处理
│   │   ├── __init__.py
│   │   ├── rag_process.py         # RAG流程处理
│   │   ├── knowledge_retrieval.py # 知识库检索（Milvus、关键字、图数据库）
│   │   └── response_generation.py # 生成回复的逻辑
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── conversation.py        # 对话历史模型
│   │   └── knowledge_base.py      # 知识库模型
│   ├── db/                        # 数据库连接与操作
│   │   ├── __init__.py
│   │   ├── mysql.py               # MySQL连接与操作
│   │   └── milvus.py              # Milvus连接与操作
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py              # 日志处理
│   │   └── embedding.py           # OpenAI嵌入函数
│   ├── config.py                  # 配置文件（如API密钥、数据库配置等）
├── templates/                     # 存放prompt模板的文件夹
│   └── prompt_template.txt        # prompt模板文件
├── requirements.txt               # 项目依赖库
├── Dockerfile                     # Docker配置文件
├── .env                           # 环境变量配置文件
└── README.md                      # 项目说明文件
```
# CFLP_RAG
