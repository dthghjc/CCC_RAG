from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
import pytz

Beijing_tz = pytz.timezone('Asia/Shanghai')
Base = declarative_base()  # 映射类的基类

# 定义一个返回当前北京时间的函数
def get_current_beijing_time():
    return datetime.now(Beijing_tz)

class TimestampMixin:
    # 将函数本身 (get_current_beijing_time) 传递给 default 和 onupdate
    created_at = Column(DateTime, default=get_current_beijing_time, nullable=False)
    updated_at = Column(DateTime, default=get_current_beijing_time, onupdate=get_current_beijing_time, nullable=False)