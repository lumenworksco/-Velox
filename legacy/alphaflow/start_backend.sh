#!/bin/bash
# Start AlphaFlow FastAPI Backend

echo "🚀 Starting AlphaFlow Backend..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start FastAPI server with hot reload
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at:
# - http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
# - ReDoc: http://localhost:8000/api/redoc
