from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.models.stage8 import QualityFinding
from app.modules.sanitization import has_prompt_injection
from app.services.language_support import is_hindi


@dataclass(frozen=True)
class CheckContext:
    content: Any
    product: dict[str, Any]
    rules: dict[str, Any]
    section: str = "campaign"
    language: str = "en-US"


class QualityCheck:
    name = "quality_check"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        raise NotImplementedError


def _walk(value: Any, path: str = "") -> list[tuple[str, str]]:
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in _walk(child, f"{path}.{key}" if path else key)]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in _walk(child, f"{path}[{index}]")]
    if isinstance(value, (str, int, float)):
        return [(path, str(value))]
    return []


def _finding(check: QualityCheck, context: CheckContext, location: str, text: str, explanation: str, suggested_fix: str, severity: str, auto_fix: bool = False) -> QualityFinding:
    rules = context.rules["severity_mapping"]
    severity = rules.get(check.name, severity)
    return QualityFinding(
        id=f"{check.name}-{len(location) + sum(map(ord, text))}",
        check_name=check.name,
        module=context.section,
        location=location,
        text=text,
        severity=severity,
        explanation=explanation,
        suggested_fix=suggested_fix,
        auto_fix_available=auto_fix,
    )


class AbsoluteClaimCheck(QualityCheck):
    name = "absolute_claim"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        found = []
        language_rules = context.rules.get("language_support", {}).get("hi", {})
        terms = list(context.rules["absolute_claim_words"])
        if is_hindi(context.language):
            terms.extend(language_rules.get("absolute_claim_words", []))
        for term in terms:
            for location, text in _walk(context.content):
                if term.lower() in text.lower() and "[add a" not in text.lower():
                    found.append(_finding(self, context, location, text, f"Contains unverifiable absolute claim '{term}'.", f"Replace '{term}' with a specific, evidence-backed statement.", "critical"))
        return found


class UnsupportedFactCheck(QualityCheck):
    name = "unsupported_fact"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        supplied_text = " ".join(str(value) for key, value in context.product.items() if key in {"product_name", "category", "usp", "brand_name", "key_features"})
        if context.product.get("price") is not None:
            supplied_text += f" {context.product['price']:g}"
        supplied_numbers = set(re.findall(r"\d+(?:\.\d+)?(?:%)?(?:ml|gb|kg)?", supplied_text, re.IGNORECASE))
        found = []
        for location, text in _walk(context.content):
            normalized_path = location.lower()
            if any(part in normalized_path for part in (
                "prompt_version", "image_prompts", "color_palette", ".day", "posting_order",
                "estimated_word_count", "duration_seconds", "suggested_time_slot",
            )):
                continue
            if re.fullmatch(r"#[0-9a-f]{6}", text.strip(), re.IGNORECASE):
                continue
            if re.search(r"\[(?:add|insert)[^\]]+\]", text, re.IGNORECASE):
                continue
            for number in re.findall(r"\d+(?:\.\d+)?(?:%)?(?:ml|gb|kg)?", text, re.IGNORECASE):
                if number.lower() not in {item.lower() for item in supplied_numbers}:
                    found.append(_finding(self, context, location, text, f"Number '{number}' is not supported by the campaign input.", f"Replace '{number}' with [Add verified value here].", "critical", True))
                    break
        return found


class RestrictedCategoryCheck(QualityCheck):
    name = "restricted_category"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        found = []
        category = str(context.product.get("category", "")).lower()
        text_blocks = " ".join(text.lower() for _, text in _walk(context.content))
        language_terms = context.rules.get("language_support", {}).get("hi", {}).get("restricted_category_terms", {})
        for category_name, rule in context.rules["restricted_categories"].items():
            terms = rule["terms"] if isinstance(rule["terms"], list) else list(rule["terms"])
            if is_hindi(context.language):
                terms = [*terms, *language_terms.get(category_name, [])]
            if category_name.lower() in category or any(term.lower() in text_blocks for term in terms):
                for location, text in _walk(context.content):
                    if any(term.lower() in text.lower() for term in terms):
                        found.append(_finding(self, context, location, text, rule["rule"], rule["disclaimer"], "critical"))
        return found


class PromptInjectionCheck(QualityCheck):
    name = "prompt_injection_echo"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        found = []
        language_phrases = context.rules.get("language_support", {}).get("hi", {}).get("prompt_injection_phrases", [])
        for location, text in _walk(context.content):
            if has_prompt_injection(text) or (
                is_hindi(context.language) and any(phrase in text for phrase in language_phrases)
            ):
                found.append(_finding(self, context, location, text, "Generated content echoes embedded instruction text.", "Remove the instruction-like text without rewriting supported product claims.", "critical"))
        return found


class PersonalDataCheck(QualityCheck):
    name = "personal_data"

    def run(self, context: CheckContext) -> list[QualityFinding]:
        supplied = json.dumps(context.product).lower()
        found = []
        for location, text in _walk(context.content):
            for match in re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE):
                if match.lower() not in supplied:
                    found.append(_finding(self, context, location, text, f"Email address '{match}' is not supplied by the user.", "Remove or replace the email with approved campaign contact details.", "critical"))
        return found


ALL_CHECKS: list[QualityCheck] = [UnsupportedFactCheck(), AbsoluteClaimCheck(), RestrictedCategoryCheck(), PromptInjectionCheck(), PersonalDataCheck()]
