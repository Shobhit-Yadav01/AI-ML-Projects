@echo off
title Aegis Health Launcher
color 0A
echo =====================================================================
echo                 AEGIS HEALTH SYSTEM AUTO-LAUNCHER
echo =====================================================================
echo.
echo [*] Checking local environment structures...

:: Check if virtual environment exists
if not exist "backend\venv\Scripts\python.exe" (
    echo [WARNING] venv python not found in backend\venv\Scripts\python.exe.
    echo Trying fallback to system python...
    set PYTHON_EXEC=python
) else (
    set PYTHON_EXEC=backend\venv\Scripts\python.exe
)

echo [*] Starting FastAPI Backend Web Server...
:: Start uvicorn from the project root directly to resolve package path imports
start "Aegis Health Backend Service" cmd /k "title Aegis Health Backend && %PYTHON_EXEC% -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"

echo [*] Starting React Frontend Web App...
start "Aegis Health Frontend Client" cmd /k "title Aegis Health Frontend && cd frontend && npm run dev"

echo.
echo =====================================================================
echo Aegis Health is initializing!
echo.
echo   - Backend Server API:  http://127.0.0.1:8000
echo   - Frontend Client:      http://localhost:5173 
echo                           (or the port shown in the frontend window)
echo =====================================================================
echo.
echo Launcher terminal is active. Press any key to exit this terminal...
pause > nul
