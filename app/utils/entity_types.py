"""
实体类型和关系类型工具函数

提供 Graphiti 知识图谱使用的实体类型和关系类型定义。
直接使用 entities.py 和 relations.py 中的规范定义，不再动态构建。

使用方式：
    from app.utils.entity_types import get_entity_types, get_relation_types
    
    # 在 add_episode 时使用
    result = await graphiti.add_episode(
        ...,
        entity_types=get_entity_types(),
        edge_types=get_relation_types(),
    )
"""
from typing import Dict, Type
from pydantic import BaseModel

from app.schemas.entities import (
    EntityType,
    PaperEntity,
    MethodEntity,
    DatasetEntity,
    TaskEntity,
    MetricEntity,
    AuthorEntity,
    InstitutionEntity,
    ConceptEntity,
    ENTITY_TYPE_MAP,
)
from app.schemas.relations import (
    RelationType,
    ProposesRelation,
    EvaluatesOnRelation,
    SolvesRelation,
    ImprovesOverRelation,
    CitesRelation,
    UsesMetricRelation,
    AuthoredByRelation,
    AffiliatedWithRelation,
    HasConceptRelation,
    RELATION_TYPE_MAP,
    RELATION_CONSTRAINTS,
)


# ==================== 实体类型 ====================

# 为 Graphiti 提供的实体类型字典
# key 是类型名称，value 是 Pydantic 模型类
ENTITY_TYPES: Dict[str, Type[BaseModel]] = {
    "Paper": PaperEntity,
    "Method": MethodEntity,
    "Dataset": DatasetEntity,
    "Task": TaskEntity,
    "Metric": MetricEntity,
    "Author": AuthorEntity,
    "Institution": InstitutionEntity,
    "Concept": ConceptEntity,
}


# ==================== 关系类型 ====================

# 为 Graphiti 提供的关系（边）类型字典
RELATION_TYPES: Dict[str, Type[BaseModel]] = {
    "PROPOSES": ProposesRelation,
    "EVALUATES_ON": EvaluatesOnRelation,
    "SOLVES": SolvesRelation,
    "IMPROVES_OVER": ImprovesOverRelation,
    "CITES": CitesRelation,
    "USES_METRIC": UsesMetricRelation,
    "AUTHORED_BY": AuthoredByRelation,
    "AFFILIATED_WITH": AffiliatedWithRelation,
    "HAS_CONCEPT": HasConceptRelation,
}


# ==================== 辅助函数 ====================

def get_entity_types() -> Dict[str, Type[BaseModel]]:
    """
    获取实体类型字典
    
    用于 Graphiti add_episode 的 entity_types 参数。
    
    Returns:
        实体类型字典，如 {"Paper": PaperEntity, "Method": MethodEntity, ...}
        
    Example:
        >>> entity_types = get_entity_types()
        >>> await graphiti.add_episode(..., entity_types=entity_types)
    """
    return ENTITY_TYPES.copy()


def get_relation_types() -> Dict[str, Type[BaseModel]]:
    """
    获取关系类型字典
    
    用于 Graphiti add_episode 的 edge_types 参数。
    
    Returns:
        关系类型字典，如 {"PROPOSES": ProposesRelation, ...}
        
    Example:
        >>> edge_types = get_relation_types()
        >>> await graphiti.add_episode(..., edge_types=edge_types)
    """
    return RELATION_TYPES.copy()


def get_relation_constraints() -> Dict[str, tuple]:
    """
    获取关系约束
    
    定义每种关系类型的合法 (源实体类型, 目标实体类型)。
    
    Returns:
        约束字典，如 {RelationType.PROPOSES: ("Paper", "Method"), ...}
    """
    return RELATION_CONSTRAINTS.copy()


def get_all_entity_type_names() -> list:
    """获取所有实体类型名称列表"""
    return list(ENTITY_TYPES.keys())


def get_all_relation_type_names() -> list:
    """获取所有关系类型名称列表"""
    return list(RELATION_TYPES.keys())


def is_valid_entity_type(type_name: str) -> bool:
    """检查实体类型是否有效"""
    return type_name in ENTITY_TYPES


def is_valid_relation_type(type_name: str) -> bool:
    """检查关系类型是否有效"""
    return type_name in RELATION_TYPES


# ==================== 领域相关（保留用于兼容） ====================

# 支持的研究领域
SUPPORTED_DOMAINS = [
    "AI",        # Artificial Intelligence
    "ML",        # Machine Learning
    "DL",        # Deep Learning
    "NLP",       # Natural Language Processing
    "CV",        # Computer Vision
    "RL",        # Reinforcement Learning
    "SE",        # Software Engineering
    "DB",        # Database
    "HCI",       # Human-Computer Interaction
    "Security",  # Cybersecurity
    "Network",   # Computer Networks
    "IR",        # Information Retrieval
    "DM",        # Data Mining
    "KG",        # Knowledge Graph
    "Robotics",  # Robotics
    "General",   # 通用/未分类
]


def normalize_domain(domain: str) -> str:
    """
    标准化 domain 名称
    
    Args:
        domain: 原始 domain 名称
        
    Returns:
        标准化后的 domain 名称（大写）
    """
    if not domain:
        return "General"
    
    # 转大写并去除空格
    normalized = domain.strip().upper()
    
    # 常见别名映射
    alias_map = {
        "ARTIFICIAL INTELLIGENCE": "AI",
        "MACHINE LEARNING": "ML",
        "DEEP LEARNING": "DL",
        "NATURAL LANGUAGE PROCESSING": "NLP",
        "COMPUTER VISION": "CV",
        "REINFORCEMENT LEARNING": "RL",
        "SOFTWARE ENGINEERING": "SE",
        "DATABASE": "DB",
        "HUMAN COMPUTER INTERACTION": "HCI",
        "CYBERSECURITY": "Security",
        "INFORMATION RETRIEVAL": "IR",
        "DATA MINING": "DM",
        "KNOWLEDGE GRAPH": "KG",
    }
    
    return alias_map.get(normalized, normalized)


def get_all_supported_domains() -> list:
    """获取所有支持的研究领域列表"""
    return SUPPORTED_DOMAINS.copy()


def is_valid_domain(domain: str) -> bool:
    """检查 domain 是否有效"""
    normalized = normalize_domain(domain)
    return normalized in SUPPORTED_DOMAINS
