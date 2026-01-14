"""
Configuration settings for the backend application.
"""
import os
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "CoomerDL"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8080"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./downloads.db")
    
    # Storage
    storage_type: str = os.getenv("STORAGE_TYPE", "local")  # "local" or "gcs"
    gcs_bucket: Optional[str] = os.getenv("GCS_BUCKET")
    local_download_folder: str = os.getenv("DOWNLOAD_FOLDER", "./downloads")
    
    # Google Cloud
    google_cloud_project: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    # Redis (for session management)
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # CORS
    cors_origins: List[str] = ["*"]

    @field_validator("cors_origins", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
