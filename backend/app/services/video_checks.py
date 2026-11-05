import re

from app.models.input import CampaignInput
from app.models.stage4 import Warning
from app.models.stage7 import VideoOutput, VideoScript
from app.services.video_formats import load_video_formats, spoken_duration_seconds

RISKY_TERMS = ("clinically proven", "cures", "guaranteed result", "#1 best", "award winning", "before and after")
BRAND_MUSIC_TERMS = ("beatles", "taylor swift", "spotify song", "celebrity", "public figure")


def run_video_checks(product: CampaignInput, video: VideoOutput, tolerance_seconds: float = 20.0) -> list[Warning]:
    warnings: list[Warning] = []
    formats = load_video_formats()
    supplied = " ".join([product.product_name, product.category, product.usp, " ".join(product.key_features)])
    supplied_numbers = set(re.findall(r"\d+(?:\.\d+)?(?:%)?", supplied))
    for duration in ("15", "30", "60"):
        script = getattr(video, "scripts_" + duration)
        config = formats[duration]
        expected = spoken_duration_seconds(script.narration, float(config["speaking_pace_words_per_second"]))
        if abs(script.estimated_spoken_seconds - expected) > tolerance_seconds:
            warnings.append(Warning(code="VIDEO_DURATION_TOLERANCE", message=f"{duration}-second script estimated duration differs from narration calculation."))
        scenes = script.scenes
        if scenes[0].start != 0 or scenes[-1].end != config["duration_seconds"]:
            warnings.append(Warning(code="VIDEO_TIMELINE", message=f"{duration}-second scenes do not start at 0 and end at target duration."))
        if any(scene.start != expected_start for scene, expected_start in zip(scenes[1:], [previous.end for previous in scenes[:-1]])):
            warnings.append(Warning(code="VIDEO_TIMELINE", message=f"{duration}-second scene timings are not continuous."))
        if scenes[0].start > 3 or not script.hook.strip():
            warnings.append(Warning(code="VIDEO_HOOK_MISSING", message=f"{duration}-second script has no hook inside the first 3 seconds."))
        if not script.cta.strip() or script.cta.lower() not in scenes[-1].narration.lower() and script.cta.lower() not in scenes[-1].on_screen_text.lower():
            warnings.append(Warning(code="VIDEO_CTA_MISSING", message=f"{duration}-second script CTA is missing from the final scene."))
        lower = script.narration.lower()
        for term in RISKY_TERMS:
            if term in lower:
                warnings.append(Warning(code="RISKY_CLAIM_WORD", message=f"{duration}-second script contains risky term '{term}'."))
        for number in re.findall(r"\d+(?:\.\d+)?(?:%)?", script.narration + script.on_screen_text if False else " ".join([scene.narration + " " + scene.on_screen_text for scene in scenes])):
            if number not in supplied_numbers:
                warnings.append(Warning(code="UNSUPPORTED_NUMBER", message=f"{duration}-second script contains unsupported number '{number}'."))
        if re.search(r"\[[^\]]+\]|\([^)]*pause[^)]*\)|\bwhisper\b", script.narration, re.IGNORECASE):
            warnings.append(Warning(code="VIDEO_STAGE_DIRECTION", message=f"{duration}-second narration contains stage directions or bracketed notes."))
        combined_visual_music = " ".join([scene.visual + " " + scene.music_mood for scene in scenes]).lower()
        for term in BRAND_MUSIC_TERMS:
            if term in combined_visual_music:
                warnings.append(Warning(code="VIDEO_COPYRIGHT_TERM", message=f"{duration}-second script contains restricted music or public-name term '{term}'."))
    return warnings
