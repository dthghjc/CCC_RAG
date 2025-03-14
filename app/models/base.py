from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
import pytz

Beijing_tz = pytz.timezone('Asia/Shanghai')
Base = declarative_base()  # 映射类的基类

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now(Beijing_tz), nullable=False)  # 创建时间
    updated_at = Column(DateTime, default=datetime.now(Beijing_tz), onupdate=datetime.now(Beijing_tz), nullable=False)  # 更新时间, 不能为空。