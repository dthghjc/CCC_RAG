from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    content: str = ""
    role: str = ""
    meta_data: Optional[dict] = None

class MessageCreate(MessageBase):
    chat_id: str
    
class MessageResponse(MessageBase):
    id: str
    chat_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        # 允许 Pydantic 从 ORM 对象（如 SQLAlchemy 的 Message）的属性直接构建实例。
        from_attributes = True

class ChatBase(BaseModel):
    title: Optional[str] = None

class ChatCreate(ChatBase):
    id: Optional[str] = None

class ChatResponse(ChatBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        # 允许 Pydantic 从 ORM 对象（如 SQLAlchemy 的 Chat）的属性直接构建实例。
        from_attributes = True
    
    