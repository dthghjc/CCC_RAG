from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import Config
from app.models.base import Base
from app.models.user import User
from app.models.chat import Chat, Message
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(Config.get_database_url)  # 创建数据库引擎

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 不自动提交事务， 不自动刷新

def get_db():
    db = SessionLocal()  # 创建一个数据库会话
    try:
        # yield db 表示将数据库会话 db 返回给调用者，同时暂停函数执行，等待外部使用完毕后再继续执行清理逻辑。
        yield db  # 返回会话，供 FastAPI 依赖注入使用
    finally:
        db.close()   # 关闭会话