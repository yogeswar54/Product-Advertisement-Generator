from __future__ import annotations

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.modules.social_generator import generate_social
from app.providers.mock import MockProvider

PRODUCT = CampaignInput(product_name="CampusFlow Bottle", category="Reusable water bottle", key_features=["700 ml capacity", "Leak-resistant lid"], usp="Easy campus carry", brand_name="CampusFlow", brand_voice="Friendly and practical", target_audience="college_students", campaign_goal="Conversions", platforms=["instagram", "linkedin", "x", "facebook", "whatsapp"], language="en-US")
AUDIENCE = AudienceProfile(tone="Friendly and practical", vocabulary_level="Plain", slang_tolerance="Low", motivations=["value"], objections=["price"], emotional_triggers=["confidence"], best_platforms=["instagram"], preferred_content_formats=["short video"], words_styles_to_avoid=["jargon"])
BRIEF = CampaignBrief(core_message="Practical campus hydration", tone="Friendly and practical", emotional_hook="Readiness", key_benefits=["700 ml capacity", "Leak-resistant lid", "Easy carry"], audience_profile_reference="college_students", dos_and_donts={"dos":["Use facts"], "donts":["Invent claims"]}, prompt_version="brief_v1")


def main() -> None:
    social = generate_social(MockProvider(), PRODUCT, AUDIENCE, BRIEF, list(PRODUCT.platforms))
    print("Source: mock provider")
    for platform, post in (("instagram", social.instagram), ("linkedin", social.linkedin), ("x", social.x), ("facebook", social.facebook), ("whatsapp", social.whatsapp)):
        print(platform + ": " + (post.caption if platform == "instagram" else post.post if platform in {"linkedin", "x"} else post.message if platform == "whatsapp" else post.post))

if __name__ == "__main__":
    main()
