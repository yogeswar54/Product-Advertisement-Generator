from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.orm import Session

from app.database import Asset, Campaign, Export, GeneratedOutput, OutputVersion, QualityReport, get_db
from app.models.input import BrandKit
from app.services.export_service import load_export_settings, create_export
from app.services.package_assembler import assemble_campaign_package
from app.services.quality import run_quality_check
from app.services.asset_storage import remove_asset_metadata, save_asset
from app.services.feature_flags import enhancement_enabled
import logging


router = APIRouter(prefix="/campaigns", tags=["campaign-history"])
logger = logging.getLogger(__name__)


class CreateCampaign(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    inputs: dict
    brief: dict = Field(default_factory=dict)
    outputs: dict = Field(default_factory=dict)
    quality: dict | None = None


class SectionEdit(BaseModel):
    value: object
    editor: str = Field(default="user", max_length=100)
    source: str = Field(default="manual_edit", pattern="^(generated|manual_edit|autofix|regenerated)$")


class ExportRequest(BaseModel):
    format: str = Field(pattern="^(json|docx|pdf|zip)$")


def _campaign_or_404(db: Session, campaign_id: str) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(404, {"code": "CAMPAIGN_NOT_FOUND", "field": "id", "message": "Campaign not found"})
    return campaign


def _error(status: int, code: str, message: str, field: str | None = None) -> HTTPException:
    return HTTPException(status, {"code": code, "field": field, "message": message})


@router.get("")
def list_campaigns(db: Session = Depends(get_db), sort: str = "updated", search: str | None = None):
    query = db.query(Campaign)
    if search:
        query = query.filter(Campaign.product_name.ilike(f"%{search}%"))
    query = query.order_by(Campaign.updated_time.desc() if sort != "created" else Campaign.created_time.desc())
    return [{"id": item.id, "name": item.name, "product": item.product_name, "status": item.status,
             "created_time": item.created_time.isoformat(), "updated_time": item.updated_time.isoformat()} for item in query.all()]


@router.post("")
def create_campaign(request: CreateCampaign, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    inputs = dict(request.inputs)
    if inputs.get("brand_kit") is not None:
        if not enhancement_enabled("ENHANCE_BRAND_KIT"):
            raise _error(422, "FEATURE_DISABLED", "Brand kits are disabled; set ENHANCE_BRAND_KIT=on to enable them", "brand_kit")
        try:
            brand_kit = BrandKit.model_validate(inputs["brand_kit"])
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(part) for part in first["loc"])
            raise _error(422, "INVALID_BRAND_KIT", first["msg"], field or "brand_kit") from exc
        if brand_kit.logo_asset_id is not None:
            raise _error(422, "INVALID_BRAND_KIT", "Upload the logo after saving the campaign", "brand_kit.logo_asset_id")
        inputs["brand_kit"] = brand_kit.model_dump()
    product_name = str(inputs.get("product_name") or request.name)
    campaign = Campaign(id=uuid4().hex, name=request.name, product_name=product_name, inputs=inputs,
                        brief=request.brief, status="draft", approval={"status": "draft"}, created_time=now, updated_time=now)
    db.add(campaign)
    db.flush()
    for section, value in request.outputs.items():
        status = value.get("status", "ready") if isinstance(value, dict) else "ready"
        data = value.get("content", value) if isinstance(value, dict) else value
        db.add(GeneratedOutput(campaign_id=campaign.id, section=section, data=data, status=status, updated_time=now))
    if request.quality:
        report_id = str(request.quality.get("report_id") or uuid4().hex)
        db.add(QualityReport(id=report_id, campaign_id=campaign.id, data=request.quality, created_time=now))
    db.commit()
    return {"id": campaign.id, "status": campaign.status}


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    return assemble_campaign_package(db, campaign_id)


@router.post("/{campaign_id}/duplicate")
def duplicate_campaign(campaign_id: str, db: Session = Depends(get_db)):
    source = _campaign_or_404(db, campaign_id)
    now = datetime.now(timezone.utc)
    duplicate_inputs = dict(source.inputs or {})
    if isinstance(duplicate_inputs.get("brand_kit"), dict):
        duplicate_brand_kit = dict(duplicate_inputs["brand_kit"])
        duplicate_brand_kit.pop("logo_asset_id", None)
        duplicate_inputs["brand_kit"] = duplicate_brand_kit
    duplicate = Campaign(id=uuid4().hex, name=f"{source.name} (Copy)", product_name=source.product_name,
                         inputs=duplicate_inputs, brief=dict(source.brief or {}),
                         status="draft", approval={"status": "draft"}, created_time=now, updated_time=now)
    db.add(duplicate)
    db.flush()
    for output in db.query(GeneratedOutput).filter(GeneratedOutput.campaign_id == campaign_id).all():
        db.add(GeneratedOutput(campaign_id=duplicate.id, section=output.section, data=dict(output.data),
                               status=output.status, updated_time=now))
    db.commit()
    return {"id": duplicate.id, "status": duplicate.status}


@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str, confirm: bool = False, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    if not confirm:
        raise _error(409, "CONFIRMATION_REQUIRED", "Set confirm=true to delete this campaign", "confirm")
    for export in db.query(Export).filter(Export.campaign_id == campaign_id).all():
        Path(export.file_path).unlink(missing_ok=True)
    asset_root = Path(__file__).resolve().parents[4] / "storage" / "assets"
    for asset in db.query(Asset).filter(Asset.campaign_id == campaign_id).all():
        candidate = Path(asset.file_path).resolve()
        if candidate.parent == asset_root.resolve():
            candidate.unlink(missing_ok=True)
        remove_asset_metadata(asset.id)
    db.delete(campaign)
    db.commit()
    logger.info("Campaign deleted: %s", campaign_id)
    return {"deleted": True}


@router.get("/{campaign_id}/package")
def package(campaign_id: str, db: Session = Depends(get_db)):
    _campaign_or_404(db, campaign_id)
    return assemble_campaign_package(db, campaign_id)


@router.put("/{campaign_id}/brand-kit/logo")
async def upload_brand_kit_logo(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    if not enhancement_enabled("ENHANCE_BRAND_KIT"):
        raise _error(404, "FEATURE_DISABLED", "Brand kit uploads are disabled")
    campaign = _campaign_or_404(db, campaign_id)
    inputs = dict(campaign.inputs or {})
    brand_kit = dict(inputs.get("brand_kit") or {})
    if not brand_kit or brand_kit.get("rights_confirmed") is not True:
        raise _error(409, "BRAND_KIT_REQUIRED", "Save a brand kit and confirm the logo/font rights before uploading a logo")

    media_type = request.headers.get("content-type", "").split(";", maxsplit=1)[0].strip().lower()
    expected_formats = {"image/png": "PNG", "image/jpeg": "JPEG", "image/webp": "WEBP"}
    expected_format = expected_formats.get(media_type)
    if expected_format is None:
        raise _error(415, "UNSUPPORTED_LOGO_TYPE", "Logo must be PNG, JPEG, or WebP; SVG is not accepted")

    max_bytes = int(os.getenv("MAX_PRODUCT_IMAGE_BYTES", "10485760"))
    if max_bytes <= 0:
        raise _error(422, "LOGO_SIZE_LIMIT", "The configured image size limit must be positive")
    chunks: list[bytes] = []
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise _error(422, "LOGO_SIZE_LIMIT", "Logo exceeds the configured image size limit")
        chunks.append(chunk)
    if total_bytes == 0:
        raise _error(422, "EMPTY_LOGO", "Logo file is empty")
    content = b"".join(chunks)
    try:
        record = save_asset(
            content,
            campaign_id,
            "brand-kit-logo",
            "brand-kit",
            "User-uploaded logo",
            "user_upload",
            "user_upload",
            max_bytes=max_bytes,
            allowed_formats={"PNG", "JPEG", "WEBP"},
            expected_format=expected_format,
            preserve_alpha=True,
            asset_role="brand_logo",
        )
    except ValueError as exc:
        raise _error(422, "INVALID_LOGO", str(exc), "logo") from exc

    file_path = Path(str(record["path"])).resolve()
    now = datetime.now(timezone.utc)
    asset = Asset(
        id=str(record["id"]),
        campaign_id=campaign_id,
        asset_type="image",
        status="ready",
        file_name=file_path.name,
        file_path=str(file_path),
        metadata_json=record,
        created_time=now,
    )
    old_asset_id = brand_kit.get("logo_asset_id")
    brand_kit["logo_asset_id"] = record["id"]
    inputs["brand_kit"] = brand_kit
    campaign.inputs = inputs
    campaign.updated_time = now
    db.add(asset)
    db.commit()
    if isinstance(old_asset_id, str) and old_asset_id != record["id"]:
        old_asset = db.get(Asset, old_asset_id)
        if old_asset is not None and old_asset.campaign_id == campaign_id:
            old_path = Path(old_asset.file_path).resolve()
            if old_path.parent == file_path.parent:
                old_path.unlink(missing_ok=True)
            db.delete(old_asset)
            db.commit()
            remove_asset_metadata(old_asset_id)
    return {"id": record["id"], "asset_role": "brand_logo", "file_name": file_path.name}


@router.patch("/{campaign_id}/sections/{section}")
def edit_section(campaign_id: str, section: str, request: SectionEdit, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    output = db.query(GeneratedOutput).filter(GeneratedOutput.campaign_id == campaign_id,
                                               GeneratedOutput.section == section).one_or_none()
    if output is None:
        raise _error(404, "SECTION_NOT_FOUND", "Section not found", section)
    if isinstance(request.value, str) and len(request.value) > 10000:
        raise _error(422, "FIELD_LIMIT_EXCEEDED", "Text exceeds configured length limit", section)
    schema_file = {
        "descriptions": "description_output.schema.json",
        "promo": "promo_output.schema.json",
        "social": "social_output.schema.json",
        "visuals": "visual_output.schema.json",
        "video": "video_output.schema.json",
    }.get(section)
    if schema_file and isinstance(request.value, (dict, list)):
        import json
        import jsonschema
        from pathlib import Path
        schema_path = Path(__file__).resolve().parents[4] / "schemas" / schema_file
        try:
            jsonschema.validate(request.value, json.loads(schema_path.read_text(encoding="utf-8")))
        except jsonschema.ValidationError as exc:
            raise _error(422, "SECTION_VALIDATION_ERROR", exc.message, ".".join(str(item) for item in exc.absolute_path) or section) from exc
    elif schema_file:
        raise _error(422, "SECTION_VALIDATION_ERROR", "Section value must match the section JSON schema", section)
    previous = json.loads(json.dumps(output.data))
    db.add(OutputVersion(campaign_id=campaign_id, section=section, previous_value=previous,
                         source=request.source, editor=request.editor, created_time=datetime.now(timezone.utc)))
    output.data = request.value
    output.updated_time = datetime.now(timezone.utc)
    campaign.status = "needs_review"
    campaign.approval = {"status": "needs_review"}
    campaign.updated_time = datetime.now(timezone.utc)
    db.query(QualityReport).filter(QualityReport.campaign_id == campaign_id).update({"outdated": 1})
    report = run_quality_check(campaign.inputs or {}, request.value, campaign_id, section)
    db.add(QualityReport(
        id=report.report_id,
        campaign_id=campaign_id,
        data=report.model_dump(),
        outdated=0,
        created_time=datetime.now(timezone.utc),
    ))
    versions = db.query(OutputVersion).filter(OutputVersion.campaign_id == campaign_id,
                                               OutputVersion.section == section).order_by(OutputVersion.created_time.asc()).all()
    limit = load_export_settings().get("version_limit", 5)
    if len(versions) > limit:
        for old in versions[:len(versions) - limit]:
            db.delete(old)
    db.commit()
    return {"section": section, "saved": True, "status": campaign.status}


@router.get("/{campaign_id}/sections/{section}/versions")
def section_versions(campaign_id: str, section: str, db: Session = Depends(get_db)):
    _campaign_or_404(db, campaign_id)
    rows = db.query(OutputVersion).filter(OutputVersion.campaign_id == campaign_id,
                                           OutputVersion.section == section).order_by(OutputVersion.created_time.desc()).all()
    return [{"previous_value": row.previous_value, "source": row.source, "editor": row.editor,
             "created_time": row.created_time.isoformat()} for row in rows]


@router.post("/{campaign_id}/sections/{section}/revert")
def revert_section(campaign_id: str, section: str, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    output = db.query(GeneratedOutput).filter(GeneratedOutput.campaign_id == campaign_id,
                                               GeneratedOutput.section == section).one_or_none()
    if output is None:
        raise _error(404, "SECTION_NOT_FOUND", "Section not found", section)
    version = db.query(OutputVersion).filter(OutputVersion.campaign_id == campaign_id,
                                              OutputVersion.section == section).order_by(OutputVersion.created_time.desc()).first()
    if version is None:
        raise _error(409, "NO_PREVIOUS_VERSION", "No previous version is available", section)
    output.data = version.previous_value
    output.updated_time = datetime.now(timezone.utc)
    campaign.status = "needs_review"
    campaign.approval = {"status": "needs_review"}
    campaign.updated_time = datetime.now(timezone.utc)
    db.query(QualityReport).filter(QualityReport.campaign_id == campaign_id).update({"outdated": 1})
    report = run_quality_check(campaign.inputs or {}, output.data, campaign_id, section)
    db.add(QualityReport(
        id=report.report_id,
        campaign_id=campaign_id,
        data=report.model_dump(),
        outdated=0,
        created_time=datetime.now(timezone.utc),
    ))
    db.delete(version)
    db.commit()
    return {"section": section, "restored": True, "value": output.data}


@router.post("/{campaign_id}/quality")
def run_campaign_quality(campaign_id: str, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    package = assemble_campaign_package(db, campaign_id)
    report = run_quality_check(campaign.inputs or {}, {
        key: value["content"] for key, value in package.items()
        if key in {"descriptions", "promo", "social", "visuals", "video"}
    }, campaign_id)
    data = report.model_dump()
    db.query(QualityReport).filter(QualityReport.campaign_id == campaign_id).update({"outdated": 1})
    db.add(QualityReport(id=report.report_id, campaign_id=campaign_id, data=data, outdated=0,
                         created_time=datetime.now(timezone.utc)))
    campaign.status = "needs_review" if report.overall_status != "pass" else campaign.status
    campaign.updated_time = datetime.now(timezone.utc)
    db.commit()
    return data


@router.post("/{campaign_id}/approve")
def approve_campaign(campaign_id: str, approved_by: str, report_id: str, db: Session = Depends(get_db)):
    campaign = _campaign_or_404(db, campaign_id)
    report = db.query(QualityReport).filter(
        QualityReport.id == report_id, QualityReport.campaign_id == campaign_id,
    ).one_or_none()
    if report is None or report.outdated:
        raise _error(409, "QUALITY_REPORT_OUTDATED", "Run quality checks on the latest campaign content before approval")
    findings = report.data.get("findings", [])
    if any(item.get("status", "open") == "open" and item.get("severity") in {"critical", "major"} for item in findings):
        raise _error(409, "CAMPAIGN_CRITICAL_FINDINGS", "Critical and major findings must be resolved or acknowledged before approval")
    campaign.approval = {
        "status": "approved",
        "approved_by": approved_by,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approved_report_id": report_id,
    }
    campaign.status = "approved"
    campaign.updated_time = datetime.now(timezone.utc)
    db.commit()
    return campaign.approval


@router.post("/{campaign_id}/exports")
def export_campaign(campaign_id: str, request: ExportRequest, db: Session = Depends(get_db)):
    _campaign_or_404(db, campaign_id)
    package = assemble_campaign_package(db, campaign_id)
    try:
        record = create_export(db, campaign_id, package, request.format)
    except PermissionError as exc:
        raise _error(409, "EXPORT_BLOCKED", str(exc)) from exc
    except ValueError as exc:
        raise _error(422, "EXPORT_UNSUPPORTED", str(exc), "format") from exc
    return {"export_id": record.id, "format": record.format, "file_size": record.file_size}


@router.get("/{campaign_id}/exports")
def export_history(campaign_id: str, db: Session = Depends(get_db)):
    _campaign_or_404(db, campaign_id)
    return [{"id": row.id, "format": row.format, "file_size": row.file_size,
             "created_time": row.created_time.isoformat()} for row in db.query(Export).filter(
                 Export.campaign_id == campaign_id).order_by(Export.created_time.desc()).all()]


@router.get("/{campaign_id}/exports/{export_id}/download")
def download_export(campaign_id: str, export_id: str, db: Session = Depends(get_db)):
    record = db.query(Export).filter(Export.id == export_id, Export.campaign_id == campaign_id).one_or_none()
    if record is None or not Path(record.file_path).is_file():
        raise _error(404, "EXPORT_NOT_FOUND", "Export not found")
    return FileResponse(record.file_path, filename=Path(record.file_path).name)
