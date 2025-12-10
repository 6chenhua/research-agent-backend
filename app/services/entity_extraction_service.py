"""实体抽取服务"""

class EntityExtractionService:
    """LLM实体和关系抽取"""
    
    async def extract_entities_from_text(self, text: str):
        """从文本中抽取实体"""
        # TODO: 使用LLM抽取实体
        pass
    
    async def extract_relations_from_text(self, text: str):
        """从文本中抽取关系"""
        # TODO: 使用LLM抽取关系
        pass
    
    async def normalize_entity(self, entity: dict):
        """实体归一化"""
        # TODO: 使用embedding相似度匹配
        pass
