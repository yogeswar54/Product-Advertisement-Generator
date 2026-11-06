from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import audiences, campaign_history, exports, inputs, personas, quality, stage4, stage5, stage6, stage7
from app.database import init_db
from app.services.export_service import load_export_settings
from app.modules.persona_library import load_personas

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_personas()
    init_db()
    yield


app = FastAPI(title="AI-Based Product Advertisement Generator", version="0.4.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_CORS_ORIGINS", "http://127.0.0.1:8501,http://localhost:8501").split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(personas.router)
app.include_router(inputs.router)
app.include_router(audiences.router)
app.include_router(stage5.router)
app.include_router(stage6.router)
app.include_router(stage7.router)
app.include_router(stage4.router)
app.include_router(quality.router)
app.include_router(campaign_history.router)
app.include_router(exports.router)

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
    return {"status": "ok", "stage": "9"}


@app.get("/config/export-settings")
def export_settings():
    return load_export_settings()
