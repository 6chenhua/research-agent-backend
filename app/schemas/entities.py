"""实体Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PaperEntity(BaseModel):
    """论文实体"""
    title: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    abstract: str = ""
    year: Optional[int] = None
    venue: Optional[str] = None
    authors: List[str] = []


class MethodEntity(BaseModel):
    """方法实体"""
    name: str
    description: str = ""
    category: Optional[str] = None


class DatasetEntity(BaseModel):
    """数据集实体"""
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None


class TaskEntity(BaseModel):
    """任务实体"""
    name: str
    description: Optional[str] = None


class MetricEntity(BaseModel):
    """评价指标实体"""
    name: str
    value: Optional[float] = None


class AuthorEntity(BaseModel):
    """作者实体"""
    name: str
    affiliation: Optional[str] = None


class InstitutionEntity(BaseModel):
    """机构实体"""
    name: str
    country: Optional[str] = None


class ConceptEntity(BaseModel):
    """概念实体"""
    name: str
    description: Optional[str] = None
