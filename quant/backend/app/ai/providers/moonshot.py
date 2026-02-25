"""Moonshot AI Provider - Chinese LLM provider"""
import httpx
import time
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError

class MoonshotProvider(AIProvider):
    BASE_URL = "https://api.moonshot.cn/v1"
    DEFAULT_MODEL = "moonshot-v1-8k"

    @property
    def name(self) -> str:
        return "moonshot"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]

    async def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        return await self.chat_completion([{"role": "user", "content": prompt}], model, max_tokens, temperature, **kwargs)

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        await self._rate_limit_check()
        start_time = time.time()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.BASE_URL}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature})
                response.raise_for_status()
                data = response.json()

            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            self._update_stats(success=True, tokens=tokens, latency_ms=int((time.time() - start_time) * 1000))
            return AIResponse(text=text, model=model, provider=self.name, tokens_used=tokens, latency_ms=int((time.time() - start_time) * 1000))
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Moonshot error: {e}")
