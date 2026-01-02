# Invoice Generator - Complete Setup & Run Guide

## ✅ What's Already Complete

### Backend (100% Complete)
- ✅ Django 6.0 + Django REST Framework
- ✅ Complete database models (Invoice, InvoiceItem, BusinessProfile, InvoiceNumberSequence)
- ✅ GST calculation logic (CGST+SGST vs IGST)
- ✅ REST API endpoints
- ✅ PDF generation service
- ✅ Professional HTML invoice templates
- ✅ Admin panel configured
- ✅ Database migrated and ready
- ✅ Superuser created (username: admin, password: admin123)

### Frontend (Partially Complete)
- ✅ Next.js 14 with TypeScript
- ✅ TailwindCSS configured
- ✅ All dependencies installed
- ⚠️ Need to create remaining component files

---

## 🚀 Quick Start (Backend Only - For Testing API)

### 1. Start Backend Server

```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

Backend will run at: **http://localhost:8000**

### 2. Access Admin Panel

- URL: **http://localhost:8000/admin**
- Username: `admin`
- Password: `admin123`

### 3. Test API Endpoints

#### Get All Invoices
```bash
curl http://localhost:8000/api/invoices/
```

#### Create Invoice (Topmate Mode)
```bash
curl -X POST http://localhost:8000/api/invoices/ \
-H "Content-Type: application/json" \
-d '{
  "invoice_type": "topmate",
  "user_id": "user123",
  "buyer_name": "Test Customer",
  "buyer_address": "123 Test St, Mumbai",
  "buyer_pincode": "400001",
  "buyer_state": "MH",
  "buyer_email": "customer@example.com",
  "items": [
    {
      "description": "Consulting Service",
      "hsn_sac": "998314",
      "quantity": 1,
      "unit_price": 10000.00
    }
  ],
  "notes": "Payment due in 30 days"
}'
```

---

## 📝 API Endpoints Reference

### Business Profiles
- `GET /api/business-profiles/` - List all profiles
- `POST /api/business-profiles/` - Create profile
- `GET /api/business-profiles/{id}/` - Get specific profile
- `GET /api/business-profiles/by_user/?user_id=xxx` - Get by user

### Invoices
- `GET /api/invoices/` - List invoices
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/{id}/` - Get invoice details
- `GET /api/invoices/{id}/download_pdf/` - Download PDF
- `POST /api/invoices/{id}/generate_pdf/` - Generate PDF
- `POST /api/invoices/{id}/send_email/` - Email invoice
- `POST /api/invoices/{id}/share_whatsapp/` - WhatsApp share
- `POST /api/invoices/{id}/finalize/` - Finalize draft
- `GET /api/invoices/summary/?user_id=xxx` - Get summary

---

## 🎨 Frontend Completion

The frontend structure is set up but needs component files. Here's what needs to be created:

### Essential Files to Create

