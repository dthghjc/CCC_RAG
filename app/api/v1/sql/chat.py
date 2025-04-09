from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat import Chat, Message
from app.models.user import User
from app.schemas.chat import ChatBase, ChatResponse, MessageCreate, MessageResponse
from app.api.v1.sql.auth import get_current_user
from app.api.exceptions import APIExceptions

router = APIRouter()

# 创建新对话
@router.post("/", response_model=ChatResponse, operation_id="create_chat")
async def create_chat(
    *,
    db: Session = Depends(get_db),  # 获取对话数据库
    chat_in: ChatBase,
    current_user: User = Depends(get_current_user)  # 获取当前登录的用户
):
    """
    创建新对话
    """
    chat = Chat(
        title=chat_in.title,
        user_id=current_user.id
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

# 获取所有对话
@router.get("/", response_model=List[ChatResponse], operation_id="list_chats")
async def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    获取当前用户的所有对话
    """
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return chats

# 删除特定对话
@router.delete("/{chat_id}", operation_id="delete_chat")
async def delete_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    删除指定对话
    """
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise APIExceptions.USER_CHAT_NOT_FOUND_EXCEPTION
    
    db.delete(chat)
    db.commit()
    return {"status": "success"}

# 获取单个对话
@router.get("/{chat_id}", response_model=ChatResponse, operation_id="get_chat")
async def get_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取指定对话
    """
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise APIExceptions.USER_CHAT_NOT_FOUND_EXCEPTION
    return chat

# 存入特定聊天（chat_id）的新消息
@router.post("/message", response_model=MessageResponse, operation_id="create_message")
async def create_message(
    *,
    db: Session = Depends(get_db),
    message: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    上传对话历史
    """
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == message.chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise APIExceptions.USER_CHAT_NOT_FOUND_EXCEPTION
    
    # 验证 role 是否合法
    valid_roles = {"system", "user", "assistant"}
    if message.role not in valid_roles:
        raise APIExceptions.INVALID_ROLE_EXCEPTION
    
    # 创建并存储新消息
    new_message = Message(
        chat_id=message.chat_id,
        role=message.role,
        content=message.content,
        meta_data=message.meta_data
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return MessageResponse(
        id=new_message.id,
        chat_id=new_message.chat_id,
        role=new_message.role,
        content=new_message.content,
        metadata=new_message.meta_data,
        created_at=new_message.created_at,
        updated_at=new_message.updated_at
    )