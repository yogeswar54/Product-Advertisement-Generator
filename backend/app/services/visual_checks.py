from __future__ import annotations

import json
import re
from pathlib import Path

from app.models.stage4 import Warning
from app.models.stage6 import VisualOutput
from app.services.visual_helpers import contrast_ratio, valid_hex, VALID_ROLES
from app.services.visual_formats import load_visual_formats

SAFETY_PATH = Path(__file__).resolve().parents[3] / "config" / "image_safety.json"


def run_visual_checks(visual: VisualOutput, supplied_text: str, brand_kit: object | None = None) -> list[Warning]:
    warnings: list[Warning] = []
    formats = load_visual_formats()
    safety = json.loads(SAFETY_PATH.read_text(encoding="utf-8"))
    supplied_numbers = set(re.findall(r"\d+(?:\.\d+)?(?:%)?", supplied_text))
    for concept in visual.concepts:
        roles = {color.role for color in concept.color_palette}
        if len(concept.color_palette) not in (4, 5) or not roles.issubset(VALID_ROLES):
            warnings.append(Warning(code="VISUAL_PALETTE_INVALID", message=f"{concept.name} has an invalid palette or role."))
        if not all(valid_hex(color.hex) for color in concept.color_palette):
            warnings.append(Warning(code="VISUAL_HEX_INVALID", message=f"{concept.name} contains an invalid hex color."))
        background = next((color.hex for color in concept.color_palette if color.role == "background"), None)
        text = next((color.hex for color in concept.color_palette if color.role == "text"), None)
        if background and text and contrast_ratio(text, background) < 4.5:
            warnings.append(Warning(code="VISUAL_LOW_CONTRAST", message=f"{concept.name} text/background contrast is below WCAG 4.5:1."))
        if set(concept.layouts) != set(formats) or set(concept.image_prompts) != set(formats):
            warnings.append(Warning(code="VISUAL_FORMATS_MISSING", message=f"{concept.name} is missing one or more configured formats."))
        prompt_text = " ".join(concept.image_prompts.values()).lower()
        for category in ("blocked_real_person_terms", "blocked_brand_terms", "blocked_artist_terms", "blocked_claim_terms"):
            for term in safety[category]:
                if term.lower() in prompt_text:
                    warnings.append(Warning(code="VISUAL_PROMPT_SAFETY", message=f"{concept.name} image prompt contains blocked term '{term}'."))
        on_image = concept.on_image_text.headline + " " + concept.on_image_text.cta
        for number in re.findall(r"\d+(?:\.\d+)?(?:%)?", on_image):
            if number not in supplied_numbers:
                warnings.append(Warning(code="VISUAL_UNSUPPORTED_NUMBER", message=f"{concept.name} contains unsupported text '{number}'."))
        if brand_kit is not None:
            primary = getattr(brand_kit, "primary_color", None)
            secondary = getattr(brand_kit, "secondary_color", None)
            if primary and secondary and valid_hex(primary) and valid_hex(secondary):
                if contrast_ratio(secondary, primary) < 4.5:
                    warnings.append(Warning(
                        code="VISUAL_BRAND_LOW_CONTRAST",
                        message=f"{concept.name} brand overlay text/background contrast is below WCAG 4.5:1.",
                    ))
    names = [concept.name.strip().lower() for concept in visual.concepts]
    ideas = [concept.idea.strip().lower() for concept in visual.concepts]
    if len(set(names)) != 3 or len(set(ideas)) != 3:
        warnings.append(Warning(code="VISUAL_CONCEPTS_TOO_SIMILAR", message="Visual concepts need more distinct names and ideas."))
    return warnings
