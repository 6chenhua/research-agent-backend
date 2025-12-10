"""Schema验证器"""

def validate_entity_type(entity_type: str) -> bool:
    """验证实体类型是否合法"""
    from app.core.constants import ENTITY_TYPES
    return entity_type in ENTITY_TYPES

def validate_relation_type(relation_type: str) -> bool:
    """验证关系类型是否合法"""
    from app.core.constants import RELATION_TYPES
    return relation_type in RELATION_TYPES
