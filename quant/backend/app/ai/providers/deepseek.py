"""
DeepSeek AI Provider

DeepSeek offers powerful open-source LLMs with competitive pricing.
Known for strong coding and reasoning capabilities.
"""

import httpx
import time
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider implementation"""

    BASE_URL = "https://api.deepseek.com/v1"

    DEFAULT_MODEL = "deepseek-chat"

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "deepseek-chat": {"input": 0.14, "output": 0.28},
        "deepseek-coder": {"input": 0.14, "output": 0.28},
    }

    @property
    def name(self) -> str:
        return "deepseek"

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
        """Generate text using DeepSeek"""
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
        """Chat completion with DeepSeek"""
        await self._rate_limit_check()

        start_time = time.time()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False,
                        **kwargs
                    }
                )
                response.raise_for_status()
                data = response.json()

            # Extract response
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

            # Calculate cost
            pricing = self.PRICING.get(model, self.PRICING[self.DEFAULT_MODEL])
            cost = (
                (input_tokens / 1_000_000) * pricing["input"] +
                (output_tokens / 1_000_000) * pricing["output"]
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Update stats
            self._update_stats(
                success=True,
                tokens=total_tokens,
                cost=cost,
                latency_ms=latency_ms
            )

            return AIResponse(
                text=text,
                model=model,
                provider=self.name,
                tokens_used=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "finish_reason": data["choices"][0].get("finish_reason"),
                }
            )

        except httpx.HTTPStatusError as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"DeepSeek API error: {e}")
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"DeepSeek request failed: {e}")
