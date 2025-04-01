import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.api import api_router
from app.core.config import Config

app = FastAPI(
    title="CFLP RAG API",
    version=Config.VERSION,
    description="API for CFLP RAG project, providing chat and authentication functionalities.",
    openapi_url=f"{Config.API_V1_STR}/openapi.json",
    servers=[
        {
            "url": f"{Config.get_api_url}",
            "description": "Development server"
        },
    ]
)

# 根路由
@app.get("/v1", operation_id="根路由")
def root():
    """
    根路由
    """
    return {"message": "Welcome to CFLP-AI API"}

app.include_router(api_router)