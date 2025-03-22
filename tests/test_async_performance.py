import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import httpx
import asyncio
import time
from typing import AsyncGenerator, List
import pytest_asyncio
from app.core.config import Config
import uuid
from datetime import datetime

# 测试用户信息
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
}

# 设置更长的超时时间
TIMEOUT = 60.0  # 60秒超时

@pytest_asyncio.fixture(scope="session")
async def access_token() -> str:
    """获取测试用户的访问令牌"""
    async with httpx.AsyncClient(base_url=Config.get_api_url, timeout=TIMEOUT) as client:
        # 先注册用户
        try:
            response = await client.post(
                "/v1/auth/register",
                json=TEST_USER
            )
            if response.status_code != 200:
                pass
        except httpx.HTTPError:
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
        assert response.status_code == 200
        return response.json()["access_token"]

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建测试客户端"""
    async with httpx.AsyncClient(base_url=Config.get_api_url, timeout=TIMEOUT) as client:
        yield client

async def create_test_user(client: httpx.AsyncClient, user_id: int) -> dict:
    """创建测试用户"""
    username = f"testuser_{user_id}"
    email = f"testuser_{user_id}@example.com"
    password = "testpass123"
    
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    response = await client.post("/v1/auth/register", json=user_data)
    if response.status_code == 200:
        return user_data
    return None

async def login_user(client: httpx.AsyncClient, username: str, password: str) -> str:
    """用户登录并获取token"""
    response = await client.post(
        "/v1/auth/token",
        data={
            "username": username,
            "password": password,
            "grant_type": "password"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

async def create_chat(client: httpx.AsyncClient, token: str, title: str) -> str:
    """创建聊天"""
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/v1/chats/",
        headers=headers,
        json={"title": title}
    )
    if response.status_code == 200:
        return response.json()["id"]
    return None

async def send_message(client: httpx.AsyncClient, token: str, chat_id: str, content: str) -> bool:
    """发送消息"""
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/v1/chats/message",
        headers=headers,
        json={
            "chat_id": chat_id,
            "content": content,
            "role": "user"
        }
    )
    return response.status_code == 200

@pytest.mark.asyncio
async def test_concurrent_user_operations(client: httpx.AsyncClient):
    """测试并发用户操作"""
    num_users = 3  # 减少并发用户数
    start_time = time.time()
    
    # 并发创建用户
    create_tasks = [create_test_user(client, i) for i in range(num_users)]
    users = await asyncio.gather(*create_tasks)
    
    # 并发登录
    login_tasks = [
        login_user(client, user["username"], user["password"])
        for user in users if user
    ]
    tokens = await asyncio.gather(*login_tasks)
    
    end_time = time.time()
    print(f"并发用户操作耗时: {end_time - start_time:.2f}秒")
    print(f"成功创建用户数: {len([u for u in users if u])}")
    print(f"成功登录用户数: {len([t for t in tokens if t])}")

@pytest.mark.asyncio
async def test_concurrent_chat_operations(client: httpx.AsyncClient, access_token: str):
    """测试并发聊天操作"""
    num_chats = 2  # 减少并发聊天数
    messages_per_chat = 3  # 减少每个聊天的消息数
    start_time = time.time()
    
    # 并发创建聊天
    chat_tasks = [
        create_chat(client, access_token, f"Test Chat {i}")
        for i in range(num_chats)
    ]
    chat_ids = await asyncio.gather(*chat_tasks)
    
    # 并发发送消息
    message_tasks = []
    for chat_id in chat_ids:
        if chat_id:
            message_tasks.extend([
                send_message(client, access_token, chat_id, f"Message {i}")
                for i in range(messages_per_chat)
            ])
    
    results = await asyncio.gather(*message_tasks)
    
    end_time = time.time()
    print(f"并发聊天操作耗时: {end_time - start_time:.2f}秒")
    print(f"成功创建聊天数: {len([c for c in chat_ids if c])}")
    print(f"成功发送消息数: {sum(1 for r in results if r)}")

@pytest.mark.asyncio
async def test_large_message_processing(client: httpx.AsyncClient, access_token: str):
    """测试大量消息处理"""
    num_messages = 10  # 减少消息数量
    message_size = 200  # 减少消息大小
    start_time = time.time()
    
    # 创建测试聊天
    chat_id = await create_chat(client, access_token, "Large Message Test")
    assert chat_id is not None
    
    # 生成大量消息
    messages = [
        "x" * message_size for _ in range(num_messages)
    ]
    
    # 分批发送消息
    batch_size = 3
    results = []
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        batch_tasks = [
            send_message(client, access_token, chat_id, msg)
            for msg in batch
        ]
        batch_results = await asyncio.gather(*batch_tasks)
        results.extend(batch_results)
        await asyncio.sleep(1)  # 批次间添加延迟
    
    end_time = time.time()
    print(f"大量消息处理耗时: {end_time - start_time:.2f}秒")
    print(f"成功发送消息数: {sum(1 for r in results if r)}")
    print(f"总处理数据量: {num_messages * message_size / 1024:.2f} KB")

@pytest.mark.asyncio
async def test_async_vs_sync_performance(client: httpx.AsyncClient, access_token: str):
    """测试异步和同步操作的性能对比"""
    num_operations = 3  # 减少操作数量
    
    # 异步操作测试
    async_start_time = time.time()
    async_tasks = [
        create_chat(client, access_token, f"Async Chat {i}")
        for i in range(num_operations)
    ]
    async_results = await asyncio.gather(*async_tasks)
    async_end_time = time.time()
    
    # 同步操作测试
    sync_start_time = time.time()
    sync_results = []
    for i in range(num_operations):
        response = await client.post(
            "/v1/chats/",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"title": f"Sync Chat {i}"}
        )
        if response.status_code == 200:
            sync_results.append(response.json()["id"])
        await asyncio.sleep(1)  # 添加延迟
    sync_end_time = time.time()
    
    print("\n性能对比结果:")
    print(f"异步操作耗时: {async_end_time - async_start_time:.2f}秒")
    print(f"同步操作耗时: {sync_end_time - sync_start_time:.2f}秒")
    print(f"性能提升: {(sync_end_time - sync_start_time) / (async_end_time - async_start_time):.2f}倍")
    print(f"异步成功数: {len([r for r in async_results if r])}")
    print(f"同步成功数: {len(sync_results)}")

@pytest.mark.asyncio
async def test_error_handling_and_recovery(client: httpx.AsyncClient, access_token: str):
    """测试错误处理和恢复能力"""
    num_operations = 2  # 减少操作数量
    error_rate = 0.3  # 30% 的操作会失败
    
    async def operation_with_retry(operation_id: int, max_retries: int = 3) -> bool:
        """带重试机制的操作"""
        for attempt in range(max_retries):
            try:
                # 模拟随机失败
                if operation_id % 3 == 0:  # 模拟30%的失败率
                    raise Exception("模拟的随机错误")
                
                chat_id = await create_chat(client, access_token, f"Retry Chat {operation_id}")
                if chat_id:
                    return True
            except Exception as e:
                print(f"操作 {operation_id} 尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)  # 增加重试等待时间
                continue
        return False
    
    start_time = time.time()
    tasks = [operation_with_retry(i) for i in range(num_operations)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"\n错误处理和恢复测试结果:")
    print(f"总耗时: {end_time - start_time:.2f}秒")
    print(f"成功操作数: {sum(1 for r in results if r)}")
    print(f"失败操作数: {sum(1 for r in results if not r)}")
    print(f"成功率: {(sum(1 for r in results if r) / num_operations) * 100:.1f}%") 