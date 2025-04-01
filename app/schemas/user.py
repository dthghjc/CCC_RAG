from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    
class UserCreate(UserBase):
    password: str
    id: Optional[str] = None  # 可选的 uuid 字段
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:  # 如果没有提供 id，则自动生成
            self.id = str(uuid.uuid4())
    
class UserUpdate(UserBase):
    password: Optional[str] = None
    
class UserInDBBase(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
