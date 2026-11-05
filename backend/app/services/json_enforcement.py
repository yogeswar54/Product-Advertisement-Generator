from __future__ import annotations

import json
import re
from typing import Any

import jsonschema

from app.providers.base import LLMProvider, ProviderError, ProviderResult


def clean_json_text(text: str) -> str:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
    stripped = re.sub(r"\s*```$", "", stripped)
    first_object = stripped.find("{")
    if first_object >= 0:
        stripped = stripped[first_object:]
    return stripped.strip()


def generate_valid_json(provider: LLMProvider, system: str, user: str, schema: dict[str, Any], temperature: float, max_tokens: int) -> tuple[dict[str, Any], ProviderResult, bool]:
    result = provider.generate_json(system, user, schema, temperature, max_tokens)
    repaired = False
    for attempt in range(2):
        try:
            data = json.loads(clean_json_text(result.text))
            jsonschema.Draft202012Validator(schema).validate(data)
            return data, result, repaired
        except (json.JSONDecodeError, jsonschema.ValidationError) as exc:
            if attempt == 1:
                raise ProviderError("INVALID_RESPONSE", "The provider returned JSON that could not be repaired.") from exc
            repaired = True
            repair_prompt = user + "\n\nREPAIR THIS INVALID RESPONSE: " + clean_json_text(result.text) + "\nValidation error: " + str(exc)
            result = provider.generate_json(system, repair_prompt, schema, temperature, max_tokens)
    raise ProviderError("INVALID_RESPONSE", "The provider returned an invalid response.")
