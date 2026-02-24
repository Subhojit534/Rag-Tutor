"""
RAG Tutor Backend - Configuration Module
Files stored on disk, paths in MySQL.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "rag_tutor"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # File Storage (files on disk, paths in MySQL)
    UPLOAD_DIR: str = "./uploads"
    FAISS_INDEX_DIR: str = "./faiss_indexes"
    
    # AI Configuration (Google Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"
    
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
