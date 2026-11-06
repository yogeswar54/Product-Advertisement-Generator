from __future__ import annotations

import json
from io import BytesIO
from datetime import datetime, timezone
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Asset, Base, Campaign, get_db
from app.main import app
from app.models.audience import AudienceProfile, AudienceProfileRequest
from app.models.input import CampaignInput
from app.models.stage4 import CampaignBrief
from app.providers.mock import MockProvider
from app.providers.base import ProviderResult
from app.services.export_service import create_zip, render_docx, render_pdf
from app.services.language_support import apply_language_policy
from app.services.quality import run_quality_check
from app.modules.visual_generator import generate_visuals
from app.services.visual_checks import run_visual_checks


INPUT = {
    "product_name": "CampusFlow Bottle",
    "category": "Reusable water bottle",
    "key_features": ["700 ml capacity", "Leak-resistant lid"],
    "usp": "Easy campus carry",
    "brand_name": "CampusFlow",
    "brand_voice": "Friendly and practical",
    "target_audience": "college_students",
    "campaign_goal": "Conversions",
    "platforms": ["instagram"],
    "language": "en-US",
}
BRAND_KIT = {
    "name": "CampusFlow",
    "primary_color": "#17324D",
    "secondary_color": "#FFFFFF",
    "font": "Sans serif",
    "font_licensing_note": "User supplied; verify license before use",
    "rights_confirmed": True,
}


@pytest.fixture
def api_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def override_db():
        with Session(engine) as db:
            yield db

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
    engine.dispose()


def _jpeg_with_exif() -> bytes:
    image = Image.new("RGB", (20, 20), (20, 80, 120))
    image.getexif()[0x010E] = "private metadata"
    output = BytesIO()
    image.save(output, format="JPEG", exif=image.getexif())
    return output.getvalue()


def test_hindi_flag_off_by_default_and_enabled_validation(api_client, monkeypatch):
    monkeypatch.setenv("ENHANCE_HINDI", "off")
    english = api_client.post("/inputs/validate", json=INPUT)
    assert english.status_code == 200
    response = api_client.post("/inputs/validate", json={**INPUT, "language": "hi"})
    assert response.status_code == 422

    monkeypatch.setenv("ENHANCE_HINDI", "on")
    response = api_client.post("/inputs/validate", json={**INPUT, "language": "hi"})
    assert response.status_code == 200
    with pytest.raises(ValueError, match="ENHANCE_HINDI=on"):
        monkeypatch.setenv("ENHANCE_HINDI", "off")
        apply_language_policy("base prompt", "hi")
    monkeypatch.setenv("ENHANCE_HINDI", "on")
    assert "उपयोगकर्ता-दृश्य पाठ" in apply_language_policy("base prompt", "hi")
    audience = api_client.post("/audiences/profile", json={"persona_id": "college_students", "language": "hi"})
    assert audience.status_code == 200
    assert "देवनागरी" in audience.json()["vocabulary_level"]
    report = run_quality_check({"language": "hi"}, {"promo": {"headline": "स्वागत"}}, "hindi-test")
    assert report.check_applicability["readability"] == "skipped for this language"
    assert report.check_applicability["stop_words"] == "skipped for this language"
    assert any("not been reviewed by a native speaker" in note for note in report.language_notes)
    assert any("not measured" in note for note in report.language_notes)


def test_brand_kit_flag_validation_and_campaign_persistence(api_client, monkeypatch):
    monkeypatch.setenv("ENHANCE_BRAND_KIT", "off")
    unchanged = api_client.post("/campaigns", json={"name": "CampusFlow", "inputs": INPUT})
    assert unchanged.status_code == 200
    disabled = api_client.post("/campaigns", json={"name": "CampusFlow", "inputs": {**INPUT, "brand_kit": BRAND_KIT}})
    assert disabled.status_code == 422

    monkeypatch.setenv("ENHANCE_BRAND_KIT", "on")
    invalid = api_client.post(
        "/campaigns",
        json={"name": "CampusFlow", "inputs": {**INPUT, "brand_kit": {**BRAND_KIT, "primary_color": "blue"}}},
    )
    assert invalid.status_code == 422
    unconfirmed = api_client.post(
        "/campaigns",
        json={"name": "CampusFlow", "inputs": {**INPUT, "brand_kit": {**BRAND_KIT, "rights_confirmed": False}}},
    )
    assert unconfirmed.status_code == 422

    created = api_client.post("/campaigns", json={"name": "CampusFlow", "inputs": {**INPUT, "brand_kit": BRAND_KIT}})
    assert created.status_code == 200
    package = api_client.get(f"/campaigns/{created.json()['id']}/package")
    assert package.status_code == 200
    assert package.json()["product_input"]["brand_kit"]["primary_color"] == BRAND_KIT["primary_color"]


