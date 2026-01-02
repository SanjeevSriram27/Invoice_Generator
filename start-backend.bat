@echo off
echo ========================================
echo  Starting Backend Server (Django)...
echo ========================================
echo.

cd backend
python manage.py runserver

echo.
echo Backend server stopped.
pause
