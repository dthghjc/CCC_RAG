import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import httpx
import asyncio
from typing import AsyncGenerator
import pytest_asyncio
from app.core.config import Config
import uuid
"""
api 测试
"""
# 测试用户信息
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
}

@pytest_asyncio.fixture(scope="session")
async def access_token() -> str:
    """获取测试用户的访问令牌"""
    async with httpx.AsyncClient(base_url=Config.get_api_url) as client:
        # 先注册用户
        try:
            response = await client.post(
                "/v1/auth/register",
                json=TEST_USER
            )
            print(f"注册响应: {response.text}")  # 添加调试信息
            if response.status_code != 200:
                print(f"注册失败: {response.text}")
                # 如果注册失败，尝试登录
                pass
        except httpx.HTTPError as e:
            print(f"注册用户时出错: {e}")
            # 如果用户已存在，继续尝试登录
            pass
        
        # 登录获取token
        response = await client.post(
            "/v1/auth/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"],
                "grant_type": "password"
            }
        )
        print(f"登录响应: {response.text}")  # 添加调试信息
        assert response.status_code == 200
        return response.json()["access_token"]

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建测试客户端"""
    async with httpx.AsyncClient(base_url=Config.get_api_url) as client:
        yield client

# 用户认证测试
@pytest.mark.asyncio
async def test_register(client: httpx.AsyncClient):
    """测试用户注册"""
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "username": f"newuser_{unique_id}",
        "password": "newpass123",
        "email": f"newuser_{unique_id}@example.com"
    }
    
    response = await client.post(
        "/v1/auth/register",
        json=test_user
    )
    print(f"注册响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_login(client: httpx.AsyncClient):
    """测试用户登录"""
    # 先确保用户已注册
    try:
        response = await client.post(
            "/v1/auth/register",
            json=TEST_USER
        )
        print(f"注册响应: {response.text}")  # 添加调试信息
    except httpx.HTTPError as e:
        print(f"注册用户时出错: {e}")
        # 如果用户已存在，忽略错误
        pass
    
    # 尝试登录
    response = await client.post(
        "/v1/auth/token",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
            "grant_type": "password"
        }
    )
    print(f"登录响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: httpx.AsyncClient, access_token: str):
    """测试获取当前用户信息"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post("/v1/auth/test_token", headers=headers)
    print(f"获取用户信息响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER["username"]

# 聊天功能测试
@pytest.mark.asyncio
async def test_create_chat(client: httpx.AsyncClient, access_token: str):
    """测试创建聊天"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/v1/chats/",
        headers=headers,
        json={"title": "Test Chat"}
    )
    print(f"创建聊天响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Chat"
    return data["id"]

@pytest.mark.asyncio
async def test_get_chats(client: httpx.AsyncClient, access_token: str):
    """测试获取聊天列表"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get("/v1/chats/", headers=headers)
    print(f"获取聊天列表响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_message(client: httpx.AsyncClient, access_token: str):
    """测试创建消息"""
    # 先创建一个聊天
    chat_id = await test_create_chat(client, access_token)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/v1/chats/message",
        headers=headers,
        json={
            "chat_id": chat_id,
            "content": "Test message",
            "role": "user"
        }
    )
    print(f"创建消息响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test message"
    assert data["chat_id"] == chat_id
    assert data["role"] == "user"

@pytest.mark.asyncio
async def test_get_chat(client: httpx.AsyncClient, access_token: str):
    """测试获取单个聊天"""
    # 先创建一个聊天
    chat_id = await test_create_chat(client, access_token)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(f"/v1/chats/{chat_id}", headers=headers)
    print(f"获取聊天响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == chat_id

@pytest.mark.asyncio
async def test_delete_chat(client: httpx.AsyncClient, access_token: str):
    """测试删除聊天"""
    # 先创建一个聊天
    chat_id = await test_create_chat(client, access_token)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.delete(f"/v1/chats/{chat_id}", headers=headers)
    print(f"删除聊天响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    
    # 验证聊天已被删除
    response = await client.get(f"/v1/chats/{chat_id}", headers=headers)
    print(f"验证删除响应: {response.text}")  # 添加调试信息
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_full_chat_flow(client: httpx.AsyncClient, access_token: str):
    """测试完整的聊天流程"""
    # 创建聊天
    chat_id = await test_create_chat(client, access_token)
    
    # 发送消息
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.post(
        "/v1/chats/message",
        headers=headers,
        json={
            "chat_id": chat_id,
            "content": "Hello, this is a test message",
            "role": "user"
        }
    )
    print(f"发送消息响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    
    # 获取聊天历史
    response = await client.get(f"/v1/chats/{chat_id}", headers=headers)
    print(f"获取聊天历史响应: {response.text}")  # 添加调试信息
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) > 0
    assert data["messages"][0]["content"] == "Hello, this is a test message"
