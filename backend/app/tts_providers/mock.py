import io
import math
import struct
import wave

from app.tts_providers.base import TTSProvider, TTSResult
from app.services.video_formats import load_voice_options


class MockTTSProvider(TTSProvider):
    def synthesize(self, text: str, voice: str, pace: str, language: str) -> TTSResult:
        options = load_voice_options()
        multiplier = float(options["pace_multiplier"].get(pace, 1.0))
        duration = max(0.5, len(text.split()) / (float(options["base_words_per_second"]) * multiplier))
        sample_rate = 8000
        samples = int(sample_rate * duration)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(b"".join(struct.pack("<h", int(600 * math.sin(2 * math.pi * 220 * index / sample_rate))) for index in range(samples)))
        return TTSResult(content=buffer.getvalue(), provider="mock", model="mock-tts-v1", estimated_duration_seconds=duration, character_count=len(text))
