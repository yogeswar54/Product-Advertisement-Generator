from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.database import Asset, Campaign, SessionLocal, init_db


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PROJECT_ROOT / "storage" / "assets" / "metadata.json"


def migrate_asset_metadata() -> int:
    """Import existing asset metadata into SQLite without removing the source JSON."""

    if not METADATA_PATH.exists():
        return 0
    records = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Asset metadata must contain a JSON list")

    init_db()
    migrated = 0
    with SessionLocal() as db:
        for record in records:
            asset_id = str(record["id"])
            campaign_id = str(record.get("campaign_id") or "legacy")
            campaign = db.get(Campaign, campaign_id)
            if campaign is None:
                now = datetime.now(timezone.utc)
                db.add(Campaign(
                    id=campaign_id,
                    name=f"Imported {campaign_id}",
                    product_name="Imported asset",
                    status="draft",
                    inputs={},
                    brief={},
                    approval={"status": "draft"},
                    created_time=now,
                    updated_time=now,
                ))
                db.flush()
            path = Path(str(record.get("path", "")))
            filename = path.name if path.name else f"{asset_id}.bin"
            asset_type = str(record.get("asset_type", "image"))
            existing = db.get(Asset, asset_id)
            if existing is None:
                db.add(Asset(
                    id=asset_id,
                    campaign_id=campaign_id,
                    asset_type=asset_type,
                    status="ready" if path.is_file() else "missing",
                    file_name=filename,
                    file_path=str(path),
                    metadata_json=record,
                    created_time=datetime.now(timezone.utc),
                ))
                migrated += 1
        db.commit()
    return migrated


if __name__ == "__main__":
    print(f"Imported {migrate_asset_metadata()} asset metadata records.")
