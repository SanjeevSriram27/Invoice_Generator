@echo off
echo ===================================
echo   Invoice Generator Backend
echo ===================================
echo.

cd backend
call venv\Scripts\activate

echo Starting Django server...
echo.
echo Backend will be available at: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo Username: admin
echo Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
