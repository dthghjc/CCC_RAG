import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
from pydantic import ConfigDict

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    # Project
    PROJECT_NAME: str = "CFLP_RAG"  # Project name
    VERSION: str = "0.1.0"  # Project version
    
    # FastAPI API
    FASTAPI_API_KEY: str = os.getenv("FASTAPI_API_KEY", "sk-key")
    FASTAPI_SERVER_URL: str = os.getenv("FASTAPI_SERVER_URL", "0.0.0.0")
    FASTAPI_SERVER_PORT: int  = int(os.getenv("FASTAPI_SERVER_PORT", 8000))
    FASTAPI_SERVER_URI_PORT: Optional[str] = None
    @property
    def get_api_url(self) -> str:
        if self.FASTAPI_SERVER_URI_PORT:
            return self.FASTAPI_SERVER_URI_PORT
        else:
            return f"{self.FASTAPI_SERVER_URL}:{self.FASTAPI_SERVER_PORT}"

    API_V1_STR: str = "/v1"
    OPENAPI_VERSION: str = "3.1.0"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")
    OPENAI_GPT_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 150
    # TEMPERATURE = 0.7
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSION: int = 3072
    # Milvus
    MILVUS_SERVICE_URI: str = os.getenv("MILVUS_SERVICE_URI")
    MILVUS_TOKEN_ROOT: str = os.getenv("MILVUS_TOKEN_ROOT")
    MILVUS_TOKEN_USER: str = os.getenv("MILVUS_TOKEN_USER")
    MILVUS_COLLECTION_NAME_CFLP: str = "collection_cflp"
    MILVUS_DB_NAME_CFLP: str = "database_cflp"
    MILVUS_SEARCH_TOP_K: int = 5
    # conversation_manager
    MAX_CONTENT_LENGTH: int = 4096
    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "cflp_mysql_server")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "dthghjc")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "24Khjcmysql")
    MYSQL_DATABASE: str = "CFLP"
    # 数据库连接 URL，使用 Optional[str] 的原因是在没有设定 MYSQL_HOST 时，SQLALCHEMY_DATABASE_URI 会被设置为 None，方便if判断。
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @property
    def get_database_url(self) -> str:
        """
        获取适用于 SQLAlchemy 的数据库连接 URL
        """
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        else:
            return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "f7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

Config = Settings()