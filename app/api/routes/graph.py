"""Graph API router.
Exposes search, entity lookup, and graph operations.
"""
from fastapi import APIRouter, Depends
from app.schemas.graph import GraphSearchRequest, GraphSearchResponse
from app.services.graph_service import GraphService

router = APIRouter()

@router.post(
    "/search",
    response_model=GraphSearchResponse,
    summary="Graph Hybrid Search",
    description="Hybrid semantic + BM25 search using Graphiti. Supports user namespaces via `group_id`."
)
async def graph_search(req: GraphSearchRequest, svc: GraphService = Depends()):
    """
    Perform hybrid graph search.

    Body:
    - **query**: Search string
    - **group_id**: Namespace identifier (e.g., `global`, `user:<id>`)

    Returns:
    - Ranked list of nodes or facts
    """
    return await svc.search(req)


@router.get(
    "/entity/{uuid}",
    summary="Get Entity by UUID",
    description="Retrieve an entity node from Graphiti by UUID."
)
async def get_entity(uuid: str, svc: GraphService = Depends()):
    """
    Fetch a graph entity using its UUID.

    Path params:
    - **uuid**: Graphiti node UUID

    Returns:
    - Entity metadata including labels, attributes, and summary
    """
    return await svc.get_entity(uuid)