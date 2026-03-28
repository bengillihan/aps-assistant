#!/usr/bin/env bash
# Start the APS Assistant FastAPI backend.
# Requires Python 3.10+. Prefers 3.12 if available, otherwise uses whatever python3 resolves to.
set -e
cd "$(dirname "$0")/backend"

PYTHON=$(command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3)
if [ -z "$PYTHON" ]; then
  echo "Error: Python 3 not found." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv with $($PYTHON --version)..."
  "$PYTHON" -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "Starting backend on http://localhost:8000"
uvicorn main:app --reload --port 8000
