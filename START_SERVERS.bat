@echo off
echo ================================================================================
echo Starting Invoice Generator - FastAPI Backend + Next.js Frontend
echo ================================================================================
echo.

REM Start FastAPI Backend
echo [1/2] Starting FastAPI Backend on port 8000...
cd backend_fastapi
start "FastAPI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak > nul

REM Start Next.js Frontend
echo [2/2] Starting Next.js Frontend on port 3001...
cd ..\frontend
start "Next.js Frontend" cmd /k "npm run dev -- --port 3001"
timeout /t 3 /nobreak > nul

echo.
echo ================================================================================
echo Servers Starting...
echo ================================================================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3001
echo.
echo Press Ctrl+C in each window to stop the servers
echo ================================================================================
