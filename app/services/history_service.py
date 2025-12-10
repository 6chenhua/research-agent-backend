"""历史记录服务"""

class HistoryService:
    """聊天和阅读历史管理"""
    
    async def save_chat_message(self, user_id: str, message: str, response: str):
        """保存聊天消息"""
        pass
    
    async def get_chat_history(self, user_id: str, limit: int = 50):
        """获取聊天历史"""
        pass
    
    async def get_reading_history(self, user_id: str, limit: int = 50):
        """获取阅读历史"""
        pass
