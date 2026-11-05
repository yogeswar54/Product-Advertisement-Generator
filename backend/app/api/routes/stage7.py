import hashlib
import json
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models.stage4 import GenerateRequest
from app.modules.video_generator import generate_video_scripts
from app.providers.factory import get_llm_provider
from app.services.asset_storage import get_asset, load_metadata, save_media
from app.tts_providers.base import TTSProviderError
from app.tts_providers.factory import get_tts_provider
from app.video.assembly import get_job, start_video_job

router = APIRouter(tags=["stage7"])
_tts_cache: dict[str, dict[str, object]] = {}


class VoiceRequest(BaseModel):
    request: GenerateRequest
    duration: int
    voice: str = "warm"
    pace: str = "normal"
    language: str = "en-US"


class AssembleRequest(BaseModel):
    request: GenerateRequest
    duration: int


@router.post("/campaigns/video/regenerate")
def regenerate_video(request: GenerateRequest, duration: int | None = None):
    if duration not in (None, 15, 30, 60):
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"duration","message":"Duration must be 15, 30, or 60."})
    try:
        video = generate_video_scripts(get_llm_provider(), request.product_input, request.audience_profile, request.brief)
        if duration:
            return {"section":"video","duration":duration,"output":getattr(video, "scripts_" + str(duration))}
        return {"section":"video","output":video}
    except Exception as exc:
        raise HTTPException(status_code=502, detail={"code":"INVALID_RESPONSE","field":"video","message":str(exc)}) from exc


@router.post("/campaigns/video/voiceover")
def voiceover(request: VoiceRequest):
    if request.duration not in (15, 30, 60):
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"duration","message":"Duration must be 15, 30, or 60."})
    campaign_id = request.request.product_input.product_name.lower().replace(" ", "-")
    count = sum(1 for item in load_metadata() if item.get("asset_type") == "audio" and item["campaign_id"] == campaign_id)
    if count >= int(os.getenv("TTS_LIMIT_PER_CAMPAIGN", "6")):
        raise HTTPException(status_code=429, detail={"code":"AUDIO_LIMIT_REACHED","field":"voiceover","message":"The configured audio generation limit has been reached."})
    try:
        video = generate_video_scripts(get_llm_provider(), request.request.product_input, request.request.audience_profile, request.request.brief)
        script = getattr(video, "scripts_" + str(request.duration))
        provider = get_tts_provider()
        cache_key = hashlib.sha256(json.dumps({"text":script.narration,"voice":request.voice,"pace":request.pace,"language":request.language,"provider":provider.__class__.__name__,"model":getattr(provider,"model","mock-tts-v1")}, sort_keys=True).encode("utf-8")).hexdigest()
        if cache_key in _tts_cache:
            record = dict(_tts_cache[cache_key])
            record["cache_hit"] = True
            return record
        result = provider.synthesize(script.narration, request.voice, request.pace, request.language)
        record = save_media(result.content, "audio", campaign_id, result.estimated_duration_seconds, request.voice, request.pace, result.provider, result.model)
        record.update({"character_count":result.character_count,"estimated_cost_note":"Estimated cost only; check current provider pricing.","placeholder":result.provider == "mock","disclosure":"AI-generated voice; disclose where required.","cache_hit":False})
        _tts_cache[cache_key] = dict(record)
        return record
    except TTSProviderError as exc:
        raise HTTPException(status_code=502, detail={"code":exc.code,"field":"voiceover","message":str(exc)}) from exc


@router.post("/campaigns/video/assemble")
def assemble(request: AssembleRequest):
    if request.duration not in (15, 30, 60):
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"duration","message":"Duration must be 15, 30, or 60."})
    campaign_id = request.request.product_input.product_name.lower().replace(" ", "-")
    video = generate_video_scripts(get_llm_provider(), request.request.product_input, request.request.audience_profile, request.request.brief)
    script = getattr(video, "scripts_" + str(request.duration))
    audio = get_tts_provider().synthesize(script.narration, "warm", "normal", "en-US")
    return start_video_job(campaign_id, request.duration, audio.content)


@router.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code":"JOB_NOT_FOUND","field":"job_id","message":"Job was not found."})
    return job
