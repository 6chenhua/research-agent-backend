"""实体Schema定义
定义8种科研知识图谱实体类型，用于Pydantic验证和类型提示
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """实体类型枚举"""
    PAPER = "Paper"
    METHOD = "Method"
    DATASET = "Dataset"
    TASK = "Task"
    METRIC = "Metric"
    AUTHOR = "Author"
    INSTITUTION = "Institution"
    CONCEPT = "Concept"


class BaseEntity(BaseModel):
    """实体基类"""
    uuid: Optional[str] = Field(None, description="Graphiti节点UUID")
    name: str = Field(..., description="实体名称")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "abc123-def456",
                "name": "Entity Name",
            }
        }


class PaperEntity(BaseEntity):
    """论文实体
    
    表示一篇科研论文，包含标题、摘要、作者、发表信息等
    """
    title: str = Field(..., description="论文标题", min_length=1)
    arxiv_id: Optional[str] = Field(None, description="arXiv ID", pattern=r'^\d{4}\.\d{4,5}(v\d+)?$')
    doi: Optional[str] = Field(None, description="DOI")
    abstract: str = Field("", description="摘要")
    year: Optional[int] = Field(None, description="发表年份", ge=1900, le=2100)
    venue: Optional[str] = Field(None, description="会议/期刊")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    pdf_url: Optional[str] = Field(None, description="PDF链接")
    citation_count: Optional[int] = Field(None, description="引用数", ge=0)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('论文标题不能为空')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "paper_001",
                "name": "Attention Is All You Need",
                "title": "Attention Is All You Need",
                "arxiv_id": "1706.03762",
                "year": 2017,
                "venue": "NeurIPS",
                "authors": ["Vaswani", "Shazeer", "Parmar"]
            }
        }


class MethodEntity(BaseEntity):
    """方法实体
    
    表示一种研究方法、模型或算法
    """
    description: str = Field("", description="方法描述")
    category: Optional[str] = Field(None, description="方法类别（如：深度学习、强化学习）")
    paper_uuid: Optional[str] = Field(None, description="提出该方法的论文UUID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "method_001",
                "name": "Transformer",
                "description": "Self-attention based neural network architecture",
                "category": "Deep Learning"
            }
        }


class DatasetEntity(BaseEntity):
    """数据集实体
    
    表示一个研究数据集
    """
    description: Optional[str] = Field(None, description="数据集描述")
    domain: Optional[str] = Field(None, description="领域（如：NLP、CV）")
    size: Optional[str] = Field(None, description="数据集大小")
    url: Optional[str] = Field(None, description="数据集链接")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "dataset_001",
                "name": "ImageNet",
                "description": "Large scale image classification dataset",
                "domain": "Computer Vision",
                "size": "1.2M images"
            }
        }


class TaskEntity(BaseEntity):
    """任务实体
    
    表示一个研究任务或问题
    """
    description: Optional[str] = Field(None, description="任务描述")
    domain: Optional[str] = Field(None, description="所属领域")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "task_001",
                "name": "Machine Translation",
                "description": "Translate text from source to target language",
                "domain": "Natural Language Processing"
            }
        }


class MetricEntity(BaseEntity):
    """评价指标实体
    
    表示一个性能评估指标
    """
    value: Optional[float] = Field(None, description="指标值")
    unit: Optional[str] = Field(None, description="单位（如：%、accuracy）")
    description: Optional[str] = Field(None, description="指标描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "metric_001",
                "name": "BLEU",
                "description": "Bilingual Evaluation Understudy",
                "unit": "score"
            }
        }


class AuthorEntity(BaseEntity):
    """作者实体
    
    表示一位研究者/作者
    """
    affiliation: Optional[str] = Field(None, description="所属机构")
    email: Optional[str] = Field(None, description="邮箱")
    h_index: Optional[int] = Field(None, description="h-index", ge=0)
    paper_count: Optional[int] = Field(None, description="论文数量", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "author_001",
                "name": "Yoshua Bengio",
                "affiliation": "University of Montreal",
                "h_index": 180
            }
        }


class InstitutionEntity(BaseEntity):
    """机构实体
    
    表示一个研究机构或大学
    """
    country: Optional[str] = Field(None, description="国家")
    city: Optional[str] = Field(None, description="城市")
    type: Optional[str] = Field(None, description="类型（如：大学、企业、研究所）")
    website: Optional[str] = Field(None, description="官网")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "inst_001",
                "name": "MIT",
                "country": "USA",
                "city": "Cambridge",
                "type": "University"
            }
        }


class ConceptEntity(BaseEntity):
    """概念实体
    
    表示一个学术概念或术语
    """
    description: Optional[str] = Field(None, description="概念描述")
    domain: Optional[str] = Field(None, description="所属领域")
    aliases: List[str] = Field(default_factory=list, description="别名列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "concept_001",
                "name": "Attention Mechanism",
                "description": "A technique to focus on relevant parts of input",
                "domain": "Deep Learning",
                "aliases": ["Self-Attention", "Attention"]
            }
        }


# 实体类型映射
ENTITY_TYPE_MAP = {
    EntityType.PAPER: PaperEntity,
    EntityType.METHOD: MethodEntity,
    EntityType.DATASET: DatasetEntity,
    EntityType.TASK: TaskEntity,
    EntityType.METRIC: MetricEntity,
    EntityType.AUTHOR: AuthorEntity,
    EntityType.INSTITUTION: InstitutionEntity,
    EntityType.CONCEPT: ConceptEntity,
}
