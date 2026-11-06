from __future__ import annotations

import itertools
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.models.input import CampaignInput
from app.models.audience import AudienceProfileRequest
from app.modules.audience_profiler import profile_audience
from app.modules.brief_builder import build_brief
from app.modules.persona_library import load_personas
from app.providers.factory import get_llm_provider
from app.services.orchestrator import generate_text_package
from app.services.platform_rules import load_platform_rules


SAMPLES = [
    {
        "name": "CampusFlow Bottle",
        "category": "Reusable water bottle",
        "facts": ["700 ml capacity", "leak-resistant lid"],
        "usp": "A reusable bottle made for campus routines",
        "price": None,
    },
    {
        "name": "Northstar Desk Lamp",
        "category": "LED desk lamp",
        "facts": ["3 brightness levels", "USB-C power input"],
        "usp": "A compact lamp for focused desk work",
        "price": None,
    },
    {
        "name": "TrailPack 25L",
        "category": "Daypack",
        "facts": ["25 liter capacity", "water-resistant shell"],
        "usp": "A daypack for ordinary trail and commute essentials",
        "price": None,
    },
    {
        "name": "QuietBean Grinder",
        "category": "Coffee grinder",
        "facts": ["12 grind settings", "120 g hopper capacity"],
        "usp": "A countertop grinder with adjustable settings",
        "price": None,
    },
]
PLATFORMS = ("instagram", "linkedin", "x", "facebook", "whatsapp")
MODULE_SCHEMAS = {
    "description": "description_output.schema.json",
    "promo": "promo_output.schema.json",
    "social": "social_output.schema.json",
    "visual": "visual_output.schema.json",
    "video": "video_output.schema.json",
}


def readability(text: str) -> float | None:
    words = re.findall(r"\b[\w'-]+\b", text)
    sentence_count = len(re.findall(r"[.!?]+", text)) or (1 if words else 0)
    if not words or not sentence_count:
        return None
    syllables = sum(max(1, len(re.findall(r"[aeiouy]+", word.lower()))) for word in words)
    return 206.835 - 1.015 * len(words) / sentence_count - 84.6 * syllables / len(words)


def _copy_strings(value: Any, path: str = "") -> list[str]:
    if isinstance(value, dict):
        return [
            text
            for key, child in value.items()
            if key not in {"prompt_version", "id", "day", "posting_order", "title", "color_palette", "image_prompts"}
            for text in _copy_strings(child, f"{path}.{key}")
        ]
    if isinstance(value, list):
        return [text for child in value for text in _copy_strings(child, path)]
    return [value] if isinstance(value, str) else []


def _jaccard(left: str, right: str) -> float:
    left_words = set(re.findall(r"\w+", left.lower()))
    right_words = set(re.findall(r"\w+", right.lower()))
    return len(left_words & right_words) / len(left_words | right_words) if left_words | right_words else 1.0


def _model_dump(value: Any) -> Any:
    return value.model_dump(mode="json", by_alias=True) if hasattr(value, "model_dump") else value


