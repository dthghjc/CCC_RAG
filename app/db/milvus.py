"""
负责与 Milvus 进行连接和交互。它包括 Milvus 客户端的初始化、配置以及与 Milvus 进行的底层数据操作（如插入、查询等）
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.core.config import Config
from pymilvus import MilvusClient
import logging
# 配置日志
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VectorDatabaseClient:
    """
    用于与 Milvus 进行交互的客户端
    """
    def __init__(self, collection_name: str):
        """
        初始化 VectorStoreUser 对象，连接 Milvus。
        :param collection_name: Milvus 集合名称
        """
        self._collection_name = collection_name  # 集合名称
        self._vector_size = int(Config.EMBEDDING_DIMENSION)
        self._client = MilvusClient(
            uri=Config.MILVUS_SERVICE_URI,
            token=Config.MILVUS_TOKEN_USER,
            db_name=Config.MILVUS_DB_NAME_CFLP
            )
        
    def search(self, query_embedding: list, top_k: int = Config.MILVUS_SEARCH_TOP_K):
        """
        search: 搜索
        """
        return self._client.search(
            collection_name=self._collection_name,
            data=[query_embedding],
            limit=top_k,
            # search_params={"metric_type": "IP", "params": {}},
            output_fields=["vector_text","metadata"],
        )
        
     
if __name__ == "__main__":
    # OpenAI客户端
    from app.services import openai_client
    openai_client = openai_client.OpenAIClient()
    question = "《采购师高级 模块五 履行谈判与管控合同》的出版单位和主编是谁？出版时间和ISBN是什么？"
    search_vec = openai_client.generate_embedding(question)
    DatabaseClient = VectorDatabaseClient(Config.MILVUS_COLLECTION_NAME_CFLP)
    search_res = DatabaseClient.search(search_vec)
     # 打印搜索结果
    print(search_res)