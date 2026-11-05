from __future__ import annotations

import shutil
import subprocess
import threading
import uuid
from pathlib import Path

from app.services.asset_storage import ASSET_ROOT, save_media
from app.services.video_formats import load_voice_options

_jobs: dict[str, dict[str, object]] = {}


def start_video_job(campaign_id: str, duration: int, placeholder_audio: bytes, image_path: Path | None = None) -> dict[str, object]:
    job_id = uuid.uuid4().hex
    _jobs[job_id] = {"job_id":job_id,"status":"queued","progress":0,"campaign_id":campaign_id,"duration":duration,"asset_id":None,"error":None}
    thread = threading.Thread(target=_assemble_placeholder, args=(job_id, campaign_id, duration, placeholder_audio), daemon=True)
    thread.start()
    return _jobs[job_id]


def _assemble_placeholder(job_id: str, campaign_id: str, duration: int, audio: bytes) -> None:
    _jobs[job_id]["status"] = "running"
    _jobs[job_id]["progress"] = 20
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["progress"] = 100
        _jobs[job_id]["error"] = "FFmpeg is not installed. Install FFmpeg and ensure it is on PATH. The rest of the app remains available."
        return
    audio_path = ASSET_ROOT / f"{job_id}-audio.wav"
    audio_path.write_bytes(audio)
    video_path = ASSET_ROOT / f"{job_id}-draft.mp4"
    _jobs[job_id]["progress"] = 55
    try:
        resolution = load_voice_options()["assembly_resolution"]
        size = f"{resolution['width']}x{resolution['height']}"
        subprocess.run([ffmpeg,"-y","-f","lavfi","-i",f"color=c=0xD9E5F2:s={size}:d={duration}","-i",str(audio_path),"-shortest","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(video_path)], check=True, capture_output=True)
        content = video_path.read_bytes()
        record = save_media(content, "video", campaign_id, float(duration), "warm", "normal", "mock", "mock-video-v1")
        _jobs[job_id]["asset_id"] = record["id"]
        _jobs[job_id]["progress"] = 100
        _jobs[job_id]["status"] = "completed"
        audio_path.unlink(missing_ok=True)
        video_path.unlink(missing_ok=True)
    except subprocess.CalledProcessError as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["progress"] = 100
        _jobs[job_id]["error"] = "Draft video assembly failed: " + exc.stderr.decode("utf-8", errors="replace")[:500]


def get_job(job_id: str) -> dict[str, object] | None:
    return _jobs.get(job_id)
