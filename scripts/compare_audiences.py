from __future__ import annotations

from app.models.audience import AudienceProfile
from app.modules.audience_profiler import profile_audience
from app.models.audience import AudienceProfileRequest
from app.models.input import CampaignInput
from app.modules.brief_builder import build_brief
from app.modules.description_generator import generate_descriptions
from app.providers.mock import MockProvider

PERSONAS = ["college_students", "young_professionals", "working_parents", "fitness_enthusiasts"]
PRODUCT = CampaignInput(product_name="CampusFlow Bottle", category="Reusable water bottle", key_features=["700 ml capacity", "Leak-resistant lid"], usp="Easy to carry between daily activities", brand_name="CampusFlow", brand_voice="Friendly and practical", target_audience="college_students", campaign_goal="Increase product-page conversions", platforms=["instagram", "facebook"], language="en-US")


def main() -> None:
    provider = MockProvider()
    print("Source: mock provider; real LLM output requires a configured key.")
    for persona_id in PERSONAS:
        product = PRODUCT.model_copy(update={"target_audience": persona_id})
        profile = profile_audience(AudienceProfileRequest(persona_id=persona_id))
        brief = build_brief(provider, product, profile)
        description = generate_descriptions(provider, product, profile, brief)
        print(f"{persona_id}: {brief.core_message} | {description.short}")


if __name__ == "__main__":
    main()
