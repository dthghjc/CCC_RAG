import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uvicorn
from fastapi import FastAPI

from app.api.v1.conversation import RAG_Client, Test_Client, SQL_ChatHistory_Client

app = FastAPI()
app.include_router(Test_Client, prefix="/v1/test_client", tags=["Test Client"])
app.include_router(RAG_Client, prefix="/v1/rag_client", tags=["RAG Client"])
app.include_router(SQL_ChatHistory_Client, prefix="/v1/sql_client", tags=["SQL Client"])


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8009, reload=True)