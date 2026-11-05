from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Platform = Literal["instagram", "linkedin", "x", "facebook", "whatsapp"]
PostType = Literal["teaser", "feature highlight", "benefit story", "social proof placeholder", "offer or CTA", "user-engagement question", "recap"]


class InstagramPost(BaseModel):
    caption: str
    hashtags: list[str]
    carousel_slide_ideas: list[str]
    reel_hook: str


class LinkedInPost(BaseModel):
    post: str
    hashtags: list[str]


class XPost(BaseModel):
    post: str
    thread: list[str] = Field(default_factory=list)


class FacebookPost(BaseModel):
    post: str
    question_or_poll: str


class WhatsAppPost(BaseModel):
    message: str


class CalendarEntry(BaseModel):
    day: int = Field(ge=1, le=7)
    platform: Platform
    post_type: PostType
    topic: str
    post_reference: str
    suggested_time_slot: str


class SocialOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instagram: InstagramPost | None = None
    linkedin: LinkedInPost | None = None
    x: XPost | None = None
    facebook: FacebookPost | None = None
    whatsapp: WhatsAppPost | None = None
    calendar: list[CalendarEntry] = Field(min_length=7, max_length=7)
    prompt_version: str = "social_v1"
