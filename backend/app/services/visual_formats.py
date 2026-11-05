import json
from pathlib import Path
from typing import Any

FORMATS_PATH = Path(__file__).resolve().parents[3] / "config" / "visual_formats.json"
REQUIRED_FORMATS = {"poster", "banner", "story", "square_social_post"}


def load_visual_formats(path: Path = FORMATS_PATH) -> dict[str, dict[str, Any]]:
    formats = json.loads(path.read_text(encoding="utf-8"))
    if set(formats) != REQUIRED_FORMATS:
        raise ValueError("visual_formats.json must contain poster, banner, story, and square_social_post")
    for name, config in formats.items():
        required = {"name", "aspect_ratio", "width", "height", "safe_zone_notes", "text_guidance", "platforms"}
        if set(config) != required or config["width"] <= 0 or config["height"] <= 0:
            raise ValueError(f"Invalid visual format: {name}")
    return formats
