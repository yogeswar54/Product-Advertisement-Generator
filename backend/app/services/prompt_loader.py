from __future__ import annotations

import re
from pathlib import Path

PROMPT_DIRECTORY = Path(__file__).resolve().parents[3] / "prompts"
PLACEHOLDER = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


class PromptLoadError(ValueError):
    pass


def load_prompt(version: str, values: dict[str, object]) -> tuple[str, float, int]:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*_v[0-9]+", version):
        raise PromptLoadError(f"Invalid prompt version: {version}")
    path = PROMPT_DIRECTORY / f"{version}.md"
    if not path.is_file():
        raise PromptLoadError(f"Prompt file not found: {path}")
    text = path.read_text(encoding="utf-8")
    metadata = parse_metadata(text)
    missing = sorted({name for name in PLACEHOLDER.findall(text) if name not in values})
    if missing:
        raise PromptLoadError("Missing prompt placeholders: " + ", ".join(missing))
    rendered = PLACEHOLDER.sub(lambda match: str(values[match.group(1)]), text)
    return rendered, float(metadata["temperature"]), int(metadata["max_tokens"])


def parse_metadata(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith("["):
            key, value = line.split(":", 1)
            if key.strip() in {"version", "temperature", "max_tokens"}:
                result[key.strip()] = value.strip()
    return result
