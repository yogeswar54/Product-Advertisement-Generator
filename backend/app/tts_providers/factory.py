import os
from app.tts_providers.base import TTSProvider
from app.tts_providers.hosted import HostedTTSProvider
from app.tts_providers.mock import MockTTSProvider


def get_tts_provider() -> TTSProvider:
    return MockTTSProvider() if os.getenv("TTS_PROVIDER", "mock").lower() == "mock" else HostedTTSProvider()
