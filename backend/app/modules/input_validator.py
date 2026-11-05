from __future__ import annotations

import mimetypes
import re
from urllib.parse import urlparse

from app.models.input import CampaignInput, ValidatedInputResponse, ValidationFlags, ValidationWarning
from app.modules.sanitization import find_restricted_categories, has_prompt_injection, normalize_text

FIELD_LIMITS = {
    "product_name": 100,
    "category": 100,
    "usp": 300,
    "brand_name": 100,
    "brand_voice": 100,
    "target_audience": 100,
    "campaign_goal": 150,
    "competitor_info": 1500,
    "product_image": 2048,
}
ALLOWED_IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def sanitize_input(payload: dict[str, object]) -> dict[str, object]:
    """Trim and sanitize supported text fields while preserving structure."""

    result = dict(payload)
    for field, limit in FIELD_LIMITS.items():
        if isinstance(result.get(field), str):
            result[field] = normalize_text(str(result[field]), limit)
    if isinstance(result.get("key_features"), list):
        result["key_features"] = [normalize_text(str(item), 1200) for item in result["key_features"]]
    return result


def validate_input(payload: dict[str, object], max_image_bytes: int = 10_485_760) -> ValidatedInputResponse:
    sanitized = sanitize_input(payload)
    validated = CampaignInput.model_validate(sanitized)
    text_values = [str(sanitized.get(field, "")) for field in FIELD_LIMITS if field != "product_image"] + [str(item) for item in validated.key_features]

    warnings: list[ValidationWarning] = []
    combined_text = " ".join(text_values)
    if has_prompt_injection(combined_text):
        warnings.append(ValidationWarning(code="PROMPT_INJECTION_WARNING", field=None, message="Text contains a prompt-instruction pattern and should be reviewed."))

    restricted = find_restricted_categories(*text_values)
    note = None
    if restricted:
        note = "Restricted category detected; review advertising rules before publication: " + ", ".join(restricted) + "."

    image = validated.product_image
    if image:
        validate_image_reference(image, max_image_bytes)

    return ValidatedInputResponse(
        validated=validated,
        warnings=warnings,
        flags=ValidationFlags(
            prompt_injection_warning=has_prompt_injection(combined_text),
            restricted_category=bool(restricted),
            restricted_category_note=note,
        ),
    )


def validate_image_reference(reference: str, max_bytes: int) -> None:
    """Validate a URL or uploaded-image metadata string without reading a network resource."""

    parsed = urlparse(reference)
    if parsed.scheme in ("http", "https"):
        suffix = parsed.path.lower()
        mime = mimetypes.guess_type(parsed.path)[0]
        if mime not in ALLOWED_IMAGE_TYPES or not any(suffix.endswith(ext) for ext in ALLOWED_IMAGE_TYPES.values()):
            raise ValueError("product_image must use png, jpg/jpeg, or webp")
        return

    metadata_match = re.match(r"^(image/(?:png|jpeg|webp)):(\d+)$", reference)
    if metadata_match:
        if max_bytes <= 0:
            raise ValueError("MAX_PRODUCT_IMAGE_BYTES must be positive")
        if int(metadata_match.group(2)) > max_bytes:
            raise ValueError("product_image exceeds the configured maximum size")
        return

    if max_bytes <= 0:
        raise ValueError("MAX_PRODUCT_IMAGE_BYTES must be positive")
    raise ValueError("product_image must be an image URL or supported image metadata")
