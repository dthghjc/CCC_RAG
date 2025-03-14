import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uvicorn
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import Config

app = FastAPI()
app.include_router(api_router)

# 根路由
@app.get("/v1")
def root():
    return {"message": "Welcome to CFLP-AI API"}

# 健康检查路由
@app.get("v1/api/health")
async def health_check():
    return {
        "status": "healthy",  # 应用状态
        "version": Config.VERSION,  # 应用版本
    }


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=Config.FASTAPI_API_PORT, reload=True)