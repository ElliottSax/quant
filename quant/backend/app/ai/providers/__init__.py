"""
Multi-Provider AI System

Unified interface for multiple AI/ML providers with automatic fallback,
rate limiting, cost tracking, and intelligent routing.

Supported Providers:
- DeepSeek
- Hugging Face
- OpenRouter
- Google Cloud (Vertex AI)
- Moonshot
- SiliconFlow
- Replicate
- Fal.ai
- GitHub Models
- Cloudflare Workers AI
"""

from .base import AIProvider, AIProviderError, AIResponse
from .deepseek import DeepSeekProvider
from .huggingface import HuggingFaceProvider
from .openrouter import OpenRouterProvider
from .google_cloud import GoogleCloudProvider
from .moonshot import MoonshotProvider
from .siliconflow import SiliconFlowProvider
from .replicate import ReplicateProvider
from .fal_ai import FalAIProvider
from .github_models import GitHubModelsProvider
from .cloudflare import CloudflareProvider
from .router import AIProviderRouter

__all__ = [
    'AIProvider',
    'AIProviderError',
    'AIResponse',
    'DeepSeekProvider',
    'HuggingFaceProvider',
    'OpenRouterProvider',
    'GoogleCloudProvider',
    'MoonshotProvider',
    'SiliconFlowProvider',
    'ReplicateProvider',
    'FalAIProvider',
    'GitHubModelsProvider',
    'CloudflareProvider',
    'AIProviderRouter',
]
