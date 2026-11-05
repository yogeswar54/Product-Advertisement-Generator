from __future__ import annotations

import json

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.models.stage6 import VisualOutput
from app.models.stage7 import VideoOutput
from app.providers.base import LLMProvider
from app.services.json_enforcement import generate_valid_json
from app.services.prompt_loader import load_prompt
from app.services.schemas import load_schema
from app.services.video_formats import load_video_formats, spoken_duration_seconds


def generate_video_scripts(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile, brief: CampaignBrief, visual: VisualOutput | None = None) -> VideoOutput:
    formats = load_video_formats()
    visual_summary = "Generic product appearance; no product image supplied." if visual is None else "; ".join(concept.name + ": " + concept.mood_and_lighting for concept in visual.concepts)
    values = {
        "audience_name": product.target_audience, "audience_tone": audience.tone, "audience_vocabulary": audience.vocabulary_level,
        "audience_slang_tolerance": audience.slang_tolerance, "audience_emotional_triggers": ", ".join(audience.emotional_triggers),
        "audience_avoid": ", ".join(audience.words_styles_to_avoid), "core_message": brief.core_message, "brief_tone": brief.tone,
        "emotional_hook": brief.emotional_hook, "key_benefits": ", ".join(brief.key_benefits), "brief_dos": ", ".join(brief.dos_and_donts["dos"]),
        "brief_donts": ", ".join(brief.dos_and_donts["donts"]), "video_formats": json.dumps(formats, sort_keys=True),
        "speaking_pace": formats["30"]["speaking_pace_words_per_second"], "visual_summary": visual_summary,
        "product_facts": "; ".join([f"product_name={product.product_name}", f"category={product.category}", f"key_features={', '.join(product.key_features)}", f"usp={product.usp}"]),
    }
    prompt, temperature, max_tokens = load_prompt("video_script_v1", values)
    system = prompt.split("[AUDIENCE INJECTION]", 1)[0].replace("[SYSTEM]", "", 1).strip()
    user = "[AUDIENCE INJECTION]" + prompt.split("[AUDIENCE INJECTION]", 1)[1]
    data, _, _ = generate_valid_json(provider, system, user, load_schema("video_output.schema.json"), temperature, max_tokens)
    return VideoOutput.model_validate(data)
