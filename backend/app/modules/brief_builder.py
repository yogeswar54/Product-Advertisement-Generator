from __future__ import annotations

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.providers.base import LLMProvider
from app.services.json_enforcement import generate_valid_json
from app.services.prompt_loader import load_prompt
from app.services.schemas import load_schema


def build_brief(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile) -> CampaignBrief:
    values = {
        "audience_name": product.target_audience,
        "audience_tone": audience.tone,
        "audience_vocabulary": audience.vocabulary_level,
        "audience_slang_tolerance": audience.slang_tolerance,
        "audience_motivations": ", ".join(audience.motivations),
        "audience_objections": ", ".join(audience.objections),
        "audience_emotional_triggers": ", ".join(audience.emotional_triggers),
        "audience_avoid": ", ".join(audience.words_styles_to_avoid),
        "product_name": product.product_name,
        "category": product.category,
        "key_features": ", ".join(product.key_features),
        "price": product.price if product.price is not None else "not provided",
        "usp": product.usp,
        "brand_name": product.brand_name or "not provided",
        "brand_voice": product.brand_voice,
        "campaign_goal": product.campaign_goal,
        "platforms": ", ".join(product.platforms),
        "language": product.language,
    }
    prompt, temperature, max_tokens = load_prompt("brief_v1", values)
    sections = prompt.split("[SYSTEM]", 1)
    system = sections[1].split("[AUDIENCE INJECTION]", 1)[0].strip() if len(sections) > 1 else prompt
    user = "[AUDIENCE INJECTION]" + prompt.split("[AUDIENCE INJECTION]", 1)[1] if "[AUDIENCE INJECTION]" in prompt else prompt
    data, _, _ = generate_valid_json(provider, system, user, load_schema("campaign_brief.schema.json"), temperature, max_tokens)
    return CampaignBrief.model_validate(data)
