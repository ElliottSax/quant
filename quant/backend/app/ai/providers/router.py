"""
AI Provider Router

Intelligent routing system that:
- Automatically selects best provider for each request
- Implements fallback logic for reliability
- Tracks costs and usage across all providers
- Load balances between providers
- Supports provider preferences and priorities
"""

import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum
import random

from .base import (
    AIProvider,
    AIResponse,
    AIProviderError,
    RateLimitError,
    ModelCapability,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class RoutingStrategy(str, Enum):
    """Routing strategies"""
    CHEAPEST = "cheapest"  # Route to cheapest provider
    FASTEST = "fastest"  # Route to fastest provider
    BEST_QUALITY = "best_quality"  # Route to highest quality
    ROUND_ROBIN = "round_robin"  # Distribute load evenly
    PRIORITY = "priority"  # Use priority order with fallback


class AIProviderRouter:
    """
    Intelligent router for managing multiple AI providers.

    Features:
    - Automatic fallback on failure
    - Cost optimization
    - Load balancing
    - Usage tracking
    """

    def __init__(
        self,
        providers: Dict[str, AIProvider],
        strategy: RoutingStrategy = RoutingStrategy.PRIORITY,
        priority_order: Optional[List[str]] = None,
    ):
        """
        Initialize router.

        Args:
            providers: Dict of provider_name -> AIProvider instance
            strategy: Routing strategy to use
            priority_order: Ordered list of provider names (for PRIORITY strategy)
        """
        self.providers = providers
        self.strategy = strategy
        self.priority_order = priority_order or list(providers.keys())
        self._round_robin_index = 0

        # Global usage tracking
        self.total_requests = 0
        self.total_cost = 0.0
        self.provider_failures: Dict[str, int] = {}

        logger.info(
            f"AI Router initialized with {len(providers)} providers: "
            f"{', '.join(providers.keys())}"
        )

    def _select_provider(
        self,
        capability: ModelCapability,
        exclude: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Select best provider based on strategy.

        Args:
            capability: Required capability
            exclude: Providers to exclude

        Returns:
            Provider name or None
        """
        exclude = exclude or []

        # Filter providers that support the capability and aren't excluded
        available = [
            name for name, provider in self.providers.items()
            if provider.supports_capability(capability) and name not in exclude
        ]

        if not available:
            return None

        if self.strategy == RoutingStrategy.PRIORITY:
            # Use priority order
            for name in self.priority_order:
                if name in available:
                    return name

        elif self.strategy == RoutingStrategy.CHEAPEST:
            # Select provider with lowest cost (based on stats)
            cheapest = min(
                available,
                key=lambda name: self.providers[name].stats.total_cost_usd
            )
            return cheapest

        elif self.strategy == RoutingStrategy.FASTEST:
            # Select provider with lowest average latency
            fastest = min(
                available,
                key=lambda name: self.providers[name].stats.average_latency_ms or float('inf')
            )
            return fastest

        elif self.strategy == RoutingStrategy.ROUND_ROBIN:
            # Round-robin distribution
            provider_name = available[self._round_robin_index % len(available)]
            self._round_robin_index += 1
            return provider_name

        elif self.strategy == RoutingStrategy.BEST_QUALITY:
            # Use priority order as proxy for quality
            for name in self.priority_order:
                if name in available:
                    return name

        return available[0] if available else None

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate text with automatic provider selection and fallback.

        Args:
            prompt: Input prompt
            model: Model to use (provider-specific)
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            preferred_provider: Specific provider to try first
            **kwargs: Additional parameters

        Returns:
            AIResponse from successful provider
        """
        self.total_requests += 1
        exclude = []
        attempts = 0
        max_attempts = len(self.providers)

        while attempts < max_attempts:
            # Select provider
            if preferred_provider and attempts == 0 and preferred_provider not in exclude:
                provider_name = preferred_provider
            else:
                provider_name = self._select_provider(
                    ModelCapability.TEXT_GENERATION,
                    exclude=exclude
                )

            if not provider_name:
                raise AIProviderError("No available providers for text generation")

            provider = self.providers[provider_name]
            logger.debug(f"Attempting text generation with {provider_name} (attempt {attempts + 1})")

            try:
                response = await provider.generate_text(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                # Update global stats
                self.total_cost += response.cost_usd

                logger.info(
                    f"Text generated successfully via {provider_name} "
                    f"({response.tokens_used} tokens, ${response.cost_usd:.4f})"
                )

                return response

            except RateLimitError as e:
                logger.warning(f"{provider_name} rate limited: {e}")
                exclude.append(provider_name)
                self.provider_failures[provider_name] = self.provider_failures.get(provider_name, 0) + 1

            except AIProviderError as e:
                logger.error(f"{provider_name} failed: {e}")
                exclude.append(provider_name)
                self.provider_failures[provider_name] = self.provider_failures.get(provider_name, 0) + 1

            except Exception as e:
                logger.error(f"{provider_name} unexpected error: {e}", exc_info=True)
                exclude.append(provider_name)
                self.provider_failures[provider_name] = self.provider_failures.get(provider_name, 0) + 1

            attempts += 1

        raise AIProviderError("All providers failed for text generation")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Chat completion with automatic provider selection and fallback"""
        self.total_requests += 1
        exclude = []
        attempts = 0
        max_attempts = len(self.providers)

        while attempts < max_attempts:
            if preferred_provider and attempts == 0 and preferred_provider not in exclude:
                provider_name = preferred_provider
            else:
                provider_name = self._select_provider(
                    ModelCapability.CHAT,
                    exclude=exclude
                )

            if not provider_name:
                raise AIProviderError("No available providers for chat completion")

            provider = self.providers[provider_name]
            logger.debug(f"Attempting chat completion with {provider_name}")

            try:
                response = await provider.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )

                self.total_cost += response.cost_usd
                logger.info(f"Chat completed via {provider_name} (${response.cost_usd:.4f})")
                return response

            except (RateLimitError, AIProviderError) as e:
                logger.warning(f"{provider_name} failed: {e}")
                exclude.append(provider_name)
                self.provider_failures[provider_name] = self.provider_failures.get(provider_name, 0) + 1
                attempts += 1

        raise AIProviderError("All providers failed for chat completion")

    async def get_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """Get embeddings with automatic provider selection"""
        exclude = []
        attempts = 0
        max_attempts = len(self.providers)

        while attempts < max_attempts:
            if preferred_provider and attempts == 0:
                provider_name = preferred_provider
            else:
                provider_name = self._select_provider(
                    ModelCapability.EMBEDDINGS,
                    exclude=exclude
                )

            if not provider_name:
                raise AIProviderError("No available providers for embeddings")

            provider = self.providers[provider_name]

            try:
                embeddings = await provider.get_embeddings(texts, model, **kwargs)
                logger.info(f"Embeddings generated via {provider_name}")
                return embeddings

            except (RateLimitError, AIProviderError, NotImplementedError) as e:
                logger.warning(f"{provider_name} failed for embeddings: {e}")
                exclude.append(provider_name)
                attempts += 1

        raise AIProviderError("All providers failed for embeddings")

    def get_all_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all providers"""
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost, 4),
            "strategy": self.strategy,
            "providers": {
                name: provider.get_stats()
                for name, provider in self.providers.items()
            },
            "failures": self.provider_failures,
        }

    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by provider"""
        return {
            name: provider.stats.total_cost_usd
            for name, provider in self.providers.items()
        }

    def get_healthiest_providers(self, limit: int = 5) -> List[str]:
        """Get providers with best success rates"""
        provider_health = []
        for name, provider in self.providers.items():
            if provider.stats.total_requests > 0:
                success_rate = (
                    provider.stats.successful_requests / provider.stats.total_requests
                )
                provider_health.append((name, success_rate))

        provider_health.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in provider_health[:limit]]
