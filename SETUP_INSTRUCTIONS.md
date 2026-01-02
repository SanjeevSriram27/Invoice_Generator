# GST Invoice Generator - Setup Instructions

Quick setup guide for running the Invoice Generator application.

## 📋 Prerequisites

Before starting, make sure you have installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

## 🚀 Quick Start (First Time Setup)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd Invoice_generator_1
```

### Step 2: Setup Backend (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
cd ..
```

### Step 3: Setup Frontend (Next.js)

```bash
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment (Optional)

Create `.env` files if needed:

**Backend (`backend/.env`):**
```
DEBUG=True
SECRET_KEY=your-secret-key
```

**Frontend (`frontend/.env.local`):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## ▶️ Running the Application

### Option 1: Using Startup Scripts (Easiest)

**Windows:**
```bash
# Double-click start.bat
# OR run in terminal:
start.bat
```

**Mac/Linux:**
```bash
./start.sh
```

**To Stop:**
```bash
# Windows: Double-click stop.bat or close the terminal windows
stop.bat

# Mac/Linux: Press Ctrl+C in the terminal
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- --turbo
```

## 🌐 Access the Application

Once both servers are running:

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000
- **Admin Panel:** http://127.0.0.1:8000/admin

## 📝 Features

1. **Topmate Invoice** - Generate invoices with Topmate as seller
2. **Personal Invoice** - Generate invoices for your business
3. **Bulk Upload** - Upload CSV to generate multiple invoices
4. **PDF Generation** - Download professional PDF invoices
5. **Email/WhatsApp** - Share invoices directly

## 🛠️ Troubleshooting

### Port Already in Use

If you see "Port already in use" errors:

**Windows:**
```bash
# Kill processes on port 3000 (Frontend)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Kill processes on port 8000 (Backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Kill processes on port 3000
lsof -ti:3000 | xargs kill -9

# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9
```

### Python Dependencies Issues

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Node Dependencies Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

## 📦 Project Structure

```
Invoice_generator_1/
├── backend/              # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   └── invoice_api/
├── frontend/             # Next.js Frontend
│   ├── package.json
│   ├── app/
│   └── components/
├── start.bat            # Windows startup script
├── start.sh             # Mac/Linux startup script
├── stop.bat             # Windows stop script
└── README.md
```

## 🔧 Development Tips

1. **Hot Reload:** Changes to frontend code auto-reload with Turbopack
2. **Backend Changes:** Django auto-reloads when you modify Python files
3. **Debug Mode:** Both servers run in debug mode by default

## 📞 Support

For issues or questions:
- Check the main README.md
- Review error messages in terminal
- Ensure all prerequisites are installed

---

**Happy Invoice Generating! 🎉**
