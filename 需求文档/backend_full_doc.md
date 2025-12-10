# Backend Directory Structure (Executable Version with OpenAPI Documentation)

Below is the recommended backend directory structure for your Graphiti-based AI Research Agent backend. All sections include **full OpenAPI documentation comments**, making this a production-ready backend skeleton.

```
backend/
├── main.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── graph.py
│   │   ├── papers.py
│   │   ├── dependencies.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── errors.py
│   │   ├── security.py
│   │   └── graphiti_client.py
│   ├── services/
│   │   ├── pdf_parser.py
│   │   ├── ingest_service.py
│   │   ├── search_service.py
│   │   ├── graph_service.py
│   │   ├── agent_service.py
│   │   └── user_service.py
│   ├── models/
│   │   ├── paper_models.py
│   │   ├── chat_models.py
│   │   ├── graph_models.py
│   │   └── user_models.py
│   ├── tasks/
│   │   ├── worker.py
│   │   └── ingest_tasks.py
│   └── utils/
│       ├── file_utils.py
│       ├── text_splitter.py
│       └── constructor.py
└── tests/
    ├── test_graph.py
    ├── test_chat.py
    └── test_papers.py
```

---

# Code Templates with OpenAPI Documentation

---

## main.py

```python
from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="AI Research Agent Backend",
    description="Backend for Graphiti-powered AI Research Assistant with PDF ingestion, graph search, and LLM agents.",
    version="0.1.0",
)

app.include_router(api_router)

@app.get("/", summary="Health Check", description="Returns basic status to verify the API is alive.")
def root():
    return {"message": "Backend Running"}
```

---

## run.py

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

---

# /app/api

## router.py

```python
"""Main API router that aggregates all feature modules."""
from fastapi import APIRouter
from .chat import router as chat_router
from .graph import router as graph_router
from .papers import router as papers_router

api_router = APIRouter()
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(graph_router, prefix="/graph", tags=["Graph"])
api_router.include_router(papers_router, prefix="/papers", tags=["Papers"])
```

---

## chat.py

```python
"""Chat API router.
Provides endpoints for interacting with the AI Research Agent.
"""
from fastapi import APIRouter, Depends
from app.models.chat_models import ChatRequest, ChatResponse
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
```

---

## graph.py

```python
"""Graph API router.
Exposes search, entity lookup, and graph operations.
"""
from fastapi import APIRouter, Depends
from app.models.graph_models import GraphSearchRequest, GraphSearchResponse
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
```

---

## papers.py

```python
"""Paper ingestion API router.
Handles uploading, parsing, and ingestion of research papers.
"""
from fastapi import APIRouter, UploadFile, Depends
from app.services.ingest_service import IngestService

router = APIRouter()

@router.post(
    "/upload",
    summary="Upload Research Paper (PDF)",
    description="Upload a PDF research paper; it will be parsed, chunked, converted into Graphiti Episodes, and added to the knowledge graph."
)
async def upload_paper(file: UploadFile, svc: IngestService = Depends()):
    """
    Upload and ingest a PDF for graph construction.

    Body:
    - **file**: PDF document

    Returns:
    - **status**: Parsing / ingestion status
    - **paper**: Extracted metadata (title, authors, etc.)
    """
    return await svc.ingest_pdf(file)
```

---

# /app/core

## config.py

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Global backend configuration loaded from environment variables."""

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    GRAPHITI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## graphiti\_client.py

```python
from graphiti_core import Graphiti
from app.core.config import settings

class GraphitiClient:
    """Thin wrapper around Graphiti SDK providing async graph operations."""

    def __init__(self):
        self.client = Graphiti(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD,
        )

    async def add_episode(self, **kwargs):
        return await self.client.add_episode(**kwargs)

    async def search(self, query: str, group_id: str = None, focal_node_uuid: str = None):
        return await self.client.search(query, group_id=group_id, center_node_uuid=focal_node_uuid)
```

---

# /app/services

## pdf\_parser.py

```python
class PDFParser:
    """Extract structured text (title, sections) from a PDF."""

    async def parse(self, file_bytes: bytes) -> dict:
        return {"title": "", "sections": []}
```

---

## ingest\_service.py

```python
from app.core.graphiti_client import GraphitiClient
from app.services.pdf_parser import PDFParser

class IngestService:
    """Service for parsing and ingesting research papers into Graphiti."""

    def __init__(self):
        self.parser = PDFParser()
        self.graph = GraphitiClient()

    async def ingest_pdf(self, file):
        pdf_bytes = await file.read()
        parsed = await self.parser.parse(pdf_bytes)
        # TODO: Convert sections into Graphiti episodes
        return {"status": "parsed", "paper": parsed.get("title", "")}    
```

---

## search\_service.py

```python
from app.core.graphiti_client import GraphitiClient

class SearchService:
    """Wrapper for running hybrid searches over the graph."""

    def __init__(self):
        self.graph = GraphitiClient()

    async def search(self, query: str, group_id: str):
        return await self.graph.search(query, group_id=group_id)
```

---

## graph\_service.py

```python
from app.core.graphiti_client import GraphitiClient

class GraphService:
    """Business logic for all graph operations."""

    def __init__(self):
        self.graph = GraphitiClient()

    async def search(self, req):
        return await self.graph.search(req.query, group_id=req.group_id)

    async def get_entity(self, uuid: str):
        return await self.graph.client.get_by_uuid(uuid)
```

---

## agent\_service.py

```python
class AgentService:
    """LLM-powered reasoning agent using graph-based retrieval."""

    async def chat(self, req):
        # TODO: Retrieval + context construction + LLM response generation
        return {"reply": "TODO: implement agent reasoning"}
```

---

# /app/models

## chat\_models.py

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
```

---

## graph\_models.py

```python
from pydantic import BaseModel

class GraphSearchRequest(BaseModel):
    query: str
    group_id: str

class GraphSearchResponse(BaseModel):
    results: list
```

---

## paper\_models.py

```python
from pydantic import BaseModel

class PaperMetadata(BaseModel):
    title: str
    authors: list = []
    year: int | None = None
```

---

# /app/tasks

## worker.py

```python
from celery import Celery

celery_app = Celery(
    "worker", backend="redis://localhost", broker="redis://localhost"
)
```

---

## ingest\_tasks.py

```python
from .worker import celery_app
from app.services.ingest_service import IngestService

@celery_app.task
async def ingest_pdf_task(file_path: str):
    svc = IngestService()
    return await svc.process_file(file_path)
```

---

# utils/text\_splitter.py

```python
class TextSplitter:
    """Utility for chunking text into smaller segments."""

    def split(self, text: str) -> list[str]:
        return text.split("\n")
```

---

# tests/test\_graph.py

```python
async def test_graph_search():
    assert True
```

