from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.models.stage5 import SocialOutput
from app.providers.base import LLMProvider
from app.services.hashtags import build_hashtags, clean_hashtags
from app.services.json_enforcement import generate_valid_json
from app.services.language_support import apply_language_policy, is_hindi
from app.services.platform_rules import load_platform_rules, platform_rules_text
from app.services.prompt_loader import load_prompt
from app.services.schemas import load_schema


def generate_social(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile, brief: CampaignBrief, selected_platforms: list[str]) -> SocialOutput:
    rules = load_platform_rules()
    values = {
        "audience_name": product.target_audience, "audience_tone": audience.tone, "audience_vocabulary": audience.vocabulary_level,
        "audience_slang_tolerance": audience.slang_tolerance, "audience_emotional_triggers": ", ".join(audience.emotional_triggers),
        "audience_avoid": ", ".join(audience.words_styles_to_avoid), "core_message": brief.core_message,
        "brief_tone": brief.tone, "emotional_hook": brief.emotional_hook, "key_benefits": ", ".join(brief.key_benefits),
        "brief_dos": ", ".join(brief.dos_and_donts["dos"]), "brief_donts": ", ".join(brief.dos_and_donts["donts"]),
        "platform_rules": platform_rules_text(rules, selected_platforms), "selected_platforms": ", ".join(selected_platforms),
        "product_facts": "; ".join([f"product_name={product.product_name}", f"category={product.category}", f"key_features={', '.join(product.key_features)}", f"usp={product.usp}"]),
    }
    prompt, temperature, max_tokens = load_prompt("social_v1", values)
    system = prompt.split("[AUDIENCE INJECTION]", 1)[0].replace("[SYSTEM]", "", 1).strip()
    system = apply_language_policy(system, product.language)
    user = "[AUDIENCE INJECTION]" + prompt.split("[AUDIENCE INJECTION]", 1)[1]
    combined: dict[str, Any] = {platform: None for platform in rules}
    prompt_version = "social_v1:language_policy_hi_v1" if is_hindi(product.language) else "social_v1"
    combined.update({"calendar": [], "prompt_version": prompt_version})

    for platform in selected_platforms:
        platform_prompt = user + f"\nGenerate only the '{platform}' platform object for this call."
        data, _, _ = generate_valid_json(provider, system, platform_prompt, load_schema("social_output.schema.json"), temperature, max_tokens)
        combined[platform] = data.get(platform)

    calendar_values = {"audience_name": product.target_audience, "audience_tone": audience.tone, "audience_motivations": ", ".join(audience.motivations),
                      "core_message": brief.core_message, "campaign_goal": product.campaign_goal, "selected_platforms": ", ".join(selected_platforms), "platform_rules": platform_rules_text(rules, selected_platforms)}
    calendar_prompt, calendar_temperature, calendar_tokens = load_prompt("calendar_v1", calendar_values)
    calendar_data, _, _ = generate_valid_json(provider, system, calendar_prompt, load_schema("social_output.schema.json"), calendar_temperature, calendar_tokens)
    combined["calendar"] = calendar_data["calendar"]

    for platform in selected_platforms:
        post = combined.get(platform)
        if isinstance(post, dict) and "hashtags" in post:
            limits = rules[platform]["hashtag_count"]
            post["hashtags"] = clean_hashtags(post["hashtags"], limits["min"], limits["max"])
    return SocialOutput.model_validate(combined)
