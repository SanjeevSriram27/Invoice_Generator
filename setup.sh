#!/bin/bash

echo "========================================"
echo " GST Invoice Generator - Setup"
echo "========================================"
echo ""

# Backend setup
echo "[1/3] Setting up FastAPI Backend..."
cd backend_fastapi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "IMPORTANT: Before running migrations, make sure:"
echo "1. PostgreSQL is installed and running"
echo "2. Create database: CREATE DATABASE invoice_db;"
echo "3. Create user: CREATE USER invoice_user WITH PASSWORD 'your_password';"
echo "4. Grant privileges: GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;"
echo "5. Create .env file in backend_fastapi/ with your database credentials"
echo ""
read -p "Press Enter after setting up PostgreSQL and .env file..."

echo "Running database migrations..."
alembic upgrade head

echo ""
echo "Backend setup complete!"
echo ""

# Frontend setup
cd ../frontend
echo "[2/3] Setting up Next.js Frontend..."
echo "Installing frontend dependencies..."
npm install

echo ""
echo "Frontend setup complete!"
echo ""

echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "To start the servers:"
echo "  Run: ./start.sh"
echo ""
echo "Or manually:"
echo "  Backend:  cd backend_fastapi && python -m uvicorn app.main:app --reload --port 8000"
echo "  Frontend: cd frontend && npm run dev -- --port 3001"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3001"
echo "  Backend:  http://127.0.0.1:8000"
echo "  API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Note: Make sure to configure your .env file with:"
echo "  - Database credentials (PostgreSQL)"
echo "  - AWS SES credentials (for email)"
echo "  - Twilio credentials (optional, for WhatsApp)"
echo ""
