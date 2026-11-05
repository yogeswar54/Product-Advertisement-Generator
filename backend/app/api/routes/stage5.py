from fastapi import APIRouter, HTTPException

from app.models.stage4 import GenerateRequest
from app.models.stage5 import SocialOutput
from app.modules.social_generator import generate_social
from app.providers.base import ProviderError
from app.providers.factory import get_llm_provider
from app.services.social_checks import run_social_checks

router = APIRouter(tags=["stage5"])
ALLOWED_PLATFORMS = {"instagram", "linkedin", "x", "facebook", "whatsapp"}


@router.post("/campaigns/social/regenerate")
def regenerate_social(request: GenerateRequest, platform: str | None = None):
    selected = [platform] if platform else list(request.product_input.platforms)
    if any(item not in ALLOWED_PLATFORMS for item in selected):
        raise HTTPException(status_code=422, detail={"code":"VALIDATION_ERROR","field":"platform","message":"Platform is not supported."})
    try:
        social = generate_social(get_llm_provider(), request.product_input, request.audience_profile, request.brief, selected)
        return {"section":"social","platform":platform,"output":social,"warnings":[warning.model_dump() for warning in run_social_checks(request.product_input, social, selected)]}
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail={"code":exc.code,"field":None,"message":exc.message}) from exc


@router.post("/campaigns/social/calendar/regenerate")
def regenerate_calendar(request: GenerateRequest):
    try:
        social = generate_social(get_llm_provider(), request.product_input, request.audience_profile, request.brief, list(request.product_input.platforms))
        warnings = run_social_checks(request.product_input, social, list(request.product_input.platforms))
        return {"section":"social_calendar","calendar":social.calendar,"warnings":[warning.model_dump() for warning in warnings]}
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail={"code":exc.code,"field":None,"message":exc.message}) from exc
