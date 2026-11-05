from __future__ import annotations

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief, DescriptionOutput
from app.providers.base import LLMProvider
from app.services.json_enforcement import generate_valid_json
from app.services.prompt_loader import load_prompt
from app.services.schemas import load_schema


def generate_descriptions(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile, brief: CampaignBrief) -> DescriptionOutput:
    values = {
        "audience_name": product.target_audience,
        "audience_tone": audience.tone,
        "audience_vocabulary": audience.vocabulary_level,
        "audience_slang_tolerance": audience.slang_tolerance,
        "audience_formats": ", ".join(audience.preferred_content_formats),
        "audience_avoid": ", ".join(audience.words_styles_to_avoid),
        "core_message": brief.core_message,
        "brief_tone": brief.tone,
        "emotional_hook": brief.emotional_hook,
        "key_benefits": ", ".join(brief.key_benefits),
        "brief_dos": ", ".join(brief.dos_and_donts["dos"]),
        "brief_donts": ", ".join(brief.dos_and_donts["donts"]),
        "product_facts": product_facts(product),
    }
    prompt, temperature, max_tokens = load_prompt("description_v1", values)
    system = prompt.split("[AUDIENCE INJECTION]", 1)[0].replace("[SYSTEM]", "", 1).strip()
    user = "[AUDIENCE INJECTION]" + prompt.split("[AUDIENCE INJECTION]", 1)[1]
    data, _, _ = generate_valid_json(provider, system, user, load_schema("description_output.schema.json"), temperature, max_tokens)
    return DescriptionOutput.model_validate(data)


def product_facts(product: CampaignInput) -> str:
    facts = [f"product_name={product.product_name}", f"category={product.category}", f"key_features={', '.join(product.key_features)}", f"usp={product.usp}"]
    if product.price is not None:
        facts.append(f"price={product.price}")
    return "; ".join(facts)
