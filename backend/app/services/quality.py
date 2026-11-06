from __future__ import annotations

import copy
import hashlib
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.stage8 import QualityFinding, QualityReport
from app.services.language_support import is_hindi
from app.services.quality_checks import ALL_CHECKS, CheckContext
from app.services.quality_rules import load_quality_rules

JUDGE_CACHE: dict[str, dict[str, Any]] = {}


def _flatten(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value)


def run_quality_check(product: dict[str, Any], campaign: dict[str, Any], campaign_reference: str = "campaign", section: str | None = None) -> QualityReport:
    rules = load_quality_rules()
    language = str(product.get("language", "en-US"))
    hindi = is_hindi(language)
    content = campaign if section is None else campaign.get(section, {})
    findings: list[QualityFinding] = []
    context = CheckContext(content=content, product=product, rules=rules, section=section or "campaign", language=language)
    for check in ALL_CHECKS:
        findings.extend(check.run(context))

    module_scores: dict[str, float] = {}
    for module in sorted({finding.module for finding in findings} | ({section} if section else {"campaign"})):
        module_findings = [finding for finding in findings if finding.module == module]
        penalty = sum(rules["score_weights"]["severity"][finding.severity] for finding in module_findings)
        module_scores[module] = max(0.0, 100.0 - penalty)
    if not module_scores:
        module_scores = {section or "campaign": 100.0}
    overall_penalty = sum(rules["score_weights"]["severity"][finding.severity] for finding in findings)
    overall_score = max(0.0, 100.0 - overall_penalty)
    statuses = {finding.severity for finding in findings if finding.status == "open"}
    if "critical" in statuses:
        overall_status = "blocked"
    elif "major" in statuses:
        overall_status = "needs_review"
    elif statuses:
        overall_status = "pass_with_warnings"
    else:
        overall_status = "pass"
    applicability = {
        "unsupported_fact": "language-aware",
        "absolute_claim": "language-aware" if hindi else "English only",
        "restricted_category": "language-aware" if hindi else "English only",
        "prompt_injection_echo": "language-aware" if hindi else "English only",
        "personal_data": "language-aware",
        "readability": "skipped for this language" if hindi else "English only",
        "stop_words": "skipped for this language" if hindi else "English only",
    }
    language_notes = []
    prompt_versions = ["judge_tone_v1", "judge_consistency_v1", "judge_facts_v1"] if os.getenv("QUALITY_LLM_JUDGE", "off") == "on" else []
    if hindi:
        language_notes.extend([
            "Hindi output has not been reviewed by a native speaker.",
            "Hindi readability is not measured; no Flesch Reading Ease score is reported. Readability and stop-word checks are not implemented for any language.",
            str(rules.get("language_support", {}).get("hi", {}).get("starting_version_note", "Hindi quality terms require native-speaker review.")),
        ])
        prompt_versions.append("language_policy_hi_v1")
    return QualityReport(
        report_id=str(uuid.uuid4()),
        campaign_reference=campaign_reference,
        rules_version=rules["rules_version"],
        prompt_versions=prompt_versions,
        timestamp=datetime.now(timezone.utc).isoformat(),
        overall_status=overall_status,
        overall_score=overall_score,
        module_scores=module_scores,
        findings=findings,
        check_applicability=applicability,
        language_notes=language_notes,
    )


def apply_quality_autofix(campaign: dict[str, Any], findings: list[QualityFinding], finding_ids: list[str]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    fixed = copy.deepcopy(campaign)
    diffs: list[dict[str, str]] = []
    selected = {finding_id for finding_id in finding_ids}
    for finding in findings:
        if finding.id not in selected or not finding.auto_fix_available or finding.status != "open":
            continue
        for path in [finding.location.split(".")]:
            current: Any = fixed
            for key in path[:-1]:
                current = current[key]
            leaf = path[-1]
            before = str(current.get(leaf, "")) if isinstance(current, dict) else ""
            after = re.sub(r"\b\d+(?:\.\d+)?(?:%|ml|gb|kg)?\b", "[Add verified value here]", before)
            if isinstance(current, dict):
                current[leaf] = after
            diffs.append({"finding_id": finding.id, "before": before, "after": after})
            finding.status = "fixed"
            break
    return fixed, diffs
