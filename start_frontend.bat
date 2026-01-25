@echo off
cd /d "%~dp0frontend"
echo Starting Next.js Frontend on port 3001...
echo.
set PORT=3001
npm run dev
