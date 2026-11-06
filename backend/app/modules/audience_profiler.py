from __future__ import annotations

import re

from app.models.audience import AudienceProfile, AudienceProfileRequest, CustomAudience
from app.modules.persona_library import get_persona, persona_to_profile

BIAS_PATTERNS = (
    r"all\s+(?:men|women|old people|young people|parents|rural people)",
    r"(?:stupid|lazy|uneducated|primitive|inferior)\s+(?:people|customers|buyers)",
    r"people\s+from\s+[^,.]+\s+(?:are|cannot|can never)",
)


def profile_audience(request: AudienceProfileRequest) -> AudienceProfile:
    profile = persona_to_profile(get_persona(request.persona_id)) if request.persona_id else custom_profile(request.custom_audience or CustomAudience())
    if request.overrides:
        allowed = set(AudienceProfile.model_fields)
        unknown = set(request.overrides) - allowed
        if unknown:
            raise ValueError("Unsupported audience profile overrides: " + ", ".join(sorted(unknown)))
        profile = AudienceProfile.model_validate({**profile.model_dump(by_alias=True), **request.overrides})
    if request.language and request.language.strip().lower().split("-", maxsplit=1)[0] == "hi":
        from app.services.feature_flags import enhancement_enabled

        if not enhancement_enabled("ENHANCE_HINDI"):
            raise ValueError("Hindi audience guidance requires ENHANCE_HINDI=on")
        profile.vocabulary_level += (
            "; हिंदी आउटपुट के लिए देवनागरी में स्पष्ट, स्वाभाविक भाषा रखें; "
            "भाषा या क्षेत्र से दर्शक की पहचान का अनुमान न लगाएँ"
        )
    return profile


def custom_profile(custom: CustomAudience) -> AudienceProfile:
    text = " ".join([custom.age_range or "", custom.income_level or "", custom.location or "", custom.tone_preference or "", " ".join(custom.interests), " ".join(custom.pain_points)])
    if bias_matches(text):
        raise ValueError("Custom audience text relies on a prohibited stereotype; describe behavior and needs instead")

    age = (custom.age_range or "").lower()
    if age and any(token in age for token in ("13", "14", "15", "16", "17", "18-24")):
        vocabulary, slang, platforms, tone = "Conversational, plain", "Light; use current terms only when natural", ["instagram", "x", "whatsapp"], "Friendly, energetic, and direct"
    elif age and any(token in age for token in ("60", "65", "70", "senior")):
        vocabulary, slang, platforms, tone = "Plain and accessible", "Minimal", ["facebook", "whatsapp"], "Respectful, calm, and clear"
    else:
        vocabulary, slang, platforms, tone = "Clear professional language", "Low", ["instagram", "linkedin", "facebook"], "Clear, practical, and trustworthy"

    tone = normalize_tone_preference(custom.tone_preference, tone)
    interests = custom.interests[:5] or ["practical value", "ease of use"]
    pain_points = custom.pain_points[:5] or ["lack of clear information"]
    return AudienceProfile(
        tone=tone,
        vocabulary_level=vocabulary,
        slang_tolerance=slang,
        motivations=interests,
        objections=["unclear value", *pain_points[:3]],
        emotional_triggers=["confidence", "convenience", "control"],
        best_platforms=platforms,
        preferred_content_formats=["short explainer", "carousel", "step-by-step demo"],
        avoid=["age stereotypes", "protected-class assumptions", "unsupported claims"],
    )


def normalize_tone_preference(preference: str | None, default: str) -> str:
    if not preference:
        return default
    sanitized = re.sub(r"[^a-zA-Z ,'-]", "", preference).strip()
    return sanitized[:150] if sanitized else default


def bias_matches(text: str) -> bool:
    normalized = text.lower()
    return any(re.search(pattern, normalized) for pattern in BIAS_PATTERNS)
