"""
Configuration management for the tagging engine application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "Automated Content Tagging Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/tagging_db"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour

    # ML Models
    MULTI_LABEL_MODEL: str = "distilroberta-base"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    NER_MODEL: str = "en_core_web_sm"
    
    # Thresholds
    CLASSIFICATION_THRESHOLD: float = 0.5
    KEYBERT_MIN_SCORE: float = 0.3
    MAX_TAGS_PER_DOCUMENT: int = 20

    # API
    API_PREFIX: str = "/api/v1"
    WORKERS: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
