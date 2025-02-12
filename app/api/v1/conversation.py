import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import APIRouter
from app.services.response_generation import OpenAI_RAG_Client
from app.db.conversation_manager import ConversationManager
import json

RAG_Client = APIRouter()
Test_Client = APIRouter()

GPT_Client = OpenAI_RAG_Client()
conversation_manager = ConversationManager()

@RAG_Client.get("/{user_id}/{query}")
def getRec(user_id: str, query: str):
    # 获取当前用户的历史对话
    history = conversation_manager.get_history(user_id)
    results = GPT_Client.generate_response(user_query = query, history=history)
    # 更新对话历史，保存用户查询和模型响应
    conversation_manager.update_history(user_id=user_id, query=query, response=results)
    print("对话历史:")
    print(json.dumps(conversation_manager.history, ensure_ascii=False, indent=4))
    return results

@Test_Client.get("/{user_id}/{query}")
def api_test(user_id: str, query: str):
    results = {"user_id": user_id, "query": query}
    return results