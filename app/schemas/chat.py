from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    content: str = ""
    role: str = ""
    meta_data: Optional[dict] = None

class MessageCreate(MessageBase):
    chat_id: int
    
class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # 允许 Pydantic 从 ORM 对象（如 SQLAlchemy 的 Message）的属性直接构建实例。
        from_attributes = True

class ChatBase(BaseModel):
    title: str = ""

class ChatResponse(ChatBase):
    id: int
    user_id : int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        # 允许 Pydantic 从 ORM 对象（如 SQLAlchemy 的 Chat）的属性直接构建实例。
        from_attributes = True
    
    