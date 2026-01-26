"""Tests for configuration module."""

import os
import pytest
from pydantic import ValidationError


class TestSettings:
    """Tests for Settings class."""

    def test_settings_loaded(self):
        """Test that settings are loaded properly."""
        from app.core.config import settings

        assert settings is not None
        assert settings.PROJECT_NAME == "Quant Analytics Platform"
        assert settings.API_V1_STR == "/api/v1"

    def test_settings_secret_key_required(self):
        """Test that SECRET_KEY is required."""
        from app.core.config import settings

        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32

    def test_settings_algorithm(self):
        """Test algorithm setting."""
        from app.core.config import settings

        assert settings.ALGORITHM == "HS256"

    def test_settings_token_expiry(self):
        """Test token expiry settings are reasonable."""
        from app.core.config import settings

        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES >= 5
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 120
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS >= 1
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS <= 30

    def test_settings_database_url(self):
        """Test database URL is set."""
        from app.core.config import settings

        assert settings.DATABASE_URL is not None
        # In test environment, should be SQLite
        assert "sqlite" in settings.DATABASE_URL

    def test_settings_cors_origins(self):
        """Test CORS origins are set."""
        from app.core.config import settings

        assert settings.BACKEND_CORS_ORIGINS is not None
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)

    def test_settings_frontend_url(self):
        """Test frontend URL setting."""
        from app.core.config import settings

        assert hasattr(settings, "FRONTEND_URL")

    def test_settings_redis_config(self):
        """Test Redis configuration property."""
        from app.core.config import settings

        redis_config = settings.redis_config
        assert "host" in redis_config
        assert "port" in redis_config
        assert "db" in redis_config

    def test_async_database_url_postgresql(self):
        """Test async database URL conversion for PostgreSQL."""
        from app.core.config import Settings

        # Create a settings instance with PostgreSQL URL
        settings = Settings(
            SECRET_KEY="a" * 32,
            DATABASE_URL="postgresql://user:pass@localhost/db",
        )

        assert "asyncpg" in settings.async_database_url

    def test_async_database_url_sqlite(self):
        """Test async database URL for SQLite."""
        from app.core.config import Settings

        settings = Settings(
            SECRET_KEY="a" * 32,
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
        )

        # SQLite URL should remain unchanged
        assert settings.async_database_url == settings.DATABASE_URL


class TestSettingsValidation:
    """Tests for settings validation."""

    def test_secret_key_minimum_length(self):
        """Test SECRET_KEY minimum length validation."""
        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(SECRET_KEY="short")

    def test_secret_key_insecure_patterns(self):
        """Test SECRET_KEY rejects insecure patterns."""
        from app.core.config import Settings

        insecure_keys = [
            "your-secret-key-here-at-least-32-chars",
            "change-this-key-to-something-secure",
            "password123456789012345678901234",
        ]

        for key in insecure_keys:
            with pytest.raises(ValidationError):
                Settings(SECRET_KEY=key)

    def test_production_debug_validation(self):
        """Test that DEBUG must be False in production."""
        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(
                SECRET_KEY="a" * 32,
                ENVIRONMENT="production",
                DEBUG=True,
            )

    def test_production_password_validation(self):
        """Test that default password is rejected in production."""
        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(
                SECRET_KEY="a" * 32,
                ENVIRONMENT="production",
                DEBUG=False,
                POSTGRES_PASSWORD="quant_password",  # Default password
            )