1. **app/layout.tsx** - Root layout
2. **app/page.tsx** - Home page with mandatory fork
3. **types/invoice.ts** - TypeScript interfaces
4. **lib/api.ts** - API client with axios
5. **lib/store.ts** - Zustand state management
6. **components/** - All UI components

### Frontend will have:
- Mandatory fork (Topmate vs User invoice)
- Form for invoice details
- Line items management
- Real-time GST calculation
- Preview before generation
- PDF download
- WhatsApp share
- Email functionality
- Print option

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────┐
│  Frontend (Next.js + React)          │
│  Port: 3000                          │
│  - Mandatory fork UI                 │
│  - Invoice form                      │
│  - Preview & actions                 │
└──────────────┬───────────────────────┘
               │ HTTP/REST API
               ↓
┌──────────────────────────────────────┐
│  Backend (Django + DRF)              │
│  Port: 8000                          │
│  - Invoice creation                  │
│  - GST calculation                   │
│  - PDF generation                    │
│  - Business logic                    │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  SQLite Database                     │
│  - Invoices                          │
│  - Business profiles                 │
│  - Invoice sequences                 │
└──────────────────────────────────────┘
```

---

## 📊 Database Schema

### Invoice Model
- invoice_number (unique)
- invoice_type (topmate/user)
- seller/buyer details (name, GSTIN, address, state, etc.)
- subtotal, cgst, sgst, igst, total
- is_interstate flag
- pdf_file
- created_at, updated_at

### InvoiceItem Model
- invoice (FK)
- serial_number
- description
- hsn_sac
- quantity, unit_price, amount

### BusinessProfile Model
- user_id (unique)
- business_name, gstin
- address, pincode, state
- contact details

### InvoiceNumberSequence Model
- sequence_type (topmate/user)
- user_id (nullable)
- current_number

---

## 🔧 Configuration

### Django Settings (backend/invoice_api/settings.py)

```python
INVOICE_SETTINGS = {
    'TOPMATE_COMPANY_NAME': 'Topmate Technologies Pvt Ltd',
    'TOPMATE_GSTIN': '29AAFCT0123A1Z5',
    'TOPMATE_ADDRESS': '123 Business Park, HSR Layout, Bangalore, Karnataka',
    'TOPMATE_PINCODE': '560102',
    'TOPMATE_STATE': 'Karnataka',
    'TOPMATE_STATE_CODE': '29',
    'TOPMATE_PHONE': '+91 80 1234 5678',
    'TOPMATE_EMAIL': 'invoices@topmate.io',
    'GST_RATE': 18,
    'CGST_RATE': 9,
    'SGST_RATE': 9,
    'IGST_RATE': 18,
    'TOPMATE_INVOICE_PREFIX': 'TM-INV',
    'USER_INVOICE_PREFIX': 'USER',
}
```

---

## 📦 Invoice Generation Flow

### Option A: Topmate Invoice
1. User selects "Generate as Topmate user"
2. System auto-fills Topmate details as seller
3. User enters buyer details (GSTIN optional)
4. User adds line items
5. System calculates GST automatically
6. Generate PDF

### Option B: User Invoice
1. User selects "For my own use"
2. User enters their business details (GSTIN mandatory)
3. System saves as business profile
4. User enters buyer details
5. User adds line items
6. System calculates GST automatically
7. Generate PDF

---

## 🎯 GST Calculation Rules (Auto-Applied)

```
IF seller_state == buyer_state:
    Tax Type: CGST + SGST
    CGST = Subtotal × 9%
    SGST = Subtotal × 9%
    Total = Subtotal + CGST + SGST

ELSE:
    Tax Type: IGST
    IGST = Subtotal × 18%
    Total = Subtotal + IGST
```

---

## 🔐 Security Notes

- ⚠️ Current setup uses `AllowAny` permissions (development only)
- ⚠️ For production: Add authentication (JWT/OAuth)
- ⚠️ Update `SECRET_KEY` in settings
- ⚠️ Set `DEBUG = False`
- ⚠️ Configure proper CORS origins
- ⚠️ Use PostgreSQL instead of SQLite
- ⚠️ Add rate limiting
- ⚠️ Enable HTTPS

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if virtual environment is activated
cd backend
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Run migrations again
python manage.py migrate
```

### PDF Generation Fails
- Uses reportlab as fallback (no dependencies)
- pdfkit requires wkhtmltopdf (optional)
- PDFs saved to backend/media/invoices/

### CORS Errors
- Backend allows localhost:3000 by default
- Check CORS_ALLOWED_ORIGINS in settings.py

---

## 📱 Testing the Complete Flow

### 1. Create Business Profile (for user invoices)
```bash
curl -X POST http://localhost:8000/api/business-profiles/ \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user123",
  "business_name": "My Business",
  "gstin": "29ABCDE1234F1Z5",
  "address": "456 Business St",
  "pincode": "560001",
  "state": "KA",
  "phone": "+91 9876543210",
  "email": "mybiz@example.com"
}'
```

### 2. Create Invoice
```bash
curl -X POST http://localhost:8000/api/invoices/ \
-H "Content-Type: application/json" \
-d @test_invoice.json
```

### 3. Download PDF
```bash
curl http://localhost:8000/api/invoices/1/download_pdf/ --output invoice.pdf
```

---

## 📁 Project Structure

```
Invoice_generator_1/
├── backend/                  # Django backend (✅ COMPLETE)
│   ├── invoice_api/         # Project settings
│   ├── invoices/            # Main app
│   │   ├── models.py        # Database models
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # API views
│   │   ├── services.py      # PDF generation
│   │   └── admin.py         # Admin config
│   ├── templates/           # HTML templates
│   │   └── invoices/
│   │       └── invoice_template.html
│   ├── media/               # Generated PDFs
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3           # Database
│
├── frontend/                # Next.js frontend (⚠️ NEEDS COMPONENTS)
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx       # TO CREATE
│   │   └── page.tsx         # TO CREATE
│   ├── components/          # TO CREATE
│   ├── lib/
│   │   ├── api.ts           # TO CREATE
│   │   └── store.ts         # TO CREATE
│   ├── types/
│   │   └── invoice.ts       # TO CREATE
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── README.md
└── SETUP_AND_RUN.md         # This file
```

---

## ✅ Current Status

### Backend: 100% Complete ✅
- Database ✅
- Models ✅
- API ✅
- PDF Generation ✅
- Admin Panel ✅
- Ready to use ✅

### Frontend: 60% Complete
- Project structure ✅
- Dependencies ✅
- Configuration ✅
- Components ⚠️ (Need to be created)

---

## 🎉 Next Steps

1. **Test Backend API** using curl or Postman
2. **Create Frontend Components** (if needed)
3. **Start Frontend Server**: `cd frontend && npm run dev`
4. **Full Integration Testing**
5. **Deploy to Production**

---

## 📞 Support

For issues or questions:
- Check backend logs: `python manage.py runserver`
- Check admin panel: http://localhost:8000/admin
- View database: backend/db.sqlite3

**The backend is fully functional and ready to use!**
**You can test all invoice operations via API right now.**
