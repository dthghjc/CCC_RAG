import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    OPENAI_GPT_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 150
    TEMPERATURE = 0.7
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIMENSION = 3072
    # Milvus
    MILVUS_SERVICE_URI = os.getenv("MILVUS_SERVICE_URI")
    MILVUS_TOKEN_ROOT = os.getenv("MILVUS_TOKEN_ROOT")
    MILVUS_TOKEN_USER = os.getenv("MILVUS_TOKEN_USER")
    MILVUS_COLLECTION_NAME_CFLP = "collection_cflp"
    MILVUS_DB_NAME_CFLP = "database_cflp"
    MILVUS_SEARCH_TOP_K = 5
    # conversation_manager
    MAX_CONTENT_LENGTH = 4096