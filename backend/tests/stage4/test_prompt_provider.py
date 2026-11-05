import pytest

from app.providers.base import ProviderError
from app.providers.mock import MockProvider
from app.services.prompt_loader import PromptLoadError, load_prompt


def test_prompt_loader_fills_placeholders():
    prompt, temperature, max_tokens = load_prompt("brief_v1", {
        "audience_name":"College Students","audience_tone":"Friendly","audience_vocabulary":"Plain","audience_slang_tolerance":"Light","audience_motivations":"value","audience_objections":"price","audience_emotional_triggers":"belonging","audience_avoid":"jargon","product_name":"Bottle","category":"Bottle","key_features":"700 ml","price":"not provided","usp":"Easy carry","brand_name":"CampusFlow","brand_voice":"Friendly","campaign_goal":"Conversions","platforms":"instagram","language":"en-US"
    })
    assert "{{" not in prompt
    assert temperature == 0.4


def test_prompt_loader_missing_placeholder():
    try:
        load_prompt("brief_v1", {})
    except PromptLoadError as exc:
        assert "Missing prompt placeholders" in str(exc)
    else:
        raise AssertionError("Missing placeholders should fail")


def test_mock_provider():
    from app.services.schemas import load_schema
    result = MockProvider().generate_json("system", "user", load_schema("description_output.schema.json"), 0.5, 1000)
    assert result.text
    assert result.usage.estimated


def test_provider_error_codes():
    timeout = ProviderError("PROVIDER_TIMEOUT", "Timed out")
    rate_limit = ProviderError("PROVIDER_RATE_LIMIT", "Limited")
    assert timeout.code == "PROVIDER_TIMEOUT"
    assert rate_limit.code == "PROVIDER_RATE_LIMIT"
