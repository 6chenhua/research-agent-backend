from app.core.graphiti_client import GraphitiClient


class SearchService:
    """Wrapper for running hybrid searches over the graph."""

    def __init__(self):
        self.graph = GraphitiClient()

    async def search(self, query: str, group_id: str):
        return await self.graph.search(query, group_id=group_id)