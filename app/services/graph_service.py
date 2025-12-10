from app.core.graphiti_client import GraphitiClient


class GraphService:
    """Business logic for all graph operations."""

    def __init__(self):
        self.graph = GraphitiClient()

    async def search(self, req):
        return await self.graph.search(req.query, group_id=req.group_id)

    async def get_entity(self, uuid: str):
        return await self.graph.client.get_by_uuid(uuid)