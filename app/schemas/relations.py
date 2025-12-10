"""关系Schema定义"""

class RelationType:
    """关系类型枚举"""
    PROPOSES = "PROPOSES"  # Paper -> Method
    EVALUATES_ON = "EVALUATES_ON"  # Paper -> Dataset
    SOLVES = "SOLVES"  # Method -> Task
    IMPROVES_OVER = "IMPROVES_OVER"  # Method -> Method
    CITES = "CITES"  # Paper -> Paper
    USES_METRIC = "USES_METRIC"  # Paper -> Metric
    AUTHORED_BY = "AUTHORED_BY"  # Paper -> Author
    AFFILIATED_WITH = "AFFILIATED_WITH"  # Author -> Institution
    HAS_CONCEPT = "HAS_CONCEPT"  # Paper -> Concept
