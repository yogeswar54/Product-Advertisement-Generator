# Developer Guide

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH="backend"
python -m pytest -q
```

## Structure

- `backend/app/api/routes`: FastAPI routes
- `backend/app/modules`: generation and validation modules
- `backend/app/providers`: hosted and mock text providers
- `backend/app/services`: orchestration, quality, storage, packages, and exports
- `frontend/app.py`: Streamlit UI
- `schemas/`: JSON Schemas
- `config/`: module configuration

Providers implement the abstraction in `backend/app/providers/base.py`. `LLM_PROVIDER=mock`
selects deterministic mock behavior; hosted providers require credentials supplied by the operator.

Personas are stored in `data/personas.json`. Add a persona by assigning a stable ID and filling
the existing tone, motivations, avoidances, platforms, and format fields.

Prompts live under `prompts/`. Keep prompt version identifiers in the prompt filename and use a
versioned loader; do not overwrite version history silently.

Quality checks belong under `backend/app/services/quality_checks.py` or a focused service, and
must reuse the quality report schema.
