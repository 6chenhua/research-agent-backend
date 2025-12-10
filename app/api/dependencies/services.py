"""服务依赖注入"""
from app.services.agent_service import AgentService
from app.services.graph_service import GraphService

def get_agent_service():
    """获取Agent服务实例"""
    return AgentService()

def get_graph_service():
    """获取图谱服务实例"""
    return GraphService()
