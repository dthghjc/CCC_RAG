from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()
# 获取 API 密钥和 Base URL
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
# 设置 OpenAI API 密钥和 Base URL（如果需要自定义）

client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

# 调用 OpenAI API 示例
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message.content)