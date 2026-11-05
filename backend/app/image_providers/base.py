from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageProviderResult:
    content: bytes
    provider: str
    model: str
    media_type: str = "image/png"


class ImageProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str, width: int, height: int, reference_image: Path | None = None) -> ImageProviderResult:
        raise NotImplementedError
