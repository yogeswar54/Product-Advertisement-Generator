from __future__ import annotations

import re

HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
VALID_ROLES = {"primary", "secondary", "accent", "background", "text"}


def valid_hex(value: str) -> bool:
    return bool(HEX_PATTERN.fullmatch(value))


def luminance(hex_color: str) -> float:
    if not valid_hex(hex_color):
        raise ValueError("Invalid hex color")
    channels = []
    for index in (1, 3, 5):
        value = int(hex_color[index:index + 2], 16) / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(first: str, second: str) -> float:
    first_luminance = luminance(first)
    second_luminance = luminance(second)
    lighter, darker = max(first_luminance, second_luminance), min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def low_contrast(text: str, background: str, threshold: float = 4.5) -> bool:
    return contrast_ratio(text, background) < threshold
