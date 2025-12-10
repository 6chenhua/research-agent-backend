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
    "AFFILIATED_WITH",
    "HAS_CONCEPT",
]

# 搜索配置
DEFAULT_SEARCH_LIMIT = 10
SEARCH_THRESHOLD = 0.5

# 重排序模式
RERANK_MODES = ["rrf", "mmr", "cross_encoder", "node_distance"]

# 路径查询配置
MAX_PATH_LENGTH = 5
MAX_PATHS = 10
PATH_TIMEOUT = 5  # seconds
