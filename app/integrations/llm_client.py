"""LLM客户端封装"""

class LLMClient:
    """LLM客户端（OpenAI/Anthropic/Local）"""
    
    async def chat(self, messages: list):
        """基础对话"""
        # TODO: 实现LLM调用
        pass
    
    async def chat_with_tools(self, messages: list, tools: list):
        """带工具调用的对话"""
        # TODO: 实现tool calling
        pass
    
    async def extract_entities(self, text: str):
        """实体抽取"""
        # TODO: 使用LLM抽取实体
        pass
