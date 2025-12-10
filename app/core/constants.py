"""常量定义"""

# 图谱命名空间
GLOBAL_NAMESPACE = "global"
USER_NAMESPACE_PREFIX = "user:"

# 实体类型
ENTITY_TYPES = [
    "Paper",
    "Method",
    "Task",
    "Dataset",
    "Metric",
    "Author",
    "Institution",
    "Concept",
]

# 关系类型
RELATION_TYPES = [
    "PROPOSES",
    "EVALUATES_ON",
    "SOLVES",
    "IMPROVES_OVER",
    "CITES",
    "USES_METRIC",
    "AUTHORED_BY",
]

# 搜索配置
DEFAULT_SEARCH_LIMIT = 10
SEARCH_THRESHOLD = 0.5
