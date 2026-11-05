from __future__ import annotations

import hashlib
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.image_providers.base import ImageProviderResult
from app.image_providers.factory import get_image_provider
from app.models.stage4 import GenerateRequest
from app.modules.visual_generator import generate_visuals
from app.providers.base import ProviderError
from app.providers.factory import get_llm_provider
from app.services.asset_storage import get_asset, load_metadata, save_asset
from app.services.visual_formats import load_visual_formats

router = APIRouter(tags=["stage6"])


class ImageRequest(BaseModel):
    request: GenerateRequest
    concept_index: int = Field(ge=0, le=2)
    format: str


@router.post("/campaigns/visuals/regenerate")
def regenerate_visuals(request: GenerateRequest, concept: int | None = None):
    try:
        visual = generate_visuals(get_llm_provider(), request.product_input, request.audience_profile, request.brief)
        if concept is not None:
            if concept < 0 or concept > 2:
                raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"concept","message":"Concept index must be 0, 1, or 2."})
            return {"section":"visual","concept_index":concept,"output":visual.concepts[concept]}
        return {"section":"visual","output":visual}
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail={"code":exc.code,"field":None,"message":exc.message}) from exc


@router.post("/campaigns/visuals/images")
def generate_image(request: ImageRequest):
    formats = load_visual_formats()
    if request.format not in formats:
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"format","message":"Unsupported visual format."})
    campaign_id = hashlib.sha256(request.request.product_input.model_dump_json().encode("utf-8")).hexdigest()[:12]
    metadata = load_metadata()
    limit = max(0, int(os.getenv("IMAGE_LIMIT_PER_CAMPAIGN", "4")))
    if sum(1 for item in metadata if item["campaign_id"] == campaign_id) >= limit:
        raise HTTPException(status_code=429, detail={"code":"IMAGE_LIMIT_REACHED","field":"images","message":"The configured image limit for this campaign has been reached."})
    try:
        visual = generate_visuals(get_llm_provider(), request.request.product_input, request.request.audience_profile, request.request.brief)
        concept = visual.concepts[request.concept_index]
        prompt = concept.image_prompts[request.format]
        config = formats[request.format]
        result = get_image_provider().generate_image(prompt, concept.negative_prompt, config["width"], config["height"])
        record = save_asset(result.content, campaign_id, concept.name, request.format, prompt, result.provider, result.model)
        record["placeholder"] = result.provider == "mock"
        record["estimated_cost_note"] = "Estimated cost only; check current vendor pricing."
        return record
    except (ProviderError, ValueError) as exc:
        raise HTTPException(status_code=502, detail={"code":getattr(exc,"code","INVALID_RESPONSE"),"field":"image","message":str(exc)}) from exc


@router.get("/assets/{asset_id}")
def serve_asset(asset_id: str):
    path = get_asset(asset_id)
    if path is None:
        raise HTTPException(status_code=404, detail={"code":"ASSET_NOT_FOUND","field":"asset_id","message":"Asset was not found."})
    media_type = "audio/wav" if path.suffix == ".wav" else "video/mp4" if path.suffix == ".mp4" else "image/png"
    return FileResponse(path, media_type=media_type)


@router.get("/campaigns/{campaign_id}/assets")
def list_assets(campaign_id: str):
    if not campaign_id or ".." in campaign_id or "/" in campaign_id or "\\" in campaign_id:
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"campaign_id","message":"Invalid campaign reference."})
    return [item for item in load_metadata() if item["campaign_id"] == campaign_id]
