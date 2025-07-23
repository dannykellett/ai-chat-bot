"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "your-secret-key-here"

    # OpenAI
    openai_api_key: str = "sk-your-api-key-here"
    openai_model: str = "gpt-4o-mini"

    # Database
    database_url: str = "sqlite:///./chatbot.db"

    # CORS - Keep as simple string and convert in property
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8501",
        validation_alias="ALLOWED_ORIGINS",
    )

    # File Upload
    max_file_size_mb: int = 10
    allowed_file_types_str: str = Field(
        default="txt,md,pdf,py,js,ts,jsx,tsx", validation_alias="ALLOWED_FILE_TYPES"
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Get allowed origins as list."""
        return [
            origin.strip()
            for origin in self.allowed_origins_str.split(",")
            if origin.strip()
        ]

    @property
    def allowed_file_types(self) -> list[str]:
        """Get allowed file types as list."""
        return [
            file_type.strip()
            for file_type in self.allowed_file_types_str.split(",")
            if file_type.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
