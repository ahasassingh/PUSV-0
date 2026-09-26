import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "CIVIC-AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./civic_ai.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    REFERENCE_VEHICLE: str = "PUSV-01"
    SW_VERSION: str = "PUSV-SW-0.1"
    MAX_VEHICLE_STATE_UPLOAD_BYTES: int = 5 * 1024 * 1024  # 5 MB
    MAX_REQUIREMENT_UPLOAD_MB: int = 10
    MAX_REQUIREMENT_UPLOAD_BYTES: int = 10 * 1024 * 1024  # 10 MB
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
