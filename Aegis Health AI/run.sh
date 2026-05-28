#!/bin/bash
# =========================================================================
# AEGIS HEALTH PLATFORM - SYSTEM AUTO-LAUNCHER (macOS & Linux)
# =========================================================================

# Function to clean up background processes on termination
cleanup() {
    echo -e "\n\033[0;31m[*]\033[0m Shutting down Aegis Health services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT) and termination (SIGTERM) signals
trap cleanup SIGINT SIGTERM

echo "====================================================================="
echo "                 AEGIS HEALTH SYSTEM AUTO-LAUNCHER"
echo "====================================================================="
echo

# 1. Verify Python Virtual Environment
if [ ! -f "backend/venv/bin/python" ]; then
    echo -e "\033[0;33m[WARNING]\033[0m Python virtual environment not found in backend/venv/bin/python"
    echo "Attempting fallback to system python3..."
    PYTHON_EXEC="python3"
else
    PYTHON_EXEC="backend/venv/bin/python"
fi

# 2. Boot FastAPI Backend Web Server in background
echo -e "\033[0;32m[*]\033[0m Starting FastAPI Backend Web Server..."
$PYTHON_EXEC -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 3. Boot React Frontend Web App in background
echo -e "\033[0;32m[*]\033[0m Starting React Frontend Web App..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "====================================================================="
echo -e "\033[0;32mAegis Health is initializing!\033[0m"
echo
echo "  - Backend Server API:  http://127.0.0.1:8000"
echo "  - Frontend Client:      http://localhost:5173"
echo "====================================================================="
echo "Press Ctrl+C to terminate both servers..."
echo

# Keep script active to capture signals and preserve children
while true; do
    sleep 1
done
