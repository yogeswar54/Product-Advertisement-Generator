from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class VideoScene(BaseModel):
    scene_number: int = Field(ge=1)
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    visual: str
    narration: str
    on_screen_text: str
    music_mood: str
    sound_effect: str


class VideoScript(BaseModel):
    title: str
    concept: str
    hook: str
    scenes: list[VideoScene]
    narration: str
    cta: str
    estimated_spoken_seconds: float = Field(ge=0)
    pronunciation_hints: dict[str, str] = Field(default_factory=dict)
    prompt_version: str = "video_script_v1"


class VideoOutput(BaseModel):
    scripts_15: VideoScript = Field(alias="15")
    scripts_30: VideoScript = Field(alias="30")
    scripts_60: VideoScript = Field(alias="60")
    prompt_version: str = "video_script_v1"

    model_config = {"populate_by_name": True}
