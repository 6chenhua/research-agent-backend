"""
Domain 前缀实体类型生成工具

提供根据研究领域（domain）动态生成 Graphiti 实体类型的功能。
实现 Domain 前缀实体类型方案的核心逻辑。

使用示例：
    # 摄入 AI 论文时
    entity_types = build_entity_types_for_domain("AI")
    # 返回: {"AI_Concept": ResearchConcept, "AI_Method": ResearchMethod, ...}
    
    # 搜索时根据 session domains 获取过滤标签
    labels = get_node_labels_for_domains(["AI", "ML"])
    # 返回: ["AI_Concept", "AI_Method", ..., "ML_Concept", "ML_Method", ...]
"""
from typing import Dict, List, Type, Optional
from pydantic import BaseModel

from app.schemas.graph_entities import (
    BASE_ENTITY_TYPES,
    BASE_EDGE_TYPES,
    DEFAULT_EDGE_TYPE_MAP,
)


# ==================== 支持的研究领域 ====================

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


def build_entity_types_for_domain(domain: str) -> Dict[str, Type[BaseModel]]:
    """
    为指定 domain 构建带前缀的 entity_types 字典
    
    Args:
        domain: 研究领域，如 "AI", "ML", "NLP"
        
    Returns:
        带 domain 前缀的实体类型字典
        例如: {"AI_Concept": ResearchConcept, "AI_Method": ResearchMethod, ...}
        
    Example:
        >>> entity_types = build_entity_types_for_domain("AI")
        >>> await graphiti.add_episode(..., entity_types=entity_types)
    """
    domain = normalize_domain(domain)
    
    return {
        f"{domain}_{type_name}": type_class
        for type_name, type_class in BASE_ENTITY_TYPES.items()
    }


def build_entity_types_for_domains(domains: List[str]) -> Dict[str, Type[BaseModel]]:
    """
    为多个 domains 构建 entity_types（合并所有 domain 的类型）
    
    Args:
        domains: 研究领域列表，如 ["AI", "ML"]
        
    Returns:
        合并后的实体类型字典
        
    Note:
        通常摄入论文时只需要单个 domain，此方法用于特殊场景
    """
    result = {}
    for domain in domains:
        result.update(build_entity_types_for_domain(domain))
    return result


def get_edge_types() -> Dict[str, Type[BaseModel]]:
    """
    获取边类型字典
    
    边类型不需要 domain 前缀，因为关系是通用的
    
    Returns:
        边类型字典
    """
    return BASE_EDGE_TYPES.copy()


def build_edge_type_map_for_domain(domain: str) -> Dict[tuple, List[str]]:
    """
    为指定 domain 构建边类型映射
    
    将默认的边类型映射转换为带 domain 前缀的版本
    
    Args:
        domain: 研究领域
        
    Returns:
        边类型映射字典
    """
    domain = normalize_domain(domain)
    result = {}
    
    for (source_type, target_type), edge_types in DEFAULT_EDGE_TYPE_MAP.items():
        # Entity 是通配符，保持不变
        if source_type == "Entity":
            new_source = "Entity"
        else:
            new_source = f"{domain}_{source_type}"
            
        if target_type == "Entity":
            new_target = "Entity"
        else:
            new_target = f"{domain}_{target_type}"
            
        result[(new_source, new_target)] = edge_types
    
    return result


def get_node_labels_for_domain(domain: str) -> List[str]:
    """
    获取单个 domain 对应的所有节点标签
    
    Args:
        domain: 研究领域
        
    Returns:
        节点标签列表，如 ["AI_Concept", "AI_Method", ...]
    """
    domain = normalize_domain(domain)
    return [f"{domain}_{type_name}" for type_name in BASE_ENTITY_TYPES.keys()]


def get_node_labels_for_domains(domains: List[str]) -> List[str]:
    """
    根据多个 domains 获取搜索时需要的 node_labels
    
    用于构建 SearchFilters，限制搜索范围在指定 domains 内
    
    Args:
        domains: 研究领域列表，如 ["AI", "ML"]
        
    Returns:
        所有相关的节点标签列表
        
    Example:
        >>> labels = get_node_labels_for_domains(["AI", "ML"])
        >>> search_filter = SearchFilters(node_labels=labels)
        >>> results = await graphiti.search(..., search_filter=search_filter)
    """
    if not domains:
        return []
    
    labels = []
    for domain in domains:
        labels.extend(get_node_labels_for_domain(domain))
    
    return labels


def get_all_supported_domains() -> List[str]:
    """
    获取所有支持的研究领域列表
    
    Returns:
        支持的 domain 列表
    """
    return SUPPORTED_DOMAINS.copy()


def is_valid_domain(domain: str) -> bool:
    """
    检查 domain 是否有效
    
    Args:
        domain: 待检查的 domain
        
    Returns:
        是否有效
    """
    normalized = normalize_domain(domain)
    return normalized in SUPPORTED_DOMAINS


def get_domain_from_label(label: str) -> Optional[str]:
    """
    从实体标签中提取 domain
    
    Args:
        label: 实体标签，如 "AI_Concept"
        
    Returns:
        domain 名称，如 "AI"；如果无法解析则返回 None
    """
    if "_" not in label:
        return None
    
    parts = label.split("_", 1)
    if len(parts) != 2:
        return None
    
    domain = parts[0]
    type_name = parts[1]
    
    # 验证 type_name 是否是已知的实体类型
    if type_name in BASE_ENTITY_TYPES:
        return domain
    
    return None


def get_entity_type_from_label(label: str) -> Optional[str]:
    """
    从实体标签中提取实体类型名
    
    Args:
        label: 实体标签，如 "AI_Concept"
        
    Returns:
        实体类型名，如 "Concept"；如果无法解析则返回 None
    """
    if "_" not in label:
        return None
    
    parts = label.split("_", 1)
    if len(parts) != 2:
        return None
    
    type_name = parts[1]
    
    if type_name in BASE_ENTITY_TYPES:
        return type_name
    
    return None

