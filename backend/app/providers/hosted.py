from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from app.providers.base import LLMProvider, ProviderError, ProviderResult, ProviderUsage


class HostedAPIProvider(LLMProvider):
    """Provider adapter for an OpenAI-compatible hosted chat endpoint.

    Stage 1 did not name a specific hosted vendor. This adapter deliberately
    uses vendor-neutral environment settings rather than claiming a vendor.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "configured-model")

    def generate_json(self, system: str, user: str, schema: dict[str, Any], temperature: float, max_tokens: int) -> ProviderResult:
        if not self.api_key:
            raise ProviderError("PROVIDER_AUTH_MISSING", "LLM_API_KEY is required for the hosted provider.")
        payload = {"model": self.model, "temperature": temperature, "max_tokens": max_tokens, "response_format":{"type":"json_object"}, "messages":[{"role":"system","content":system},{"role":"user","content":user}]}
        last_error: ProviderError | None = None
        for attempt in range(3):
            try:
                response = requests.post(self.base_url + "/chat/completions", headers={"Authorization":"Bearer " + self.api_key,"Content-Type":"application/json"}, json=payload, timeout=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")))
                if response.status_code == 429:
                    raise ProviderError("PROVIDER_RATE_LIMIT", "The hosted provider rate limit was reached.")
                response.raise_for_status()
                body = response.json()
                text = body["choices"][0]["message"]["content"]
                usage = body.get("usage", {})
                return ProviderResult(text=text, usage=ProviderUsage(input_tokens=int(usage.get("prompt_tokens", 0)), output_tokens=int(usage.get("completion_tokens", 0))), model=self.model)
            except ProviderError as exc:
                if exc.code != "PROVIDER_RATE_LIMIT" or attempt == 2:
                    raise
                last_error = exc
            except requests.Timeout as exc:
                raise ProviderError("PROVIDER_TIMEOUT", "The hosted provider timed out.") from exc
            except requests.RequestException as exc:
                last_error = ProviderError("PROVIDER_UNAVAILABLE", "The hosted provider is unavailable.")
            time.sleep(2 ** attempt)
        if last_error:
            raise last_error
        raise ProviderError("PROVIDER_UNAVAILABLE", "The hosted provider is unavailable.")
