@echo off
echo ========================================
echo  Stopping All Servers...
echo ========================================
echo.

echo Killing Node.js processes (Frontend)...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% == 0 (
    echo Frontend stopped successfully
) else (
    echo No Node.js processes found
)
echo.

echo Killing Python processes (Backend)...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% == 0 (
    echo Backend stopped successfully
) else (
    echo No Python processes found
)
echo.

echo ========================================
echo  All servers stopped!
echo ========================================
echo.
pause
