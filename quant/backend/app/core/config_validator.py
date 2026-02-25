"""
Environment configuration validator.

Validates all required environment variables at startup to prevent
runtime errors due to misconfiguration.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from enum import Enum
import re
from urllib.parse import urlparse

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfigStatus(str, Enum):
    """Configuration validation status"""
    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"
    WARNING = "warning"


class ConfigValidator:
    """
    Validates environment configuration at startup.
    
    Features:
    - Required vs optional validation
    - Format validation (URLs, keys, etc.)
    - Security checks
    - Environment-specific validation
    """
    
    def __init__(self, environment: str = "development"):
        """
        Initialize validator.
        
        Args:
            environment: Current environment (development/production/test)
        """
        self.environment = environment
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> bool:
        """
        Run all validations.
        
        Returns:
            True if all validations pass, False otherwise
        """
        logger.info(f"Starting configuration validation for {self.environment} environment")
        
        # Core validations
        self._validate_core_settings()
        self._validate_database()
        self._validate_security()
        self._validate_redis()
        
        # Environment-specific validations
        if self.environment == "production":
            self._validate_production()
        
        # Optional services
        self._validate_external_apis()
        self._validate_ai_providers()
        self._validate_monitoring()
        
        # Report results
        self._report_results()
        
        return len(self.errors) == 0
    
    def _validate_core_settings(self):
        """Validate core application settings."""
        # Required core settings
        required = {
            "PROJECT_NAME": str,
            "VERSION": str,
            "API_V1_STR": str,
            "ENVIRONMENT": ["development", "production", "test"],
        }
        
        for key, expected in required.items():
            value = os.getenv(key)
            
            if not value:
                self.errors.append(f"Missing required setting: {key}")
                continue
            
            if isinstance(expected, list):
                if value not in expected:
                    self.errors.append(
                        f"{key} must be one of {expected}, got '{value}'"
                    )
            elif expected == str and not value.strip():
                self.errors.append(f"{key} cannot be empty")
    
    def _validate_database(self):
        """Validate database configuration."""
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            self.errors.append("DATABASE_URL is required")
            return
        
        # Validate PostgreSQL URL format
        try:
            parsed = urlparse(db_url)
            
            if not parsed.scheme.startswith("postgresql"):
                self.errors.append(
                    f"DATABASE_URL must be PostgreSQL URL, got scheme '{parsed.scheme}'"
                )
            
            if not parsed.hostname:
                self.errors.append("DATABASE_URL missing hostname")
            
            if not parsed.path or parsed.path == "/":
                self.errors.append("DATABASE_URL missing database name")
            
            # Check for default passwords in production
            if self.environment == "production":
                if parsed.password == "quant_password":
                    self.errors.append(
                        "Default password detected in DATABASE_URL for production"
                    )
        
        except Exception as e:
            self.errors.append(f"Invalid DATABASE_URL format: {e}")
    
    def _validate_security(self):
        """Validate security settings."""
        # SECRET_KEY validation
        secret_key = os.getenv("SECRET_KEY")
        
        if not secret_key:
            self.errors.append("SECRET_KEY is required")
        elif len(secret_key) < 32:
            self.errors.append("SECRET_KEY must be at least 32 characters")
        else:
            # Check for insecure patterns
            insecure_patterns = [
                "your-secret-key",
                "change-this",
                "changeme",
                "secret",
                "password",
                "12345",
                "example",
                "test"
            ]
            
            secret_lower = secret_key.lower()
            for pattern in insecure_patterns:
                if pattern in secret_lower:
                    self.errors.append(
                        f"SECRET_KEY contains insecure pattern '{pattern}'"
                    )
                    break
            
            # Check entropy (simple check)
            if len(set(secret_key)) < 10:
                self.warnings.append(
                    "SECRET_KEY has low entropy, consider using more random characters"
                )
        
        # Algorithm validation
        algorithm = os.getenv("ALGORITHM", "HS256")
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        
        if algorithm not in valid_algorithms:
            self.errors.append(
                f"ALGORITHM must be one of {valid_algorithms}, got '{algorithm}'"
            )
        
        # Token expiry validation
        try:
            access_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            if access_expire < 5:
                self.warnings.append(
                    "ACCESS_TOKEN_EXPIRE_MINUTES is very short (<5 minutes)"
                )
            elif access_expire > 1440:
                self.warnings.append(
                    "ACCESS_TOKEN_EXPIRE_MINUTES is very long (>24 hours)"
                )
        except ValueError:
            self.errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer")
        
        try:
            refresh_expire = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
            if refresh_expire < 1:
                self.errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be at least 1")
            elif refresh_expire > 90:
                self.warnings.append(
                    "REFRESH_TOKEN_EXPIRE_DAYS is very long (>90 days)"
                )
        except ValueError:
            self.errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be an integer")
    
    def _validate_redis(self):
        """Validate Redis configuration."""
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            self.warnings.append(
                "REDIS_URL not configured, caching will be disabled"
            )
            return
        
        # Validate Redis URL format
        try:
            parsed = urlparse(redis_url)
            
            if parsed.scheme not in ["redis", "rediss"]:
                self.errors.append(
                    f"REDIS_URL must use redis:// or rediss:// scheme, got '{parsed.scheme}'"
                )
            
            if not parsed.hostname:
                self.errors.append("REDIS_URL missing hostname")
            
            # Warn about non-local Redis in development
            if self.environment == "development" and parsed.hostname not in ["localhost", "127.0.0.1"]:
                self.warnings.append(
                    f"Using remote Redis in development: {parsed.hostname}"
                )
        
        except Exception as e:
            self.errors.append(f"Invalid REDIS_URL format: {e}")
    
    def _validate_production(self):
        """Production-specific validations."""
        # DEBUG must be False
        debug = os.getenv("DEBUG", "false").lower()
        if debug in ["true", "1", "yes"]:
            self.errors.append("DEBUG must be False in production")
        
        # Sentry should be configured
        if not os.getenv("SENTRY_DSN"):
            self.warnings.append(
                "SENTRY_DSN not configured for production monitoring"
            )
        
        # CORS origins should be specific
        cors = os.getenv("BACKEND_CORS_ORIGINS", "")
        if "localhost" in cors or "127.0.0.1" in cors:
            self.warnings.append(
                "BACKEND_CORS_ORIGINS contains localhost in production"
            )
    
    def _validate_external_apis(self):
        """Validate external API configurations."""
        # These are optional but warn if missing
        optional_apis = {
            "POLYGON_API_KEY": "Polygon.io (stock data)",
            "ALPHA_VANTAGE_API_KEY": "Alpha Vantage (financial data)"
        }
        
        for key, service in optional_apis.items():
            if not os.getenv(key):
                self.warnings.append(
                    f"{key} not configured, {service} will be unavailable"
                )
    
    def _validate_ai_providers(self):
        """Validate AI provider configurations."""
        # Check if at least one AI provider is configured
        ai_providers = [
            "OPENROUTER_API_KEY",
            "DEEPSEEK_API_KEY",
            "HUGGINGFACE_API_KEY",
            "CLAUDE_API_KEY",
            "MOONSHOT_API_KEY",
            "SILICONFLOW_API_KEY",
            "REPLICATE_API_KEY",
            "FAL_AI_API_KEY",
            "GITHUB_MODELS_API_KEY",
            "CLOUDFLARE_API_KEY"
        ]
        
        configured_providers = [
            key for key in ai_providers
            if os.getenv(key)
        ]
        
        if not configured_providers:
            self.warnings.append(
                "No AI providers configured, ML features will be limited"
            )
        else:
            logger.info(f"Found {len(configured_providers)} configured AI providers")
        
        # Validate provider-specific settings
        for provider in configured_providers:
            base_name = provider.replace("_API_KEY", "")
            
            # Check if provider is enabled
            enabled_key = f"{base_name}_ENABLED"
            enabled = os.getenv(enabled_key, "true").lower()
            
            if enabled in ["false", "0", "no"]:
                self.warnings.append(
                    f"{provider} is configured but {enabled_key} is False"
                )
            
            # Check rate limits
            rate_limit_key = f"{base_name}_RATE_LIMIT"
            rate_limit = os.getenv(rate_limit_key)
            
            if rate_limit:
                try:
                    limit = int(rate_limit)
                    if limit < 1:
                        self.errors.append(f"{rate_limit_key} must be positive")
                except ValueError:
                    self.errors.append(f"{rate_limit_key} must be an integer")
    
    def _validate_monitoring(self):
        """Validate monitoring configuration."""
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if sentry_dsn:
            # Basic Sentry DSN validation
            if not sentry_dsn.startswith(("http://", "https://")):
                self.errors.append("SENTRY_DSN must be a valid URL")
            
            # Check environment tag
            sentry_env = os.getenv("SENTRY_ENVIRONMENT", self.environment)
            if sentry_env != self.environment:
                self.warnings.append(
                    f"SENTRY_ENVIRONMENT ({sentry_env}) doesn't match "
                    f"application environment ({self.environment})"
                )
    
    def _report_results(self):
        """Report validation results."""
        if self.errors:
            logger.error("Configuration validation failed:")
            for error in self.errors:
                logger.error(f"  ❌ {error}")
        
        if self.warnings:
            logger.warning("Configuration warnings:")
            for warning in self.warnings:
                logger.warning(f"  ⚠️  {warning}")
        
        if not self.errors and not self.warnings:
            logger.info("✅ Configuration validation passed")
        elif not self.errors:
            logger.info("✅ Configuration valid with warnings")


def validate_config_on_startup():
    """
    Validate configuration on application startup.
    
    Exits with error code if critical errors found.
    """
    environment = os.getenv("ENVIRONMENT", "development")
    validator = ConfigValidator(environment)
    
    if not validator.validate_all():
        logger.critical("Configuration validation failed - cannot start application")
        
        if environment == "production":
            # In production, fail hard on configuration errors
            sys.exit(1)
        else:
            # In development, allow startup with warnings
            logger.warning("Continuing startup in development mode despite errors")
    
    return True


def get_config_status() -> Dict[str, Any]:
    """
    Get current configuration status for health checks.
    
    Returns:
        Dictionary with configuration status
    """
    environment = os.getenv("ENVIRONMENT", "development")
    validator = ConfigValidator(environment)
    validator.validate_all()
    
    return {
        "environment": environment,
        "status": "error" if validator.errors else "ok",
        "errors": validator.errors,
        "warnings": validator.warnings,
        "error_count": len(validator.errors),
        "warning_count": len(validator.warnings)
    }