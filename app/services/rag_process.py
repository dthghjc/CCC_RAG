"""
协调整个 RAG 流程。接收用户 query，调用知识库检索模块,整合所有的知识。
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.services.knowledge_retrieval import retrieve_knowledge

def extract_answers_from_knowledge(knowledge):
    data_str = knowledge[0]
    answers_str = "\n".join([item["entity"]["metadata"]["answer"] for item in data_str])
    return(answers_str)

class RAGProcessor:
    def __init__(self):
        self.knowledge_retrieval = retrieve_knowledge
    
    def process_query(self, user_query: str):
        """
        处理用户查询，执行 RAG 流程。
        :param user_query: 用户输入的查询字符串
        :return: 模型生成的回复
        """
        try:
            # 第一步：调用知识库检索模块获取相关知识
            knowledge = self.knowledge_retrieval(user_query)
            if not knowledge:
                return "对不起，未能找到相关信息。"
            # 第二步：整合知识
            knowledge_str = extract_answers_from_knowledge(knowledge)
            return(knowledge_str)
        except Exception as e:
            return f"查询过程中发生错误: {str(e)}"
        
if __name__ == "__main__":
    # 创建 RAGProcessor 实例
    rag_processor = RAGProcessor()
    # 测试 RAGProcessor 的 process_query 方法
    user_query = "《采购师高级 模块五 履行谈判与管控合同》的责任编辑和校对人员有哪些？"
    response = rag_processor.process_query(user_query)
    print(response)