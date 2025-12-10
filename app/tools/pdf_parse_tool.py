"""PDF解析工具"""
from .base import BaseTool, ToolInput, ToolOutput

class PDFParseInput(ToolInput):
    file_path: str
    user_id: str

class PDFParseOutput(ToolOutput):
    paper_id: str
    status: str

class PDFParseTool(BaseTool):
    """PDF解析工具"""
    name = "pdf_parse"
    description = "解析PDF论文并摄入图谱"
    
    async def execute(self, input_data: PDFParseInput) -> PDFParseOutput:
        # TODO: 实现PDF解析
        return PDFParseOutput(paper_id="", status="pending")
