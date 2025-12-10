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