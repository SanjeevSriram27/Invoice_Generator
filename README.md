# GST Invoice Generator

A simple invoice generator for Indian businesses with automatic GST calculation and PDF generation.

## What Does It Do?

- Create professional invoices with GST compliance
- Automatically calculates CGST, SGST, or IGST based on states
- Generate and download PDF invoices
- Send invoices via email or WhatsApp
- Save your business details for quick reuse

## Technology Used

**Frontend:** Next.js 14, TypeScript, TailwindCSS
**Backend:** Django 4.2, Django REST Framework, SQLite

## Setup Instructions

### What You Need

- Node.js 18 or higher
- Python 3.8 or higher

### Installation Steps

**1. Clone this repository**

```bash
git clone https://github.com/SanjeevSriram27/invoice-generator.git
cd invoice-generator
```

**2. Setup Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # On Windows
source venv/bin/activate       # On Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at: http://localhost:8000

**3. Setup Frontend** (open new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

## How to Use

1. Open http://localhost:3000 in your browser
2. Choose invoice type (Platform or Personal)
3. Enter your business details (saved automatically)
4. Add customer details
5. Add items with prices and HSN/SAC codes
6. System calculates GST automatically
7. Generate PDF and download or share

## GST Calculation

- **Same State:** CGST (9%) + SGST (9%) = 18%
- **Different States:** IGST (18%)

## Environment Setup

**Backend** - Create `backend/.env` file:

```
DEBUG=True
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

**Frontend** - Create `frontend/.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Common Problems

**Backend won't start:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Frontend can't connect:**
- Check backend is running on port 8000
- Verify `.env.local` file exists with correct API URL

**PDF not generating:**
- Install wkhtmltopdf:
  - Windows: Download from wkhtmltopdf.org
  - Mac: `brew install wkhtmltopdf`
  - Linux: `sudo apt-get install wkhtmltopdf`

## Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first.

## Questions?

Open an issue on GitHub if you need help.
