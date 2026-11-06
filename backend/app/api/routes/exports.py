from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Export, get_db


router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/{export_id}")
def download_export(export_id: str, db: Session = Depends(get_db)):
    record: Export | None = db.get(Export, export_id)
    if record is None:
        raise HTTPException(404, {"code": "EXPORT_NOT_FOUND", "field": "id", "message": "Export not found"})
    path = Path(record.file_path)
    if not path.is_file():
        raise HTTPException(409, {"code": "EXPORT_INTEGRITY_FAILURE", "field": "file", "message": "Stored export is missing"})
    if path.stat().st_size != record.file_size:
        raise HTTPException(409, {"code": "EXPORT_INTEGRITY_FAILURE", "field": "file", "message": "Stored export size does not match"})
    return FileResponse(path, filename=path.name)
