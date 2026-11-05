from __future__ import annotations

from typing import Literal
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

Platform = Literal["instagram", "linkedin", "x", "facebook", "whatsapp"]


class AudienceProfile(BaseModel):
    """Audience profile returned by the Audience Profiler."""

    model_config = ConfigDict(extra="forbid")

    tone: str = Field(min_length=1, max_length=150)
    vocabulary_level: str = Field(min_length=1, max_length=150)
    slang_tolerance: str = Field(min_length=1, max_length=150)
    motivations: list[str] = Field(min_length=1)
    objections: list[str] = Field(min_length=1)
    emotional_triggers: list[str] = Field(min_length=1)
    best_platforms: list[Platform] = Field(min_length=1)
    preferred_content_formats: list[str] = Field(min_length=1)
    words_styles_to_avoid: list[str] = Field(validation_alias=AliasChoices("words_styles_to_avoid", "avoid"), serialization_alias="words_styles_to_avoid", min_length=1)


class Persona(BaseModel):
    """Persona record loaded from data/personas.json."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    name: str
    age_range: str
    interests: list[str]
    motivations: list[str]
    pain_points: list[str]
    objections: list[str]
    tone_of_voice: str
    vocabulary_level: str
    slang_tolerance: str
    emotional_triggers: list[str]
    best_platforms: list[Platform]
    preferred_content_formats: list[str]
    avoid: list[str]


class CustomAudience(BaseModel):
    age_range: str | None = None
    interests: list[str] = Field(default_factory=list)
    income_level: str | None = None
    location: str | None = None
    pain_points: list[str] = Field(default_factory=list)
    tone_preference: str | None = None


class AudienceProfileRequest(BaseModel):
    persona_id: str | None = None
    custom_audience: CustomAudience | None = None
    overrides: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_selector(self) -> "AudienceProfileRequest":
        if self.persona_id is None and self.custom_audience is None:
            raise ValueError("persona_id or custom_audience is required")
        return self
