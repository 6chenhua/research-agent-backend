"""命名空间管理服务"""
from app.core.constants import GLOBAL_NAMESPACE, USER_NAMESPACE_PREFIX

class NamespaceService:
    """图谱命名空间管理"""
    
    def get_user_namespace(self, user_id: str) -> str:
        """获取用户命名空间"""
        return f"{USER_NAMESPACE_PREFIX}{user_id}"
    
    def get_global_namespace(self) -> str:
        """获取全局命名空间"""
        return GLOBAL_NAMESPACE
    
    async def search_with_fallback(self, query: str, user_id: str):
        """
        多层级搜索：用户图谱 -> 全局图谱 -> 外部搜索
        TODO: 实现完整的fallback逻辑
        """
        pass
