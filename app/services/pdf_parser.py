class PDFParser:
    """Extract structured text (title, sections) from a PDF."""

    async def parse(self, file_bytes: bytes) -> dict:
        return {"title": "", "sections": []}