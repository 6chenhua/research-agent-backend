"""
图谱实体类型定义

定义 Graphiti 知识图谱中使用的自定义实体类型和边类型。
这些类型用于指导 LLM 在摄入论文时提取结构化的实体和关系。

使用方式：
    在 add_episode 时传入 entity_types 和 edge_types 参数
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== 实体类型 (Entity Types) ====================

class ResearchConcept(BaseModel):
    """
    研究概念/术语
    
    用于表示学术研究中的核心概念、理论或术语。
    例如：Attention Mechanism, Backpropagation, Design Pattern
    """
    definition: Optional[str] = Field(
        None, 
        description="Brief definition of the concept"
    )
    category: Optional[str] = Field(
        None, 
        description="Category of the concept (e.g., algorithm, theory, paradigm)"
    )


class ResearchMethod(BaseModel):
    """
    研究方法/技术
    
    用于表示研究中使用的方法、技术或途径。
    例如：Transfer Learning, A/B Testing, Code Review
    """
    description: Optional[str] = Field(
        None, 
        description="Brief description of the method"
    )
    application: Optional[str] = Field(
        None, 
        description="Common applications or use cases"
    )


class Algorithm(BaseModel):
    """
    算法
    
    用于表示具体的算法实现。
    例如：Transformer, ResNet, QuickSort
    """
    complexity: Optional[str] = Field(
        None, 
        description="Time/space complexity if applicable"
    )
    purpose: Optional[str] = Field(
        None, 
        description="What problem this algorithm solves"
    )


class Dataset(BaseModel):
    """
    数据集
    
    用于表示研究中使用的数据集。
    例如：ImageNet, MNIST, GLUE
    """
    size: Optional[str] = Field(
        None, 
        description="Size of the dataset (e.g., number of samples)"
    )
    source: Optional[str] = Field(
        None, 
        description="Source or origin of the dataset"
    )
    task: Optional[str] = Field(
        None, 
        description="Primary task this dataset is used for"
    )


class Tool(BaseModel):
    """
    工具/框架
    
    用于表示软件工具、库或框架。
    例如：PyTorch, TensorFlow, Git
    """
    version: Optional[str] = Field(
        None, 
        description="Version of the tool"
    )
    language: Optional[str] = Field(
        None, 
        description="Primary programming language"
    )
    purpose: Optional[str] = Field(
        None, 
        description="Main purpose or use case"
    )


class Metric(BaseModel):
    """
    评估指标
    
    用于表示研究中使用的评估指标。
    例如：Accuracy, F1-Score, BLEU
    """
    formula: Optional[str] = Field(
        None, 
        description="Mathematical formula if applicable"
    )
    range: Optional[str] = Field(
        None, 
        description="Value range (e.g., 0-1, 0-100)"
    )
    interpretation: Optional[str] = Field(
        None, 
        description="How to interpret this metric (higher/lower is better)"
    )


class Paper(BaseModel):
    """
    论文
    
    用于表示引用的学术论文。
    """
    year: Optional[int] = Field(
        None, 
        description="Publication year"
    )
    venue: Optional[str] = Field(
        None, 
        description="Conference or journal name"
    )
    doi: Optional[str] = Field(
        None, 
        description="DOI if available"
    )


class Author(BaseModel):
    """
    作者/研究者
    
    用于表示论文作者或研究者。
    """
    affiliation: Optional[str] = Field(
        None, 
        description="Author's institution or organization"
    )
    email: Optional[str] = Field(
        None, 
        description="Contact email if available"
    )


class Organization(BaseModel):
    """
    组织/机构
    
    用于表示研究机构、公司或组织。
    例如：Google, MIT, OpenAI
    """
    type: Optional[str] = Field(
        None, 
        description="Type of organization (university, company, research lab)"
    )
    location: Optional[str] = Field(
        None, 
        description="Location or headquarters"
    )


class Task(BaseModel):
    """
    研究任务
    
    用于表示具体的研究任务或问题。
    例如：Image Classification, Machine Translation, Code Generation
    """
    description: Optional[str] = Field(
        None, 
        description="Description of the task"
    )
    input_type: Optional[str] = Field(
        None, 
        description="Type of input data"
    )
    output_type: Optional[str] = Field(
        None, 
        description="Type of output data"
    )


# ==================== 边类型 (Edge Types) ====================

class Uses(BaseModel):
    """
    使用关系
    
    表示一个实体使用另一个实体。
    例如：Paper uses Method, Method uses Algorithm
    """
    context: Optional[str] = Field(
        None, 
        description="Context in which the usage occurs"
    )


class Implements(BaseModel):
    """
    实现关系
    
    表示一个实体实现另一个实体。
    例如：Tool implements Algorithm
    """
    version: Optional[str] = Field(
        None, 
        description="Implementation version"
    )


class Evaluates(BaseModel):
    """
    评估关系
    
    表示一个实体评估另一个实体。
    例如：Paper evaluates Method using Metric
    """
    result: Optional[str] = Field(
        None, 
        description="Evaluation result"
    )


class Extends(BaseModel):
    """
    扩展关系
    
    表示一个实体扩展或改进另一个实体。
    例如：MethodB extends MethodA
    """
    improvement: Optional[str] = Field(
        None, 
        description="What improvement was made"
    )


class ComparesTo(BaseModel):
    """
    比较关系
    
    表示两个实体之间的比较。
    """
    comparison_result: Optional[str] = Field(
        None, 
        description="Result of comparison"
    )


class AppliesTo(BaseModel):
    """
    应用关系
    
    表示一个实体应用于另一个实体。
    例如：Method applies to Task
    """
    effectiveness: Optional[str] = Field(
        None, 
        description="How effective the application is"
    )


class AuthoredBy(BaseModel):
    """
    作者关系
    
    表示论文由作者撰写。
    """
    contribution: Optional[str] = Field(
        None, 
        description="Author's contribution type (first author, corresponding, etc.)"
    )


class AffiliatedWith(BaseModel):
    """
    隶属关系
    
    表示作者隶属于某个组织。
    """
    role: Optional[str] = Field(
        None, 
        description="Role within the organization"
    )


class Cites(BaseModel):
    """
    引用关系
    
    表示一篇论文引用另一篇论文。
    """
    citation_context: Optional[str] = Field(
        None, 
        description="Context of the citation"
    )


# ==================== 实体类型字典 ====================

ENTITY_TYPES = {
    "Concept": ResearchConcept,
    "Method": ResearchMethod,
    "Algorithm": Algorithm,
    "Dataset": Dataset,
    "Tool": Tool,
    "Metric": Metric,
    "Paper": Paper,
    "Author": Author,
    "Organization": Organization,
    "Task": Task,
}


# ==================== 边类型字典 ====================

EDGE_TYPES = {
    "Uses": Uses,
    "Implements": Implements,
    "Evaluates": Evaluates,
    "Extends": Extends,
    "ComparesTo": ComparesTo,
    "AppliesTo": AppliesTo,
    "AuthoredBy": AuthoredBy,
    "AffiliatedWith": AffiliatedWith,
    "Cites": Cites,
}


# ==================== 边类型映射 ====================

EDGE_TYPE_MAP = {
    # Paper 相关
    ("Paper", "Method"): ["Uses", "Evaluates"],
    ("Paper", "Algorithm"): ["Uses", "Evaluates"],
    ("Paper", "Dataset"): ["Uses", "Evaluates"],
    ("Paper", "Metric"): ["Uses"],
    ("Paper", "Tool"): ["Uses"],
    ("Paper", "Task"): ["AppliesTo"],
    ("Paper", "Author"): ["AuthoredBy"],
    ("Paper", "Paper"): ["Cites", "Extends", "ComparesTo"],
    
    # Method 相关
    ("Method", "Algorithm"): ["Uses", "Implements"],
    ("Method", "Method"): ["Extends", "ComparesTo"],
    ("Method", "Task"): ["AppliesTo"],
    ("Method", "Dataset"): ["Evaluates"],
    ("Method", "Metric"): ["Uses"],
    
    # Algorithm 相关
    ("Algorithm", "Algorithm"): ["Extends", "ComparesTo"],
    ("Algorithm", "Task"): ["AppliesTo"],
    
    # Tool 相关
    ("Tool", "Algorithm"): ["Implements"],
    ("Tool", "Method"): ["Implements"],
    ("Tool", "Tool"): ["Extends", "Uses"],
    
    # Author 相关
    ("Author", "Organization"): ["AffiliatedWith"],
    ("Author", "Author"): ["AffiliatedWith"],
    
    # Concept 相关
    ("Concept", "Concept"): ["Extends"],
    ("Concept", "Method"): ["Uses"],
    ("Concept", "Algorithm"): ["Uses"],
    
    # 通用回退
    ("Entity", "Entity"): ["Uses", "Extends"],
}


# 为 entity_types.py 提供别名（保持向后兼容）
BASE_ENTITY_TYPES = ENTITY_TYPES
BASE_EDGE_TYPES = EDGE_TYPES
DEFAULT_EDGE_TYPE_MAP = EDGE_TYPE_MAP


def get_entity_types() -> dict:
    """获取所有实体类型"""
    return ENTITY_TYPES.copy()


def get_edge_types() -> dict:
    """获取所有边类型"""
    return EDGE_TYPES.copy()


def get_edge_type_map() -> dict:
    """获取边类型映射"""
    return EDGE_TYPE_MAP.copy()
