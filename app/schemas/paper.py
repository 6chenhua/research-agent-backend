"""
论文相关的Pydantic模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PaperMetadata(BaseModel):
    """论文元数据"""
    title: str = Field(..., description="论文标题")
    authors: List[str] = Field(default=[], description="作者列表")
    year: Optional[int] = Field(None, description="发表年份")
    abstract: Optional[str] = Field(None, description="摘要")
    venue: Optional[str] = Field(None, description="会议/期刊")


class PaperUploadResponse(BaseModel):
    """论文上传响应（只上传，不解析）"""
    paper_id: str = Field(..., description="论文ID")
    filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    status: str = Field(..., description="处理状态（uploaded）")
    message: Optional[str] = Field(None, description="提示信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": "paper_abc123def456",
                "filename": "attention_is_all_you_need.pdf",
                "file_size": 1234567,
                "status": "uploaded",
                "message": "Paper uploaded successfully. It will be parsed when used in chat."
            }
        }


class EntityInfo(BaseModel):
    """实体信息"""
    uuid: str = Field(..., description="实体UUID")
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型")
    summary: Optional[str] = Field(None, description="实体摘要")


class RelatedPaper(BaseModel):
    """相关论文"""
    paper_id: str = Field(..., description="论文ID")
    title: str = Field(..., description="论文标题")
    relevance_score: float = Field(..., description="相关度分数")


class PaperDetailResponse(BaseModel):
    """论文详情响应"""
    paper_id: str = Field(..., description="论文ID")
    title: str = Field(..., description="论文标题")
    authors: List[str] = Field(default=[], description="作者列表")
    abstract: Optional[str] = Field(None, description="摘要")
    year: Optional[int] = Field(None, description="发表年份")
    venue: Optional[str] = Field(None, description="会议/期刊")
    citations_count: int = Field(default=0, description="引用数")
    read_count: int = Field(default=0, description="阅读次数")
    pdf_url: Optional[str] = Field(None, description="PDF链接")
    entities: List[EntityInfo] = Field(default=[], description="提取的实体列表")
    related_papers: List[RelatedPaper] = Field(default=[], description="相关论文推荐")
    created_at: Optional[str] = Field(None, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": "paper_abc123def456",
                "title": "Attention Is All You Need",
                "authors": ["Vaswani, Ashish", "Shazeer, Noam"],
                "abstract": "The dominant sequence transduction models...",
                "year": 2017,
                "venue": "NeurIPS",
                "citations_count": 50000,
                "read_count": 120,
                "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                "entities": [
                    {
                        "uuid": "entity_123",
                        "name": "Transformer",
                        "type": "Method",
                        "summary": "A neural network architecture based on attention mechanisms"
                    }
                ],
                "related_papers": [
                    {
                        "paper_id": "paper_xyz789",
                        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                        "relevance_score": 0.92
                    }
                ],
                "created_at": "2025-12-10T10:30:00"
            }
        }

