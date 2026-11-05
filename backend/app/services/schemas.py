import json
from pathlib import Path
from typing import Any

SCHEMA_DIRECTORY = Path(__file__).resolve().parents[3] / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIRECTORY / name
    if not path.is_file():
        raise FileNotFoundError(f"Schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
