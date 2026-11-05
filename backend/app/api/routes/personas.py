from fastapi import APIRouter, HTTPException

from app.models.errors import ErrorDetail, ErrorResponse
from app.modules.persona_library import get_persona, list_personas

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("")
def personas():
    return list_personas()


@router.get("/{persona_id}", responses={404: {"model": ErrorResponse}})
def persona(persona_id: str):
    try:
        return get_persona(persona_id)
    except LookupError:
        raise HTTPException(status_code=404, detail={"code": "PERSONA_NOT_FOUND", "field": "persona_id", "message": f"Persona '{persona_id}' was not found."})
