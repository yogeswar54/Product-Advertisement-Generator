import json
from pathlib import Path

FORMATS_PATH = Path(__file__).resolve().parents[3] / "config" / "video_formats.json"
VOICE_PATH = Path(__file__).resolve().parents[3] / "config" / "voice_options.json"


def load_video_formats(path: Path = FORMATS_PATH) -> dict[str, dict[str, object]]:
    formats = json.loads(path.read_text(encoding="utf-8"))
    if set(formats) != {"15", "30", "60"}:
        raise ValueError("video_formats.json must contain 15, 30, and 60")
    for duration, config in formats.items():
        required = {"duration_seconds", "speaking_pace_words_per_second", "min_words", "max_words", "scene_count", "hook_window_seconds", "cta_window_seconds", "platforms"}
        if set(config) != required or config["duration_seconds"] != int(duration):
            raise ValueError(f"Invalid video format: {duration}")
        if config["speaking_pace_words_per_second"] <= 0 or config["min_words"] < 1 or config["max_words"] < config["min_words"]:
            raise ValueError(f"Invalid duration estimates: {duration}")
    return formats


def load_voice_options(path: Path = VOICE_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def spoken_duration_seconds(text: str, words_per_second: float, pace: str = "normal") -> float:
    voices = load_voice_options()
    multiplier = float(voices["pace_multiplier"].get(pace, 1.0))
    words = len(text.split())
    return words / (words_per_second * multiplier)
