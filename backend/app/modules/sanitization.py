from __future__ import annotations

import html
import re
import unicodedata

SCRIPT_PATTERN = re.compile(r"<(?:script|style)[^>]*>.*?</(?:script|style)>|<[^>]+>", re.IGNORECASE | re.DOTALL)
INJECTION_PATTERNS = (
    r"\b(?:ignore|disregard|override|forget|bypass)\b.{0,60}\b(?:instructions?|prompts?|rules?|polic(?:y|ies)|system|safety|checks?|guardrails?)\b",
    r"\b(?:reveal|print|show|repeat|output|expose)\b.{0,60}\b(?:system prompt|hidden instructions?|api key|secret|developer message)\b",
    r"\b(?:system prompt|hidden instructions?|developer message)\b",
    r"\b(?:act|role[- ]?play|pretend|behave)\s+(?:as|like)\s+(?:(?:an?|my|your|the)\s+)?(?:admin|developer|system|unrestricted|root|assistant)\b",
    r"\byou are now\s+(?:an?\s+)?(?:admin|developer|unrestricted|system)\b",
    r"\bfollow these new instructions\b",
    r"\b(?:jailbreak|prompt injection)\b",
    r"jailbreak",
)
RESTRICTED_TERMS = {
    "health": ("supplement", "treats", "cures", "prevent disease", "medical claim", "medication"),
    "alcohol": ("alcohol", "beer", "wine", "spirits", "cocktail"),
    "finance": ("investment", "loan", "mortgage", "credit", "guaranteed return"),
    "tobacco": ("tobacco", "cigarette", "vape", "nicotine", "cigar"),
}


def normalize_text(value: str, limit: int) -> str:
    """Normalize Unicode, remove markup, decode entities, and trim whitespace."""

    value = unicodedata.normalize("NFKC", value)
    value = SCRIPT_PATTERN.sub(" ", value)
    value = html.unescape(value)
    value = re.sub(r"\bjavascript\s*:", "blocked:", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def has_prompt_injection(value: str) -> bool:
    normalized = unicodedata.normalize("NFKC", value).lower()
    return any(re.search(pattern, normalized, re.IGNORECASE) for pattern in INJECTION_PATTERNS)


def find_restricted_categories(*texts: str | None) -> list[str]:
    combined = " ".join(text for text in texts if text).lower()
    return [category for category, terms in RESTRICTED_TERMS.items() if any(term in combined for term in terms)]
