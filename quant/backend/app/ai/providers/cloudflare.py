"""Cloudflare Workers AI Provider - Edge inference"""
import httpx
import time
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError

class CloudflareProvider(AIProvider):
    BASE_URL_TEMPLATE = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
    DEFAULT_MODEL = "@cf/meta/llama-2-7b-chat-int8"

    def __init__(self, api_key: str, account_id: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.account_id = account_id
        self.base_url = self.BASE_URL_TEMPLATE.format(account_id=account_id)

    @property
    def name(self) -> str:
        return "cloudflare"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [ModelCapability.TEXT_GENERATION, ModelCapability.IMAGE_GENERATION, ModelCapability.EMBEDDINGS]

    async def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        await self._rate_limit_check()
        start_time = time.time()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/{model}", headers={"Authorization": f"Bearer {self.api_key}"}, json={"prompt": prompt, "max_tokens": max_tokens})
                response.raise_for_status()
                data = response.json()

            text = data.get("result", {}).get("response", "")
            self._update_stats(success=True, latency_ms=int((time.time() - start_time) * 1000))
            return AIResponse(text=text, model=model, provider=self.name, latency_ms=int((time.time() - start_time) * 1000))
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Cloudflare error: {e}")

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return await self.generate_text(prompt, model, max_tokens, temperature, **kwargs)
