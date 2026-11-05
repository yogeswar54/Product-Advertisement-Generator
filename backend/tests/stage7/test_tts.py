import io
import wave

from unittest.mock import Mock

from app.tts_providers.mock import MockTTSProvider
from app.tts_providers.hosted import HostedTTSProvider
from app.tts_providers.base import TTSProviderError


def test_mock_tts_wav():
    result = MockTTSProvider().synthesize("one two three four five", "warm", "normal", "en-US")
    with wave.open(io.BytesIO(result.content), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getnframes() > 0


def test_hosted_tts_timeout(monkeypatch):
    import requests
    import app.tts_providers.hosted as hosted
    monkeypatch.setenv("TTS_API_KEY", "test")
    monkeypatch.setattr(hosted.requests, "post", Mock(side_effect=requests.Timeout()))
    try:
        HostedTTSProvider().synthesize("hello", "warm", "normal", "en-US")
    except TTSProviderError as exc:
        assert exc.code == "PROVIDER_TIMEOUT"
    else:
        raise AssertionError("Timeout should map to PROVIDER_TIMEOUT")


def test_hosted_tts_success(monkeypatch):
    import app.tts_providers.hosted as hosted
    monkeypatch.setenv("TTS_API_KEY", "test")
    response = Mock()
    response.raise_for_status = Mock()
    response.content = b"RIFFtest audio"
    response.status_code = 200
    monkeypatch.setattr(hosted.requests, "post", Mock(return_value=response))
    result = HostedTTSProvider().synthesize("hello", "warm", "normal", "en-US")
    assert result.provider == "hosted"


def test_hosted_tts_requires_key(monkeypatch):
    monkeypatch.delenv("TTS_API_KEY", raising=False)
    try:
        HostedTTSProvider().synthesize("hello", "warm", "normal", "en-US")
    except TTSProviderError as exc:
        assert exc.code == "PROVIDER_AUTH_MISSING"
    else:
        raise AssertionError("Missing key should fail")
