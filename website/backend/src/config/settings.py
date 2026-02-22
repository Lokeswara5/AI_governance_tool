"""Configuration settings for the backend."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_governance.db")

    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]

    # File storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour

    # Analyzer settings
    MIN_COMPLIANCE_SCORE: float = 0.6
    ENABLE_PROXIMITY_ANALYSIS: bool = True

    class Config:
        env_file = ".env"

settings = Settings()