import io

from PIL import Image

import app.services.asset_storage as storage
from app.services.asset_storage import cleanup_assets, get_asset, load_metadata, save_asset


def test_asset_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    buffer = io.BytesIO()
    Image.new("RGB", (40, 40), "white").save(buffer, format="PNG")
    record = save_asset(buffer.getvalue(), "campaign-1", "Campus Morning", "poster", "Bottle", "mock", "mock-image-v1")
    assert get_asset(record["id"])


def test_asset_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    try:
        save_asset(b"not-an-image", "../campaign", "Campus", "poster", "Bottle", "mock", "mock")
    except (ValueError, KeyError):
        return
    raise AssertionError("Traversal campaign ID should fail")


def test_asset_load_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    assert load_metadata() == []


def test_cleanup_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    assert cleanup_assets(30) == 0


def test_asset_rejects_invalid_image(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "ASSET_ROOT", tmp_path)
    monkeypatch.setattr(storage, "METADATA_PATH", tmp_path / "metadata.json")
    try:
        save_asset(b"not-an-image", "campaign-1", "Campus", "poster", "Bottle", "mock", "mock")
    except ValueError:
        return
    raise AssertionError("Invalid image should fail")
