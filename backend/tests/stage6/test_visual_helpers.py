import pytest
from app.services.visual_helpers import contrast_ratio, low_contrast, valid_hex
from app.services.visual_formats import load_visual_formats


def test_all_visual_formats():
    assert set(load_visual_formats()) == {"poster", "banner", "story", "square_social_post"}


def test_hex_validation():
    assert valid_hex("#FFFFFF")
    assert not valid_hex("FFFFFF")
    assert not valid_hex("#FFF")


def test_contrast_ratio():
    assert contrast_ratio("#FFFFFF", "#000000") >= 20
    assert low_contrast("#FFFFFF", "#FFFFFF")
    assert not low_contrast("#FFFFFF", "#000000")
