from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.models.stage5 import SocialOutput
from app.modules.social_generator import generate_social
from app.providers.mock import MockProvider
from app.services.social_checks import run_social_checks

PRODUCT = CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_name="CampusFlow",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram","linkedin"],language="en-US")
AUDIENCE = AudienceProfile(tone="Friendly",vocabulary_level="Plain",slang_tolerance="Low",motivations=["value"],objections=["price"],emotional_triggers=["confidence"],best_platforms=["instagram"],preferred_content_formats=["short video"],words_styles_to_avoid=["jargon"])
BRIEF = CampaignBrief(core_message="Practical hydration",tone="Friendly",emotional_hook="Readiness",key_benefits=["700 ml capacity","Leak-resistant lid","Easy carry"],audience_profile_reference="college_students",dos_and_donts={"dos":["Use facts"],"donts":["Invent claims"]},prompt_version="brief_v1")


def test_social_checks_accept_mock_output():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["instagram", "linkedin"])
    assert isinstance(run_social_checks(PRODUCT, social, ["instagram", "linkedin"]), list)


def test_unsupported_number_warning():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["instagram"])
    social.instagram.caption = "Guaranteed by 99 sources"
    warnings = run_social_checks(PRODUCT, social, ["instagram"])
    assert any(item.code == "UNSUPPORTED_NUMBER" or item.code == "RISKY_CLAIM_WORD" for item in warnings)


def test_calendar_rejects_unselected_platform():
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, ["instagram"])
    social.calendar[0].platform = "linkedin"
    warnings = run_social_checks(PRODUCT, social, ["instagram"])
    assert any(item.code == "CALENDAR_UNSELECTED_PLATFORM" for item in warnings)
