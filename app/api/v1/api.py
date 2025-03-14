from fastapi import APIRouter

from app.api.v1.sql import auth, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/v1/chats", tags=["chats"])