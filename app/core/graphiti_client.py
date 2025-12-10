from graphiti_core import Graphiti
from app.core.config import settings
from graphiti_core.llm_client.openai_client import OpenAIClient, LLMConfig  # 自定义LLM
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig  # 自定义embedder
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient  # 自定义reranker


class GraphitiClient:
    """Thin wrapper around Graphiti SDK providing async graph operations."""

    def __init__(self):
        self.client = Graphiti(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD,
            llm_client=OpenAIClient(  # 默认AsyncOpenAI
                config=LLMConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                    # model="gpt-4o"
                ),
            ),
            embedder=OpenAIEmbedder(  # 默认AsyncOpenAI
                config=OpenAIEmbedderConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                    # embedding_model="embedding-001"
                )
            ),
            cross_encoder=OpenAIRerankerClient(  # 默认AsyncOpenAI
                config=LLMConfig(
                    base_url=settings.BASE_URL,
                    api_key=settings.GRAPHITI_API_KEY,
                    # model="gpt-4.1-nano"
                )
            ),
            max_coroutines=10,  # default value is ten
        )

    async def add_episode(self, **kwargs):
        return await self.client.add_episode(**kwargs)

    async def search(self, query: str, group_id: str = None, focal_node_uuid: str = None):
        return await self.client.search(query, group_id=group_id, center_node_uuid=focal_node_uuid)