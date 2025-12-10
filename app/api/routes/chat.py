"""Chat API router.
Provides endpoints for interacting with the AI Research Agent.
"""
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService

router = APIRouter()

@router.post(
    "/",
    response_model=ChatResponse,
    summary="Agent Chat Endpoint",
    description="Send a message to the AI agent and receive a generated response."
)
async def chat(req: ChatRequest, agent: AgentService = Depends()):
    """
    Handle a chat request.

    - **user_id**: ID of the user (determines the user's private graph namespace)
    - **message**: User query text

    The agent performs:
    - Hybrid graph search (Graphiti)
    - Context construction
    - LLM reasoning

    Returns:
    - **reply**: Agent-generated natural language response
    """
    return await agent.chat(req)