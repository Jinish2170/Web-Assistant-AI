from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "DariusAI Web Assistant"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./darius_ai.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI/ML settings
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # File upload settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "txt", "docx", "xlsx", "csv", 
        "jpg", "jpeg", "png", "gif", "mp3", "wav"
    ]
    
    # Web scraping settings
    MAX_SCRAPE_PAGES: int = 10
    SCRAPE_TIMEOUT: int = 30
    
    # Voice settings
    TTS_ENGINE: str = "pyttsx3"  # or "openai" for better quality
    DEFAULT_VOICE_SPEED: int = 150
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
