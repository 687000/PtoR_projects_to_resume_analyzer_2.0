#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Installing frontend dependencies..."
cd frontend && npm install && cd ..

echo "Done. Run ./run.sh to start."
