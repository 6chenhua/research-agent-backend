from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Global backend configuration loaded from environment variables."""

    # Neo4j配置
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Graphiti配置
    BASE_URL: str
    GRAPHITI_API_KEY: str
    
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str = "research_agent"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # PRD要求：30分钟
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # PRD要求：7天
    
    # OpenAI/LLM配置
    # LLM_BASE_URL默认使用BASE_URL，如果有独立的LLM服务则单独配置
    LLM_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"
    
    # 应用配置
    DEBUG: bool = False
    APP_NAME: str = "AI Research Agent"
    APP_VERSION: str = "1.0.0"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "temp/uploads"
    
    # arXiv配置
    ARXIV_MAX_RESULTS: int = 10
    
    # Semantic Scholar配置
    S2_API_KEY: Optional[str] = None
    
    # Embedding配置
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Configuration for Pydantic V2
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
