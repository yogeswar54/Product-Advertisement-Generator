from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.database import Campaign, GeneratedOutput, QualityReport


SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "campaign_package.schema.json"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def assemble_campaign_package(db: Session, campaign_id: str) -> dict[str, Any]:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise KeyError(campaign_id)

    outputs = {row.section: {"status": row.status, "content": row.data} for row in
               db.query(GeneratedOutput).filter(GeneratedOutput.campaign_id == campaign_id).all()}

    report_rows = db.query(QualityReport).filter(QualityReport.campaign_id == campaign_id).order_by(
        QualityReport.created_time.desc()).all()
    report = report_rows[0].data if report_rows else {}

    approval = dict(campaign.approval or {})
    package = {
        "package_id": f"{campaign_id}:{_iso(campaign.updated_time)}",
        "campaign_id": campaign_id,
        "created_time": _iso(campaign.created_time),
        "updated_time": _iso(campaign.updated_time),
        "product_input": dict(campaign.inputs or {}),
        "audience_summary": dict((campaign.inputs or {}).get("audience", {})),
        "campaign_brief": dict(campaign.brief or {}),
        "descriptions": outputs.get("descriptions", {"status": "missing", "content": {}}),
        "promo": outputs.get("promo", {"status": "missing", "content": {}}),
        "social": outputs.get("social", {"status": "missing", "content": {}}),
        "visuals": outputs.get("visuals", {"status": "missing", "content": {}}),
        "video": outputs.get("video", {"status": "missing", "content": {}}),
        "quality_summary": {
            "status": report.get("overall_status", "missing"),
            "score": report.get("overall_score", 0),
            "open_findings_count": sum(
                1 for item in report.get("findings", [])
                if item.get("status", "open") == "open"
            ),
        },
        "approval": {
            "status": approval.get("status", campaign.status),
            "approved_by": approval.get("approved_by"),
            "approved_at": approval.get("approved_at"),
            "approved_report_id": approval.get("approved_report_id"),
        },
        "prompt_versions": [],
        "rules_version": campaign.inputs.get("rules_version"),
        "model_names": [],
        "disclosure": json.loads((Path(__file__).resolve().parents[3] / "config" / "export_settings.json").read_text(encoding="utf-8"))["disclosure_text"],
    }
    return package
