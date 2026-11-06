from __future__ import annotations

import os
from typing import Literal


FeatureFlag = Literal["ENHANCE_HINDI", "ENHANCE_BRAND_KIT"]


def enhancement_enabled(name: FeatureFlag) -> bool:
    value = os.getenv(name, "off").strip().lower()
    if value not in {"off", "on"}:
        raise ValueError(f"{name} must be off or on")
    return value == "on"
