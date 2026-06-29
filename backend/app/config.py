"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="LLM Spend API", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://litellm:litellm@localhost:5432/litellm",
        description="Async database URL for LiteLLM database",
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "vscode-webview://*"],
        description="Allowed CORS origins",
    )

    # Cache (optional)
    redis_url: str = Field(default="", description="Redis URL for caching (optional)")

    # Budget defaults
    default_monthly_budget: float = Field(
        default=25.0, description="Default monthly budget in currency units"
    )
    default_currency: str = Field(default="EUR", description="Default currency code")
    budget_warning_threshold: float = Field(
        default=80.0, description="Budget warning threshold percentage"
    )
    budget_exceeded_threshold: float = Field(
        default=100.0, description="Budget exceeded threshold percentage"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()
