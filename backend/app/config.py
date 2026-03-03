"""
RAG Tutor Backend - Configuration Module
Files stored on disk, paths in MySQL.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # JWT
    JWT_SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # File Storage (files on disk, paths in MySQL)
    UPLOAD_DIR: str = "./uploads"
    FAISS_INDEX_DIR: str = "./faiss_indexes"
    
    # AI Configuration
    OLLAMA_BASE_URL: str | None = None
    OLLAMA_MODEL: str | None = None
    BEDROCK_AWS_API: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str | None = None
    
    # Rate Limiting
    AI_RATE_LIMIT_PER_MINUTE: int = 10
    
    @property
    def DATABASE_URL(self) -> str:
        """MySQL connection URL for SQLAlchemy."""
        from urllib.parse import quote_plus
        return f"mysql+pymysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def uploads_path(self) -> Path:
        """Get uploads directory path, create if not exists."""
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def faiss_path(self) -> Path:
        """Get FAISS indexes directory path, create if not exists."""
        path = Path(self.FAISS_INDEX_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()