from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.user import User
from app.models.chat import Chat, Message
from app.schemas.chat import ChatBase, ChatResponse, MessageCreate, MessageResponse

from app.api.v1.sql.auth import get_current_user


router = APIRouter()

# 创建对话
@router.post("/", response_model=ChatResponse)
def create_chat(
    *,
    db: Session = Depends(get_db),  # 获取对话数据库
    chat_in: ChatBase,
    current_user: User = Depends(get_current_user)  # 获取当前登录的用户
) -> Any:    
    chat = Chat(
        title=chat_in.title,
        user_id=current_user.id,
    )
    # 将这次对话储存到数据库
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat
# 获取所有对话
@router.get("/", response_model=List[ChatResponse]) 
def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return chats
# 删除特定对话
@router.delete("/{chat_id}")
def delete_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"status": "success"}

# 获取单个对话
@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

# 存入特定聊天（chat_id）的新消息
@router.post("/{chat_id}/message")
def create_message(
    *,  # * 是一个特殊的语法，用于强制指定后续的参数必须以关键字参数（keyword-only arguments）的形式传递，而不是位置参数（positional arguments）。
    db: Session = Depends(get_db),
    chat_id: int, # 聊天ID
    message: MessageCreate,
    current_user: User = Depends(get_current_user)  # 当前登录用户
) -> Any:
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        # 抛出 HTTPException
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # 验证 role 是否合法
    valid_roles = {"system", "user", "assistant"}
    if message.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of {valid_roles}")
    
    # 创建并存储新消息
    new_message = Message(
        chat_id=chat_id,
        role=message.role,
        content=message.content,
        meta_data=message.metadata
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)  # 刷新以获取 id 和时间戳
    
    # 返回响应
    return MessageResponse(
        id=new_message.id,
        chat_id=new_message.chat_id,
        role=new_message.role,
        content=new_message.content,
        metadata=new_message.metadata,
        created_at=new_message.created_at,
        updated_at=new_message.updated_at
    )