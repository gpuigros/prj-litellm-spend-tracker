"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import List

from pydantic import Field, model_validator
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
    # Optional discrete DB connection parts. When DB_HOST is set, these
    # take precedence over DATABASE_URL so the LiteLLM RDS host can be
    # configured without embedding credentials in a single URL string.
    db_host: str = Field(default="", description="Database host (overrides DATABASE_URL host)")
    db_user: str = Field(default="", description="Database user (overrides DATABASE_URL user)")
    db_password: str = Field(
        default="", description="Database password (overrides DATABASE_URL password)"
    )

    # LiteLLM master key (management endpoints)
    litellm_master_key: str = Field(
        default="",
        description="LiteLLM master key used to authenticate management endpoints",
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

    @model_validator(mode="after")
    def _assemble_database_url(self) -> "Settings":
        """Build DATABASE_URL from DB_HOST/DB_USER/DB_PASSWORD when present.

        When ``DB_HOST`` is set, the discrete parts take precedence over
        the literal ``DATABASE_URL`` value. This lets the LiteLLM RDS
        host be configured via separate env vars without embedding the
        password inside the URL string. The ``DB_HOST`` value may
        already include a ``:port`` suffix.
        """
        if not self.db_host:
            return self

        host = self.db_host
        user = self.db_user or "litellm"
        password = self.db_password
        # database_url default already carries the asyncpg driver prefix;
        # preserve whatever driver the user configured, defaulting to asyncpg.
        scheme = "postgresql+asyncpg"
        self.database_url = f"{scheme}://{user}:{password}@{host}/litellm"
        return self


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()
