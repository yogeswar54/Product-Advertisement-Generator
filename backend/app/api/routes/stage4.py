from fastapi import APIRouter, HTTPException

from app.models.stage4 import BriefRequest, CampaignBrief, GenerateRequest, RegenerateRequest
from app.modules.brief_builder import build_brief
from app.modules.description_generator import generate_descriptions
from app.modules.promo_generator import generate_promo
from app.providers.base import ProviderError
from app.providers.factory import get_llm_provider
from app.services.lightweight_checks import run_lightweight_checks
from app.services.orchestrator import generate_text_package

router = APIRouter(tags=["stage4"])
_briefs: dict[str, CampaignBrief] = {}


def provider_error(exc: ProviderError) -> HTTPException:
    status = 503 if exc.code in {"PROVIDER_TIMEOUT", "PROVIDER_UNAVAILABLE"} else 429 if exc.code == "PROVIDER_RATE_LIMIT" else 502
    return HTTPException(status_code=status, detail={"code":exc.code,"field":None,"message":exc.message})


@router.post("/campaigns/brief")
def create_brief(request: BriefRequest):
    try:
        brief = build_brief(get_llm_provider(), request.product_input, request.audience_profile)
    except ProviderError as exc:
        raise provider_error(exc) from exc
    key = request.product_input.product_name.lower()
    _briefs[key] = brief
    return brief


@router.put("/campaigns/brief")
def edit_brief(request: GenerateRequest):
    key = request.product_input.product_name.lower()
    _briefs[key] = request.brief
    return request.brief


@router.post("/campaigns/generate")
def generate(request: GenerateRequest):
    try:
        return generate_text_package(get_llm_provider(), request.product_input, request.audience_profile, request.brief)
    except ProviderError as exc:
        raise provider_error(exc) from exc


@router.post("/campaigns/{section}/regenerate")
def regenerate(section: str, request: RegenerateRequest):
    if section not in {"description", "promo"}:
        raise HTTPException(status_code=404, detail={"code":"SECTION_NOT_FOUND","field":"section","message":"Only description and promo sections can be regenerated."})
    try:
        provider = get_llm_provider()
        if section == "description":
            output = generate_descriptions(provider, request.product_input, request.audience_profile, request.brief)
            warnings = run_lightweight_checks(request.product_input, output)
        else:
            output = generate_promo(provider, request.product_input, request.audience_profile, request.brief)
            warnings = run_lightweight_checks(request.product_input, promo=output)
        return {"section":section,"output":output,"warnings":[warning.model_dump() for warning in warnings],"estimated_tokens_used":350}
    except ProviderError as exc:
        raise provider_error(exc) from exc
