import json
from pathlib import Path
from app.models.stage7 import VideoOutput
from app.services.video_checks import run_video_checks
from app.models.input import CampaignInput

PRODUCT=CampaignInput(product_name="CampusFlow Bottle",category="Reusable water bottle",key_features=["700 ml capacity"],usp="Easy campus carry",brand_voice="Friendly",target_audience="college_students",campaign_goal="Conversions",platforms=["instagram"],language="en-US")


def load_video():
    return VideoOutput.model_validate(json.loads(Path("schemas/examples/video_output.example.json").read_text()))


def test_missing_hook():
    video=load_video(); video.scripts_15.hook=""
    warnings=run_video_checks(PRODUCT,video)
    assert any(w.code == "VIDEO_HOOK_MISSING" for w in warnings)


def test_risky_claim():
    video=load_video(); video.scripts_15.narration="This clinically proven bottle cures fatigue"
    warnings=run_video_checks(PRODUCT,video)
    assert any(w.code == "RISKY_CLAIM_WORD" for w in warnings)


def test_stage_direction():
    video=load_video(); video.scripts_15.narration="[whisper] CampusFlow bottle."
    warnings=run_video_checks(PRODUCT,video)
    assert any(w.code == "VIDEO_STAGE_DIRECTION" for w in warnings)
