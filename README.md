# AI-Based Product Advertisement Generator

A mock-first FastAPI and Streamlit application for drafting audience-adapted advertisements,
running quality checks, and exporting campaign packages for human review.

## Requirements

- Python 3.12
- Docker Desktop with Compose, optional
- No API key is required in mock mode

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the UI in another terminal:

```powershell
python -m streamlit run frontend/app.py --server.address 127.0.0.1
```

- UI: `http://127.0.0.1:8501`
- API documentation: `http://127.0.0.1:8000/docs`

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Containers default to mock providers and do not require keys.

## Verification

```powershell
$env:PYTHONPATH="backend"
python -m pytest -q
python scripts/demo_export.py
```

## Documentation

- [User guide](docs/user-guide.md)
- [Developer guide](docs/developer-guide.md)
- [API reference](docs/api.md)
- [Deployment guide](docs/deployment/deployment_guide.md)
- [Responsible use](docs/responsible-use.md)
- [Evaluation summary](docs/evaluation-summary.md)

Generated advertising content is a draft and requires human review before publication.