def test_logo_upload_reencodes_image_and_rejects_svg_and_size(api_client, monkeypatch, tmp_path):
    monkeypatch.setenv("ENHANCE_BRAND_KIT", "on")
    monkeypatch.setattr("app.services.asset_storage.ASSET_ROOT", tmp_path / "assets")
    monkeypatch.setattr("app.services.asset_storage.METADATA_PATH", tmp_path / "assets" / "metadata.json")
    created = api_client.post("/campaigns", json={"name": "CampusFlow", "inputs": {**INPUT, "brand_kit": BRAND_KIT}})
    campaign_id = created.json()["id"]
    preflight = api_client.options(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        headers={
            "origin": "http://127.0.0.1:8501",
            "access-control-request-method": "PUT",
            "access-control-request-headers": "content-type",
        },
    )
    assert preflight.status_code == 200
    assert "PUT" in preflight.headers["access-control-allow-methods"]

    rejected = api_client.put(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        content=b"<svg xmlns='http://www.w3.org/2000/svg'></svg>",
        headers={"content-type": "image/svg+xml"},
    )
    assert rejected.status_code == 415
    monkeypatch.setenv("ENHANCE_BRAND_KIT", "off")
    disabled = api_client.put(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        content=_jpeg_with_exif(),
        headers={"content-type": "image/jpeg"},
    )
    assert disabled.status_code == 404
    monkeypatch.setenv("ENHANCE_BRAND_KIT", "on")
    mismatch = api_client.put(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        content=_jpeg_with_exif(),
        headers={"content-type": "image/png"},
    )
    assert mismatch.status_code == 422

    uploaded = api_client.put(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        content=_jpeg_with_exif(),
        headers={"content-type": "image/jpeg"},
    )
    assert uploaded.status_code == 200
    asset = api_client.get(f"/assets/{uploaded.json()['id']}")
    assert asset.status_code == 200
    with Image.open(BytesIO(asset.content)) as image:
        assert image.format == "PNG"
        assert not image.getexif()

    monkeypatch.setenv("MAX_PRODUCT_IMAGE_BYTES", "20")
    too_large = api_client.put(
        f"/campaigns/{campaign_id}/brand-kit/logo",
        content=_jpeg_with_exif(),
        headers={"content-type": "image/jpeg"},
    )
    assert too_large.status_code == 422


