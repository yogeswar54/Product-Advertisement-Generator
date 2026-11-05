from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TTSResult:
    content: bytes
    provider: str
    model: str
    estimated_duration_seconds: float
    character_count: int
    media_type: str = "audio/wav"


class TTSProviderError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str, pace: str, language: str) -> TTSResult:
        raise NotImplementedError
