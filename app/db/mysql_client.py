import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.config import Config
import mysql.connector
import json
from uuid import uuid4
from datetime import datetime, timezone
import pytz

class SQLClient:
    def __init__(self):
        """
        初始化数据库连接。
        """
        self.host = Config.MYSQL_HOST
        self.port = Config.MYSQL_PORT
        self.user = Config.MYSQL_USER
        self.password = Config.MYSQL_PASSWORD
        self.database = Config.MYSQL_DATABASE

    def get_connection(self):
        """
        获取数据库连接。
        """
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def execute_query(self, query: str, params: tuple = (), fetch: bool = False):
        """
        执行 SQL 语句。
        :param query: SQL 查询语句
        :param params: 查询参数
        :param fetch: 是否返回查询结果
        """
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        
        result = cursor.fetchall() if fetch else None
        connection.commit()
        cursor.close()
        connection.close()
        return result

    def user_exists(self, username: str):
        """
        检查用户是否存在。
        :return: 用户 ID 或 None
        """
        query = "SELECT id FROM users WHERE username = %s"
        result = self.execute_query(query, (username,), fetch=True)
        return result[0]['id'] if result else None

    def create_user(self, username: str):
        """
        创建新用户。
        :return: 新用户 ID
        """
        user_id = str(uuid4())
        query = "INSERT INTO users (id, username) VALUES (%s, %s)"
        self.execute_query(query, (user_id, username))
        return user_id

    def get_or_create_user(self, username: str):
        """
        获取或创建用户。
        :return: 用户 ID
        """
        user_id = self.user_exists(username)
        return user_id if user_id else self.create_user(username)

    def conversation_exists(self, user_id: str, conversation_id: str):
        """
        检查对话是否存在。
        :return: 是否存在
        """
        query = "SELECT id FROM chat_history WHERE id = %s AND user_id = %s"
        result = self.execute_query(query, (conversation_id, user_id), fetch=True)
        return bool(result)

    def create_conversation(self, user_id: str):
        """
        创建新对话。
        :return: 对话 ID
        """
        conversation_id = str(uuid4())
        system_message = [{"role": "system", "content": "你是一个专业的问答助手，专注于基于已知信息回答用户的问题。"}]
        query = "INSERT INTO chat_history (id, user_id, conversation_history, timestamp) VALUES (%s, %s, %s, %s)"
        # timestamp = datetime.now(timezone.utc)
        # 使用 pytz 设置为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        timestamp = datetime.now(beijing_tz)
        self.execute_query(query, (conversation_id, user_id, json.dumps(system_message), timestamp))
        return conversation_id

    def get_or_create_conversation(self, user_id: str, conversation_id: str = None):
        """
        获取或创建对话。
        :return: 对话 ID
        """
        if conversation_id and self.conversation_exists(user_id, conversation_id):
            return conversation_id
        return self.create_conversation(user_id)

    def append_to_conversation(self, username: str, conversation_id: str, message: str, is_user: bool):
        """
        追加对话内容。
        :param username: 用户名
        :param conversation_id: 对话 ID
        :param message: 对话内容
        :param is_user: 是否为用户消息
        """
        user_id = self.get_or_create_user(username)
        conversation_id = self.get_or_create_conversation(user_id, conversation_id)
        
        role = "user" if is_user else "assistant"
        new_message = {"role": role, "content": message}
        
        # 获取当前的会话历史
        query = "SELECT conversation_history FROM chat_history WHERE id = %s"
        result = self.execute_query(query, (conversation_id,), fetch=True)
        
        if result:
            history = json.loads(result[0]['conversation_history'])
            history.append(new_message)
            updated_history = json.dumps(history)
            # timestamp = datetime.now(timezone.utc)
            # 使用 pytz 设置为北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            timestamp = datetime.now(beijing_tz)
            
            query = "UPDATE chat_history SET conversation_history = %s, timestamp = %s WHERE id = %s"
            self.execute_query(query, (updated_history, timestamp, conversation_id))

        return conversation_id

if __name__ == "__main__":
    db_client = SQLClient()
    conversation_id = db_client.append_to_conversation("test_user", None, "你好！", is_user=True)
    db_client.append_to_conversation("test_user", conversation_id, "你好！我可以帮你什么？", is_user=False)