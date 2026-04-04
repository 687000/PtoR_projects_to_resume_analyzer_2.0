#!/bin/bash
trap "kill 0" EXIT

echo "Starting API server on http://localhost:8000"
uvicorn src.api:app --reload --port 8000 &

echo "Starting frontend on http://localhost:5173"
cd frontend && npm run dev &

wait