def test_brand_palette_is_applied_and_low_contrast_is_reported(monkeypatch):
    monkeypatch.setenv("ENHANCE_BRAND_KIT", "on")
    kit = {**BRAND_KIT, "primary_color": "#111111", "secondary_color": "#111111"}
    product = CampaignInput.model_validate({**INPUT, "brand_kit": kit})
    audience = AudienceProfile(
        tone="Friendly",
        vocabulary_level="Plain",
        slang_tolerance="Low",
        motivations=["value"],
        objections=["price"],
        emotional_triggers=["confidence"],
        best_platforms=["instagram"],
        preferred_content_formats=["short video"],
        words_styles_to_avoid=["jargon"],
    )
    brief = CampaignBrief(
        core_message="Practical hydration",
        tone="Friendly",
        emotional_hook="Readiness",
        key_benefits=["700 ml capacity", "Leak-resistant lid", "Easy carry"],
        audience_profile_reference="college_students",
        dos_and_donts={"dos": ["Use supplied facts"], "donts": ["Invent claims"]},
        prompt_version="brief_v1",
    )

    class MissingBrandRolesProvider(MockProvider):
        last_user_prompt = ""

        def generate_json(self, system, user, schema, temperature, max_tokens):
            self.last_user_prompt = user
            result = super().generate_json(system, user, schema, temperature, max_tokens)
            if schema.get("title") == "Visual Output":
                output = json.loads(result.text)
                for concept in output["concepts"]:
                    concept["color_palette"] = [
                        {"hex": "#FFFFFF", "role": "background"},
                        {"hex": "#D9E5F2", "role": "accent"},
                        {"hex": "#172033", "role": "text"},
                        {"hex": "#7BB661", "role": "accent"},
                        {"hex": "#F7F9FC", "role": "background"},
                    ]
                result = ProviderResult(json.dumps(output), result.usage, result.model)
            return result

    provider = MissingBrandRolesProvider()
    visual = generate_visuals(provider, product, audience, brief)
    assert "Preferred brand palette:" in provider.last_user_prompt
    for concept in visual.concepts:
        primary = next(color for color in concept.color_palette if color.role == "primary")
        secondary = next(color for color in concept.color_palette if color.role == "secondary")
        assert primary.hex == kit["primary_color"]
        assert secondary.hex == kit["secondary_color"]
    warnings = run_visual_checks(visual, "700 ml campus bottle", product.brand_kit)
    assert any(warning.code == "VISUAL_BRAND_LOW_CONTRAST" for warning in warnings)
    default_provider = MissingBrandRolesProvider()
    generate_visuals(default_provider, CampaignInput.model_validate(INPUT), audience, brief)
    assert "Preferred brand palette:" not in default_provider.last_user_prompt


def test_hindi_pdf_and_zip_are_blocked_before_writing(tmp_path):
    package = {"product_input": {"language": "hi"}}
    with pytest.raises(ValueError, match="Devanagari-capable embedded font"):
        render_pdf(None, "hindi-campaign", package)
    destination = tmp_path / "hindi-export.zip"
    with pytest.raises(ValueError, match="Devanagari-capable embedded font"):
        create_zip(None, "hindi-campaign", package, destination)
    assert not destination.exists()


def test_campaign_logo_is_embedded_in_docx_and_pdf_only_when_uploaded(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.export_service.ASSET_ROOT", tmp_path / "assets")
    asset_root = tmp_path / "assets"
    asset_root.mkdir()
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = Session(engine)
    now = datetime.now(timezone.utc)
    campaign_id = "brand-export-test"
    db.add(Campaign(
        id=campaign_id,
        name="CampusFlow",
        product_name="CampusFlow",
        inputs={**INPUT, "brand_kit": BRAND_KIT},
        brief={},
        status="draft",
        approval={"status": "draft"},
        created_time=now,
        updated_time=now,
    ))
    db.commit()
    package = {
        "campaign_id": campaign_id,
        "product_input": INPUT,
        "audience_summary": {},
        "campaign_brief": {},
        "descriptions": {},
        "promo": {},
        "social": {},
        "visuals": {},
        "video": {},
    }

    docx_without_logo = render_docx(db, campaign_id, package)
    with ZipFile(BytesIO(docx_without_logo)) as archive:
        assert not any(name.startswith("word/media/") for name in archive.namelist())
    assert b"/Subtype /Image" not in render_pdf(db, campaign_id, package)

    image_path = asset_root / "logo.png"
    Image.new("RGBA", (16, 16), (20, 80, 120, 200)).save(image_path)
    db.add(Asset(
        id="a" * 32,
        campaign_id=campaign_id,
        asset_type="image",
        status="ready",
        file_name=image_path.name,
        file_path=str(image_path),
        created_time=now,
    ))
    db.commit()
    docx_with_logo = render_docx(db, campaign_id, package)
    with ZipFile(BytesIO(docx_with_logo)) as archive:
        assert any(name.startswith("word/media/") for name in archive.namelist())
    assert b"/Subtype /Image" in render_pdf(db, campaign_id, package)
    db.close()
    engine.dispose()
