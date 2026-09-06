#!/usr/bin/env bash
# One command to run the demo locally.
#
# With no .env it runs in snapshot mode and says so on screen.
# With a .env carrying CONSENT_APP credentials it connects to the warehouse.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a; . ./.env; set +a
  echo "Using .env — attempting a live warehouse connection."
else
  echo "No .env found — starting in snapshot mode. Copy .env.example to .env for live mode."
fi

PY=.venv/bin/python
[ -x "$PY" ] || { python3 -m venv .venv; .venv/bin/pip install -q -r requirements.txt; }

exec .venv/bin/streamlit run app/streamlit_app.py
