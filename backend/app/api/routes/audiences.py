from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.models.audience import AudienceProfile, AudienceProfileRequest
from app.modules.audience_profiler import profile_audience
from app.modules.persona_library import get_persona

router = APIRouter(prefix="/audiences", tags=["audiences"])


@router.post("/profile", response_model=AudienceProfile)
def profile(request: AudienceProfileRequest):
    try:
        return profile_audience(request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail={"code": "PERSONA_NOT_FOUND", "field": "persona_id", "message": str(exc)}) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "field": None, "message": exc.errors()[0]["msg"]}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "BIAS_GUARD_REJECTED", "field": "custom_audience", "message": str(exc)}) from exc
