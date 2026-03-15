#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Auto-kill previous sessions on port 8000
lsof -t -i:8000 | xargs kill -9 2>/dev/null || true
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"

# Ensure .env exists
if [ ! -f .env ]; then
    echo "GOOGLE_API_KEY=your_key_here" > .env
    echo ".env file created. Please add your Gemini API Key."
fi

uvicorn main:app --reload --host 0.0.0.0 --port 8000

