from __future__ import annotations

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Asset, Base, Campaign
from scripts import migrate_asset_metadata


def test_asset_metadata_migration_preserves_source_and_is_idempotent(tmp_path, monkeypatch):
    source = tmp_path / "metadata.json"
    records = [{
        "id": "asset-id",
        "campaign_id": "campaign-id",
        "asset_type": "audio",
        "path": str(tmp_path / "voice.wav"),
        "provider": "mock",
        "model": "mock",
    }]
    source.write_text(json.dumps(records), encoding="utf-8")
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    monkeypatch.setattr(migrate_asset_metadata, "METADATA_PATH", source)
    monkeypatch.setattr(migrate_asset_metadata, "SessionLocal", test_sessions)
    monkeypatch.setattr(migrate_asset_metadata, "init_db", lambda: Base.metadata.create_all(engine))

    assert migrate_asset_metadata.migrate_asset_metadata() == 1
    with test_sessions() as db:
        asset = db.get(Asset, "asset-id")
        campaign = db.get(Campaign, "campaign-id")
        assert asset is not None
        assert asset.asset_type == "audio"
        assert campaign is not None
    assert json.loads(source.read_text(encoding="utf-8")) == records
    assert migrate_asset_metadata.migrate_asset_metadata() == 0
    engine.dispose()
