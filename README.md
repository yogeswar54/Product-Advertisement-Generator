# AI-Based Product Advertisement Generator - Stage 3

Stage 3 implements input validation, the persona library, Audience Profiler, local API, and Streamlit UI. It makes no LLM, image, TTS, or external network calls.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Run backend

```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API documentation: `http://127.0.0.1:8000/docs`

## Run frontend

In a second terminal:

```powershell
python -m streamlit run frontend/app.py --server.address 127.0.0.1
```

UI: `http://127.0.0.1:8501`

## Tests

```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests --cov=app/modules/input_validator.py --cov=app/modules/audience_profiler.py --cov-report=term-missing
```

## Endpoint examples

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/personas
Invoke-RestMethod http://127.0.0.1:8000/personas/college_students
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/inputs/validate -ContentType 'application/json' -Body (Get-Content schemas/examples/input.example.json -Raw)
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/audiences/profile -ContentType 'application/json' -Body '{"persona_id":"college_students"}'
```
