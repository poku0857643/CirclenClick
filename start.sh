#!/bin/bash
# CircleNClick Startup Script
# Starts the FastAPI backend server

cd "$(dirname "$0")"

echo "🚀 Starting CircleNClick Backend..."
echo ""

# Check if backend is already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8080 is already in use"
    echo "Stopping existing process..."
    pkill -f "uvicorn api.app:app"
    sleep 2
fi

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo "──────────────────────────────────────────────────────"
echo ""

python -m uvicorn api.app:app --host localhost --port 8080 --reload

echo ""
echo "✅ Server stopped"
