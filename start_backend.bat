@echo off
cd /d "%~dp0backend_fastapi"
echo Starting FastAPI Backend on port 8000...
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
