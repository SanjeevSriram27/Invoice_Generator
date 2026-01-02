#!/bin/bash

echo "========================================"
echo " GST Invoice Generator - Starting..."
echo "========================================"
echo ""

echo "[1/2] Starting Backend Server (Django)..."
cd backend
python manage.py runserver &
BACKEND_PID=$!
echo "Backend started on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo ""

echo "[2/2] Starting Frontend Server (Next.js with Turbopack)..."
cd ../frontend
npm run dev -- --turbo &
FRONTEND_PID=$!
echo "Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""

echo "========================================"
echo " Both servers are running!"
echo "========================================"
echo ""
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
