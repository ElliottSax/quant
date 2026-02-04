"""Application configuration."""

from typing import Any
from urllib.parse import urlparse
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CacheSettings(BaseSettings):
    """Cache configuration settings."""

    # Default cache TTL values (in seconds)
    DEFAULT_TTL: int = 3600  # 1 hour
    FOURIER_ANALYSIS_TTL: int = 1800  # 30 minutes
    PATTERN_ANALYSIS_TTL: int = 3600  # 1 hour
    MARKET_DATA_TTL: int = 300  # 5 minutes
    STATS_SHORT_TTL: int = 300  # 5 minutes (7d data)
    STATS_LONG_TTL: int = 3600  # 1 hour (90d, 1y data)
    PREMIUM_PATTERNS_TTL: int = 1800  # 30 minutes
    CONGRESSIONAL_SCRAPER_TTL: int = 3600  # 1 hour
    API_KEY_CACHE_TTL: int = 300  # 5 minutes
    QUERY_CACHE_TTL: int = 300  # 5 minutes
    MOBILE_SYNC_CACHE_TTL: int = 3600  # 1 hour
    ANALYTICS_ENSEMBLE_TTL: int = 3600  # 1 hour

    # Cache control settings
    HTTP_CACHE_MAX_AGE: int = 300  # 5 minutes for HTTP ETag caching
    CORS_PREFLIGHT_MAX_AGE: int = 3600  # 1 hour for CORS preflight
    CSRF_TOKEN_MAX_AGE: int = 3600  # 1 hour for CSRF tokens


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration settings."""

    # Per-tier rate limits (requests per minute)
    FREE_TIER_RPM: int = 20
    BASIC_TIER_RPM: int = 60
    PREMIUM_TIER_RPM: int = 200

    # Per-tier hourly limits
    FREE_TIER_RPH: int = 500
    BASIC_TIER_RPH: int = 2000
    PREMIUM_TIER_RPH: int = 10000

    # Endpoint-specific limits (requests per minute)
    ANALYTICS_ENSEMBLE_LIMIT: int = 10
    ANALYTICS_NETWORK_LIMIT: int = 5
    EXPORT_LIMIT: int = 20
    AUTH_LOGIN_LIMIT: int = 5
    AUTH_REGISTER_LIMIT: int = 3

    # General rate limiting
    DEFAULT_REQUESTS_PER_MINUTE: int = 60
    DEFAULT_REQUESTS_PER_HOUR: int = 1000

    # Anonymous/IP-based limit
    IP_LIMIT_MAX: int = 30

    # Window settings
    RATE_LIMIT_WINDOW_SECONDS: int = 60


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    # Account lockout settings
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30

    # Retry and timeout settings
    DEFAULT_RETRY_COUNT: int = 3
    DEFAULT_TIMEOUT_SECONDS: int = 30

    # Database pool timeout
    DB_POOL_TIMEOUT_SECONDS: int = 30


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    # Connection pool settings (PostgreSQL)
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 40
    POOL_RECYCLE_SECONDS: int = 3600  # 1 hour

    # Query optimization
    DEFAULT_QUERY_CHUNK_SIZE: int = 1000


class PerformanceSettings(BaseSettings):
    """Performance and optimization settings."""

    # Compression settings
    MIN_COMPRESS_SIZE_BYTES: int = 500
    GZIP_COMPRESSION_LEVEL: int = 6

    # Request cleanup intervals
    RATE_LIMIT_CLEANUP_INTERVAL_SECONDS: int = 300  # 5 minutes

    # ML/AI settings
    DEFAULT_MAX_TOKENS: int = 1000
    ML_TASK_TIME_LIMIT_SECONDS: int = 14400  # 4 hours
    ML_TASK_SOFT_TIME_LIMIT_SECONDS: int = 10800  # 3 hours

    # Market data intervals (in seconds)
    MARKET_INTERVAL_5MIN: int = 300
    MARKET_INTERVAL_30MIN: int = 1800
    MARKET_INTERVAL_1HOUR: int = 3600

    # Backtesting and simulation defaults
    DEFAULT_NUM_SIMULATIONS: int = 10000
    DEFAULT_INITIAL_CAPITAL: float = 10000.0
    MIN_TRADES_FOR_ANALYSIS: int = 50

    # Mobile sync settings
    MOBILE_SYNC_INTERVAL_SECONDS: int = 300  # 5 minutes


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

    # Configuration sub-settings
    # These can be overridden via environment variables with prefix
    # e.g., CACHE_DEFAULT_TTL=7200
    cache: CacheSettings = CacheSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    security: SecuritySettings = SecuritySettings()
    database: DatabaseSettings = DatabaseSettings()
    performance: PerformanceSettings = PerformanceSettings()

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./quant_dev.db"
    POSTGRES_USER: str = "quant_user"
    POSTGRES_PASSWORD: str = "quant_password"
    POSTGRES_DB: str = "quant_db"

    # Redis (optional for development)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ML_URL: str = "redis://localhost:6380/0"  # For ML caching
    REDIS_ENABLED: bool = True  # Set to False if Redis not available

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # External Market Data APIs
    POLYGON_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    IEX_API_KEY: str = ""
    NEWSAPI_KEY: str = ""  # NewsAPI.org for news sentiment

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    # Alerting
    SLACK_WEBHOOK_URL: str = ""
    ALERT_WEBHOOK_URL: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Frontend URL (for email links, etc.)
    FRONTEND_URL: str = "http://localhost:3000"

    # Email Configuration
    RESEND_API_KEY: str = ""
    EMAIL_DOMAIN: str = "example.com"
    ALERT_EMAIL: str = ""  # Comma-separated list of emails for alerts
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Trusted Proxies (for X-Forwarded-For header validation)
    # Add your load balancer/proxy IPs here in production
    TRUSTED_PROXIES: list[str] = [
        "127.0.0.1",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]
    TRUST_PROXY_HEADERS: bool = False  # Set to True only behind trusted proxy

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
        if self.DATABASE_URL.startswith("sqlite"):
            # SQLite URLs are already async-compatible with aiosqlite
            return self.DATABASE_URL
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
            "decode_responses": True  # ML cache uses JSON serialization
        }


settings = Settings()
