from __future__ import annotations

from app.models.stage5 import CalendarEntry
from app.services.platform_rules import ALLOWED_PLATFORMS

POST_TYPES = ["teaser", "feature highlight", "benefit story", "social proof placeholder", "offer or CTA", "user-engagement question", "recap"]


def validate_calendar(entries: list[CalendarEntry], selected_platforms: list[str]) -> None:
    if len(entries) != 7:
        raise ValueError("Calendar must contain exactly 7 days")
    if [entry.day for entry in entries] != list(range(1, 8)):
        raise ValueError("Calendar days must be numbered 1 through 7")
    if any(entry.platform not in selected_platforms for entry in entries):
        raise ValueError("Calendar contains an unselected platform")
    if any(entry.post_type not in POST_TYPES for entry in entries):
        raise ValueError("Calendar contains an unsupported post type")
    if not ALLOWED_PLATFORMS.issuperset(selected_platforms):
        raise ValueError("Calendar contains an unsupported platform")
