"""Schema验证器
提供实体和关系的验证功能，确保知识图谱数据的一致性
"""
from typing import Tuple, Optional
from app.core.constants import ENTITY_TYPES, RELATION_TYPES


def validate_entity_type(entity_type: str) -> bool:
    """验证实体类型是否合法
    
    Args:
        entity_type: 实体类型字符串
        
    Returns:
        bool: 是否为有效的实体类型
        
    Example:
        >>> validate_entity_type("Paper")
        True
        >>> validate_entity_type("InvalidType")
        False
    """
    return entity_type in ENTITY_TYPES


def validate_relation_type(relation_type: str) -> bool:
    """验证关系类型是否合法
    
    Args:
        relation_type: 关系类型字符串
        
    Returns:
        bool: 是否为有效的关系类型
        
    Example:
        >>> validate_relation_type("PROPOSES")
        True
        >>> validate_relation_type("INVALID_RELATION")
        False
    """
    return relation_type in RELATION_TYPES


def validate_relation_constraint(
    relation_type: str, 
    source_type: str, 
    target_type: str
) -> Tuple[bool, Optional[str]]:
    """验证关系的源和目标实体类型约束
    
    确保关系连接的实体类型符合领域规范。
    例如：PROPOSES关系必须从Paper指向Method
    
    Args:
        relation_type: 关系类型
        source_type: 源实体类型
        target_type: 目标实体类型
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        
    Example:
        >>> validate_relation_constraint("PROPOSES", "Paper", "Method")
        (True, None)
        >>> validate_relation_constraint("PROPOSES", "Paper", "Dataset")
        (False, "PROPOSES requires source=Paper, target=Method")
    """
    from app.schemas.relations import RELATION_CONSTRAINTS
    
    if relation_type not in RELATION_CONSTRAINTS:
        return False, f"Unknown relation type: {relation_type}"
    
    expected_source, expected_target = RELATION_CONSTRAINTS[relation_type]
    
    if source_type != expected_source or target_type != expected_target:
        return False, (
            f"{relation_type} requires source={expected_source}, target={expected_target}, "
            f"got source={source_type}, target={target_type}"
        )
    
    return True, None


def validate_uuid(uuid: str) -> bool:
    """验证UUID格式
    
    Args:
        uuid: UUID字符串
        
    Returns:
        bool: 是否为有效的UUID格式
    """
    if not uuid or not isinstance(uuid, str):
        return False
    # 简单验证：非空且长度合理
    return len(uuid) > 0 and len(uuid) < 100


def validate_arxiv_id(arxiv_id: str) -> bool:
    """验证arXiv ID格式
    
    Args:
        arxiv_id: arXiv ID字符串（如：2103.14030 或 1706.03762v2）
        
    Returns:
        bool: 是否为有效的arXiv ID
        
    Example:
        >>> validate_arxiv_id("2103.14030")
        True
        >>> validate_arxiv_id("1706.03762v2")
        True
        >>> validate_arxiv_id("invalid")
        False
    """
    import re
    if not arxiv_id:
        return False
    # arXiv ID格式：YYMM.NNNNN 或 YYMM.NNNNNvN
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    return bool(re.match(pattern, arxiv_id))


def validate_year(year: int) -> bool:
    """验证年份是否合理
    
    Args:
        year: 年份整数
        
    Returns:
        bool: 年份是否在合理范围内（1900-2100）
    """
    return 1900 <= year <= 2100


def validate_weight(weight: float) -> bool:
    """验证权重值是否在有效范围
    
    Args:
        weight: 权重浮点数
        
    Returns:
        bool: 权重是否在 [0, 1] 范围内
    """
    return 0.0 <= weight <= 1.0
