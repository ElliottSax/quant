"""
OpenRouter Provider

Unified API for 100+ AI models from various providers.
Automatic routing to best/cheapest model for your needs.
"""

import httpx
import time
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError


class OpenRouterProvider(AIProvider):
    """OpenRouter unified AI API provider"""

    BASE_URL = "https://openrouter.ai/api/v1"

    DEFAULT_MODEL = "anthropic/claude-3-sonnet"

    # Popular models available through OpenRouter
    MODELS = {
        "auto": "Auto-select best model",
        "anthropic/claude-3-sonnet": "Claude 3 Sonnet",
        "anthropic/claude-3-opus": "Claude 3 Opus",
        "openai/gpt-4-turbo": "GPT-4 Turbo",
        "openai/gpt-3.5-turbo": "GPT-3.5 Turbo",
        "google/gemini-pro": "Gemini Pro",
        "meta-llama/llama-3-70b": "Llama 3 70B",
        "mistralai/mistral-large": "Mistral Large",
        "cohere/command-r-plus": "Command R+",
    }

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
        ]

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate text via OpenRouter"""
        return await self.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Chat completion via OpenRouter"""
        await self._rate_limit_check()

        start_time = time.time()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://quant-analytics.ai",  # Optional
                        "X-Title": "Quant Analytics Platform",  # Optional
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        **kwargs
                    }
                )
                response.raise_for_status()
                data = response.json()

            # Extract response
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            # Get cost from OpenRouter's response
            cost = 0.0
            if "usage" in data and "total_cost" in data["usage"]:
                cost = float(data["usage"]["total_cost"])

            latency_ms = int((time.time() - start_time) * 1000)

            # Get actual model used (OpenRouter may route to different model)
            actual_model = data.get("model", model)

            self._update_stats(
                success=True,
                tokens=total_tokens,
                cost=cost,
                latency_ms=latency_ms
            )

            return AIResponse(
                text=text,
                model=actual_model,
                provider=self.name,
                tokens_used=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                metadata={
                    "requested_model": model,
                    "routed_model": actual_model,
                    "finish_reason": data["choices"][0].get("finish_reason"),
                }
            )

        except httpx.HTTPStatusError as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"OpenRouter API error: {e}")
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"OpenRouter request failed: {e}")
