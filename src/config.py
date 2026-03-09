"""
Application configuration using Pydantic Settings.
"""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AutoFlow Finance Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins."""
        if isinstance(v, str):
            # Если строка начинается с [, парсим как JSON
            if v.startswith("["):
                import json
                return json.loads(v)
            # Иначе разбиваем по запятой
            return [i.strip() for i in v.split(",")]
        return v

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgresql+asyncpg://")
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format."""
        if not v:
            raise ValueError("REDIS_URL cannot be empty")
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    # Security
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def validate_celery_url(cls, v: str) -> str:
        """Validate Celery Redis URL format."""
        if not v:
            raise ValueError("Celery URL cannot be empty")
        if not v.startswith("redis://"):
            raise ValueError("Celery URL must start with redis://")
        return v

    # LLM
    LLM_PROVIDER: Literal["openai", "anthropic", "ollama"] = "openai"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    OLLAMA_BASE_URL: str | None = None

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # Telegram
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_WEBHOOK_URL: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

