from __future__ import annotations

import io
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

ASSET_ROOT = Path(__file__).resolve().parents[3] / "storage" / "assets"
METADATA_PATH = ASSET_ROOT / "metadata.json"
MAX_ASSET_BYTES = 15 * 1024 * 1024


def save_asset(content: bytes, campaign_id: str, concept: str, format_name: str, prompt: str, provider: str, model: str, max_bytes: int = MAX_ASSET_BYTES) -> dict[str, object]:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    if len(content) > max_bytes:
        raise ValueError("Generated image exceeds configured size limit")
    if not safe_component(campaign_id) or not safe_component(concept) or not safe_component(format_name):
        raise ValueError("Unsafe asset metadata component")
    try:
        source = Image.open(io.BytesIO(content))
        source.verify()
    except Exception as exc:
        raise ValueError("Generated asset is not a valid image") from exc
    source = Image.open(io.BytesIO(content)).convert("RGB")
    asset_id = uuid.uuid4().hex
    path = ASSET_ROOT / f"{asset_id}.png"
    source.save(path, format="PNG", optimize=True)
    metadata = load_metadata()
    record = {"id":asset_id,"campaign_id":campaign_id,"concept":concept,"format":format_name,"prompt":prompt,"provider":provider,"model":model,"created_time":datetime.now(timezone.utc).isoformat(),"path":str(path)}
    metadata.append(record)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return record


def load_metadata() -> list[dict[str, object]]:
    if not METADATA_PATH.exists():
        return []
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def safe_component(value: str) -> bool:
    return bool(value) and ".." not in value and not re.search(r"[/\\]", value) and bool(re.fullmatch(r"[A-Za-z0-9 _-]+", value.strip()))


def get_asset(asset_id: str) -> Path | None:
    if not re.fullmatch(r"[0-9a-f]{32}", asset_id):
        return None
    for extension in ("png", "wav", "mp4"):
        path = ASSET_ROOT / f"{asset_id}.{extension}"
        if path.is_file():
            return path
    return None


def save_media(content: bytes, asset_type: str, campaign_id: str, duration: float, voice: str, pace: str, provider: str, model: str, max_bytes: int = MAX_ASSET_BYTES) -> dict[str, object]:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    if asset_type not in {"audio", "video"}:
        raise ValueError("asset_type must be audio or video")
    if len(content) > max_bytes:
        raise ValueError("Media asset exceeds configured size limit")
    if not safe_component(campaign_id):
        raise ValueError("Unsafe campaign reference")
    extension = "wav" if asset_type == "audio" else "mp4"
    asset_id = uuid.uuid4().hex
    path = ASSET_ROOT / f"{asset_id}.{extension}"
    path.write_bytes(content)
    metadata = load_metadata()
    record = {"id":asset_id,"asset_type":asset_type,"campaign_id":campaign_id,"duration":duration,"voice":voice,"pace":pace,"provider":provider,"model":model,"created_time":datetime.now(timezone.utc).isoformat(),"path":str(path)}
    metadata.append(record)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return record


def cleanup_assets(days: int = 30) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(days, 0))
    removed = 0
    metadata = load_metadata()
    retained = []
    for record in metadata:
        created = datetime.fromisoformat(str(record["created_time"]))
        path = Path(str(record["path"]))
        if created < cutoff and path.resolve().parent == ASSET_ROOT.resolve():
            path.unlink(missing_ok=True)
            removed += 1
        else:
            retained.append(record)
    METADATA_PATH.write_text(json.dumps(retained, indent=2), encoding="utf-8")
    return removed
