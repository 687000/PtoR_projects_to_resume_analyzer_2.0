#!/bin/bash
set -e

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "==> Installing frontend dependencies..."
cd frontend && npm install && cd ..

echo ""
echo "==> Building frontend..."
cd frontend && npm run build && cd ..

echo ""
echo "==> Setup complete."
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and fill in ANTHROPIC_API_KEY"
echo "  2. Run: bash run.sh"
