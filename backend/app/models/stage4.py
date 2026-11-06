from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput


class CampaignBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")
    core_message: str = Field(min_length=1, max_length=300)
    tone: str = Field(min_length=1, max_length=150)
    emotional_hook: str = Field(min_length=1, max_length=300)
    key_benefits: list[str] = Field(min_length=3, max_length=5)
    audience_profile_reference: str = Field(min_length=1, max_length=100)
    dos_and_donts: dict[str, list[str]]
    prompt_version: str


class DescriptionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    short: str
    medium: str
    long: str
    seo_keywords: list[str] = Field(min_length=1, max_length=10)
    prompt_version: str


class AdCopyVariant(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    style: Literal["banner", "email", "search-ad"]
    text: str = Field(alias="copy")


class ABVariant(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    angle: Literal["urgency", "trust", "fun"]
    id: Literal["A", "B", "C"]
    text: str = Field(alias="copy")


class PromoOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    headlines: list[str] = Field(min_length=5, max_length=5)
    taglines: list[str] = Field(min_length=5, max_length=5)
    ad_copy_variants: list[AdCopyVariant] = Field(min_length=3, max_length=3)
    ctas: list[str] = Field(min_length=5, max_length=10)
    ab_variants: list[ABVariant] = Field(min_length=3, max_length=3)
    prompt_version: str


class BriefRequest(BaseModel):
    product_input: CampaignInput
    audience_profile: AudienceProfile


class GenerateRequest(BaseModel):
    product_input: CampaignInput
    audience_profile: AudienceProfile
    brief: CampaignBrief


class RegenerateRequest(BaseModel):
    product_input: CampaignInput
    audience_profile: AudienceProfile
    brief: CampaignBrief


class Warning(BaseModel):
    code: str
    message: str
