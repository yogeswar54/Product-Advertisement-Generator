from __future__ import annotations

import os

from app.providers.base import LLMProvider
from app.providers.hosted import HostedAPIProvider
from app.providers.mock import MockProvider


def get_llm_provider() -> LLMProvider:
    setting = os.getenv("LLM_PROVIDER", "mock").lower()
    if setting == "mock":
        return MockProvider()
    return HostedAPIProvider()
