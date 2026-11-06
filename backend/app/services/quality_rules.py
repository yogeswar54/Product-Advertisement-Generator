from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RULES_PATH = Path(__file__).resolve().parents[3] / "config" / "quality_rules.json"


def load_quality_rules() -> dict[str, Any]:
    data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    required = {"rules_version", "absolute_claim_words", "risky_claim_words", "restricted_categories", "severity_mapping", "score_weights", "thresholds"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Quality rules missing required keys: {sorted(missing)}")
    return data
