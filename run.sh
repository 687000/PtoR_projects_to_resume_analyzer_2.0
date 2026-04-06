#!/bin/bash
set -e

# Optionally build frontend in dev mode
if [ "$1" = "--dev" ]; then
  echo "Starting backend (port 8000) and frontend dev server (port 5173)..."
  uvicorn src.api:app --reload --port 8000 &
  BACKEND_PID=$!
  cd frontend && npm run dev
  kill $BACKEND_PID 2>/dev/null || true
else
  echo "Starting PtoR server on http://localhost:8000"
  uvicorn src.api:app --host 0.0.0.0 --port 8000
fi
