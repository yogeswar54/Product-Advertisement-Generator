import json
from pathlib import Path

import jsonschema

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.modules.social_generator import generate_social
from app.providers.mock import MockProvider
from app.services.schemas import load_schema

PRODUCT = CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_name="CampusFlow",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram","linkedin","x","whatsapp"],language="en-US")
AUDIENCE = AudienceProfile(tone="Friendly and practical",vocabulary_level="Plain",slang_tolerance="Low",motivations=["value"],objections=["price"],emotional_triggers=["confidence"],best_platforms=["instagram"],preferred_content_formats=["short video"],words_styles_to_avoid=["jargon"])
BRIEF = CampaignBrief(core_message="Practical campus hydration",tone="Friendly and practical",emotional_hook="Readiness",key_benefits=["700 ml capacity","Leak-resistant lid","Easy carry"],audience_profile_reference="college_students",dos_and_donts={"dos":["Use facts"],"donts":["Invent claims"]},prompt_version="brief_v1")


def test_mock_social_output_validates():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["instagram", "linkedin"])
    jsonschema.Draft202012Validator(load_schema("social_output.schema.json")).validate(json.loads(social.model_dump_json()))
    assert social.instagram
    assert social.linkedin


def test_only_selected_platforms_are_generated():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["x"])
    assert social.x
    assert social.instagram is None
    assert social.facebook is None


def test_calendar_is_exactly_seven_days():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["instagram", "whatsapp"])
    assert len(social.calendar) == 7
