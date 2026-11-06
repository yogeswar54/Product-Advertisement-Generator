#!/usr/bin/env sh
set -eu
export PYTHONPATH=backend
python -m pytest -q
python scripts/demo_export.py
python scripts/content_metrics.py
