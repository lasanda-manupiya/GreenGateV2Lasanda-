from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sustaingate.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Storage
    STORAGE_PATH: str = "./storage"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Seed data on startup. Keep True for demo/local; set False in production
    # after the first deploy so restarts don't keep re-running the seed.
    SEED_ON_STARTUP: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        """Normalise DATABASE_URL to an async-compatible SQLAlchemy URL.

        Railway/Heroku provide `postgres://...` or `postgresql://...` which
        SQLAlchemy's async engine cannot use directly. Rewrite to
        `postgresql+asyncpg://` so the same env var works in both local
        (SQLite) and deployed (Postgres) environments.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url


settings = Settings()
