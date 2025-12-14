"""
用户画像服务

负责分析用户行为，构建和更新用户画像，实现个性化功能。

用户画像数据存储在 users.preferences 字段中（JSON格式）。

个性化维度：
- research_interests: 研究兴趣（从 session domains 统计）
- expertise_level: 知识水平（从提问复杂度推断）
- frequently_asked_topics: 常问话题
- interaction_stats: 交互统计
"""
import json
import logging
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import User
from app.crud.user import UserRepository

logger = logging.getLogger(__name__)


# ==================== 用户画像结构 ====================

DEFAULT_PROFILE = {
    # 研究兴趣（domain: 出现次数）
    "research_interests": {},
    
    # 知识水平：beginner / intermediate / expert
    "expertise_level": "intermediate",
    
    # 偏好设置
    "preferred_depth": "normal",  # brief / normal / detailed
    "preferred_language": "zh-CN",
    
    # 常问话题（自动提取的关键词）
    "frequently_asked_topics": [],
    
    # 交互统计
    "interaction_stats": {
        "total_sessions": 0,
        "total_messages": 0,
        "total_papers": 0,
        "last_active_at": None,
    },
}


class ProfileService:
    """
    用户画像服务
    
    提供用户画像的读取、更新和分析功能。
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化服务
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像字典
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return DEFAULT_PROFILE.copy()
        
        # 从 preferences 中提取画像数据
        preferences = user.preferences or {}
        
        # 合并默认值
        profile = DEFAULT_PROFILE.copy()
        profile.update(preferences)
        
        return profile
    
    async def update_from_message(
        self,
        user_id: str,
        message: str,
        session_domains: List[str]
    ) -> Dict[str, Any]:
        """
        根据用户消息更新画像
        
        每次用户发送消息时调用此方法，分析消息内容并更新画像。
        
        Args:
            user_id: 用户ID
            message: 用户消息内容
            session_domains: 当前会话的研究领域
            
        Returns:
            更新后的用户画像
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found: {user_id}")
                return DEFAULT_PROFILE.copy()
            
            # 获取当前画像
            profile = user.preferences or DEFAULT_PROFILE.copy()
            
            # 1. 更新研究兴趣（基于 session domains）
            research_interests = profile.get("research_interests", {})
            for domain in session_domains:
                research_interests[domain] = research_interests.get(domain, 0) + 1
            profile["research_interests"] = research_interests
            
            # 2. 提取并更新常问话题
            topics = profile.get("frequently_asked_topics", [])
            new_keywords = self._extract_keywords(message)
            topics = self._update_topics(topics, new_keywords)
            profile["frequently_asked_topics"] = topics
            
            # 3. 推断知识水平（基于提问复杂度）
            expertise = self._infer_expertise(message, profile.get("expertise_level", "intermediate"))
            profile["expertise_level"] = expertise
            
            # 4. 更新交互统计
            stats = profile.get("interaction_stats", {})
            stats["total_messages"] = stats.get("total_messages", 0) + 1
            stats["last_active_at"] = datetime.utcnow().isoformat()
            profile["interaction_stats"] = stats
            
            # 5. 保存更新
            user.preferences = profile
            await self.user_repo.update(user)
            
            logger.debug(f"Updated profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return DEFAULT_PROFILE.copy()
    
    async def update_session_count(self, user_id: str) -> None:
        """
        更新用户的会话计数
        
        在创建新会话时调用。
        
        Args:
            user_id: 用户ID
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return
            
            profile = user.preferences or DEFAULT_PROFILE.copy()
            stats = profile.get("interaction_stats", {})
            stats["total_sessions"] = stats.get("total_sessions", 0) + 1
            profile["interaction_stats"] = stats
            
            user.preferences = profile
            await self.user_repo.update(user)
            
        except Exception as e:
            logger.error(f"Failed to update session count: {e}")
    
    async def update_paper_count(self, user_id: str, count: int = 1) -> None:
        """
        更新用户的论文计数
        
        在用户上传论文时调用。
        
        Args:
            user_id: 用户ID
            count: 新增论文数量
        """
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return
            
            profile = user.preferences or DEFAULT_PROFILE.copy()
            stats = profile.get("interaction_stats", {})
            stats["total_papers"] = stats.get("total_papers", 0) + count
            profile["interaction_stats"] = stats
            
            user.preferences = profile
            await self.user_repo.update(user)
            
        except Exception as e:
            logger.error(f"Failed to update paper count: {e}")
    
    def _extract_keywords(self, message: str, max_keywords: int = 5) -> List[str]:
        """
        从消息中提取关键词
        
        Args:
            message: 用户消息
            max_keywords: 最大关键词数量
            
        Returns:
            关键词列表
        """
        if not message:
            return []
        
        # 简单的关键词提取（后续可以用更复杂的 NLP 方法）
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', message)
        
        # 分词
        words = text.split()
        
        # 过滤短词和停用词
        stopwords = {
            # 中文停用词
            '的', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
            '好', '自己', '这', '那', '什么', '怎么', '为什么', '如何', '可以', '能',
            '吗', '呢', '啊', '了', '吧', '嗯', '哦',
            # 英文停用词
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
            'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'until', 'while', 'about', 'against', 'this', 'that',
            'these', 'those', 'what', 'which', 'who', 'whom', 'whose',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        }
        
        keywords = []
        for word in words:
            word_lower = word.lower()
            if len(word) >= 2 and word_lower not in stopwords:
                keywords.append(word_lower)
        
        # 取频率最高的关键词
        word_counts = Counter(keywords)
        top_keywords = [word for word, _ in word_counts.most_common(max_keywords)]
        
        return top_keywords
    
    def _update_topics(
        self, 
        existing_topics: List[Dict], 
        new_keywords: List[str],
        max_topics: int = 20
    ) -> List[Dict]:
        """
        更新常问话题列表
        
        Args:
            existing_topics: 现有话题列表
            new_keywords: 新提取的关键词
            max_topics: 最大话题数量
            
        Returns:
            更新后的话题列表
        """
        # 转换为字典以便更新
        topic_dict = {t["topic"]: t["count"] for t in existing_topics if isinstance(t, dict)}
        
        # 更新计数
        for keyword in new_keywords:
            topic_dict[keyword] = topic_dict.get(keyword, 0) + 1
        
        # 排序并截取
        sorted_topics = sorted(topic_dict.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"topic": topic, "count": count}
            for topic, count in sorted_topics[:max_topics]
        ]
    
    def _infer_expertise(self, message: str, current_level: str) -> str:
        """
        根据消息推断用户知识水平
        
        这是一个简化的启发式方法，可以后续用 LLM 或更复杂的分析替代。
        
        Args:
            message: 用户消息
            current_level: 当前知识水平
            
        Returns:
            推断的知识水平
        """
        # 专家级别指标
        expert_indicators = [
            # 学术术语
            'methodology', 'hypothesis', 'empirical', 'theoretical',
            'ablation', 'baseline', 'benchmark', 'sota', 'state-of-the-art',
            'gradient', 'backpropagation', 'optimization', 'convergence',
            'attention mechanism', 'transformer', 'embedding', 'latent space',
            '方法论', '假设', '实证', '理论', '消融', '基线', '梯度', '反向传播',
            '优化', '收敛', '注意力机制', '嵌入', '潜在空间',
        ]
        
        # 初学者级别指标
        beginner_indicators = [
            'what is', 'how to', 'explain', 'introduce', 'basic',
            'beginner', 'simple', 'easy', 'start', 'learn',
            '什么是', '怎么', '解释', '介绍', '基础', '入门', '简单', '学习',
            '请问', '帮我', '能不能',
        ]
        
        message_lower = message.lower()
        
        # 计算指标匹配
        expert_score = sum(1 for ind in expert_indicators if ind in message_lower)
        beginner_score = sum(1 for ind in beginner_indicators if ind in message_lower)
        
        # 基于分数调整级别
        if expert_score >= 2:
            return "expert"
        elif beginner_score >= 2:
            return "beginner"
        
        # 保持当前级别
        return current_level
    
    def build_personalization_context(self, profile: Dict[str, Any]) -> str:
        """
        构建个性化上下文（用于 LLM prompt）
        
        Args:
            profile: 用户画像
            
        Returns:
            个性化上下文字符串
        """
        expertise = profile.get("expertise_level", "intermediate")
        depth = profile.get("preferred_depth", "normal")
        
        # 获取主要研究兴趣
        interests = profile.get("research_interests", {})
        top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]
        interest_str = ", ".join([domain for domain, _ in top_interests]) if top_interests else "Not specified"
        
        # 获取常问话题
        topics = profile.get("frequently_asked_topics", [])
        top_topics = [t["topic"] for t in topics[:5]] if topics else []
        topics_str = ", ".join(top_topics) if top_topics else "Not specified"
        
        # 构建上下文
        context = f"""User Profile:
- Expertise Level: {expertise}
- Research Interests: {interest_str}
- Frequently Asked Topics: {topics_str}
- Preferred Response Depth: {depth}

Personalization Guidelines:
"""
        
        # 根据专业水平添加指导
        if expertise == "expert":
            context += "- User is an expert. Use technical terms freely, assume strong background knowledge.\n"
            context += "- Focus on advanced concepts, recent research, and nuanced discussions.\n"
        elif expertise == "beginner":
            context += "- User is a beginner. Explain concepts clearly, avoid jargon, use simple analogies.\n"
            context += "- Provide background context and foundational information.\n"
        else:
            context += "- User has intermediate knowledge. Balance technical accuracy with clarity.\n"
            context += "- Provide explanations when using advanced terminology.\n"
        
        # 根据深度偏好添加指导
        if depth == "brief":
            context += "- User prefers concise responses. Be direct and to the point.\n"
        elif depth == "detailed":
            context += "- User prefers detailed responses. Provide comprehensive explanations with examples.\n"
        
        return context


# ==================== 便捷函数 ====================

async def get_user_profile(session: AsyncSession, user_id: str) -> Dict[str, Any]:
    """获取用户画像的便捷函数"""
    service = ProfileService(session)
    return await service.get_user_profile(user_id)


async def update_profile_from_message(
    session: AsyncSession,
    user_id: str,
    message: str,
    session_domains: List[str]
) -> Dict[str, Any]:
    """更新用户画像的便捷函数"""
    service = ProfileService(session)
    return await service.update_from_message(user_id, message, session_domains)

