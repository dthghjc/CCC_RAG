import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import APIRouter
from app.services.response_generation import OpenAI_RAG_Client
from app.db.conversation_manager import ConversationManager
from app.db.mysql_client import SQLClient
from app.models.conversation_base import ConversationRequest, ConversationResponse, ChatHistoryRequest
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

@RAG_Client.post("/cflp")
def generate_response_for_user(request: ConversationRequest):
    """
    处理用户查询，获取历史对话并生成新的回复
    :param user_id: 用户 ID
    :param conversation_id : 会话ID
    :param query: 用户的查询内容
    :return: 返回 OpenAI 的回复
    """
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
def add_chat_history(request: ChatHistoryRequest):
    """
    直接向数据库中添加聊天历史记录。
    如果 conversation_id 为空，则自动生成新的会话ID。

    :param request: ChatHistoryRequest 包含 user_id, conversation_id, message, is_user
    :return: 返回包含 user_id、conversation_id 和状态信息的响应
    """
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
def api_test(request: ConversationRequest):
    request.conversation_id = str(uuid4())
    results = request
    return results