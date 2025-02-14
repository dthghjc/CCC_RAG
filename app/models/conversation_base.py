from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ConversationRequest(BaseModel):
    user_id: str = "user_test"
    conversation_id: str = ""
    query: str = "Hello."

class ConversationResponse(BaseModel):
    user_id: str
    conversation_id: str
    model_response: str

class ChatHistoryRequest(BaseModel):
    user_id: str = "user_test"
    conversation_id: str = ""
    message: str = "这是一条测试文本。"
    is_user: bool = True

class ConversationHistory(BaseModel):
    message: str
    timestamp: datetime

class Metadata(BaseModel):
    rounds: int
    retrieved_knowledge_ids: List[UUID]
    knowledge_retrieved: bool

class Conversation(BaseModel):
    id: UUID
    user_id: UUID
    timestamp: datetime
    conversation_history: List[ConversationHistory]
    metadata: Metadata
