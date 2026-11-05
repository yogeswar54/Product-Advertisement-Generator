import json
from pathlib import Path

from app.models.audience import AudienceProfile
from app.models.input import CampaignInput

ROOT = Path(__file__).resolve().parents[2]


def test_input_example_matches_model():
    data = json.loads((ROOT / "schemas/examples/input.example.json").read_text(encoding="utf-8"))
    CampaignInput.model_validate(data)


def test_audience_profile_example_matches_model():
    data = json.loads((ROOT / "schemas/examples/audience_profile.example.json").read_text(encoding="utf-8"))
    AudienceProfile.model_validate(data)
