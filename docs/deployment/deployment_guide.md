# Deployment Guide

No public cloud deployment was performed. The supported deployment target documented here is local
Docker. Docker Desktop must be started before these commands.

## Local Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- UI: http://127.0.0.1:8501
- API: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

The containers use mock text, image, and TTS providers by default. Stop with
`docker compose down`; restart persistent local storage with `docker compose up`.

## Local without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Chosen cloud host

None. Local container hosting is documented until a host account, billing controls, and persistence
model are available. Any future host pricing must be checked from the vendor's current site on the
deployment date.
