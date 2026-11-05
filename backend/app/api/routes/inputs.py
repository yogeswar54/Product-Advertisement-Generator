from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.models.input import ValidatedInputResponse
from app.modules.input_validator import validate_input

router = APIRouter(prefix="/inputs", tags=["inputs"])


@router.post("/validate", response_model=ValidatedInputResponse)
def validate(payload: dict[str, object]):
    try:
        return validate_input(payload)
    except ValidationError as exc:
        errors = exc.errors()
        first = errors[0]
        field = ".".join(str(part) for part in first["loc"] if isinstance(part, (str, int)))
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "field": field, "message": first["msg"]}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "IMAGE_VALIDATION_FAILED", "field": "product_image", "message": str(exc)}) from exc
