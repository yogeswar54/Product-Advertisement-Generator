from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderUsage:
    input_tokens: int
    output_tokens: int
    estimated: bool = True


@dataclass
class ProviderResult:
    text: str
    usage: ProviderUsage
    model: str


class ProviderError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, system: str, user: str, schema: dict[str, Any], temperature: float, max_tokens: int) -> ProviderResult:
        raise NotImplementedError
