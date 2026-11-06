from __future__ import annotations

import re

from app.models.input import CampaignInput
from app.models.stage4 import DescriptionOutput, PromoOutput, Warning


def run_lightweight_checks(product: CampaignInput, description: DescriptionOutput | None = None, promo: PromoOutput | None = None) -> list[Warning]:
    warnings: list[Warning] = []
    texts = []
    if description:
        texts.extend([description.short, description.medium, description.long])
    if promo:
        texts.extend(promo.headlines + promo.taglines + [item.text for item in promo.ad_copy_variants] + [item.text for item in promo.ab_variants])
    supplied_numbers = set(re.findall(r"(?<!\w)\d+(?:\.\d+)?(?:%)?(?!\w)", product_facts_text(product)))
    combined = " ".join(texts)
    for number in re.findall(r"(?<!\w)\d+(?:\.\d+)?(?:%)?(?!\w)", combined):
        if number not in supplied_numbers:
            warnings.append(Warning(code="UNSUPPORTED_NUMBER", message=f"Copy contains number '{number}' that was not supplied in product input."))
            break
    if promo:
        normalized = [item.strip().lower() for item in promo.headlines + promo.taglines]
        if len(normalized) != len(set(normalized)):
            warnings.append(Warning(code="DUPLICATE_COPY", message="Duplicate headline or tagline text was detected."))
        for headline in promo.headlines:
            if len(headline) > 60:
                warnings.append(Warning(code="PROMO_LENGTH", message=f"Headline exceeds 60 characters: {headline}"))
    return warnings


def product_facts_text(product: CampaignInput) -> str:
    parts = [product.product_name, product.category, product.usp, " ".join(product.key_features)]
    if product.price is not None:
        parts.append(str(product.price))
    return " ".join(part for part in parts if part)
