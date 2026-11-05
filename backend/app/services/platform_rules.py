import json
from pathlib import Path
from typing import Any

RULES_PATH = Path(__file__).resolve().parents[3] / "config" / "platform_rules.json"
ALLOWED_PLATFORMS = {"instagram", "linkedin", "x", "facebook", "whatsapp"}


def load_platform_rules(path: Path = RULES_PATH) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if set(data) != ALLOWED_PLATFORMS:
        raise ValueError("platform_rules.json must contain exactly instagram, linkedin, x, facebook, and whatsapp")
    for platform, rules in data.items():
        required = {"max_characters", "recommended_length", "hashtag_count", "emoji_tolerance", "link_handling", "tone_notes"}
        if set(rules) != required:
            raise ValueError(f"Platform {platform} is missing required rule fields")
        hashtag_range = rules["hashtag_count"]
        if not 0 <= hashtag_range["min"] <= hashtag_range["max"]:
            raise ValueError(f"Platform {platform} has an invalid hashtag range")
        if rules["max_characters"] <= 0 or rules["recommended_length"] <= 0:
            raise ValueError(f"Platform {platform} has an invalid length")
    return data


def platform_rules_text(rules: dict[str, dict[str, Any]], selected: list[str]) -> str:
    return "\n".join(f"{platform}: {rules[platform]}" for platform in selected)
