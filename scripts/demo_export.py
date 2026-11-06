from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from datetime import datetime, timezone
from uuid import uuid4

from app.database import Campaign, GeneratedOutput, QualityReport, init_db, SessionLocal
from app.services.package_assembler import assemble_campaign_package
from app.services.export_service import create_export


def main() -> list[str]:
    init_db()
    now = datetime.now(timezone.utc)
    campaign_id = uuid4().hex
    report_id = uuid4().hex
    db = SessionLocal()
    campaign = Campaign(
        id=campaign_id,
        name="CampusFlow Water Bottle",
        product_name="CampusFlow Water Bottle",
        inputs={"product_name": "CampusFlow Water Bottle", "category": "Reusable bottle",
                "audience_summary": {"audience_id": "college_students"}},
        brief={"objective": "Launch awareness"},
        status="approved",
        approval={"status": "approved", "approved_by": "demo", "approved_at": now.isoformat(),
                  "approved_report_id": report_id},
        created_time=now,
        updated_time=now,
    )
    db.add(campaign)
    db.add(QualityReport(id=report_id, campaign_id=campaign_id, data={
        "overall_status": "pass", "overall_score": 100, "findings": [],
        "rules_version": "demo-v1",
    }, created_time=now))
    outputs = {
        "descriptions": {"short": "A reusable bottle designed for campus life."},
        "promo": {"headlines": ["Stay ready for campus."]},
        "social": {"instagram": {"caption": "Hydration made for campus."}},
        "visuals": {"concepts": []},
        "video": {"scripts": []},
    }
    for section, data in outputs.items():
        db.add(GeneratedOutput(campaign_id=campaign_id, section=section, data=data, status="ready", updated_time=now))
    db.commit()

    package = assemble_campaign_package(db, campaign_id)
    paths = []
    for format_name in ("json", "docx", "pdf"):
        export = create_export(db, campaign_id, package, format_name)
        paths.append(export.file_path)
        print(f"{format_name.upper()}: {export.file_path}")
    db.close()
    return paths


if __name__ == "__main__":
    main()
