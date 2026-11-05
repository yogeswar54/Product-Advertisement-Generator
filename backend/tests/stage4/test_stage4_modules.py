from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.modules.brief_builder import build_brief
from app.modules.description_generator import generate_descriptions
from app.modules.promo_generator import generate_promo
from app.providers.mock import MockProvider
from app.services.lightweight_checks import run_lightweight_checks

PRODUCT = CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity","Leak-resistant lid"],usp="Easy campus carry",brand_name="CampusFlow",brand_voice="Friendly and practical",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram"],language="en-US")
AUDIENCE = AudienceProfile(tone="Friendly, energetic, practical",vocabulary_level="Conversational, plain",slang_tolerance="Light",motivations=["value"],objections=["price"],emotional_triggers=["belonging"],best_platforms=["instagram"],preferred_content_formats=["short video"],words_styles_to_avoid=["corporate jargon"])


def test_generators_validate_and_use_prompt_versions():
    provider = MockProvider()
    brief = build_brief(provider, PRODUCT, AUDIENCE)
    description = generate_descriptions(provider, PRODUCT, AUDIENCE, brief)
    promo = generate_promo(provider, PRODUCT, AUDIENCE, brief)
    assert brief.prompt_version == "brief_v1"
    assert description.prompt_version == "description_v1"
    assert promo.prompt_version == "promo_v1"


def test_unsupported_number_warning():
    from app.models.stage4 import DescriptionOutput
    description = DescriptionOutput(short="A 99 percent result.",medium="A 99 percent result.",long="A 99 percent result.",seo_keywords=["bottle"],prompt_version="description_v1")
    warnings = run_lightweight_checks(PRODUCT, description=description)
    assert any(warning.code == "UNSUPPORTED_NUMBER" for warning in warnings)


def test_duplicate_promo_warning():
    from app.models.stage4 import PromoOutput
    promo = PromoOutput(headlines=["Same headline","Same headline","Three","Four","Five"],taglines=["One","Two","Three","Four","Five"],ad_copy_variants=[{"style":"banner","copy":"x"},{"style":"email","copy":"y"},{"style":"search-ad","copy":"z"}],ctas=["One","Two","Three","Four","Five"],ab_variants=[{"angle":"urgency","id":"A","copy":"x"},{"angle":"trust","id":"B","copy":"y"},{"angle":"fun","id":"C","copy":"z"}],prompt_version="promo_v1")
    warnings = run_lightweight_checks(PRODUCT, promo=promo)
    assert any(warning.code == "DUPLICATE_COPY" for warning in warnings)


def test_headline_length_warning():
    from app.models.stage4 import PromoOutput
    promo = PromoOutput(headlines=["x"*61,"Two","Three","Four","Five"],taglines=["One","Two","Three","Four","Five"],ad_copy_variants=[{"style":"banner","copy":"x"},{"style":"email","copy":"y"},{"style":"search-ad","copy":"z"}],ctas=["One","Two","Three","Four","Five"],ab_variants=[{"angle":"urgency","id":"A","copy":"x"},{"angle":"trust","id":"B","copy":"y"},{"angle":"fun","id":"C","copy":"z"}],prompt_version="promo_v1")
    warnings = run_lightweight_checks(PRODUCT, promo=promo)
    assert any(warning.code == "PROMO_LENGTH" for warning in warnings)
