from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import audiences, inputs, personas, stage4, stage5, stage6, stage7
from app.modules.persona_library import load_personas

app = FastAPI(title="AI-Based Product Advertisement Generator", version="0.4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_CORS_ORIGINS", "http://127.0.0.1:8501,http://localhost:8501").split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(personas.router)
app.include_router(inputs.router)
app.include_router(audiences.router)
app.include_router(stage5.router)
app.include_router(stage6.router)
app.include_router(stage7.router)
app.include_router(stage4.router)


@app.on_event("startup")
def startup() -> None:
    load_personas()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        detail = exc.detail
    else:
        detail = {"code": "HTTP_ERROR", "field": None, "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": detail, "details": []})


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    details = exc.errors()
    first = details[0]
    field = ".".join(str(part) for part in first["loc"] if isinstance(part, (str, int)))
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "field": field, "message": first["msg"]}, "details": []})


@app.get("/health")
def health():
    return {"status": "ok", "stage": "5"}
