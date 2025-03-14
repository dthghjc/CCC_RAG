from app.models.base import Base, TimestampMixin
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT, JSON

class Chat(Base, TimestampMixin):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base, TimestampMixin):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(255), nullable=False)
    content = Column(LONGTEXT, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)  # 外键约束
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    