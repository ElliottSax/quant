"""Application configuration."""

from typing import Any
from urllib.parse import urlparse
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # Application
    PROJECT_NAME: str = "Quant Analytics Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "quant_user"
    POSTGRES_PASSWORD: str = "quant_password"
    POSTGRES_DB: str = "quant_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ML_URL: str = "redis://localhost:6380/0"  # For ML caching

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # External APIs
    POLYGON_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate SECRET_KEY is secure."""
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")

        # Check for common insecure patterns
        insecure_patterns = [
            "your-secret-key",
            "change-this",
            "changeme",
            "secret",
            "password",
            "12345",
        ]

        v_lower = v.lower()
        for pattern in insecure_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"SECRET_KEY contains insecure pattern '{pattern}'. "
                    "Please use a cryptographically random key."
                )

        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate production-specific settings."""
        if self.ENVIRONMENT == "production":
            # Ensure DEBUG is disabled in production
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")

            # Ensure default passwords aren't used in production
            if self.POSTGRES_PASSWORD == "quant_password":
                raise ValueError(
                    "Default POSTGRES_PASSWORD detected. "
                    "Please set a secure password in production."
                )

            # Ensure CORS is properly configured
            if "*" in self.BACKEND_CORS_ORIGINS:
                raise ValueError(
                    "Wildcard CORS origins not allowed in production"
                )

        return self

    @property
    def async_database_url(self) -> str:
        """Get async database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def redis_config(self) -> dict:
        """Parse Redis URL into connection params."""
        parsed = urlparse(self.REDIS_URL)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "decode_responses": True
        }

    @property
    def redis_ml_config(self) -> dict:
        """Parse Redis ML URL into connection params."""
        parsed = urlparse(self.REDIS_ML_URL)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6380,
            "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
            "password": parsed.password,
            "decode_responses": False  # ML cache uses pickle
        }


settings = Settings()
