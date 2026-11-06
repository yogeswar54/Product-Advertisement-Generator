from __future__ import annotations

from app.models.input import CampaignInput
from app.services.fact_ledger import build_fact_ledger
from app.services.quality import apply_quality_autofix, run_quality_check
from app.services.quality_rules import load_quality_rules


def product(**changes):
    data = {
        "product_name": "CampusFlow",
        "category": "bottle",
        "key_features": ["700 ml capacity", "leak-resistant lid"],
        "price": 20.0,
        "usp": "Easy campus hydration",
        "brand_name": "CampusFlow",
        "brand_voice": "friendly",
        "target_audience": "college_students",
        "campaign_goal": "sell bottles",
        "platforms": ["instagram"],
        "language": "en-US",
    }
    data.update(changes)
    return CampaignInput(**data)


def test_quality_rules_are_complete():
    rules = load_quality_rules()
    assert rules["rules_version"]
    assert rules["absolute_claim_words"]
    assert rules["restricted_categories"]


def test_fact_ledger_exact_and_number_entries():
    ledger = build_fact_ledger(product())
    assert any(entry.fact_type == "product_name" and entry.value == "CampusFlow" for entry in ledger)
    assert any(entry.fact_type == "price" and entry.value == "20" for entry in ledger)
    assert any(entry.value == "700 ml" for entry in ledger)


def test_absolute_claim_and_clean_content():
    clean = run_quality_check(product().model_dump(), {"description": {"text": "CampusFlow has a leak-resistant lid."}})
    assert clean.overall_status == "pass"
    bad = run_quality_check(product().model_dump(), {"description": {"text": "CampusFlow is the best and clinically proven."}})
    assert bad.overall_status == "blocked"
    assert "absolute_claim" in [finding.check_name for finding in bad.findings]


def test_unsupported_number_and_placeholder():
    report = run_quality_check(product().model_dump(), {"promo": {"text": "Save 90% today with CampusFlow."}})
    assert "unsupported_fact" in [finding.check_name for finding in report.findings]
    placeholder = run_quality_check(product().model_dump(), {"promo": {"text": "[Add a real review here]"}})
    assert not [finding for finding in placeholder.findings if finding.check_name == "unsupported_fact"]


def test_unsupported_fact_check_ignores_structural_metadata():
    report = run_quality_check(product().model_dump(), {
        "description": {
            "text": "CampusFlow carries 700 ml.",
            "prompt_version": "description_v1",
        },
        "social": {"calendar": [{"day": 7, "suggested_time_slot": "09:00"}]},
        "visuals": {"color_palette": [{"hex": "#1F4B99"}]},
    })
    unsupported = [finding for finding in report.findings if finding.check_name == "unsupported_fact"]
    assert not unsupported


def test_autofix_is_reversible_and_diffed():
    campaign = {"description": {"text": "Save 50% today."}}
    report = run_quality_check(product().model_dump(), campaign, "demo")
    finding = next(finding for finding in report.findings if finding.check_name == "unsupported_fact")
    fixed, diffs = apply_quality_autofix(campaign, report.findings, [finding.id])
    assert fixed != campaign
    assert diffs and diffs[0]["before"] != diffs[0]["after"]


def test_blocked_needs_review_and_pass_statuses():
    blocked = run_quality_check(product().model_dump(), {"text": "clinically proven"})
    assert blocked.overall_status == "blocked"
    clean = run_quality_check(product().model_dump(), {"text": "CampusFlow is easy to carry."})
    assert clean.overall_status == "pass"
