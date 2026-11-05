import json
from app.services.video_formats import load_video_formats, load_voice_options, spoken_duration_seconds


def test_video_configs():
    formats = load_video_formats()
    assert set(formats) == {"15", "30", "60"}
    for duration, config in formats.items():
        assert config["duration_seconds"] == int(duration)
        assert config["speaking_pace_words_per_second"] > 0


def test_voice_options():
    options = load_voice_options()
    assert "normal" in options["paces"]
    assert options["pace_multiplier"]["normal"] == 1.0


def test_spoken_duration():
    assert spoken_duration_seconds("one two three four five", 2.5) == 2.0
