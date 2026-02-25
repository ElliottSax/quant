"""
Base AI Provider Interface

Defines the common interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import time


class ModelCapability(str, Enum):
    """AI model capabilities"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    EMBEDDINGS = "embeddings"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    TEXT_TO_SPEECH = "text_to_speech"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"


class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass


class RateLimitError(AIProviderError):
    """Rate limit exceeded"""
    pass


class AuthenticationError(AIProviderError):
    """Authentication failed"""
    pass


class QuotaExceededError(AIProviderError):
    """Quota exceeded"""
    pass


@dataclass
class AIResponse:
    """Unified response from AI providers"""
    text: str
    model: str
    provider: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"{self.provider}/{self.model}: {self.text[:100]}..."


@dataclass
class UsageStats:
    """Provider usage statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    average_latency_ms: float = 0.0
    last_request: Optional[datetime] = None
    last_error: Optional[str] = None


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All AI providers must implement this interface for consistent
    usage across different services.
    """

    def __init__(
        self,
        api_key: str,
        rate_limit_rpm: int = 60,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize AI provider.

        Args:
            api_key: API key for the provider
            rate_limit_rpm: Requests per minute limit
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key
        self.rate_limit_rpm = rate_limit_rpm
        self.timeout = timeout
        self.max_retries = max_retries

        # Rate limiting
        self._request_times: List[float] = []
        self._lock = asyncio.Lock()

        # Usage tracking
        self.stats = UsageStats()

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass

    @property
    @abstractmethod
    def supported_capabilities(self) -> List[ModelCapability]:
        """List of capabilities this provider supports"""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            model: Model to use (provider-specific)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional provider-specific parameters

        Returns:
            AIResponse with generated text
        """
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Chat completion with conversation history.

        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            AIResponse with chat completion
        """
        pass

    async def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Get embeddings for text(s).

        Args:
            texts: Single text or list of texts
            model: Embedding model to use
            **kwargs: Additional parameters

        Returns:
            List of embedding vectors
        """
        raise NotImplementedError(f"{self.name} does not support embeddings")

    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = "1024x1024",
        **kwargs
    ) -> str:
        """
        Generate image from prompt.

        Args:
            prompt: Image description
            model: Model to use
            size: Image size
            **kwargs: Additional parameters

        Returns:
            Image URL or base64 data
        """
        raise NotImplementedError(f"{self.name} does not support image generation")

    async def _rate_limit_check(self):
        """Check and enforce rate limits"""
        async with self._lock:
            now = time.time()

            # Remove requests older than 1 minute
            self._request_times = [t for t in self._request_times if now - t < 60]

            # Check if we're at limit
            if len(self._request_times) >= self.rate_limit_rpm:
                # Calculate wait time
                oldest = self._request_times[0]
                wait_time = 60 - (now - oldest)
                if wait_time > 0:
                    raise RateLimitError(
                        f"Rate limit of {self.rate_limit_rpm} RPM exceeded. "
                        f"Wait {wait_time:.1f}s"
                    )

            # Record this request
            self._request_times.append(now)

    def _update_stats(
        self,
        success: bool,
        tokens: int = 0,
        cost: float = 0.0,
        latency_ms: int = 0,
        error: Optional[str] = None,
    ):
        """Update usage statistics"""
        self.stats.total_requests += 1
        if success:
            self.stats.successful_requests += 1
            self.stats.total_tokens += tokens
            self.stats.total_cost_usd += cost

            # Update average latency
            total_latency = (
                self.stats.average_latency_ms * (self.stats.successful_requests - 1) +
                latency_ms
            )
            self.stats.average_latency_ms = total_latency / self.stats.successful_requests
        else:
            self.stats.failed_requests += 1
            self.stats.last_error = error

        self.stats.last_request = datetime.utcnow()

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "provider": self.name,
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "success_rate": (
                self.stats.successful_requests / self.stats.total_requests
                if self.stats.total_requests > 0
                else 0
            ),
            "total_tokens": self.stats.total_tokens,
            "total_cost_usd": round(self.stats.total_cost_usd, 4),
            "average_latency_ms": round(self.stats.average_latency_ms, 2),
            "last_request": self.stats.last_request.isoformat() if self.stats.last_request else None,
            "last_error": self.stats.last_error,
        }

    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if provider supports a capability"""
        return capability in self.supported_capabilities
