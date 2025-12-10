"""Graphiti客户端封装
提供对Graphiti SDK的封装，简化图谱操作接口
"""
from graphiti_core import Graphiti
from app.core.config import settings
from graphiti_core.llm_client.openai_client import OpenAIClient, LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GraphitiClient:
    """Graphiti SDK封装类
    
    提供异步图谱操作接口：
    - Episode添加（自动实体抽取）
    - 混合搜索（语义+BM25）
    - 节点和边的CRUD操作
    - 社区检测
    """

    def __init__(self):
        """初始化Graphiti客户端
        
        配置LLM、Embedder和Cross-Encoder
        """
        self.client = Graphiti(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD,
            llm_client=OpenAIClient(
                config=LLMConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                ),
            ),
            embedder=OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                )
            ),
            cross_encoder=OpenAIRerankerClient(
                config=LLMConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                )
            ),
            max_coroutines=10,
        )

    async def add_episode(self, **kwargs):
        """添加Episode（文档片段）到图谱
        
        Graphiti会自动进行实体抽取和关系抽取
        
        Args:
            **kwargs: 传递给Graphiti.add_episode的参数
                - content: 文本内容
                - source: 来源标识
                - group_id: 命名空间ID
                - source_description: 来源描述
                
        Returns:
            添加结果
        """
        try:
            return await self.client.add_episode(**kwargs)
        except Exception as e:
            logger.error(f"Add episode error: {str(e)}")
            raise

    async def search(
        self, 
        query: str, 
        group_id: Optional[str] = None, 
        focal_node_uuid: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """执行混合搜索（语义+BM25）
        
        Args:
            query: 搜索查询字符串
            group_id: 命名空间ID（如：global, user:123）
            focal_node_uuid: 中心节点UUID（用于局部搜索）
            limit: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            results = await self.client.search(
                query, 
                group_ids=[group_id] if group_id else None,
                center_node_uuid=focal_node_uuid
            )
            return results[:limit] if results else []
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    async def get_node(self, uuid: str) -> Dict[str, Any]:
        """通过UUID获取节点
        
        Args:
            uuid: 节点UUID
            
        Returns:
            节点信息字典
        """
        try:
            node = await self.client.get_node(uuid)
            return node if node else {}
        except Exception as e:
            logger.error(f"Get node error: {str(e)}")
            raise

    async def get_edges_by_nodes(
        self, 
        source_uuid: str, 
        target_uuid: str
    ) -> List[Dict[str, Any]]:
        """获取两个节点之间的所有边
        
        Args:
            source_uuid: 源节点UUID
            target_uuid: 目标节点UUID
            
        Returns:
            边列表
        """
        try:
            # TODO: 实现实际的边查询
            return []
        except Exception as e:
            logger.error(f"Get edges error: {str(e)}")
            return []

    async def build_communities(
        self, 
        group_id: Optional[str] = None,
        update_communities: bool = True
    ):
        """构建社区
        
        Args:
            group_id: 命名空间ID
            update_communities: 是否更新现有社区
            
        Returns:
            社区构建结果
        """
        try:
            return await self.client.build_communities(
                group_id=group_id,
                update_communities=update_communities
            )
        except Exception as e:
            logger.error(f"Build communities error: {str(e)}")
            raise

    async def get_communities(
        self, 
        group_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取社区列表
        
        Args:
            group_id: 命名空间ID
            
        Returns:
            社区列表
        """
        try:
            # TODO: 实现实际的社区查询
            return []
        except Exception as e:
            logger.error(f"Get communities error: {str(e)}")
            return []

    async def close(self):
        """关闭客户端连接"""
        try:
            await self.client.close()
        except Exception as e:
            logger.error(f"Close client error: {str(e)}")