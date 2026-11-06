# Stage 9 Summary

## What was built

Stage 9 adds SQLite/SQLAlchemy campaign persistence, package assembly, reversible section editing,
campaign history, JSON/DOCX/PDF/ZIP exports, export approval gating, export settings, Stage 9 API
routes, and smoke-test coverage.

## Running

- Mock/demo: `python scripts/demo_export.py`
- API: `python -m uvicorn app.main:app --app-dir backend`
- Tests: `python -m pytest -q`

## Database

SQLite is initialized automatically at startup using `storage/campaigns.db`. Schema creation is
idempotent through SQLAlchemy `create_all`. Existing asset metadata remains compatible with the
existing `asset_storage` module. Import legacy assets from PowerShell:

```powershell
$env:PYTHONPATH="backend"
python scripts\migrate_asset_metadata.py
```

The script is idempotent and preserves `metadata.json`.

## Export gating

Export approval is enabled by default through `EXPORT_REQUIRES_APPROVAL=true` semantics in
`config/export_settings.json`. When disabled, this is a testing-only mode and exports remain
unapproved drafts.

## FR-27 deviation

FR-27 remains a Won't item from Stage 1. Stage 9 implements only the last manually edited value
per section, with a configurable five-version retention window and revert support.

## Assumptions and corrections

- The MVP uses SQLite and local files, not PostgreSQL or object storage.
- The package schema was added because no campaign-package schema existed in the repository.
- Export disclosure wording is configuration-driven in `config/export_settings.json`.
- Live export approval must be supplied by a current quality report and approval record.
- The Streamlit history panel saves generated campaigns and exposes package review, section JSON
  editing/revert, quality rerun, approval, duplication, deletion, and exports. It does not provide
  an individual inline editor for every nested text property.
