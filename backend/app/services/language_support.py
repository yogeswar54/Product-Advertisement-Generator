from __future__ import annotations

from app.services.feature_flags import enhancement_enabled
from app.services.prompt_loader import load_prompt


def is_hindi(language: str) -> bool:
    return language.strip().lower().split("-", maxsplit=1)[0] == "hi"


def apply_language_policy(system_prompt: str, language: str) -> str:
    if not is_hindi(language):
        return system_prompt
    if not enhancement_enabled("ENHANCE_HINDI"):
        raise ValueError("Hindi generation requires ENHANCE_HINDI=on")
    policy, _, _ = load_prompt("language_policy_hi_v1", {})
    return f"{system_prompt}\n\n{policy.strip()}"
