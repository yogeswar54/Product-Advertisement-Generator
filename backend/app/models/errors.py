from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
    details: list[ErrorDetail] = []
