from __future__ import annotations

from pydantic import BaseModel, Field


class ColorRole(BaseModel):
    hex: str
    role: str


class Typography(BaseModel):
    heading_style: str
    body_style: str


class OnImageText(BaseModel):
    headline: str = Field(max_length=60)
    cta: str = Field(max_length=30)


class VisualConcept(BaseModel):
    name: str
    idea: str
    scene: str
    people_or_models: str
    props_and_product_placement: str
    mood_and_lighting: str
    color_palette: list[ColorRole] = Field(min_length=4, max_length=5)
    typography: Typography
    layouts: dict[str, str]
    on_image_text: OnImageText
    image_prompts: dict[str, str]
    negative_prompt: str


class VisualOutput(BaseModel):
    concepts: list[VisualConcept] = Field(min_length=3, max_length=3)
    prompt_version: str = "visual_concepts_v1"
