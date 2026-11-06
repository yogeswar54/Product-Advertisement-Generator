$ErrorActionPreference = "Stop"
Write-Host "Stage 10 mock-mode suite"
python -m pytest -q backend/tests tests/test_stage10_reliability.py tests/security/test_stage10_safety.py
python scripts/content_metrics.py
python scripts/eval_human_results.py
Write-Host "Suite summary: automated tests passed; review docs/stage10 reports for gates."
