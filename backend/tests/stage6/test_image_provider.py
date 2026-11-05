import io
from pathlib import Path

import pytest
from PIL import Image

from app.image_providers.hosted import HostedImageProvider, ImageProviderError
from app.image_providers.mock import MockImageProvider


def test_mock_image_dimensions():
    result = MockImageProvider().generate_image("A #1F4B99 reusable bottle, square composition, 1:1 aspect ratio", "logos", 1080, 1080)
    image = Image.open(io.BytesIO(result.content))
    assert image.size == (1080, 1080)
    assert image.format == "PNG"
    assert result.provider == "mock"


def test_hosted_provider_requires_key(monkeypatch):
    monkeypatch.delenv("IMAGE_API_KEY", raising=False)
    try:
        HostedImageProvider().generate_image("Bottle", "logos", 100, 100)
    except ImageProviderError as exc:
        assert exc.code == "PROVIDER_AUTH_MISSING"
    else:
        raise AssertionError("Hosted provider without key should fail")


def test_mock_reference_image_is_optional(tmp_path: Path):
    reference = tmp_path / "reference.png"
    Image.new("RGB", (20, 20), "white").save(reference)
    result = MockImageProvider().generate_image("Bottle", "logos", 100, 100, reference)
    assert result.content
