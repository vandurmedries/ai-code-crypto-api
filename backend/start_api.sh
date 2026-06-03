#!/bin/bash
# AI Code & Crypto API — Startup Script
# Used by launchd to start the API server

cd /Users/arianeheylen/CascadeProjects/ai-earning-platform/backend

# Activate virtual environment
source venv/bin/activate

# Start uvicorn with production settings
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --log-level info
