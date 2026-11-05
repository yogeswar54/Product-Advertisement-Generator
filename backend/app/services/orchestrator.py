from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief, DescriptionOutput, PromoOutput
from app.modules.description_generator import generate_descriptions
from app.modules.promo_generator import generate_promo
from app.modules.social_generator import generate_social
from app.modules.visual_generator import generate_visuals
from app.modules.video_generator import generate_video_scripts
from app.services.video_checks import run_video_checks
from app.services.visual_checks import run_visual_checks
from app.services.social_checks import product_facts, run_social_checks
from app.providers.base import LLMProvider
from app.services.cache import cache_key, get_cached, set_cached
from app.services.lightweight_checks import run_lightweight_checks


def generate_text_package(provider: LLMProvider, product: CampaignInput, audience: AudienceProfile, brief: CampaignBrief) -> dict[str, Any]:
    model_name = getattr(provider, "model", "mock-v1")
    selected_platforms = list(product.platforms)
    key = cache_key(product.model_dump(), audience.model_dump(by_alias=True) | {"selected_platforms": selected_platforms}, "brief_v1:description_v1:promo_v1:social_v1:visual_concepts_v1:video_script_v1", model_name)
    cached = get_cached(key)
    if cached is not None:
        cached = dict(cached)
        cached["cache_hit"] = True
        return cached

    modules: dict[str, Any] = {"description": {"status":"pending"}, "promo":{"status":"pending"}, "social":{"status":"pending", "platforms":{platform:{"status":"pending"} for platform in selected_platforms}}, "visual":{"status":"pending"}, "video":{"status":"pending", "durations":{duration:{"status":"pending"} for duration in (15,30,60)}}}
    description: DescriptionOutput | None = None
    promo: PromoOutput | None = None
    with ThreadPoolExecutor(max_workers=4) as executor:
        description_future = executor.submit(generate_descriptions, provider, product, audience, brief)
        promo_future = executor.submit(generate_promo, provider, product, audience, brief)
        social_future = executor.submit(generate_social, provider, product, audience, brief, selected_platforms)
        visual_future = executor.submit(generate_visuals, provider, product, audience, brief)
        video_future = executor.submit(generate_video_scripts, provider, product, audience, brief)
        try:
            description = description_future.result()
            modules["description"] = {"status":"success", "output":description}
        except Exception as exc:
            modules["description"] = {"status":"failed", "error":str(exc)}
        try:
            promo = promo_future.result()
            modules["promo"] = {"status":"success", "output":promo}
        except Exception as exc:
            modules["promo"] = {"status":"failed", "error":str(exc)}
        try:
            social = social_future.result()
            modules["social"] = {"status":"success", "output":social, "platforms":{platform:{"status":"success"} for platform in selected_platforms}}
        except Exception as exc:
            modules["social"] = {"status":"failed", "error":str(exc), "platforms":{platform:{"status":"failed", "error":str(exc)} for platform in selected_platforms}}
        try:
            visual = visual_future.result()
            modules["visual"] = {"status":"success", "output":visual}
        except Exception as exc:
            modules["visual"] = {"status":"failed", "error":str(exc)}
        try:
            video = video_future.result()
            modules["video"] = {"status":"success", "output":video, "durations":{duration:{"status":"success"} for duration in (15,30,60)}}
        except Exception as exc:
            modules["video"] = {"status":"failed", "error":str(exc), "durations":{duration:{"status":"failed", "error":str(exc)} for duration in (15,30,60)}}

    social_output = modules["social"].get("output")
    warnings = run_lightweight_checks(product, description, promo)
    if social_output:
        warnings.extend(run_social_checks(product, social_output, selected_platforms))
    visual_output = modules["visual"].get("output")
    if visual_output:
        warnings.extend(run_visual_checks(visual_output, product_facts(product)))
    video_output = modules["video"].get("output")
    if video_output:
        warnings.extend(run_video_checks(product, video_output))
    output = {"modules":modules, "warnings":[warning.model_dump() for warning in warnings], "estimated_tokens_used":1450, "provider":"mock" if provider.__class__.__name__ == "MockProvider" else "hosted", "cache_hit":False}
    set_cached(key, output)
    return output
