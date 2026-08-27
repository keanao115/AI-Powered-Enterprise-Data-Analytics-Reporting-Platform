import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-super-secret-key-in-production-min-32-chars-long!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    ANALYTICS_DATABASE_URL: str = "duckdb:///./analytics_demo.duckdb"

    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-3.1-flash-lite-preview"
    GEMINI_API_KEY: Optional[str] = "AQ.Ab8RN6Lvapi3koHifCNG3P7CgIpsUgih4bgMPRaoPoONcVSLTw"
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ALLOW_EXTERNAL_LLM_DATA: bool = True

    MAX_QUERY_ROWS: int = 10000
    MAX_QUERY_SECONDS: int = 30
    MAX_SANDBOX_SECONDS: int = 15
    MAX_EXPORT_ROWS: int = 50000
    AI_DAILY_BUDGET_USD: float = 50.0

    ENABLE_SANDBOX: bool = True
    ENABLE_REPORTS: bool = True
    ENABLE_EXPORTS: bool = True
    ENABLE_MULTI_TENANCY: bool = True
    ENABLE_PII_FIREWALL: bool = True
    ENABLE_GROUNDING_VALIDATOR: bool = True

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3300",
        "http://127.0.0.1:3300",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


settings = Settings()
