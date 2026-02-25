"""
Hugging Face Provider

Access to thousands of open-source models via Hugging Face Inference API.
Supports text generation, embeddings, image generation, and more.
"""

import httpx
import time
from typing import Dict, List, Optional, Union
from .base import AIProvider, AIResponse, ModelCapability, AIProviderError


class HuggingFaceProvider(AIProvider):
    """Hugging Face Inference API provider"""

    BASE_URL = "https://api-inference.huggingface.co/models"

    DEFAULT_TEXT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_IMAGE_MODEL = "stabilityai/stable-diffusion-2-1"

    @property
    def name(self) -> str:
        return "huggingface"

    @property
    def supported_capabilities(self) -> List[ModelCapability]:
        return [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.EMBEDDINGS,
            ModelCapability.IMAGE_GENERATION,
            ModelCapability.CLASSIFICATION,
            ModelCapability.SUMMARIZATION,
        ]

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate text using Hugging Face model"""
        await self._rate_limit_check()

        start_time = time.time()
        model = model or self.DEFAULT_TEXT_MODEL

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/{model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": temperature,
                            "return_full_text": False,
                            **kwargs
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()

            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                text = data[0].get("generated_text", str(data[0]))
            else:
                text = data.get("generated_text", str(data))

            latency_ms = int((time.time() - start_time) * 1000)

            # Estimate tokens (rough approximation)
            estimated_tokens = len(prompt.split()) + len(text.split())

            self._update_stats(
                success=True,
                tokens=estimated_tokens,
                cost=0.0,  # Free tier or custom pricing
                latency_ms=latency_ms
            )

            return AIResponse(
                text=text,
                model=model,
                provider=self.name,
                tokens_used=estimated_tokens,
                cost_usd=0.0,
                latency_ms=latency_ms,
                metadata={"model_type": "open_source"}
            )

        except httpx.HTTPStatusError as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Hugging Face API error: {e}")
        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Hugging Face request failed: {e}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Chat completion - convert to single prompt"""
        # Format messages into single prompt
        prompt = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        prompt += "\nassistant:"

        return await self.generate_text(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

    async def get_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """Get embeddings from Hugging Face"""
        await self._rate_limit_check()

        model = model or self.DEFAULT_EMBED_MODEL
        if isinstance(texts, str):
            texts = [texts]

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.BASE_URL}/{model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"inputs": texts}
                )
                response.raise_for_status()
                embeddings = response.json()

            self._update_stats(success=True, tokens=len(texts))
            return embeddings

        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Hugging Face embeddings failed: {e}")

    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = "512x512",
        **kwargs
    ) -> str:
        """Generate image using Hugging Face Diffusion models"""
        await self._rate_limit_check()

        model = model or self.DEFAULT_IMAGE_MODEL

        try:
            async with httpx.AsyncClient(timeout=60) as client:  # Longer timeout for images
                response = await client.post(
                    f"{self.BASE_URL}/{model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"inputs": prompt, **kwargs}
                )
                response.raise_for_status()

                # Response is raw image bytes
                image_bytes = response.content

                # Convert to base64 for easy transfer
                import base64
                image_b64 = base64.b64encode(image_bytes).decode()

                self._update_stats(success=True)
                return f"data:image/png;base64,{image_b64}"

        except Exception as e:
            self._update_stats(success=False, error=str(e))
            raise AIProviderError(f"Hugging Face image generation failed: {e}")
