from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Platform = Literal["instagram", "linkedin", "x", "facebook", "whatsapp"]


class CampaignInput(BaseModel):
    """Canonical campaign input accepted by Stage 3."""

    model_config = ConfigDict(extra="forbid")

    product_name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)
    key_features: list[str] = Field(min_length=1, max_length=12)
    price: float | None = Field(default=None, ge=0)
    usp: str = Field(min_length=1, max_length=300)
    brand_name: str = Field(default="", max_length=100)
    brand_voice: str = Field(min_length=1, max_length=100)
    target_audience: str = Field(min_length=1, max_length=100)
    campaign_goal: str = Field(min_length=1, max_length=150)
    platforms: list[Platform] = Field(min_length=1, max_length=6)
    language: str = Field(pattern=r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
    product_image: str | None = Field(default=None, max_length=2048)
    competitor_info: str = Field(default="", max_length=1500)

    @field_validator("key_features")
    @classmethod
    def validate_features(cls, value: list[str]) -> list[str]:
        if len({item.strip() for item in value}) != len(value):
            raise ValueError("key_features must not contain duplicates")
        if any(not item.strip() or len(item.strip()) > 120 for item in value):
            raise ValueError("each key feature must contain 1-120 characters")
        if len(set(value)) != len(value):
            raise ValueError("key_features must contain unique values")
        return value


class ValidationWarning(BaseModel):
    code: str
    field: str | None = None
    message: str


class ValidationFlags(BaseModel):
    prompt_injection_warning: bool = False
    restricted_category: bool = False
    restricted_category_note: str | None = None


class ValidatedInputResponse(BaseModel):
    validated: CampaignInput
    warnings: list[ValidationWarning] = Field(default_factory=list)
    flags: ValidationFlags = Field(default_factory=ValidationFlags)
