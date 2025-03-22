from fastapi import APIRouter, Header, HTTPException, Depends
from app.services.response_generation import OpenAI_RAG_Client
from app.db.conversation_manager import ConversationManager
from app.db.mysql_client import SQLClient
from app.models.conversation_base import ConversationRequest, ConversationResponse, ChatHistoryRequest
from app.core.config import Config
from typing import Optional
import json
from uuid import uuid4
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAG_Client = APIRouter()
Test_Client = APIRouter()
SQL_ChatHistory_Client = APIRouter()

GPT_Client = OpenAI_RAG_Client()
SQL_client = SQLClient()
conversation_manager = ConversationManager()

API_KEY = Config.FASTAPI_API_KEY
# 验证 API 密钥的依赖项
def api_key_auth(api_key: Optional[str] = Header(None)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@RAG_Client.post("/cflp")
def generate_response_for_user(request: ConversationRequest, api_key: str = Depends(api_key_auth)):
    # 用户输入写入SQL
    conversation_id = SQL_client.append_to_conversation(
        username=request.user_id,
        conversation_id=request.conversation_id,
        message=request.query,
        is_user=True
        )
    # 获取当前对话的历史对话
    history = conversation_manager.get_history(request.conversation_id)
    response = GPT_Client.generate_response(user_query = request.query, history=history)
    # 更新对话历史，保存用户查询和模型响应
    conversation_manager.update_history(conversation_id=conversation_id, query=request.query, response=response)
    # 模型响应写入SQL
    SQL_client.append_to_conversation(
        username=request.user_id,
        conversation_id=conversation_id,
        message=response,
        is_user=False
        )
    return ConversationResponse(
        user_id=request.user_id,
        conversation_id=conversation_id,
        model_response=response
    )

@SQL_ChatHistory_Client.post("/chat_history")
async def add_chat_history(request: ChatHistoryRequest, api_key: str = Depends(api_key_auth)):
    try:
        # 如果 request.conversation_id 为空，SQL_client.append_to_conversation 内部应生成新的会话ID
        conversation_id = SQL_client.append_to_conversation(
            username=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
            is_user=request.is_user
        )
        return {
            "user_id": request.user_id,
            "conversation_id": conversation_id,
            "status": "History added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding chat history: {e}")
        return {
            "user_id": request.user_id,
            "conversation_id": request.conversation_id,
            "error": f"Failed to add chat history: {str(e)}"
        }

# 测试接口
@Test_Client.post("/")
async def api_test(request: ConversationRequest, api_key: str = Depends(api_key_auth)):
    request.conversation_id = str(uuid4())
    results = request
    return results