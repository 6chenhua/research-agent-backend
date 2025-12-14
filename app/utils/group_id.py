"""
Group ID 构建工具函数

用于构建 Graphiti 知识图谱的命名空间标识符。

架构设计（简化版）：
1. 公共领域图谱：domain:{domain} - 所有用户共享，论文知识
2. 用户私有笔记：user:{user_id}:notes - 用户私有，消息/笔记

所有论文都进入公共图谱，实现知识共享和集体智慧。
用户可选择将消息/回复添加到私有笔记图谱。
"""
from typing import List, Optional


# ==================== 支持的研究领域 ====================

SUPPORTED_DOMAINS = [
    "AI",       # Artificial Intelligence
    "ML",       # Machine Learning
    "DL",       # Deep Learning
    "NLP",      # Natural Language Processing
    "CV",       # Computer Vision
    "SE",       # Software Engineering
    "DB",       # Database
    "HCI",      # Human-Computer Interaction
    "Security", # Cybersecurity
    "Network",  # Computer Networks
    "IR",       # Information Retrieval
    "KG",       # Knowledge Graph
    "RL",       # Reinforcement Learning
    "Robotics", # Robotics
    "Graphics", # Computer Graphics
    "General",  # 通用/未分类
]


# ==================== 公共领域图谱 ====================

def get_domain_group_id(domain: str) -> str:
    """
    获取公共领域图谱的 group_id
    
    所有用户共享的领域知识空间。
    
    Args:
        domain: 研究领域
        
    Returns:
        格式: "domain:{domain}"
        
    Example:
        get_domain_group_id("AI") → "domain:ai"
    """
    return f"domain:{domain.lower()}"


def get_domain_group_ids(domains: List[str]) -> List[str]:
    """
    获取多个领域的 group_ids
    
    Args:
        domains: 研究领域列表
        
    Returns:
        group_ids 列表
        
    Example:
        get_domain_group_ids(["AI", "NLP"]) → ["domain:ai", "domain:nlp"]
    """
    if not domains:
        return [get_domain_group_id("General")]
    
    return [get_domain_group_id(d) for d in domains]


# ==================== 用户私有笔记图谱 ====================

def get_user_notes_group_id(user_id: str) -> str:
    """
    获取用户私有笔记的 group_id
    
    存储用户主动添加的消息/回复/笔记。
    
    Args:
        user_id: 用户ID
        
    Returns:
        格式: "user:{user_id}:notes"
        
    Example:
        get_user_notes_group_id("user_123") → "user:user_123:notes"
    """
    return f"user:{user_id}:notes"


# ==================== 搜索时的 Group ID 构建 ====================

def get_search_group_ids(
    user_id: str,
    domains: List[str],
    include_user_notes: bool = True
) -> List[str]:
    """
    构建搜索时需要的 group_ids
    
    搜索公共领域图谱 + 可选的用户私有笔记。
    
    Args:
        user_id: 用户ID
        domains: 研究领域列表
        include_user_notes: 是否包含用户私有笔记（默认 True）
        
    Returns:
        group_ids 列表
        
    Example:
        get_search_group_ids("user_123", ["AI", "NLP"])
        → ["domain:ai", "domain:nlp", "user:user_123:notes"]
    """
    group_ids = get_domain_group_ids(domains)
    
    # 可选：包含用户私有笔记
    if include_user_notes:
        group_ids.append(get_user_notes_group_id(user_id))
    
    return group_ids


# ==================== 摄入时的 Group ID 构建 ====================

def get_paper_ingest_group_ids(domains: List[str]) -> List[str]:
    """
    构建论文摄入时需要的 group_ids
    
    所有论文都进入公共领域图谱（不区分用户）。
    
    Args:
        domains: 论文领域列表
        
    Returns:
        group_ids 列表
        
    Example:
        get_paper_ingest_group_ids(["AI", "SE"])
        → ["domain:ai", "domain:se"]
    """
    return get_domain_group_ids(domains)


def get_notes_ingest_group_id(user_id: str) -> str:
    """
    获取用户笔记摄入时的 group_id
    
    用户消息/回复添加到私有笔记图谱。
    
    Args:
        user_id: 用户ID
        
    Returns:
        group_id
    """
    return get_user_notes_group_id(user_id)


# ==================== 领域标准化 ====================

def normalize_domain(domain: str) -> str:
    """
    标准化领域名称
    
    Args:
        domain: 原始领域名称
        
    Returns:
        标准化后的领域名称（大写）
    """
    if not domain:
        return "General"
    
    domain_upper = domain.upper().strip()
    
    # 常见别名映射
    aliases = {
        "ARTIFICIAL_INTELLIGENCE": "AI",
        "ARTIFICIAL INTELLIGENCE": "AI",
        "MACHINE_LEARNING": "ML",
        "MACHINE LEARNING": "ML",
        "DEEP_LEARNING": "DL",
        "DEEP LEARNING": "DL",
        "NATURAL_LANGUAGE_PROCESSING": "NLP",
        "NATURAL LANGUAGE PROCESSING": "NLP",
        "COMPUTER_VISION": "CV",
        "COMPUTER VISION": "CV",
        "SOFTWARE_ENGINEERING": "SE",
        "SOFTWARE ENGINEERING": "SE",
        "DATABASE": "DB",
        "DATABASES": "DB",
        "HUMAN_COMPUTER_INTERACTION": "HCI",
        "HUMAN COMPUTER INTERACTION": "HCI",
        "HUMAN-COMPUTER INTERACTION": "HCI",
        "CYBERSECURITY": "Security",
        "CYBER SECURITY": "Security",
        "INFORMATION_RETRIEVAL": "IR",
        "INFORMATION RETRIEVAL": "IR",
        "KNOWLEDGE_GRAPH": "KG",
        "KNOWLEDGE_GRAPHS": "KG",
        "KNOWLEDGE GRAPH": "KG",
        "REINFORCEMENT_LEARNING": "RL",
        "REINFORCEMENT LEARNING": "RL",
    }
    
    return aliases.get(domain_upper, domain_upper)


def validate_domains(domains: List[str]) -> List[str]:
    """
    验证并标准化领域列表
    
    Args:
        domains: 原始领域列表
        
    Returns:
        标准化后的领域列表（去重）
    """
    if not domains:
        return ["General"]
    
    normalized = []
    seen = set()
    
    for domain in domains:
        norm = normalize_domain(domain)
        if norm not in seen:
            normalized.append(norm)
            seen.add(norm)
    
    return normalized


def is_valid_domain(domain: str) -> bool:
    """
    检查领域是否在支持列表中
    
    Args:
        domain: 领域名称
        
    Returns:
        是否有效
    """
    norm = normalize_domain(domain)
    return norm in SUPPORTED_DOMAINS
