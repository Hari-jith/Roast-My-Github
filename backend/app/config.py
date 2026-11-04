"""Application configuration settings."""

from typing import List, Optional
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings loaded from environment or .env file."""

    GITHUB_TOKEN: Optional[str] = Field(default=None)
    CACHE_TTL_SECONDS: int = Field(default=300)
    MAX_REPOS: int = Field(
        default=100,
        validation_alias=AliasChoices("MAX_REPOS", "MAX_REPOS_TO_ANALYZE"),
    )
    PORT: int = Field(default=8000)
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
