import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.core.config import Config

class ConversationManager:
    def __init__(self):
        self.history = {}
        self.max_context_length = Config.MAX_CONTENT_LENGTH

    def get_history(self, conversation_id: str):
        # 初始化对话历史记录，如果没有的话
        if conversation_id not in self.history:
            self.history[conversation_id] = [
                {
                    "role": "system",
                    "content": "你是一个专业的问答助手，专注于基于已知信息回答用户的问题。"
                }
            ]
        self._trim_history(conversation_id)  # 确保历史记录符合最大长度限制
        return self.history[conversation_id]

    def update_history(self, conversation_id: str, query: str, response: str):
        # 更新对话历史
        self.get_history(conversation_id)  # 确保历史初始化
        self.history[conversation_id].append({"role": "user", "content": query})
        self.history[conversation_id].append({"role": "assistant", "content": response})
        self._trim_history(conversation_id)  # 更新历史后，检查并修剪

    def _trim_history(self, conversation_id: str):
        # 截取对话历史，确保其长度不超过最大限制
        history = self.history[conversation_id]
        total_length = sum(len(item["content"]) for item in history)
        
        # 保留"role": "system"部分，剔除多余的对话轮次
        while total_length > self.max_context_length and len(history) > 1:
            # 删除最早的对话轮次（user 和 assistant）
            history.pop(1)
            history.pop(1)
            total_length = sum(len(item["content"]) for item in history)

if __name__ == "__main__":
    # 示例使用
    conversation_manager = ConversationManager()

    # 更新对话历史
    conversation_manager.update_history(conversation_id="conversation_1", query="What is AI?", response="AI is the simulation of human intelligence in machines.")
    conversation_manager.update_history(conversation_id="conversation_1", query="What are the applications of AI?", response="AI is used in healthcare, finance, and more.")

    # 获取对话历史
    history = conversation_manager.get_history(conversation_id="conversation_1")
    print(history)
