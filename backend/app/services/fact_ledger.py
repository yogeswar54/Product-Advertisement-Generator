from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from app.models.input import CampaignInput


@dataclass(frozen=True)
class LedgerEntry:
    fact_type: str
    value: str
    origin: str
    derived: bool = False
    note: str | None = None


def build_fact_ledger(product: CampaignInput) -> list[LedgerEntry]:
    """Build exact and derived factual entries from validated campaign input."""
    entries = [
        LedgerEntry("product_name", product.product_name, "input"),
        LedgerEntry("brand", product.brand_name, "input"),
        LedgerEntry("category", product.category, "input"),
        LedgerEntry("usp", product.usp, "input"),
    ]
    for feature in product.key_features:
        entries.append(LedgerEntry("feature", feature, "input"))
    if product.price is not None:
        entries.append(LedgerEntry("price", f"{product.price:g}", "input"))
    text = " ".join([product.product_name, product.category, product.usp, *product.key_features])
    for number in re.findall(r"\b\d+(?:\.\d+)?(?:\s*(?:%|ml|gb|kg|oz))?\b", text, re.IGNORECASE):
        entries.append(LedgerEntry("number", number, "input"))
    return entries


def ledger_values(entries: list[LedgerEntry]) -> set[str]:
    return {entry.value.lower() for entry in entries}


def ledger_as_dict(entries: list[LedgerEntry]) -> list[dict]:
    return [asdict(entry) for entry in entries]
