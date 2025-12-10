"""关系Schema定义
定义9种科研知识图谱关系类型，描述实体之间的联系
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class RelationType(str, Enum):
    """关系类型枚举
    
    定义9种核心关系类型，覆盖科研知识图谱的主要联系
    """
    PROPOSES = "PROPOSES"  # Paper -> Method (论文提出方法)
    EVALUATES_ON = "EVALUATES_ON"  # Paper -> Dataset (论文在数据集上评估)
    SOLVES = "SOLVES"  # Method -> Task (方法解决任务)
    IMPROVES_OVER = "IMPROVES_OVER"  # Method -> Method (方法改进自另一方法)
    CITES = "CITES"  # Paper -> Paper (论文引用论文)
    USES_METRIC = "USES_METRIC"  # Paper -> Metric (论文使用指标)
    AUTHORED_BY = "AUTHORED_BY"  # Paper -> Author (论文由作者撰写)
    AFFILIATED_WITH = "AFFILIATED_WITH"  # Author -> Institution (作者隶属机构)
    HAS_CONCEPT = "HAS_CONCEPT"  # Paper -> Concept (论文包含概念)


class BaseRelation(BaseModel):
    """关系基类"""
    uuid: Optional[str] = Field(None, description="Graphiti边UUID")
    relation_type: RelationType = Field(..., description="关系类型")
    source_uuid: str = Field(..., description="源节点UUID")
    target_uuid: str = Field(..., description="目标节点UUID")
    weight: Optional[float] = Field(1.0, description="关系权重", ge=0.0, le=1.0)
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "uuid": "rel_001",
                "relation_type": "PROPOSES",
                "source_uuid": "paper_001",
                "target_uuid": "method_001",
                "weight": 0.95
            }
        }


class ProposesRelation(BaseRelation):
    """PROPOSES关系: Paper -> Method
    
    表示论文提出了某个方法/模型/算法
    """
    relation_type: RelationType = Field(default=RelationType.PROPOSES, Literal=True)
    is_primary: bool = Field(True, description="是否为论文的主要贡献")
    description: Optional[str] = Field(None, description="方法描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_transformer",
                "target_uuid": "method_transformer",
                "is_primary": True,
                "description": "Paper proposes the Transformer architecture"
            }
        }


class EvaluatesOnRelation(BaseRelation):
    """EVALUATES_ON关系: Paper -> Dataset
    
    表示论文在某个数据集上进行了实验评估
    """
    relation_type: RelationType = Field(default=RelationType.EVALUATES_ON, Literal=True)
    metric_value: Optional[float] = Field(None, description="评估结果")
    metric_name: Optional[str] = Field(None, description="评估指标名称")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_bert",
                "target_uuid": "dataset_squad",
                "metric_value": 93.2,
                "metric_name": "F1 Score"
            }
        }


class SolvesRelation(BaseRelation):
    """SOLVES关系: Method -> Task
    
    表示某方法解决/应用于某个任务
    """
    relation_type: RelationType = Field(default=RelationType.SOLVES, Literal=True)
    effectiveness: Optional[str] = Field(None, description="效果描述（如：SOTA、competitive）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "method_gpt",
                "target_uuid": "task_text_generation",
                "effectiveness": "State-of-the-art"
            }
        }


class ImprovesOverRelation(BaseRelation):
    """IMPROVES_OVER关系: Method -> Method
    
    表示某方法改进自/优于另一方法
    """
    relation_type: RelationType = Field(default=RelationType.IMPROVES_OVER, Literal=True)
    improvement_percentage: Optional[float] = Field(None, description="改进百分比")
    improvement_description: Optional[str] = Field(None, description="改进说明")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "method_bert",
                "target_uuid": "method_lstm",
                "improvement_percentage": 15.3,
                "improvement_description": "Better performance on NLU tasks"
            }
        }


class CitesRelation(BaseRelation):
    """CITES关系: Paper -> Paper
    
    表示一篇论文引用了另一篇论文
    """
    relation_type: RelationType = Field(default=RelationType.CITES, Literal=True)
    citation_context: Optional[str] = Field(None, description="引用上下文")
    section: Optional[str] = Field(None, description="引用出现的章节")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_gpt3",
                "target_uuid": "paper_transformer",
                "citation_context": "Building upon the Transformer architecture...",
                "section": "Introduction"
            }
        }


class UsesMetricRelation(BaseRelation):
    """USES_METRIC关系: Paper -> Metric
    
    表示论文使用了某个评估指标
    """
    relation_type: RelationType = Field(default=RelationType.USES_METRIC, Literal=True)
    reported_value: Optional[float] = Field(None, description="报告的指标值")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_resnet",
                "target_uuid": "metric_accuracy",
                "reported_value": 96.4
            }
        }


class AuthoredByRelation(BaseRelation):
    """AUTHORED_BY关系: Paper -> Author
    
    表示论文由某作者撰写
    """
    relation_type: RelationType = Field(default=RelationType.AUTHORED_BY, Literal=True)
    author_position: Optional[int] = Field(None, description="作者顺序（1为第一作者）", ge=1)
    contribution: Optional[str] = Field(None, description="贡献描述")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_transformer",
                "target_uuid": "author_vaswani",
                "author_position": 1,
                "contribution": "First author, led the research"
            }
        }


class AffiliatedWithRelation(BaseRelation):
    """AFFILIATED_WITH关系: Author -> Institution
    
    表示作者隶属于某机构
    """
    relation_type: RelationType = Field(default=RelationType.AFFILIATED_WITH, Literal=True)
    start_date: Optional[str] = Field(None, description="开始时间")
    end_date: Optional[str] = Field(None, description="结束时间（None表示当前）")
    position: Optional[str] = Field(None, description="职位（如：Professor、PhD Student）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "author_hinton",
                "target_uuid": "inst_toronto",
                "position": "Professor",
                "start_date": "1987"
            }
        }


class HasConceptRelation(BaseRelation):
    """HAS_CONCEPT关系: Paper -> Concept
    
    表示论文涉及/使用了某个概念
    """
    relation_type: RelationType = Field(default=RelationType.HAS_CONCEPT, Literal=True)
    relevance: Optional[float] = Field(None, description="相关度", ge=0.0, le=1.0)
    mention_count: Optional[int] = Field(None, description="提及次数", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_uuid": "paper_transformer",
                "target_uuid": "concept_attention",
                "relevance": 0.98,
                "mention_count": 47
            }
        }


# 关系类型映射
RELATION_TYPE_MAP = {
    RelationType.PROPOSES: ProposesRelation,
    RelationType.EVALUATES_ON: EvaluatesOnRelation,
    RelationType.SOLVES: SolvesRelation,
    RelationType.IMPROVES_OVER: ImprovesOverRelation,
    RelationType.CITES: CitesRelation,
    RelationType.USES_METRIC: UsesMetricRelation,
    RelationType.AUTHORED_BY: AuthoredByRelation,
    RelationType.AFFILIATED_WITH: AffiliatedWithRelation,
    RelationType.HAS_CONCEPT: HasConceptRelation,
}


# 关系的源和目标实体类型约束
RELATION_CONSTRAINTS = {
    RelationType.PROPOSES: ("Paper", "Method"),
    RelationType.EVALUATES_ON: ("Paper", "Dataset"),
    RelationType.SOLVES: ("Method", "Task"),
    RelationType.IMPROVES_OVER: ("Method", "Method"),
    RelationType.CITES: ("Paper", "Paper"),
    RelationType.USES_METRIC: ("Paper", "Metric"),
    RelationType.AUTHORED_BY: ("Paper", "Author"),
    RelationType.AFFILIATED_WITH: ("Author", "Institution"),
    RelationType.HAS_CONCEPT: ("Paper", "Concept"),
}
