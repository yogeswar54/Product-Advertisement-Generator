from __future__ import annotations

import json

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.models.stage6 import ColorRole, VisualOutput
from app.providers.base import LLMProvider
from app.services.json_enforcement import generate_valid_json
from app.services.language_support import apply_language_policy
from app.services.prompt_loader import load_prompt
from app.services.schemas import load_schema
from app.services.visual_formats import load_visual_formats


def generate_visuals(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile, brief: CampaignBrief, promo: object | None = None, product_image_note: str = "No product image uploaded; keep appearance generic.") -> VisualOutput:
    formats = load_visual_formats()
    headline = getattr(promo, "headlines", [])[0] if promo and getattr(promo, "headlines", []) else ""
    formats_prompt = json.dumps(formats, sort_keys=True)
    if product.brand_kit:
        formats_prompt += (
            f"\nPreferred brand palette: primary {product.brand_kit.primary_color}; "
            f"secondary {product.brand_kit.secondary_color}."
        )
    values = {
        "audience_name": product.target_audience, "audience_tone": audience.tone, "audience_vocabulary": audience.vocabulary_level,
        "audience_emotional_triggers": ", ".join(audience.emotional_triggers), "audience_avoid": ", ".join(audience.words_styles_to_avoid),
        "core_message": brief.core_message, "brief_tone": brief.tone, "emotional_hook": brief.emotional_hook,
        "key_benefits": ", ".join(brief.key_benefits), "brief_dos": ", ".join(brief.dos_and_donts["dos"]), "brief_donts": ", ".join(brief.dos_and_donts["donts"]),
        "visual_formats": formats_prompt, "product_facts": "; ".join([f"product_name={product.product_name}", f"category={product.category}", f"key_features={', '.join(product.key_features)}", f"usp={product.usp}", f"promo_headline={headline}"]),
        "product_image_note": product_image_note,
    }
    prompt, temperature, max_tokens = load_prompt("visual_concepts_v1", values)
    system = prompt.split("[AUDIENCE INJECTION]", 1)[0].replace("[SYSTEM]", "", 1).strip()
    system = apply_language_policy(system, product.language)
    user = "[AUDIENCE INJECTION]" + prompt.split("[AUDIENCE INJECTION]", 1)[1]
    data, _, _ = generate_valid_json(provider, system, user, load_schema("visual_output.schema.json"), temperature, max_tokens)
    visual = VisualOutput.model_validate(data)
    if product.brand_kit:
        for concept in visual.concepts:
            for role, color in (
                ("primary", product.brand_kit.primary_color),
                ("secondary", product.brand_kit.secondary_color),
            ):
                existing = next((item for item in concept.color_palette if item.role == role), None)
                if existing:
                    existing.hex = color
                elif len(concept.color_palette) < 5:
                    concept.color_palette.append(ColorRole(hex=color, role=role))
                else:
                    replaceable = next(
                        (
                            item for item in reversed(concept.color_palette)
                            if item.role not in {"background", "text", "primary", "secondary"}
                        ),
                        next(
                            (
                                item for item in reversed(concept.color_palette)
                                if item.role not in {"primary", "secondary"}
                            ),
                            concept.color_palette[-1],
                        ),
                    )
                    replaceable.hex = color
                    replaceable.role = role
    return visual
