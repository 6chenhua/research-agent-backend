"""
用户私有笔记的实体类型和关系类型定义

用于用户将消息/回复添加到私有知识图谱时的实体提取。
这些实体类型专注于用户的研究笔记和思考。
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List


# ==================== 笔记实体类型 ====================

class ResearchInsight(BaseModel):
    """研究洞见：用户从阅读/讨论中获得的见解"""
    content: str = Field(..., description="洞见内容")
    source: Optional[str] = Field(None, description="来源（论文/讨论）")
    confidence: Optional[str] = Field(None, description="确信度: high/medium/low")


class ResearchQuestion(BaseModel):
    """研究问题：用户想要探索的问题"""
    question: str = Field(..., description="问题内容")
    status: Optional[str] = Field(None, description="状态: open/exploring/resolved")
    related_domains: Optional[List[str]] = Field(None, description="相关领域")


class Note(BaseModel):
    """笔记：用户的自由形式笔记"""
    content: str = Field(..., description="笔记内容")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class KeyConcept(BaseModel):
    """关键概念：用户理解的重要概念"""
    name: str = Field(..., description="概念名称")
    definition: Optional[str] = Field(None, description="用户的理解/定义")


class Reference(BaseModel):
    """引用：用户标记的重要引用"""
    citation: str = Field(..., description="引用内容")
    source: Optional[str] = Field(None, description="来源论文/书籍")
    note: Optional[str] = Field(None, description="用户批注")


# ==================== 笔记关系类型 ====================

class Relates(BaseModel):
    """关联关系：两个概念/笔记之间的关联"""
    description: Optional[str] = Field(None, description="关联描述")


class Answers(BaseModel):
    """回答关系：某内容回答了某问题"""
    completeness: Optional[str] = Field(None, description="完整性: partial/full")


class Inspires(BaseModel):
    """启发关系：某内容启发了某洞见"""
    pass


class Contradicts(BaseModel):
    """矛盾关系：两个观点存在矛盾"""
    resolution: Optional[str] = Field(None, description="解决方案")


class Supports(BaseModel):
    """支持关系：某内容支持某观点"""
    pass


# ==================== 导出配置 ====================

NOTE_ENTITY_TYPES: Dict[str, type] = {
    "ResearchInsight": ResearchInsight,
    "ResearchQuestion": ResearchQuestion,
    "Note": Note,
    "KeyConcept": KeyConcept,
    "Reference": Reference,
}

NOTE_EDGE_TYPES: Dict[str, type] = {
    "Relates": Relates,
    "Answers": Answers,
    "Inspires": Inspires,
    "Contradicts": Contradicts,
    "Supports": Supports,
}

# 边类型映射：(源实体, 目标实体) -> 允许的边类型
NOTE_EDGE_TYPE_MAP: Dict[tuple, List[str]] = {
    ("ResearchInsight", "ResearchQuestion"): ["Answers", "Relates"],
    ("ResearchQuestion", "ResearchQuestion"): ["Relates"],
    ("Note", "KeyConcept"): ["Relates"],
    ("KeyConcept", "KeyConcept"): ["Relates", "Contradicts"],
    ("Reference", "ResearchInsight"): ["Inspires", "Supports"],
    ("Reference", "KeyConcept"): ["Supports"],
}


def get_note_entity_types() -> Dict[str, type]:
    """获取笔记实体类型"""
    return NOTE_ENTITY_TYPES


def get_note_edge_types() -> Dict[str, type]:
    """获取笔记边类型"""
    return NOTE_EDGE_TYPES

