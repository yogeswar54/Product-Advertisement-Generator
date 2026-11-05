import json

import jsonschema
import pytest

from app.providers.base import LLMProvider, ProviderResult, ProviderUsage
from app.services.json_enforcement import clean_json_text, generate_valid_json
from app.services.schemas import load_schema


class BrokenProvider(LLMProvider):
    def __init__(self):
        self.calls = 0
    def generate_json(self, system, user, schema, temperature, max_tokens):
        self.calls += 1
        text = '{"bad":true}' if self.calls == 1 else '{"bad":true}'
        return ProviderResult(text=text, usage=ProviderUsage(1,1,True), model="broken")


class RepairProvider(LLMProvider):
    def __init__(self): self.calls = 0
    def generate_json(self, system, user, schema, temperature, max_tokens):
        self.calls += 1
        if self.calls == 1:
            text = "not json"
        else:
            text = json.dumps(json.loads(__import__('pathlib').Path('schemas/examples/description_output.example.json').read_text()))
        return ProviderResult(text=text, usage=ProviderUsage(1,1,True), model="repair")


def test_clean_fenced_json():
    assert clean_json_text("```json\n{\"ok\":true}\n```") == '{"ok":true}'


def test_repair_attempt_succeeds():
    provider = RepairProvider()
    data, _, repaired = generate_valid_json(provider, "", "", load_schema("description_output.schema.json"), 0.5, 1000)
    assert repaired is True
    assert provider.calls == 2
    assert data["prompt_version"] == "description_v1"


def test_invalid_json_fails_cleanly():
    from app.providers.base import ProviderError
    try:
        generate_valid_json(BrokenProvider(), "", "", load_schema("campaign_brief.schema.json"), 0.5, 1000)
    except ProviderError as exc:
        assert exc.code == "INVALID_RESPONSE"
    else:
        raise AssertionError("Invalid JSON should fail")
