# backend/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    # FastAPI
    app_name: str = "Aforo API"
    debug: bool = True
    version: str = "1.0.0"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-prod")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"]
    
    # ML Model
    model_path: str = "models/yolov8n.pt"
    confidence_threshold: float = 0.5
    
    # Default Aforo Settings
    default_max_capacity: int = 10
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()

