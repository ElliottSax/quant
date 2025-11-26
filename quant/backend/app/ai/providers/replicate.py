"""Replicate AI Provider - Run ML models in the cloud"""
import httpx
import time
import asyncio
from typing import Dict, List, Optional
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError

class ReplicateProvider(AIProvider):
    BASE_URL = "https://api.replicate.com/v1"
    DEFAULT_MODEL = "meta/llama-2-70b-chat"

    @property
    def name(self) -> str:
        return "replicate"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [ModelCapability.TEXT_GENERATION, ModelCapability.IMAGE_GENERATION, ModelCapability.AUDIO_TRANSCRIPTION]

    async def generate_text(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        await self._rate_limit_check()
        start_time = time.time()
        model = model or self.DEFAULT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.BASE_URL}/predictions", headers={"Authorization": f"Token {self.api_key}"}, json={"version": model, "input": {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}})
                response.raise_for_status()
                prediction = response.json()

                # Poll for completion
                prediction_url = prediction["urls"]["get"]
                for _ in range(30):  # Max 30 attempts
                    await asyncio.sleep(1)
                    status_resp = await client.get(prediction_url, headers={"Authorization": f"Token {self.api_key}"})
                    status_data = status_resp.json()
                    if status_data["status"] == "succeeded":
                        text = "".join(status_data["output"]) if isinstance(status_data["output"], list) else status_data["output"]
                        self._update_stats(success=True, latency_ms=int((time.time() - start_time) * 1000))
                        return AIResponse(text=text, model=model, provider=self.name, latency_ms=int((time.time() - start_time) * 1000))
                    elif status_data["status"] == "failed":
                        raise AIProviderError(f"Prediction failed: {status_data.get('error')}")

                raise AIProviderError("Prediction timeout")
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Replicate error: {e}")

    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> AIResponse:
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        return await self.generate_text(prompt, model, max_tokens, temperature, **kwargs)
