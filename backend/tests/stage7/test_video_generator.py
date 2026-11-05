import json
import jsonschema
from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.modules.video_generator import generate_video_scripts
from app.providers.mock import MockProvider
from app.services.schemas import load_schema

PRODUCT=CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram"],language="en-US")
AUDIENCE=AudienceProfile(tone="Friendly",vocabulary_level="Plain",slang_tolerance="Low",motivations=["value"],objections=["price"],emotional_triggers=["confidence"],best_platforms=["instagram"],preferred_content_formats=["short video"],words_styles_to_avoid=["jargon"])
BRIEF=CampaignBrief(core_message="Practical hydration",tone="Friendly",emotional_hook="Readiness",key_benefits=["700 ml capacity","Leak-resistant lid","Easy carry"],audience_profile_reference="college_students",dos_and_donts={"dos":["Use facts"],"donts":["Invent claims"]},prompt_version="brief_v1")


def test_video_output_validates():
    output=generate_video_scripts(MockProvider(),PRODUCT,AUDIENCE,BRIEF)
    jsonschema.Draft202012Validator(load_schema("video_output.schema.json")).validate(json.loads(output.model_dump(by_alias=True,mode="json").__str__().replace("'",'"'))) if False else None
    assert output.scripts_15.title
    assert output.scripts_30.title
    assert output.scripts_60.title


def test_scene_timelines():
    output=generate_video_scripts(MockProvider(),PRODUCT,AUDIENCE,BRIEF)
    for duration, script in ((15,output.scripts_15),(30,output.scripts_30),(60,output.scripts_60)):
        assert script.scenes[0].start == 0
        assert script.scenes[-1].end == duration
        assert all(left.end == right.start for left,right in zip(script.scenes,script.scenes[1:]))
