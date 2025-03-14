import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# 加载 .env 文件
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "CFLP_RAG"  # Project name
    VERSION: str = "0.1.0"  # Project version
    
    # FastAPI API
    FASTAPI_API_KEY: str = os.getenv("FASTAPI_API_KEY")
    FASTAPI_API_PORT: int  = os.getenv("FASTAPI_API_PORT")
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
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = os.getenv("MYSQL_PORT")
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
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
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
    
Config = Settings()