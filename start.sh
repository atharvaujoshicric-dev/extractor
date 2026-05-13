#!/bin/bash

echo "============================================"
echo "  ContactMine — B2B Contact Intelligence"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is required. Please install it first."
    exit 1
fi

# Install deps
echo "[1/3] Installing Python dependencies..."
cd backend
pip install -r requirements.txt -q
echo "      ✓ Dependencies installed"

# Start backend
echo "[2/3] Starting Flask backend on port 5000..."
python3 app.py &
BACKEND_PID=$!
echo "      ✓ Backend running (PID: $BACKEND_PID)"

# Wait for backend
sleep 2

# Open frontend
echo "[3/3] Opening frontend..."
FRONTEND_PATH="$(pwd)/../frontend/index.html"

if command -v xdg-open &> /dev/null; then
    xdg-open "$FRONTEND_PATH"
elif command -v open &> /dev/null; then
    open "$FRONTEND_PATH"
else
    echo "      Open this file in your browser: $FRONTEND_PATH"
fi

echo ""
echo "============================================"
echo "  ✓ ContactMine is running!"
echo "  Backend: http://localhost:5000"
echo "  Frontend: frontend/index.html"
echo "  Press Ctrl+C to stop"
echo "============================================"

wait $BACKEND_PID
