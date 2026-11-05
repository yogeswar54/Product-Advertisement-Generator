from app.models.stage6 import VisualOutput
from app.services.visual_checks import run_visual_checks


def visual_output() -> VisualOutput:
    import json
    from pathlib import Path
    data = json.loads(Path("schemas/examples/visual_output.example.json").read_text(encoding="utf-8"))
    return VisualOutput.model_validate(data)


def test_safety_check():
    visual = visual_output()
    visual.concepts[0].image_prompts["poster"] += " in the style of a famous artist"
    warnings = run_visual_checks(visual, "700 ml")
    assert any(warning.code == "VISUAL_PROMPT_SAFETY" for warning in warnings)


def test_low_contrast_warning():
    visual = visual_output()
    for color in visual.concepts[0].color_palette:
        if color.role == "text":
            color.hex = "#FFFFFF"
    warnings = run_visual_checks(visual, "700 ml")
    assert any(warning.code == "VISUAL_LOW_CONTRAST" for warning in warnings)


def test_unsupported_image_text_number():
    visual = visual_output()
    visual.concepts[0].on_image_text.headline = "99 reasons"
    warnings = run_visual_checks(visual, "700 ml")
    assert any(warning.code == "VISUAL_UNSUPPORTED_NUMBER" for warning in warnings)
