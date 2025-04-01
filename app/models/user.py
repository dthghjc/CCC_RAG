from app.models.base import Base, TimestampMixin
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
import uuid

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    chats = relationship("Chat", back_populates="user")