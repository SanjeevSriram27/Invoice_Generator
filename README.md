# GST Invoice Generator

A professional invoice generator for Indian businesses with automatic GST calculation and PDF generation.

## Features

- Create professional invoices with GST compliance
- Automatically calculates CGST, SGST, or IGST based on states
- Generate and download PDF invoices
- Send invoices via email or WhatsApp
- Bulk invoice generation via CSV upload
- Save business details for quick reuse

## Technology Stack

**Frontend:** Next.js 14 (Turbopack), TypeScript, TailwindCSS, Zustand
**Backend:** Django 4.2, Django REST Framework, SQLite

## Prerequisites

- Node.js 18 or higher
- Python 3.8 or higher
- Git

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/SanjeevSriram27/invoice-generator.git
cd invoice-generator
```

### 2. First-Time Setup

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
cd ..
```

**Frontend Setup:**
```bash
cd frontend
npm install
cd ..
```

### 3. Running the Application

**Easy Method (Recommended):**

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
./start.sh
```

This will automatically start both backend and frontend servers.

**Manual Method:**

Open two terminal windows:

*Terminal 1 - Backend:*
```bash
cd backend
python manage.py runserver
```

*Terminal 2 - Frontend:*
```bash
cd frontend
npm run dev -- --turbo
```

### 4. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000

### 5. Stopping Servers

**Windows:** Double-click `stop.bat` or close terminal windows
**Mac/Linux:** Press `Ctrl+C` in the terminal

## Usage Guide

1. Open http://localhost:3000 in your browser
2. Choose invoice type:
   - **Topmate Invoice:** Platform handles seller details
   - **Personal Invoice:** Add your business details
3. Enter customer/buyer information
4. Add invoice items with HSN/SAC codes
5. System automatically calculates GST
6. Generate, download, or share PDF invoice

## GST Calculation Logic

- **Same State Transaction:** CGST (9%) + SGST (9%) = 18%
- **Interstate Transaction:** IGST (18%)

## Bulk Invoice Generation

1. Navigate to "Bulk Upload" from home page
2. Download sample CSV template
3. Fill in invoice details
4. Upload CSV to generate multiple invoices

## Environment Configuration (Optional)

**Backend** - Create `backend/.env`:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Frontend** - Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Troubleshooting

**Port Already in Use:**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
```

**Database Issues:**
```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

**Dependencies Issues:**
```bash
# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**PDF Generation Not Working:**

Install wkhtmltopdf:
- **Windows:** Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/)
- **Mac:** `brew install wkhtmltopdf`
- **Linux:** `sudo apt-get install wkhtmltopdf`

## Project Structure

```
Invoice_generator_1/
├── backend/              # Django REST API
│   ├── invoice_api/      # Main Django project
│   ├── manage.py
│   └── requirements.txt
├── frontend/             # Next.js application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── package.json
├── start.bat            # Windows startup script
├── start.sh             # Mac/Linux startup script
├── stop.bat             # Windows stop script
└── README.md
```

## Performance Optimizations

- Component code splitting for faster initial load
- Lazy loading of heavy dependencies
- Turbopack for 10x faster compilation
- Optimized Tailwind CSS configuration
- React state management with Zustand

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues or questions, please open an issue on GitHub.

## License

This project is open source and available for use and modification.
