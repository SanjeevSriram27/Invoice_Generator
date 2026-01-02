@echo off
echo ========================================
echo  GST Invoice Generator - Starting...
echo ========================================
echo.

echo [1/2] Starting Backend Server (Django)...
cd backend
start "Django Backend" cmd /k "python manage.py runserver"
echo Backend starting on http://127.0.0.1:8000
echo.

echo [2/2] Starting Frontend Server (Next.js with Turbopack)...
cd ..\frontend
start "Next.js Frontend" cmd /k "npm run dev -- --turbo"
echo Frontend starting on http://localhost:3000
echo.

echo ========================================
echo  Both servers are starting!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
echo (The servers will continue running in separate windows)
pause >nul
