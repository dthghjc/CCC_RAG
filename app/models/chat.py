from app.models.base import Base, TimestampMixin
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT, JSON
import uuid

class Chat(Base, TimestampMixin):
    __tablename__ = 'chats'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_id = Column(Integer, autoincrement=True, unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.sequence_id.asc()"
    )

class Message(Base, TimestampMixin):
    __tablename__ = 'messages'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_id = Column(Integer, autoincrement=True, unique=True, nullable=False, index=True)
    role = Column(String(255), nullable=False)
    content = Column(LONGTEXT, nullable=False)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)  # 外键约束
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")