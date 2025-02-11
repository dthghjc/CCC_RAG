"""
实现多种知识库检索逻辑，如向量检索（Milvus）、关键字检索、图数据库检索等。
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.config import Config
from app.db.milvus import VectorDatabaseClient
from app.services.openai_client import OpenAIClient
import logging

def retrieve_knowledge(user_query: str):
    """
    使用用户查询从 Milvus 向量数据库检索相关的知识。
    :param user_query: 用户输入的查询字符串
    :return: 返回检索到的知识文本，或者返回 None 如果没有相关结果
    """
    # 获取查询的向量嵌入
    openai_client = OpenAIClient()
    query_embedding = openai_client.generate_embedding(user_query)
    logging.info(f"Generated embedding for query: {user_query}")
    # 查询 Milvus 获取相关内容
    milvus_client = VectorDatabaseClient(collection_name=Config.MILVUS_COLLECTION_NAME_CFLP)  # 根据实际情况修改
    search_results = milvus_client.search(query_embedding)
    # 如果检索到结果，返回相关信息；如果没有，则返回提示
    if search_results:
        # 示例：返回第一个检索到的结果（根据实际结构进行修改）
        knowledge = search_results
        logging.info(f"Retrieved knowledge: {knowledge}")
        return knowledge
    else:
        logging.info("No relevant knowledge found.")
        return None
    
if __name__ == "__main__":
    user_query = "《采购师高级 模块五 履行谈判与管控合同》的出版单位和主编是谁？出版时间和ISBN是什么?"
    print(retrieve_knowledge(user_query))