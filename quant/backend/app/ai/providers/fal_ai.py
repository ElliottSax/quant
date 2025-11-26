"""Fal.ai Provider - Fast AI inference"""
import httpx
import time
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError

class FalAIProvider(AIProvider):
    BASE_URL = "https://fal.run"
    DEFAULT_MODEL = "fal-ai/fast-sdxl"

    @property
    def name(self) -> str:
        return "fal_ai"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [ModelCapability.IMAGE_GENERATION, ModelCapability.TEXT_GENERATION]

    async def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        # Stub - primarily used for image generation
        raise NotImplementedError("Fal.ai primarily for image generation")

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        raise NotImplementedError("Fal.ai primarily for image generation")

    async def generate_image(self, prompt: str, model: Optional[str] = None, size: str = "1024x1024", **kwargs) -> str:
        await self._rate_limit_check()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(f"{self.BASE_URL}/{model}", headers={"Authorization": f"Key {self.api_key}"}, json={"prompt": prompt, **kwargs})
                response.raise_for_status()
                data = response.json()

            image_url = data.get("images", [{}])[0].get("url", "")
            self._update_stats(success=True)
            return image_url
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Fal.ai error: {e}")
