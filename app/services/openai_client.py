import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from openai import OpenAI
from app.config import Config

"""

"""

class OpenAIClient:
    def __init__(self):
        # 初始化 OpenAI 客户端
        self._client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
        # 嵌入模型和维度
        self._embedding_model = Config.OPENAI_EMBEDDING_MODEL
        self._embedding_dimension = Config.EMBEDDING_DIMENSION
        # GPT 模型和客户端
        self._gpt_model = Config.OPENAI_GPT_MODEL
        self._temperature = Config.TEMPERATURE
        
    def generate_embedding(self, text):
        """
        使用 OpenAI 生成文本嵌入（Embedding）。
        :param text: 输入的文本
        :return: 返回嵌入向量
        """
        response = self._client.embeddings.create(input=text, model=self._embedding_model)
        embedding = response.data[0].embedding # 获取嵌入向量
        return embedding

    def generate_response(self, messages):
        """
        使用 GPT 模型生成回复。
        :param messages: 消息列表，包含历史消息
        :param max_tokens: 最大 token 数
        :param temperature: 控制生成文本的多样性
        :return: 返回生成的文本
        """
        response = self._client.chat.completions.create(
            model=self._gpt_model,
            messages=messages,
            temperature=self._temperature,
            )
        return response.choices[0].message.content
    
    def generate_response_stream(self, messages):
        """
        使用 GPT 模型生成流式回复。
        :param messages: 消息列表，包含历史消息
        :return: 返回流式生成的文本
        """
        # 启用流式输出
        stream = self._client.chat.completions.create(
            model=self._gpt_model,
            messages=messages,
            temperature=self._temperature,
            stream=True,  # 设置为 True 开启流式输出
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

if __name__ == "__main__":
    
    OpenAIClient = OpenAIClient()

    # 获取文本的嵌入向量
    text = "This is a sample text for embedding."
    embedding = OpenAIClient.generate_embedding(text)
    print("向量:")
    print(embedding)
    # 获取大模型回复
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
    response = OpenAIClient.generate_response(messages)
    print("模型回复：")
    print(response)
    print("流式模型回复：")
    OpenAIClient.generate_response_stream(messages)