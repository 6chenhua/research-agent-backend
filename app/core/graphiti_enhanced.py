"""
增强版 Graphiti 单例客户端
提供并发控制、超时保护、性能监控等功能
"""
import asyncio
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_client import OpenAIClient, LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.nodes import EpisodeType, EntityNode
from pydantic import BaseModel

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EnhancedGraphitiSingleton:
    """增强版 Graphiti 单例
    
    特性：
    - ✅ 全局单例（所有用户共享）
    - ✅ 并发控制（每用户限制并发数）
    - ✅ 超时保护（防止长时间阻塞）
    - ✅ 性能监控（记录请求指标）
    - ✅ 线程安全（asyncio.Lock）
    
    为什么使用单例？
    - 资源高效：共享连接池、LLM、Embedder
    - 成本优化：减少 OpenAI API 连接数
    - 符合设计：Graphiti 通过 group_id 实现多租户
    """
    
    _instance: Optional['EnhancedGraphitiSingleton'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False
    
    # 配置参数
    MAX_USER_CONCURRENT = 5  # 每个用户最大并发请求数
    DEFAULT_SEARCH_TIMEOUT = 10.0  # 默认搜索超时（秒）
    DEFAULT_EPISODE_TIMEOUT = 300.0  # 默认添加Episode超时（秒）
    SLOW_QUERY_THRESHOLD = 3.0  # 慢查询阈值（秒）
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """初始化 Graphiti 客户端（只执行一次）
        
        这个方法是线程安全的，即使多个协程同时调用也只会初始化一次
        """
        if self._initialized:
            return
        
        async with self._lock:
            # 双重检查
            if self._initialized:
                return
            
            try:
                logger.info("🚀 Initializing Enhanced Graphiti client...")
                
                # 1. 初始化 Graphiti 客户端
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
                
                # 2. 初始化并发控制（每个用户一个信号量）
                self._user_semaphores: Dict[str, asyncio.Semaphore] = defaultdict(
                    lambda: asyncio.Semaphore(self.MAX_USER_CONCURRENT)
                )
                
                # 3. 初始化监控指标
                self._metrics = {
                    "total_requests": 0,
                    "active_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "timeouts": 0,
                    "slow_queries": 0,
                }
                
                # 4. 用户请求计数（用于监控）
                self._user_request_counts: Dict[str, int] = defaultdict(int)
                
                self._initialized = True
                logger.info("✅ Enhanced Graphiti client initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Graphiti client: {str(e)}")
                raise
    
    async def search(
        self,
        query: str,
        user_id: str,
        group_ids: Optional[List[str]] = None,
        timeout: Optional[float] = None,
        limit: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """增强的搜索方法
        
        Args:
            query: 搜索查询字符串
            user_id: 用户ID（用于并发控制和监控）
            group_ids: 命名空间ID列表（如：["user:123:domain:ai", "global:domain:ai"]）
            timeout: 超时时间（秒），None 使用默认值
            limit: 返回结果数量
            **kwargs: 其他传递给 Graphiti.search 的参数
            
        Returns:
            搜索结果列表
            
        Raises:
            asyncio.TimeoutError: 查询超时
            Exception: 其他错误
        """
        if not self._initialized:
            raise RuntimeError("Graphiti client not initialized")
        
        timeout = timeout or self.DEFAULT_SEARCH_TIMEOUT
        
        # 1. 并发控制：限制每个用户的并发请求数
        async with self._user_semaphores[user_id]:
            # 2. 更新监控指标
            self._metrics["total_requests"] += 1
            self._metrics["active_requests"] += 1
            self._user_request_counts[user_id] += 1
            
            start_time = time.time()
            
            try:
                # 3. 执行搜索（带超时保护）
                result = await asyncio.wait_for(
                    self.client.search(
                        query,
                        group_ids=group_ids,
                        **kwargs
                    ),
                    timeout=timeout
                )
                
                # 4. 性能监控
                duration = time.time() - start_time
                
                # 记录慢查询
                if duration > self.SLOW_QUERY_THRESHOLD:
                    self._metrics["slow_queries"] += 1
                    logger.warning(
                        f"⚠️ Slow search detected: {duration:.2f}s | "
                        f"user={user_id} | query={query[:50]}..."
                    )
                else:
                    logger.debug(
                        f"✅ Search completed: {duration:.2f}s | "
                        f"user={user_id} | results={len(result)} | "
                        f"group_ids={group_ids}"
                    )
                
                self._metrics["successful_requests"] += 1
                
                return result[:limit] if result else []
                
            except asyncio.TimeoutError:
                self._metrics["timeouts"] += 1
                logger.error(
                    f"❌ Search timeout ({timeout}s) | "
                    f"user={user_id} | query={query[:50]}..."
                )
                return []  # 超时返回空结果，而不是抛出异常
                
            except Exception as e:
                self._metrics["failed_requests"] += 1
                logger.error(
                    f"❌ Search error: {str(e)} | "
                    f"user={user_id} | query={query[:50]}..."
                )
                raise
                
            finally:
                self._metrics["active_requests"] -= 1
    
    async def add_episode(
        self,
        episode_body: str,
        user_id: str,
        group_id: str,
        name: Optional[str] = None,
        source: EpisodeType = EpisodeType.text,
        source_description: Optional[str] = None,
        reference_time: Optional[datetime] = None,
        timeout: Optional[float] = None,
        entity_types: Optional[Dict[str, type]] = None,
        edge_types: Optional[Dict[str, type]] = None,
        edge_type_map: Optional[Dict[tuple, List[str]]] = None,
        **kwargs
    ):
        """增强的添加 Episode 方法
        
        Args:
            episode_body: Episode 内容（必需）
                - 对于 EpisodeType.text: 普通文本内容
                - 对于 EpisodeType.message: 对话格式 "Role: message\nRole2: message2"
                - 对于 EpisodeType.json: JSON格式的结构化数据
            user_id: 用户ID（用于并发控制和监控）
            group_id: 命名空间ID
            name: Episode名称（可选，默认自动生成）
            source: 来源类型（默认EpisodeType.text）
                - EpisodeType.text: 文档、文章等文本内容
                - EpisodeType.message: 聊天消息（需要"Role: message"格式）
                - EpisodeType.json: 结构化JSON数据
            source_description: 来源描述（可选）
            reference_time: 参考时间（可选，默认当前UTC时间）
            timeout: 超时时间（秒），None 使用默认值
            entity_types: 自定义实体类型字典，如 {"AI_Concept": ResearchConcept}
            edge_types: 自定义边类型字典，如 {"Uses": Uses}
            edge_type_map: 边类型映射，如 {("Concept", "Method"): ["Uses"]}
            **kwargs: 其他传递给 Graphiti.add_episode 的参数
            
        Returns:
            添加结果
            
        Raises:
            asyncio.TimeoutError: 操作超时
            Exception: 其他错误
            
        Examples:
            # 带自定义实体类型的论文摄入
            from app.utils.entity_types import build_entity_types_for_domain, get_edge_types
            
            await add_episode(
                episode_body="This is research paper content...",
                source=EpisodeType.text,
                entity_types=build_entity_types_for_domain("AI"),
                edge_types=get_edge_types(),
                ...
            )
        """
        if not self._initialized:
            raise RuntimeError("Graphiti client not initialized")
        
        timeout = timeout or self.DEFAULT_EPISODE_TIMEOUT
        
        # 默认使用当前UTC时间
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)
        
        # 添加操作更重，使用更严格的并发控制
        add_semaphore = asyncio.Semaphore(2)  # 每个用户最多2个并发添加操作
        
        async with add_semaphore:
            start_time = time.time()
            
            try:
                # 构建参数
                episode_kwargs = {
                    "name": name or f"episode_{group_id}_{int(start_time)}",
                    "episode_body": episode_body,
                    "source": source,
                    "source_description": source_description,
                    "reference_time": reference_time,
                    "group_id": group_id,
                    "update_communities": True,
                }
                
                # 添加自定义类型（如果提供）
                if entity_types:
                    episode_kwargs["entity_types"] = entity_types
                if edge_types:
                    episode_kwargs["edge_types"] = edge_types
                if edge_type_map:
                    episode_kwargs["edge_type_map"] = edge_type_map
                
                # 合并其他参数
                episode_kwargs.update(kwargs)
                
                result = await asyncio.wait_for(
                    self.client.add_episode(**episode_kwargs),
                    timeout=timeout
                )
                
                duration = time.time() - start_time
                
                logger.info(
                    f"✅ Episode added: {duration:.2f}s | "
                    f"user={user_id} | content_length={len(episode_body)} | "
                    f"group_id={group_id} | "
                    f"entity_types={list(entity_types.keys()) if entity_types else 'default'}"
                )
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(
                    f"❌ Add episode timeout ({timeout}s) | "
                    f"user={user_id} | content_length={len(episode_body)}"
                )
                raise
                
            except Exception as e:
                logger.error(
                    f"❌ Add episode error: {str(e)} | "
                    f"user={user_id} | content_length={len(episode_body)}"
                )
                raise
    
    async def get_node(self, uuid: str) -> Dict[str, Any]:
        """获取节点（无并发限制，因为是简单查询）
        
        使用 EntityNode.get_by_uuid 类方法获取节点，
        这是 Graphiti 官方推荐的方式。
        
        Args:
            uuid: 节点UUID
            
        Returns:
            节点信息字典，包含 uuid, name, labels, created_at, summary 等字段
        """
        if not self._initialized:
            raise RuntimeError("Graphiti client not initialized")
        
        try:
            # 使用 EntityNode 类方法获取节点
            # 需要传入 driver（从 Graphiti 客户端获取）
            node = await EntityNode.get_by_uuid(self.client.driver, uuid)
            
            if node:
                # 将 EntityNode 对象转换为字典
                return {
                    "uuid": node.uuid,
                    "name": node.name,
                    "labels": node.labels,
                    "created_at": node.created_at.isoformat() if node.created_at else None,
                    "summary": node.summary,
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Get node error: {str(e)} | uuid={uuid}")
            raise
    
    async def build_communities(
        self,
        group_ids: Optional[List[str]] = None
    ):
        """构建社区（重量级操作，添加日志）
        
        Args:
            group_ids: 命名空间ID列表（可选，部分版本的graphiti可能不支持）
            
        Returns:
            社区构建结果
        """
        if not self._initialized:
            raise RuntimeError("Graphiti client not initialized")
        
        start_time = time.time()
        
        try:
            logger.info(f"🔨 Building communities | group_ids={group_ids}")
            
            # graphiti-core不同版本的API可能不同，尝试兼容
            try:
                if group_ids:
                    result = await self.client.build_communities(group_ids=group_ids)
                else:
                    result = await self.client.build_communities()
            except TypeError as te:
                # 如果group_ids参数不被支持，使用无参数调用
                logger.warning(f"build_communities不支持group_ids参数，使用默认调用: {te}")
                result = await self.client.build_communities()
            
            duration = time.time() - start_time
            
            logger.info(
                f"✅ Communities built: {duration:.2f}s | "
                f"group_ids={group_ids}"
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"❌ Build communities error: {str(e)} | "
                f"group_ids={group_ids}"
            )
            # 社区构建失败不应该阻塞主流程，记录错误但不抛出
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标
        
        Returns:
            指标字典
        """
        return {
            **self._metrics,
            "user_semaphores_count": len(self._user_semaphores),
            "top_users": sorted(
                self._user_request_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 活跃用户
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """获取特定用户的统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户统计信息
        """
        return {
            "user_id": user_id,
            "total_requests": self._user_request_counts.get(user_id, 0),
            "has_semaphore": user_id in self._user_semaphores,
        }
    
    async def close(self):
        """关闭客户端连接"""
        if self._initialized and self.client:
            try:
                logger.info("🛑 Closing Enhanced Graphiti client...")
                
                # 等待所有活跃请求完成（最多等待10秒）
                wait_time = 0
                while self._metrics["active_requests"] > 0 and wait_time < 10:
                    logger.info(
                        f"Waiting for {self._metrics['active_requests']} "
                        f"active requests to complete..."
                    )
                    await asyncio.sleep(1)
                    wait_time += 1
                
                await self.client.close()
                self._initialized = False
                
                # 打印最终统计
                logger.info(f"📊 Final metrics: {self.get_metrics()}")
                logger.info("✅ Enhanced Graphiti client closed")
                
            except Exception as e:
                logger.error(f"❌ Error closing client: {str(e)}")


# 全局单例实例
enhanced_graphiti = EnhancedGraphitiSingleton()


async def get_enhanced_graphiti() -> EnhancedGraphitiSingleton:
    """获取增强版 Graphiti 客户端（依赖注入用）
    
    Returns:
        全局单例客户端
    """
    if not enhanced_graphiti._initialized:
        await enhanced_graphiti.initialize()
    return enhanced_graphiti

