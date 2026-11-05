from __future__ import annotations

import json
from pathlib import Path

from app.models.audience import AudienceProfile, Persona

PERSONA_FILE = Path(__file__).resolve().parents[3] / "data" / "personas.json"
_ALLOWED_FORMAT_NORMALIZATION = {
    "youtube-style short video": "Instagram Reels",
}
_PLATFORM_NORMALIZATION = {
    "youtube-style short video": "instagram",
}
_ALLOWED_PLATFORMS = {"instagram", "linkedin", "x", "facebook", "whatsapp"}
_personas: dict[str, Persona] | None = None


def load_personas(path: Path = PERSONA_FILE) -> list[Persona]:
    global _personas
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("data/personas.json must contain a list")

    normalized: dict[str, Persona] = {}
    for raw in data:
        raw = dict(raw)
        raw["preferred_content_formats"] = [_ALLOWED_FORMAT_NORMALIZATION.get(item, item) for item in raw["preferred_content_formats"]]
        normalized_platforms = [_PLATFORM_NORMALIZATION.get(item, item) for item in raw["best_platforms"]]
        if normalized_platforms != raw["best_platforms"] and "Instagram Reels" not in raw["preferred_content_formats"]:
            raw["preferred_content_formats"] = [*raw["preferred_content_formats"][:], "Instagram Reels"]
        raw["best_platforms"] = normalized_platforms
        persona = Persona.model_validate(raw)
        invalid_platforms = set(persona.best_platforms) - _ALLOWED_PLATFORMS
        if invalid_platforms:
            raise ValueError(f"Persona {persona.id} has unsupported platforms: {sorted(invalid_platforms)}")
        normalized[persona.id] = persona
    _personas = normalized
    return list(normalized.values())


def list_personas() -> list[Persona]:
    if _personas is None:
        return load_personas()
    return list(_personas.values())


def get_persona(persona_id: str) -> Persona:
    if _personas is None:
        load_personas()
    assert _personas is not None
    try:
        return _personas[persona_id]
    except KeyError as exc:
        raise LookupError(f"Persona '{persona_id}' was not found") from exc


def persona_to_profile(persona: Persona) -> AudienceProfile:
    return AudienceProfile(
        tone=persona.tone_of_voice,
        vocabulary_level=persona.vocabulary_level,
        slang_tolerance=persona.slang_tolerance,
        motivations=persona.motivations,
        objections=persona.objections,
        emotional_triggers=persona.emotional_triggers,
        best_platforms=persona.best_platforms,
        preferred_content_formats=persona.preferred_content_formats,
        words_styles_to_avoid=persona.avoid,
    )
