import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ContestMate API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    # Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY: str = "your-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-service-role-key"
    SUPABASE_JWT_SECRET: str = "your-jwt-secret"
    DATABASE_URL: str = ""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://contestmate.vercel.app"
    ]

    # Scraper settings
    SCRAPER_HEADLESS: bool = True
    SCRAPER_REQUEST_TIMEOUT: int = 15
    SCRAPER_INTERVAL_HOURS: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
