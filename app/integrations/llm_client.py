"""
LLM客户端封装
根据PRD_研究与聊天模块.md设计
支持OpenAI兼容的API调用
"""
import logging
from typing import List, Dict, Any, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端（OpenAI/Anthropic/Local）"""
    
    def __init__(self):
        """初始化LLM客户端
        
        优先使用OPENAI_API_KEY，如果为空则使用GRAPHITI_API_KEY
        这样可以支持使用同一个API服务
        """
        # 选择API密钥：优先使用OPENAI_API_KEY，否则使用GRAPHITI_API_KEY
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == "your_openai_api_key":
            api_key = settings.GRAPHITI_API_KEY
        
        # 选择base_url：优先使用LLM_BASE_URL，否则使用BASE_URL
        base_url = settings.LLM_BASE_URL
        if not base_url:
            base_url = settings.BASE_URL
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = settings.OPENAI_MODEL
        
        logger.info(f"LLM Client initialized with base_url: {base_url}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        基础对话
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            model: 模型名称（可选，默认使用配置中的模型）
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应内容
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise
    
    async def chat_with_context(
        self,
        query: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        带context的对话（用于研究助手）
        
        Args:
            query: 用户查询
            context: 检索到的context信息
            history: 历史对话记录
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            LLM响应内容
        """
        history = history or []
        
        # 构建system prompt
        system_prompt = self._build_research_system_prompt(context)
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史消息（最近10条）
        for msg in history[-10:]:
            role = msg.get("role", "user")
            # 将agent角色转换为assistant
            if role == "agent":
                role = "assistant"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })
        
        # 添加当前查询
        messages.append({
            "role": "user",
            "content": query
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM chat_with_context error: {e}")
            # 返回降级响应
            return "抱歉，我目前无法处理您的请求。请稍后再试。"
    
    def _build_research_system_prompt(self, context: str) -> str:
        """
        构建研究助手的system prompt
        
        Args:
            context: 检索到的context信息
            
        Returns:
            完整的system prompt
        """
        if context:
            return f"""你是一个学术研究助手，帮助用户进行文献调研和知识管理。

以下是从用户的知识图谱中检索到的相关信息：
{context}

请基于上述信息回答用户的问题。回答时请注意：
1. 如果检索结果与问题相关，请引用这些信息来回答
2. 如果检索结果不完全相关，可以结合你的知识进行补充，但要明确指出哪些是来自检索结果，哪些是你的补充
3. 如果检索结果完全不相关，请如实告知用户，并尽可能根据你的知识提供帮助
4. 回答要准确、专业、有条理
5. 如果涉及学术概念，请给出准确的定义和解释"""
        else:
            return """你是一个学术研究助手，帮助用户进行文献调研和知识管理。

目前没有从知识图谱中检索到相关信息。

请根据你的知识尽可能回答用户的问题。回答时请注意：
1. 回答要准确、专业、有条理
2. 如果涉及学术概念，请给出准确的定义和解释
3. 如果不确定，请如实告知用户
4. 建议用户上传相关论文以获得更精准的答案"""
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        带工具调用的对话
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            包含响应和工具调用的字典
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "tool_calls": []
            }
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"LLM chat_with_tools error: {e}")
            raise
    
    async def extract_entities(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        实体抽取
        
        Args:
            text: 要抽取实体的文本
            model: 模型名称
            
        Returns:
            实体列表
        """
        system_prompt = """你是一个实体抽取专家。请从给定的文本中抽取关键实体。

对于每个实体，请提供：
1. name: 实体名称
2. type: 实体类型（如：Person, Organization, Technology, Concept, Method等）
3. description: 简短描述

请以JSON数组格式返回结果。"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("entities", [])
            
        except Exception as e:
            logger.error(f"LLM extract_entities error: {e}")
            return []
    
    async def generate_summary(
        self,
        text: str,
        max_length: int = 500,
        model: Optional[str] = None
    ) -> str:
        """
        生成摘要
        
        Args:
            text: 要摘要的文本
            max_length: 最大摘要长度
            model: 模型名称
            
        Returns:
            摘要文本
        """
        system_prompt = f"""你是一个学术文本摘要专家。请为给定的文本生成一个简洁、准确的摘要。

要求：
1. 摘要长度不超过{max_length}字
2. 保留关键信息和核心观点
3. 使用学术化的语言风格"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=max_length * 2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM generate_summary error: {e}")
            return ""
