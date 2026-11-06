from __future__ import annotations

import json
import os
import re
import shutil
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import jsonschema
from docx import Document
from PIL import Image
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.database import Asset, Export, QualityReport
from app.services.language_support import is_hindi


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config" / "export_settings.json"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "campaign_package.schema.json"
EXPORT_ROOT = PROJECT_ROOT / "storage" / "exports"
ASSET_ROOT = PROJECT_ROOT / "storage" / "assets"


def load_export_settings() -> dict[str, Any]:
    settings = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    approval_setting = os.getenv("EXPORT_REQUIRES_APPROVAL")
    if approval_setting is not None:
        normalized = approval_setting.strip().lower()
        if normalized not in {"true", "false"}:
            raise ValueError("EXPORT_REQUIRES_APPROVAL must be true or false")
        settings["export_requires_approval"] = normalized == "true"
    return settings


def validate_package(package: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(package, schema)


def export_gate(db: Session, campaign_id: str, package: dict[str, Any]) -> str | None:
    settings = load_export_settings()
    approval = package["approval"]
    report = db.query(QualityReport).filter(QualityReport.campaign_id == campaign_id).order_by(
        QualityReport.created_time.desc()).first()
    findings = report.data.get("findings", []) if report else []
    if report and report.outdated:
        return "Approved quality report is outdated"
    if any(finding.get("severity") == "critical" and finding.get("status", "open") == "open" for finding in findings):
        return "Package contains open critical findings"
    if not approval.get("approved_report_id") and settings["export_requires_approval"]:
        return "Campaign approval is required before export"
    return None


def _assets(db: Session, campaign_id: str) -> list[Asset]:
    return db.query(Asset).filter(
        Asset.campaign_id == campaign_id,
        Asset.status == "ready",
    ).all()


def _safe_asset_path(asset: Asset) -> Path:
    candidate = (ASSET_ROOT / asset.file_name).resolve()
    if candidate.parent != ASSET_ROOT.resolve():
        raise ValueError("Asset path escapes storage root")
    if not candidate.is_file():
        raise FileNotFoundError(asset.file_name)
    return candidate


def _image_bytes(asset: Asset, max_width: int) -> bytes:
    path = _safe_asset_path(asset)
    with Image.open(path) as image:
        image.thumbnail((max_width, max_width * 10), Image.Resampling.LANCZOS)
        output = BytesIO()
        image.convert("RGB").save(output, format="JPEG", quality=90)
        return output.getvalue()


def _package_lines(package: dict[str, Any]) -> list[str]:
    lines = [
        "Campaign Package",
        package["campaign_id"],
        "Product summary",
        json.dumps(package["product_input"], ensure_ascii=False, sort_keys=True),
        "Audience summary",
        json.dumps(package["audience_summary"], ensure_ascii=False, sort_keys=True),
        "Campaign brief",
        json.dumps(package["campaign_brief"], ensure_ascii=False, sort_keys=True),
    ]
    for name in ("descriptions", "promo", "social", "visuals", "video"):
        lines.extend([name.replace("_", " ").title(), json.dumps(package[name], ensure_ascii=False, sort_keys=True)])
    return lines


def render_json(package: dict[str, Any]) -> bytes:
    validate_package(package)
    return (json.dumps(package, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def render_docx(db: Session, campaign_id: str, package: dict[str, Any]) -> bytes:
    settings = load_export_settings()
    document = Document()
    document.add_heading("Campaign Package", 0)
    for name, value in (
        ("Product Summary", package["product_input"]),
        ("Audience Summary", package["audience_summary"]),
        ("Campaign Brief", package["campaign_brief"]),
    ):
        document.add_heading(name, level=1)
        document.add_paragraph(json.dumps(value, ensure_ascii=False, indent=2))
    for section in ("Descriptions", "Promo", "Social", "Visuals", "Video"):
        document.add_heading(section, level=1)
        document.add_paragraph(json.dumps(package[section.lower()], ensure_ascii=False, indent=2))
    document.add_heading("AI-generated content disclosure", level=1)
    document.add_paragraph(settings["disclosure_text"])
    for asset in _assets(db, campaign_id):
        if asset.asset_type == "image":
            image = BytesIO(_image_bytes(asset, settings["image_max_width"]))
            document.add_picture(image)
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def render_pdf(db: Session, campaign_id: str, package: dict[str, Any]) -> bytes:
    _require_pdf_language_support(package)
    settings = load_export_settings()
    output = BytesIO()
    page_size = LETTER if settings["page_size"] == "LETTER" else A4
    pdf = canvas.Canvas(output, pagesize=page_size)
    width, height = page_size
    y = height - 72
    for line in _package_lines(package):
        for wrapped in _wrap(line, 100):
            if y < 72:
                pdf.showPage()
                y = height - 72
            pdf.drawString(54, y, wrapped)
            y -= 14
    for asset in _assets(db, campaign_id):
        if asset.asset_type == "image":
            if y < 240:
                pdf.showPage()
                y = height - 72
            pdf.drawImage(ImageReader(BytesIO(_image_bytes(asset, settings["image_max_width"]))), 54, y - 180, width=240, preserveAspectRatio=True, mask="auto")
            y -= 210
    pdf.setFont("Helvetica", 9)
    pdf.drawString(54, 36, settings["disclosure_text"])
    pdf.save()
    return output.getvalue()


def _require_pdf_language_support(package: dict[str, Any]) -> None:
    if is_hindi(str(package.get("product_input", {}).get("language", "en-US"))):
        raise ValueError("PDF export for Hindi requires a Devanagari-capable embedded font; use DOCX or JSON.")


def _wrap(text: str, width: int) -> list[str]:
    text = str(text)
    return [text[index:index + width] for index in range(0, max(len(text), 1), width)]


def create_export(db: Session, campaign_id: str, package: dict[str, Any], format_name: str) -> Export:
    gate_error = export_gate(db, campaign_id, package)
    if gate_error:
        raise PermissionError(gate_error)
    if format_name in {"pdf", "zip"}:
        _require_pdf_language_support(package)
    validate_package(package)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    export_id = uuid4().hex
    extension = "json" if format_name == "json" else "docx" if format_name == "docx" else "pdf"
    if format_name == "zip":
        extension = "zip"
    path = EXPORT_ROOT / f"{export_id}.{extension}"
    if format_name == "json":
        content = render_json(package)
        path.write_bytes(content)
    elif format_name == "docx":
        path.write_bytes(render_docx(db, campaign_id, package))
    elif format_name == "pdf":
        path.write_bytes(render_pdf(db, campaign_id, package))
    elif format_name == "zip":
        create_zip(db, campaign_id, package, path)
    else:
        raise ValueError("Unsupported export format")
    settings = load_export_settings()
    if path.stat().st_size > settings["max_export_bytes"]:
        path.unlink()
        raise ValueError("Export exceeds configured size limit")
    record = Export(
        id=export_id,
        campaign_id=campaign_id,
        format=format_name,
        file_path=str(path.resolve()),
        file_size=path.stat().st_size,
        package_version=package["package_id"],
        approval_report_id=package["approval"].get("approved_report_id"),
        created_time=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    db.add(record)
    db.commit()
    return record


def create_zip(db: Session, campaign_id: str, package: dict[str, Any], destination: Path) -> None:
    _require_pdf_language_support(package)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("package.json", render_json(package))
        archive.writestr("campaign.docx", render_docx(db, campaign_id, package))
        archive.writestr("campaign.pdf", render_pdf(db, campaign_id, package))
        for asset in _assets(db, campaign_id):
            path = _safe_asset_path(asset)
            archive.write(path, arcname=f"assets/{asset.file_name}")
