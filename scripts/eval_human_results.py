from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path


CRITERIA = ("relevance", "creativity", "tone_match", "persuasiveness", "clarity")


def analyze(path: Path) -> dict[str, object]:
    values: dict[str, list[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            label = row.get("label", "unknown")
            for criterion in CRITERIA:
                values[f"{label}:{criterion}"].append(float(row.get(criterion, 0)))
    report = {}
    for key, scores in values.items():
        report[key] = {
            "mean": statistics.fmean(scores),
            "median": statistics.median(scores),
            "standard_deviation": statistics.pstdev(scores),
            "rater_count": len(scores),
        }
    return report


def main() -> None:
    source = Path(__file__).resolve().parents[1] / "tests" / "human_eval" / "ratings.csv"
    print(analyze(source) if source.exists() else {"status": "pending", "reason": "No human ratings available"})


if __name__ == "__main__":
    main()
