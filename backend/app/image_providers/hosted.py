from __future__ import annotations

import os
from pathlib import Path

import requests

from app.image_providers.base import ImageProvider, ImageProviderResult


class ImageProviderError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class HostedImageProvider(ImageProvider):
    def generate_image(self, prompt: str, negative_prompt: str, width: int, height: int, reference_image: Path | None = None) -> ImageProviderResult:
        api_key = os.getenv("IMAGE_API_KEY", "")
        if not api_key:
            raise ImageProviderError("PROVIDER_AUTH_MISSING", "IMAGE_API_KEY is required for hosted image generation.")
        base_url = os.getenv("IMAGE_API_BASE_URL", "https://api.example.invalid/v1").rstrip("/")
        try:
            response = requests.post(base_url + "/images/generations", headers={"Authorization":"Bearer " + api_key,"Content-Type":"application/json"}, json={"prompt":prompt,"negative_prompt":negative_prompt,"width":width,"height":height,"model":os.getenv("IMAGE_MODEL","configured-image-model")}, timeout=float(os.getenv("IMAGE_TIMEOUT_SECONDS","60")))
            response.raise_for_status()
            body = response.json()
            encoded = body["data"][0].get("b64_json", "")
            import base64
            return ImageProviderResult(content=base64.b64decode(encoded), provider="hosted", model=os.getenv("IMAGE_MODEL","configured-image-model"))
        except requests.Timeout as exc:
            raise ImageProviderError("PROVIDER_TIMEOUT", "Image provider timed out.") from exc
        except requests.RequestException as exc:
            if getattr(exc.response, "status_code", None) == 429:
                raise ImageProviderError("PROVIDER_RATE_LIMIT", "Image provider rate limit reached.") from exc
            raise ImageProviderError("PROVIDER_UNAVAILABLE", "Image provider is unavailable.") from exc
