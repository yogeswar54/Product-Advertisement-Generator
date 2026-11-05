import os
import requests

from app.tts_providers.base import TTSProvider, TTSProviderError, TTSResult
from app.services.video_formats import load_voice_options


class HostedTTSProvider(TTSProvider):
    def synthesize(self, text: str, voice: str, pace: str, language: str) -> TTSResult:
        api_key = os.getenv("TTS_API_KEY", "")
        if not api_key:
            raise TTSProviderError("PROVIDER_AUTH_MISSING", "TTS_API_KEY is required for hosted TTS.")
        try:
            response = requests.post(os.getenv("TTS_API_BASE_URL", "https://api.example.invalid/v1") + "/speech", headers={"Authorization":"Bearer " + api_key,"Content-Type":"application/json"}, json={"text":text,"voice":voice,"pace":pace,"language":language,"model":os.getenv("TTS_MODEL","configured-tts-model")}, timeout=float(os.getenv("TTS_TIMEOUT_SECONDS","30")))
            response.raise_for_status()
            options = load_voice_options()
            multiplier = float(options["pace_multiplier"].get(pace, 1.0))
            duration = len(text.split()) / (float(options["base_words_per_second"]) * multiplier)
            return TTSResult(content=response.content, provider="hosted", model=os.getenv("TTS_MODEL","configured-tts-model"), estimated_duration_seconds=duration, character_count=len(text))
        except requests.Timeout as exc:
            raise TTSProviderError("PROVIDER_TIMEOUT", "TTS provider timed out.") from exc
        except requests.RequestException as exc:
            if getattr(exc.response, "status_code", None) == 429:
                raise TTSProviderError("PROVIDER_RATE_LIMIT", "TTS provider rate limit reached.") from exc
            raise TTSProviderError("PROVIDER_UNAVAILABLE", "TTS provider is unavailable.") from exc
