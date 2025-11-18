"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本信息
    APP_NAME: str = "TravelMate AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # LLM配置 (支持OpenAI和SambaNova)
    LLM_PROVIDER: str = "sambanova"  # "openai" or "sambanova"
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # SambaNova配置
    SAMBANOVA_API_KEY: str = ""
    SAMBANOVA_API_BASE: str = "https://api.sambanova.ai/v1"
    SAMBANOVA_MODEL: str = "Meta-Llama-3.1-8B-Instruct"
    
    # LLM参数
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    MAX_DIALOGUE_ROUNDS: int = 10
    
    # RAG配置
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    CHROMA_DB_PATH: str = "./data/vector_db/chroma"
    
    # 天气API
    WEATHER_API_KEY: str = ""
    
    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./travelmate.db"
    
    # 数据路径
    ATTRACTIONS_DATA_DIR: str = "./data/attractions"
    KNOWLEDGE_BASE_DIR: str = "./data/knowledge_base"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """CORS允许的来源"""
        return ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"  # 忽略.env中的额外字段


# 创建全局配置实例
settings = Settings()

