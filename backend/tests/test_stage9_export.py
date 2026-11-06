from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Asset, Base, Campaign, GeneratedOutput, QualityReport
from app.services.export_service import (
    EXPORT_ROOT, create_export, create_zip, export_gate, load_export_settings,
    render_docx, render_json, render_pdf, validate_package,
)
from app.services.package_assembler import assemble_campaign_package


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_stage9_package_and_json_export():
    db = _session()
    now = datetime.now(timezone.utc)
    campaign = Campaign(
        id="campaign-1", name="CampusFlow", product_name="CampusFlow", inputs={"product_name": "CampusFlow"},
        brief={}, status="approved", approval={"status": "approved", "approved_report_id": "report-1"},
        created_time=now, updated_time=now,
    )
    db.add(campaign)
    db.add(QualityReport(id="report-1", campaign_id="campaign-1", data={
        "overall_status": "pass", "overall_score": 100, "findings": [],
    }, created_time=now))
    db.add(GeneratedOutput(campaign_id="campaign-1", section="promo", data={"headlines": ["Stay hydrated"]},
                           status="ready", updated_time=now))
    db.commit()

    package = assemble_campaign_package(db, "campaign-1")
    validate_package(package)
    assert package["approval"]["approved_report_id"] == "report-1"
    assert b"Stay hydrated" in render_json(package)
    assert load_export_settings()["export_requires_approval"] is True


def test_stage9_document_exports_and_export_record(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.export_service.EXPORT_ROOT", tmp_path / "exports")
    monkeypatch.setattr("app.services.export_service.ASSET_ROOT", tmp_path / "assets")
    db = _session()
    now = datetime.now(timezone.utc)
    db.add(Campaign(
        id="campaign-2", name="CampusFlow", product_name="CampusFlow",
        inputs={"product_name": "CampusFlow"}, brief={}, status="approved",
        approval={"status": "approved", "approved_report_id": "report-2"},
        created_time=now, updated_time=now,
    ))
    db.add(QualityReport(id="report-2", campaign_id="campaign-2", data={
        "overall_status": "pass", "overall_score": 100, "findings": [],
    }, created_time=now))
    asset_name = "stage9-test.png"
    asset_path = tmp_path / "assets" / asset_name
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    Image.new("RGB", (16, 16), (255, 255, 255)).save(asset_path)
    db.add(Asset(id="asset-2", campaign_id="campaign-2", asset_type="image", status="ready",
                 file_name=asset_name, file_path=str(asset_path),
                 created_time=now))
    db.commit()
    package = assemble_campaign_package(db, "campaign-2")
    assert b"PK" in create_docx(package, db, "campaign-2")
    assert b"PDF" in create_pdf(package, db, "campaign-2")
    record = create_export(db, "campaign-2", package, "json")
    assert record.file_size > 0
    zip_path = tmp_path / "stage9-test.zip"
    create_zip(db, "campaign-2", package, zip_path)
    assert zip_path.is_file()
    assert export_gate(db, "campaign-2", package) is None


def test_stage9_asset_and_export_gates():
    db = _session()
    now = datetime.now(timezone.utc)
    db.add(Campaign(
        id="campaign-3", name="CampusFlow", product_name="CampusFlow",
        inputs={"product_name": "CampusFlow"}, brief={}, status="draft",
        approval={"status": "draft"}, created_time=now, updated_time=now,
    ))
    db.add(QualityReport(id="report-3", campaign_id="campaign-3", data={
        "overall_status": "blocked", "overall_score": 20,
        "findings": [{"severity": "critical", "status": "open"}],
    }, created_time=now))
    db.add(Asset(id="asset-3", campaign_id="campaign-3", asset_type="image", status="ready",
                 file_name="missing.png", file_path="missing.png", created_time=now))
    db.commit()
    package = assemble_campaign_package(db, "campaign-3")
    assert "critical findings" in export_gate(db, "campaign-3", package)


def test_stage9_outdated_report_blocks_export():
    db = _session()
    now = datetime.now(timezone.utc)
    db.add(Campaign(
        id="campaign-4", name="CampusFlow", product_name="CampusFlow",
        inputs={"product_name": "CampusFlow"}, brief={}, status="approved",
        approval={"status": "approved", "approved_report_id": "report-4"},
        created_time=now, updated_time=now,
    ))
    db.add(QualityReport(id="report-4", campaign_id="campaign-4", data={
        "overall_status": "pass", "overall_score": 100, "findings": [],
    }, outdated=1, created_time=now))
    db.commit()
    package = assemble_campaign_package(db, "campaign-4")
    assert export_gate(db, "campaign-4", package) == "Approved quality report is outdated"


def test_export_approval_environment_override(monkeypatch):
    monkeypatch.setenv("EXPORT_REQUIRES_APPROVAL", "false")
    assert load_export_settings()["export_requires_approval"] is False
    monkeypatch.setenv("EXPORT_REQUIRES_APPROVAL", "invalid")
    try:
        load_export_settings()
    except ValueError as exc:
        assert "true or false" in str(exc)
    else:
        raise AssertionError("Invalid export approval setting should fail")


def create_docx(package, db, campaign_id):
    return render_docx(db, campaign_id, package)


def create_pdf(package, db, campaign_id):
    return render_pdf(db, campaign_id, package)
