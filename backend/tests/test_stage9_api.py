from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


def test_campaign_history_edit_approval_and_export_flow(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_db():
        with Session(engine) as db:
            yield db

    monkeypatch.setattr("app.services.export_service.EXPORT_ROOT", tmp_path / "exports")
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app, raise_server_exceptions=False)
    original_overrides = app.dependency_overrides.copy()
    try:
        created = client.post("/campaigns", json={
            "name": "CampusFlow",
            "inputs": {
                "product_name": "CampusFlow",
                "category": "water bottle",
                "key_features": ["700 ml capacity", "leak-resistant lid"],
                "usp": "Easy campus hydration",
                "brand_name": "CampusFlow",
            },
            "brief": {"core_message": "Easy hydration"},
            "outputs": {
                "descriptions": {
                    "status": "ready",
                    "content": {
                        "short": "CampusFlow holds 700 ml.",
                        "medium": "CampusFlow holds 700 ml for daily use.",
                        "long": "CampusFlow is a reusable bottle with 700 ml capacity.",
                        "seo_keywords": ["campus bottle"],
                        "prompt_version": "description_v1",
                    },
                },
            },
        })
        assert created.status_code == 200
        campaign_id = created.json()["id"]

        report_response = client.post(f"/campaigns/{campaign_id}/quality")
        assert report_response.status_code == 200
        report = report_response.json()
        assert report["overall_status"] in {"pass", "pass_with_warnings"}

        invalid_edit = client.patch(
            f"/campaigns/{campaign_id}/sections/descriptions",
            json={"value": {"short": ""}, "source": "manual_edit"},
        )
        assert invalid_edit.status_code == 422

        approved = client.post(
            f"/campaigns/{campaign_id}/approve",
            params={"approved_by": "test", "report_id": report["report_id"]},
        )
        assert approved.status_code == 200
        export = client.post(f"/campaigns/{campaign_id}/exports", json={"format": "json"})
        assert export.status_code == 200

        package = client.get(f"/campaigns/{campaign_id}/package").json()
        edited = dict(package["descriptions"]["content"])
        edited["short"] = "Edited CampusFlow 700 ml bottle."
        edit_response = client.patch(
            f"/campaigns/{campaign_id}/sections/descriptions",
            json={"value": edited, "source": "manual_edit"},
        )
        assert edit_response.status_code == 200
        assert client.post(f"/campaigns/{campaign_id}/exports", json={"format": "json"}).status_code == 409
        assert client.get(f"/campaigns/{campaign_id}/sections/descriptions/versions").json()
        reverted = client.post(f"/campaigns/{campaign_id}/sections/descriptions/revert")
        assert reverted.status_code == 200

        duplicate = client.post(f"/campaigns/{campaign_id}/duplicate")
        assert duplicate.status_code == 200
        duplicate_id = duplicate.json()["id"]
        assert client.delete(f"/campaigns/{duplicate_id}").status_code == 409
        assert client.delete(f"/campaigns/{duplicate_id}?confirm=true").status_code == 200
        assert client.delete(f"/campaigns/{campaign_id}?confirm=true").status_code == 200
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
        engine.dispose()
