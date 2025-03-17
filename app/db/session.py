from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError
from app.core.config import Config
from app.models.base import Base
from app.models.user import User
from app.models.chat import Chat, Message
import logging
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(Config.get_database_url)  # 创建数据库引擎
# 添加重试逻辑
max_retries = 5
retry_interval = 5
# 创建数据库表
for attempt in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)
        print(f"Successfully created tables on attempt {attempt + 1}")
        break
    except DatabaseError as e:
        print(f"Failed to connect to database, attempt {attempt + 1}/{max_retries}: {e}")
        if attempt < max_retries - 1:
            time.sleep(retry_interval)
        else:
            raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 不自动提交事务， 不自动刷新

def get_db():
    db = SessionLocal()  # 创建一个数据库会话
    try:
        # yield db 表示将数据库会话 db 返回给调用者，同时暂停函数执行，等待外部使用完毕后再继续执行清理逻辑。
        yield db  # 返回会话，供 FastAPI 依赖注入使用
    finally:
        db.close()   # 关闭会话