def run_metrics(live: bool = False) -> dict[str, Any]:
    if live and not os.getenv("LLM_API_KEY"):
        raise RuntimeError("Live metrics require the operator to configure LLM_API_KEY.")
    if not live:
        os.environ["LLM_PROVIDER"] = "mock"
    provider = get_llm_provider()
    platform_rules = load_platform_rules()
    personas = load_personas()
    report: dict[str, Any] = {
        "provider_mode": "live" if live else "mock",
        "target_basis": "Estimates are project test goals, not external benchmarks.",
        "samples": {},
        "aggregate": {},
    }
    headline_texts: dict[str, list[str]] = {}
    persona_readability: dict[str, list[float]] = {}
    similarities: list[float] = []
    length_results: list[bool] = []
    fact_results: list[bool] = []
    keyword_results: list[bool] = []
    forbidden_results: list[bool] = []
    schema_results: list[bool] = []
    elapsed_values: list[float] = []
    total = len(SAMPLES) * len(personas)
    completed = 0

    for sample in SAMPLES:
        per_sample: dict[str, Any] = {}
        product_headlines: list[str] = []
        persona_texts: dict[str, str] = {}
        product_payload = " ".join(
            [sample["name"], sample["category"], sample["usp"], *sample["facts"]]
        )
        input_numbers = set(re.findall(r"\d+(?:\.\d+)?", product_payload))
        for persona in personas:
            product = CampaignInput(
                product_name=sample["name"],
                category=sample["category"],
                key_features=sample["facts"],
                price=sample["price"],
                usp=sample["usp"],
                brand_name=sample["name"].split()[0],
                brand_voice="clear and practical",
                target_audience=persona.id,
                campaign_goal="Build product awareness",
                platforms=list(PLATFORMS),
                language="en-US",
            )
            audience = profile_audience(AudienceProfileRequest(persona_id=persona.id))
            started = time.perf_counter()
            brief = build_brief(provider, product, audience)
            generated = generate_text_package(provider, product, audience, brief)
            elapsed = time.perf_counter() - started
            elapsed_values.append(elapsed)
            completed += 1
            modules = generated["modules"]

            schema_valid = True
            for module_name, schema_file in MODULE_SCHEMAS.items():
                module = modules.get(module_name, {})
                if module.get("status") != "success":
                    schema_valid = False
                    continue
                try:
                    schema_path = ROOT / "schemas" / schema_file
                    jsonschema.validate(_model_dump(module["output"]), json.loads(schema_path.read_text(encoding="utf-8")))
                except (jsonschema.ValidationError, ValueError):
                    schema_valid = False
            schema_results.append(schema_valid)

            description = _model_dump(modules.get("description", {}).get("output"))
            promo = _model_dump(modules.get("promo", {}).get("output"))
            social = _model_dump(modules.get("social", {}).get("output"))
            serialized_modules = {
                name: _model_dump(module.get("output"))
                for name, module in modules.items()
                if isinstance(module, dict) and module.get("status") == "success"
            }
            all_strings = _copy_strings(serialized_modules)
            output_text = " ".join(all_strings)
            persona_texts[persona.id] = output_text
            output_numbers = set(re.findall(r"\d+(?:\.\d+)?", output_text))
            fact_ok = output_numbers.issubset(input_numbers)
            fact_results.append(fact_ok)

            social_posts = [
                (platform, (social or {}).get(platform, {}))
                for platform in PLATFORMS
                if isinstance((social or {}).get(platform), dict)
            ]
            for platform, post in social_posts:
                body = str(post.get("caption") or post.get("post") or post.get("message") or "")
                compliant = len(body) <= platform_rules[platform]["max_characters"]
                length_results.append(compliant)
            headline_values = (promo or {}).get("headlines", [])
            product_headlines.extend(str(headline) for headline in headline_values)
            if description:
                text = " ".join(str(description.get(key, "")) for key in ("short", "medium", "long"))
                score = readability(text)
                if score is not None:
                    persona_readability.setdefault(persona.id, []).append(score)
            copy_for_metrics = " ".join(_copy_strings({"description": description, "promo": promo, "social": social}))
            benefits = list(brief.key_benefits)
            keyword_results.extend(
                any(benefit.lower() in copy_for_metrics.lower() for benefit in [*benefits, *(description or {}).get("seo_keywords", [])])
                for benefit in [*benefits, *(description or {}).get("seo_keywords", [])]
            )
            forbidden_results.append(not any(word.lower() in copy_for_metrics.lower() for word in audience.words_styles_to_avoid))

            per_sample[persona.id] = {
                "provider": generated["provider"],
                "duration_seconds": round(elapsed, 3),
                "social_posts_within_platform_limits": sum(
                    len(str(post.get("caption") or post.get("post") or post.get("message") or "")) <= platform_rules[platform]["max_characters"]
                    for platform, post in social_posts
                ),
                "social_posts_checked": len(social_posts),
                "numbers_supported": fact_ok,
                "schemas_valid_after_generation": schema_valid,
                "headline_count": len(headline_values),
                "quality_status": (generated.get("quality") or {}).get("overall_status", "not_completed"),
            }
        headline_texts[sample["name"]] = product_headlines
        product_unique = len(set(headline.lower().strip() for headline in product_headlines))
        report["samples"][sample["name"]] = {
            "persona_count": len(per_sample),
            "headline_uniqueness_percent": round(100 * product_unique / max(len(product_headlines), 1), 2),
            "persona_results": per_sample,
        }
        for left, right in itertools.combinations(persona_texts, 2):
            similarities.append(_jaccard(persona_texts[left], persona_texts[right]))

    def percent(values: list[bool]) -> float | None:
        return round(100 * sum(values) / len(values), 2) if values else None

    report["aggregate"] = {
        "product_count": len(SAMPLES),
        "persona_count": len(personas),
        "generation_runs": completed,
        "social_length_compliance_percent": percent(length_results),
        "description_length_ranges": "Not scored: no authoritative range values are configured.",
        "headline_length_compliance": "Not scored: no headline limit is configured.",
        "readability_by_persona": {
            key: {
                "mean": round(statistics.fmean(values), 2),
                "range": [round(min(values), 2), round(max(values), 2)],
                "n": len(values),
            }
            for key, values in persona_readability.items()
        },
        "fact_fidelity_percent": percent(fact_results),
        "schema_valid_after_generation_percent": percent(schema_results),
        "schema_valid_first_attempt": "Not exposed by the current generation interface.",
        "keyword_inclusion_percent": percent(keyword_results),
        "forbidden_word_compliance_percent": percent(forbidden_results),
        "mean_persona_jaccard_similarity": round(statistics.fmean(similarities), 4) if similarities else None,
        "mean_generation_duration_seconds": round(statistics.fmean(elapsed_values), 3) if elapsed_values else None,
        "estimated_targets": {
            "social_length_compliance_percent": {"target": 100, "reason": "Configured hard platform limits should be satisfied."},
            "fact_fidelity_percent": {"target": 100, "reason": "Unsupported numerical product claims are high risk."},
            "schema_valid_after_generation_percent": {"target": 100, "reason": "Outputs must conform to existing JSON contracts."},
        },
    }
    return report


def main() -> None:
    live = "--live" in sys.argv
    metrics = run_metrics(live=live)
    output_dir = ROOT / "docs" / "stage10"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / f"content_metrics_{metrics['provider_mode']}.json"
    result_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
