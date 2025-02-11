"""
拼接 prompt 后调用大模型（例如封装的 OpenAIClient），并处理返回结果。
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.openai_client import OpenAIClient
from app.services.rag_process import RAGProcessor
from app.config import Config

def load_prompt_template():
    """
    加载存储在 app/templates/prompt_template.txt 中的 Prompt 模板。
    :return: 返回 Prompt 模板字符串
    """
    template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'templates', 'prompt_template.txt')
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"加载 Prompt 模板时发生错误: {str(e)}")
    
def generate_final_response(user_query: str, knowledge_str: str):
    """
    生成最终的回复，将用户查询和整合的知识拼接到完整的 Prompt 中，并调用大模型生成回复。
    :param user_query: 用户输入的查询
    :param knowledge_str: 从知识库检索到的知识
    :return: 模型生成的最终回复
    """
    # 加载 Prompt 模板
    prompt_template = load_prompt_template()
    # 拼接完整的 Prompt
    prompt = prompt_template.format(query=user_query, context=knowledge_str)
    return(prompt)

class OpenAI_RAG_Client:
    """
    封装 OpenAI 客户端，提供 RAG（Retrieval Augmented Generation）能力。
    """
    def __init__(self):
        self._client = OpenAIClient()
        self._rag_processor = RAGProcessor()
    
    def generate_response(self, user_query: str):
        """
        根据用户查询生成回复。
        :param user_query: 用户输入的查询
        :return: 模型生成的回复
        """
        # 使用 RAGProcessor 处理查询，获取知识
        knowledge = self._rag_processor.process_query(user_query)
        prompt = generate_final_response(user_query, knowledge)
        messages = [{"role": "user", "content": prompt}]
        response = self._client.generate_response(messages)
        return response
    
if __name__ == "__main__":
    RAG_Client = OpenAI_RAG_Client()
    user_query = "《采购师高级 模块五 履行谈判与管控合同》的责任编辑和校对人员有哪些？"
    response = RAG_Client.generate_response(user_query)
    print(response)