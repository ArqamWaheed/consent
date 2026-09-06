#!/usr/bin/env bash
# One command to run the demo locally.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "Copy .env.example to .env and fill it in."; exit 1; }
set -a; . ./.env; set +a
python3 -m pip install -q streamlit snowflake-connector-python
exec streamlit run app/streamlit_app.py
