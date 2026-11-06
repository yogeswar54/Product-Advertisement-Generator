from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.quality import run_quality_check


def main() -> None:
    fixture_path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "quality_cases.json"
    cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    product = {
        "product_name": "CampusFlow",
        "brand_name": "CampusFlow",
        "category": "bottle",
        "usp": "Easy campus hydration",
        "key_features": ["700 ml capacity", "leak-resistant lid"],
        "price": 20,
    }
    metrics: dict[str, dict[str, int]] = {}
    for case in cases:
        expected = case["expected_check"]
        metrics.setdefault(expected, {"tp": 0, "fp": 0, "fn": 0})
        report = run_quality_check(product, {"content": {"text": case["text"]}}, case["id"])
        detected = {finding.check_name for finding in report.findings}
        if case["should_flag"] and expected in detected:
            metrics[expected]["tp"] += 1
        elif case["should_flag"]:
            metrics[expected]["fn"] += 1
        elif detected:
            metrics[expected]["fp"] += 1

    print("check,true_positives,false_positives,false_negatives,precision,recall")
    for check, counts in sorted(metrics.items()):
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        print(f"{check},{tp},{fp},{fn},{precision:.2f},{recall:.2f}")


if __name__ == "__main__":
    main()
