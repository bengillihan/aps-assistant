#!/usr/bin/env bash
# Start the APS Assistant FastAPI backend
set -e
cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv with Python 3.12..."
  python3.12 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo "Starting backend on http://localhost:8000"
uvicorn main:app --reload --port 8000
