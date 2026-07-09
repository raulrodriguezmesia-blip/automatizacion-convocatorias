"""
Environment-based configuration for Convocatoria AI Engine.
Support for dev, staging, and production environments.
"""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Environment
    ENVIRONMENT: str = Field(default="development", alias="ENV")

    # Application
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")  # json or text

    # API Settings
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)

    # OpenAI/Azure OpenAI (for future integration)
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str | None = None
    OPENAI_API_VERSION: str | None = None
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")

    # Google Calendar
    GOOGLE_CREDENTIALS_PATH: str | None = None
    GOOGLE_CALENDAR_ID: str = Field(default="primary")

    # Slack
    SLACK_WEBHOOK_URL: str | None = None

    # Teams
    TEAMS_WEBHOOK_URL: str | None = None

    # Database
    DATABASE_URL: str | None = Field(default="sqlite:///data/convocatorias.db")

    # Redis (for caching and rate limiting)
    REDIS_URL: str | None = None

    # Circuit breaker settings
    CIRCUIT_FAILURE_THRESHOLD: int = Field(default=5)
    CIRCUIT_RECOVERY_TIMEOUT: float = Field(default=60.0)
    API_RETRY_ATTEMPTS: int = Field(default=3)
    API_RETRY_BACKOFF: float = Field(default=1.0)

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=60)  # seconds

    # Metrics
    METRICS_PORT: int = Field(default=8000)
    METRICS_PATH: str = Field(default="/metrics")

    # Security
    SECRET_KEY: str | None = None

    # Health check
    HEALTH_CHECK_TIMEOUT: float = Field(default=5.0)

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @model_validator(mode="after")
    def validate_environment(self):
        if self.ENVIRONMENT == "production":
            missing = []
            if not self.OPENAI_API_KEY and not self.GOOGLE_CREDENTIALS_PATH:
                missing.append("OPENAI_API_KEY or GOOGLE_CREDENTIALS_PATH")
            if not self.SECRET_KEY:
                missing.append("SECRET_KEY")

            if missing:
                # Log warning but don't fail - allow graceful degradation
                import logging

                logging.warning(f"Production environment may be missing required vars: {missing}")
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
