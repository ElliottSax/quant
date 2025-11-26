"""
AI Provider Configuration

Centralized configuration for all AI providers.
Supports environment variables and secure key management.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import os


class ProviderConfig(BaseModel):
    """Configuration for a single provider"""
    enabled: bool = True
    api_key: Optional[str] = None
    rate_limit_rpm: int = 60
    timeout: int = 30
    max_retries: int = 3
    priority: int = 100  # Lower = higher priority
    metadata: Dict = {}


class AIProvidersConfig(BaseSettings):
    """Global AI providers configuration"""

    # DeepSeek
    DEEPSEEK_ENABLED: bool = True
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_RATE_LIMIT: int = 60
    DEEPSEEK_PRIORITY: int = 10

    # Hugging Face
    HUGGINGFACE_ENABLED: bool = True
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_RATE_LIMIT: int = 100
    HUGGINGFACE_PRIORITY: int = 50

    # OpenRouter
    OPENROUTER_ENABLED: bool = True
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_RATE_LIMIT: int = 60
    OPENROUTER_PRIORITY: int = 5

    # Google Cloud
    GOOGLE_CLOUD_ENABLED: bool = False
    GOOGLE_CLOUD_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_CLOUD_PRIORITY: int = 15

    # Moonshot
    MOONSHOT_ENABLED: bool = True
    MOONSHOT_API_KEY: Optional[str] = None
    MOONSHOT_RATE_LIMIT: int = 60
    MOONSHOT_PRIORITY: int = 30

    # SiliconFlow
    SILICONFLOW_ENABLED: bool = True
    SILICONFLOW_API_KEY: Optional[str] = None
    SILICONFLOW_RATE_LIMIT: int = 100
    SILICONFLOW_PRIORITY: int = 40

    # Replicate
    REPLICATE_ENABLED: bool = True
    REPLICATE_API_KEY: Optional[str] = None
    REPLICATE_RATE_LIMIT: int = 50
    REPLICATE_PRIORITY: int = 60

    # Fal.ai
    FAL_AI_ENABLED: bool = True
    FAL_AI_API_KEY: Optional[str] = None
    FAL_AI_RATE_LIMIT: int = 100
    FAL_AI_PRIORITY: int = 70

    # GitHub Models
    GITHUB_MODELS_ENABLED: bool = True
    GITHUB_MODELS_API_KEY: Optional[str] = None
    GITHUB_MODELS_RATE_LIMIT: int = 60
    GITHUB_MODELS_PRIORITY: int = 20

    # Cloudflare
    CLOUDFLARE_ENABLED: bool = True
    CLOUDFLARE_API_KEY: Optional[str] = None
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = None
    CLOUDFLARE_RATE_LIMIT: int = 100
    CLOUDFLARE_PRIORITY: int = 80

    # Router settings
    ROUTER_STRATEGY: str = "priority"  # priority, cheapest, fastest, round_robin
    ROUTER_DEFAULT_PROVIDER: str = "openrouter"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        provider_upper = provider_name.upper().replace("-", "_")

        enabled = getattr(self, f"{provider_upper}_ENABLED", False)
        if not enabled:
            return None

        api_key = getattr(self, f"{provider_upper}_API_KEY", None)
        if not api_key:
            return None

        return ProviderConfig(
            enabled=enabled,
            api_key=api_key,
            rate_limit_rpm=getattr(self, f"{provider_upper}_RATE_LIMIT", 60),
            priority=getattr(self, f"{provider_upper}_PRIORITY", 100),
        )


# Global config instance
ai_config = AIProvidersConfig()


def get_priority_order() -> list[str]:
    """Get providers sorted by priority"""
    providers_with_priority = [
        ("deepseek", ai_config.DEEPSEEK_PRIORITY, ai_config.DEEPSEEK_ENABLED),
        ("openrouter", ai_config.OPENROUTER_PRIORITY, ai_config.OPENROUTER_ENABLED),
        ("github_models", ai_config.GITHUB_MODELS_PRIORITY, ai_config.GITHUB_MODELS_ENABLED),
        ("moonshot", ai_config.MOONSHOT_PRIORITY, ai_config.MOONSHOT_ENABLED),
        ("siliconflow", ai_config.SILICONFLOW_PRIORITY, ai_config.SILICONFLOW_ENABLED),
        ("huggingface", ai_config.HUGGINGFACE_PRIORITY, ai_config.HUGGINGFACE_ENABLED),
        ("replicate", ai_config.REPLICATE_PRIORITY, ai_config.REPLICATE_ENABLED),
        ("fal_ai", ai_config.FAL_AI_PRIORITY, ai_config.FAL_AI_ENABLED),
        ("cloudflare", ai_config.CLOUDFLARE_PRIORITY, ai_config.CLOUDFLARE_ENABLED),
    ]

    # Filter enabled, sort by priority (lower = higher priority)
    enabled_providers = [name for name, _, enabled in providers_with_priority if enabled]
    enabled_providers.sort(key=lambda name: next(
        priority for pname, priority, _ in providers_with_priority if pname == name
    ))

    return enabled_providers
