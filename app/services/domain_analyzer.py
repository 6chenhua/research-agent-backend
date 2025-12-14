"""
Domain 分析服务

使用 LLM 分析论文 abstract，自动识别论文所属的研究领域。
这是 "加入图谱" 功能的核心组件。

使用方式：
    analyzer = DomainAnalyzer(llm_client)
    domains = await analyzer.analyze_domains(abstract)
    # domains: ["AI", "NLP"]
"""
import json
import logging
import re
from typing import List, Optional

from app.integrations.llm_client import LLMClient
from app.utils.group_id import SUPPORTED_DOMAINS

logger = logging.getLogger(__name__)


class DomainAnalyzer:
    """
    论文领域分析器
    
    使用 LLM 分析论文的 abstract，从预定义的领域列表中识别相关领域。
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化分析器
        
        Args:
            llm_client: LLM 客户端，如果为 None 则创建新实例
        """
        self.llm_client = llm_client or LLMClient()
    
    async def analyze_domains(
        self, 
        abstract: str,
        title: Optional[str] = None,
        max_domains: int = 3
    ) -> List[str]:
        """
        分析论文 abstract，识别研究领域
        
        Args:
            abstract: 论文摘要
            title: 论文标题（可选，用于辅助判断）
            max_domains: 最多返回的领域数量（默认 3）
            
        Returns:
            识别出的领域列表，如 ["AI", "NLP"]
            
        Example:
            >>> analyzer = DomainAnalyzer()
            >>> domains = await analyzer.analyze_domains(
            ...     abstract="We propose a novel attention mechanism for NLP tasks...",
            ...     title="Attention Is All You Need"
            ... )
            >>> print(domains)
            ["AI", "NLP", "DL"]
        """
        if not abstract or len(abstract.strip()) < 50:
            logger.warning("Abstract too short, returning default domain")
            return ["General"]
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(abstract, title, max_domains)
        
        try:
            # 调用 LLM
            response = await self.llm_client.chat(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 低温度以获得更确定的结果
                max_tokens=200
            )
            
            # 解析响应
            domains = self._parse_response(response)
            
            if not domains:
                logger.warning(f"Failed to parse domains from LLM response: {response}")
                return ["General"]
            
            logger.info(f"Analyzed domains: {domains}")
            return domains[:max_domains]
            
        except Exception as e:
            logger.error(f"Domain analysis failed: {e}")
            return ["General"]
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        domains_str = ", ".join(SUPPORTED_DOMAINS)
        
        return f"""You are a research paper classifier. Your task is to identify the research domains of academic papers based on their abstracts.

Available research domains:
{domains_str}

Domain descriptions:
- AI: Artificial Intelligence (general AI topics, reasoning, knowledge representation)
- ML: Machine Learning (learning algorithms, model training, optimization)
- DL: Deep Learning (neural networks, deep architectures)
- NLP: Natural Language Processing (text, language, speech)
- CV: Computer Vision (image, video, visual recognition)
- RL: Reinforcement Learning (agents, rewards, policies)
- SE: Software Engineering (software development, testing, maintenance)
- DB: Database (data storage, query processing, data management)
- HCI: Human-Computer Interaction (user interface, user experience)
- Security: Cybersecurity (encryption, privacy, security attacks)
- Network: Computer Networks (protocols, distributed systems)
- IR: Information Retrieval (search, ranking, recommendation)
- DM: Data Mining (pattern discovery, knowledge extraction)
- KG: Knowledge Graph (semantic web, ontology, graph databases)
- Robotics: Robotics (robot control, perception, planning)
- General: If no specific domain matches

Rules:
1. Select 1-3 domains that best describe the paper
2. Only use domains from the provided list
3. Prefer specific domains over general ones
4. If the paper is interdisciplinary, include multiple relevant domains
5. Return ONLY a JSON array, e.g., ["AI", "NLP"]"""

    def _build_analysis_prompt(
        self, 
        abstract: str, 
        title: Optional[str],
        max_domains: int
    ) -> str:
        """构建分析提示词"""
        prompt_parts = []
        
        if title:
            prompt_parts.append(f"Title: {title}")
        
        prompt_parts.append(f"Abstract: {abstract}")
        prompt_parts.append(f"\nIdentify up to {max_domains} research domains for this paper.")
        prompt_parts.append("Respond with a JSON array only, e.g., [\"AI\", \"NLP\"]")
        
        return "\n\n".join(prompt_parts)
    
    def _parse_response(self, response: str) -> List[str]:
        """
        解析 LLM 响应，提取领域列表
        
        Args:
            response: LLM 响应文本
            
        Returns:
            领域列表
        """
        if not response:
            return []
        
        # 尝试直接解析 JSON
        try:
            # 清理响应文本
            cleaned = response.strip()
            
            # 尝试找到 JSON 数组
            json_match = re.search(r'\[.*?\]', cleaned, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                domains = json.loads(json_str)
                
                if isinstance(domains, list):
                    # 验证并过滤有效的领域
                    valid_domains = []
                    for domain in domains:
                        if isinstance(domain, str):
                            normalized = self._normalize_domain(domain)
                            if normalized and normalized not in valid_domains:
                                valid_domains.append(normalized)
                    
                    return valid_domains
        except json.JSONDecodeError:
            pass
        
        # 如果 JSON 解析失败，尝试从文本中提取
        return self._extract_domains_from_text(response)
    
    def _normalize_domain(self, domain: str) -> Optional[str]:
        """
        标准化领域名称
        
        Args:
            domain: 原始领域名称
            
        Returns:
            标准化后的领域名称，如果无效则返回 None
        """
        if not domain:
            return None
        
        domain_upper = domain.strip().upper()
        
        # 直接匹配
        for supported in SUPPORTED_DOMAINS:
            if domain_upper == supported.upper():
                return supported
        
        # 别名映射
        aliases = {
            "ARTIFICIAL INTELLIGENCE": "AI",
            "MACHINE LEARNING": "ML",
            "DEEP LEARNING": "DL",
            "NATURAL LANGUAGE PROCESSING": "NLP",
            "COMPUTER VISION": "CV",
            "REINFORCEMENT LEARNING": "RL",
            "SOFTWARE ENGINEERING": "SE",
            "DATABASE": "DB",
            "DATABASES": "DB",
            "HUMAN COMPUTER INTERACTION": "HCI",
            "HUMAN-COMPUTER INTERACTION": "HCI",
            "CYBERSECURITY": "Security",
            "CYBER SECURITY": "Security",
            "INFORMATION RETRIEVAL": "IR",
            "DATA MINING": "DM",
            "KNOWLEDGE GRAPH": "KG",
            "KNOWLEDGE GRAPHS": "KG",
        }
        
        return aliases.get(domain_upper)
    
    def _extract_domains_from_text(self, text: str) -> List[str]:
        """
        从文本中提取领域（备用方法）
        
        Args:
            text: 包含领域信息的文本
            
        Returns:
            提取的领域列表
        """
        domains = []
        text_upper = text.upper()
        
        for domain in SUPPORTED_DOMAINS:
            if domain.upper() in text_upper:
                if domain not in domains:
                    domains.append(domain)
        
        return domains


# 便捷函数
async def analyze_paper_domains(
    abstract: str,
    title: Optional[str] = None,
    llm_client: Optional[LLMClient] = None
) -> List[str]:
    """
    分析论文领域的便捷函数
    
    Args:
        abstract: 论文摘要
        title: 论文标题（可选）
        llm_client: LLM 客户端（可选）
        
    Returns:
        领域列表
    """
    analyzer = DomainAnalyzer(llm_client)
    return await analyzer.analyze_domains(abstract, title)

