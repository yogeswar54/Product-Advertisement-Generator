import json
import jsonschema

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.modules.visual_generator import generate_visuals
from app.providers.mock import MockProvider
from app.services.schemas import load_schema

PRODUCT = CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram"],language="en-US")
AUDIENCE = AudienceProfile(tone="Friendly and practical",vocabulary_level="Plain",slang_tolerance="Low",motivations=["value"],objections=["price"],emotional_triggers=["confidence"],best_platforms=["instagram"],preferred_content_formats=["short video"],words_styles_to_avoid=["jargon"])
BRIEF = CampaignBrief(core_message="Practical hydration",tone="Friendly and practical",emotional_hook="Readiness",key_benefits=["700 ml capacity","Leak-resistant lid","Easy carry"],audience_profile_reference="college_students",dos_and_donts={"dos":["Use facts"],"donts":["Invent claims"]},prompt_version="brief_v1")


def test_visual_output_validates():
    output = generate_visuals(MockProvider(), PRODUCT, AUDIENCE, BRIEF)
    jsonschema.Draft202012Validator(load_schema("visual_output.schema.json")).validate(json.loads(output.model_dump_json()))
    assert len(output.concepts) == 3
    for concept in output.concepts:
        assert set(concept.layouts) == {"poster","banner","story","square_social_post"}
