from __future__ import annotations

import hashlib
import json
from typing import Any

_CACHE: dict[str, Any] = {}


def cache_key(validated_input: dict[str, Any], audience_profile: dict[str, Any], prompt_version: str, model_name: str) -> str:
    payload = json.dumps({"input": validated_input, "audience_profile": audience_profile, "prompt_version": prompt_version, "model_name": model_name}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_cached(key: str) -> Any | None:
    return _CACHE.get(key)


def set_cached(key: str, value: Any) -> None:
    _CACHE[key] = value


def clear_cache() -> None:
    _CACHE.clear()
