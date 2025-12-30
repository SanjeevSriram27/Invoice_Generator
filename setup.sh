#!/bin/bash

echo "🚀 Setting up Invoice Generator Project..."

# Create backend
echo "\n📦 Setting up Django Backend..."
cd backend
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "\n🗄️ Setting up database..."
python manage.py migrate
python manage.py loaddata initial_data.json

echo "\n✅ Backend setup complete!"

# Create frontend
cd ../frontend
echo "\n📦 Setting up Next.js Frontend..."
npm install

echo "\n✅ Frontend setup complete!"

echo "\n🎉 Setup Complete!"
echo "\nTo start the project:"
echo "  Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "  Frontend: cd frontend && npm run dev"
echo "\nAccess:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  Admin:    http://localhost:8000/admin"
