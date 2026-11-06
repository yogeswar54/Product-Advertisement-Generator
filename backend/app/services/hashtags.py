from __future__ import annotations

import re

CLAIM_TAGS = {"1best", "clinicallyproven", "guaranteedresults", "numberone", "bestintheworld"}


def camel_case(value: str) -> str:
    parts = [part for part in re.split(r"[^A-Za-z0-9]+", value) if part]
    if not parts:
        return ""
    return parts[0].lower() + "".join(part[:1].upper() + part[1:].lower() for part in parts[1:])


def clean_hashtags(values: list[str], minimum: int, maximum: int) -> list[str]:
    if minimum < 0 or maximum < 0 or minimum > maximum:
        raise ValueError("Hashtag range is invalid")
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        tag = camel_case(value.lstrip("#"))
        if not tag or tag.lower() in CLAIM_TAGS:
            continue
        normalized = tag.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append("#" + tag)
    if len(cleaned) > maximum:
        cleaned = cleaned[:maximum]
    return cleaned


def build_hashtags(product_name: str, category: str, audience_id: str, campaign_goal: str, minimum: int, maximum: int) -> list[str]:
    candidates = ["#" + camel_case(product_name), "#" + camel_case(category), "#" + camel_case(audience_id.replace("_", " ")), "#Campaign"]
    if "launch" in campaign_goal.lower():
        candidates.append("#NewProduct")
    if "conversion" in campaign_goal.lower() or "sale" in campaign_goal.lower():
        candidates.append("#ShopNow")
    return clean_hashtags(candidates, minimum, maximum)
