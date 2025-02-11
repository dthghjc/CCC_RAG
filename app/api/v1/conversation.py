import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fastapi import APIRouter
from app.services.response_generation import OpenAI_RAG_Client

RAG_Client = APIRouter()
Test_Client = APIRouter()

@RAG_Client.get("/{user_id}/{query}")
def getRec(user_id: str, query: str):
    Client = OpenAI_RAG_Client()
    user_query = query
    results = Client.generate_response(user_query)
    return results

@Test_Client.get("/{user_id}/{query}")
def api_test(user_id: str, query: str):
    results = {"user_id": user_id, "query": query}
    return results