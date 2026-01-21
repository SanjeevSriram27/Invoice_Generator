# GST Invoice Generator

A professional, production-ready invoice generator for Indian businesses with GST compliance, PDF generation, and multi-channel distribution.

## Features

- Create GST-compliant invoices with automatic tax calculation
- Automatically calculates CGST, SGST, or IGST based on states
- Generate professional PDF invoices with company logos
- Send invoices via AWS SES email and WhatsApp
- Bulk invoice generation via CSV upload
- Business profile management with logo support
- Draft invoice support
- Dark mode UI
- Save business details locally for quick reuse

## Technology Stack

**Frontend:** Next.js 14, TypeScript, TailwindCSS, React Hot Toast
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
**Services:** AWS SES (Email), Twilio (WhatsApp), ReportLab (PDF)

## Prerequisites

- Node.js 18 or higher
- Python 3.12 or higher
- PostgreSQL 14 or higher
- Git
- AWS account (for SES email)
- Twilio account (optional, for WhatsApp)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/SanjeevSriram27/Invoice_Generator.git
cd Invoice_Generator
```

### 2. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE invoice_db;
CREATE USER invoice_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_db TO invoice_user;
```

### 3. Backend Setup

```bash
cd backend_fastapi
pip install -r requirements.txt
```

Create `.env` file in `backend_fastapi/` directory:

```env
# Database
DATABASE_URL=postgresql://invoice_user:your_password@localhost:5432/invoice_db

# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
SES_SENDER_EMAIL=your-verified-email@example.com
EMAIL_FROM_NAME=Invoice Generator

# Twilio WhatsApp (Optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Application
SECRET_KEY=your-secret-key-here
DEBUG=False
MEDIA_ROOT=./media
```

Run database migrations:

```bash
alembic upgrade head
cd ..
```

### 4. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 5. Running the Application

**Windows (Recommended):**

Double-click `START_SERVERS.bat` or run:

```bash
START_SERVERS.bat
```

This automatically starts both backend and frontend servers.

**Manual Method:**

Open two terminal windows:

*Terminal 1 - Backend:*
```bash
cd backend_fastapi
uvicorn app.main:app --reload --port 8000
```

*Terminal 2 - Frontend:*
```bash
cd frontend
npm run dev -- --port 3001
```

### 6. Access Application

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 7. Stopping Servers

**Windows:** Press `Ctrl+C` in the terminal running START_SERVERS.bat
**Manual:** Press `Ctrl+C` in each terminal window

## Usage Guide

### Creating Single Invoice

1. Open http://localhost:3001 in your browser
2. Choose invoice type:
   - **Topmate Invoice:** Platform-managed invoices with preset seller details
   - **Personal Invoice:** Custom business details with optional logo upload
3. Enter buyer/customer information
4. Add invoice items with HSN/SAC codes and quantities
5. System automatically calculates GST based on state codes
6. Generate invoice (or save as draft)
7. Download PDF, send via email, or share via WhatsApp

### Logo Support

- Upload business logo (PNG, JPG, JPEG, GIF)
- Automatically resized to fit invoice format (2cm × 1.8cm)
- Stored locally in `backend_fastapi/media/logos/`
- Supports base64 encoded images from frontend

### Bulk Invoice Generation

1. Navigate to "Bulk Upload" from home page
2. Download CSV template (`invoice_bulk_upload_template.csv`)
3. Fill in invoice details for multiple buyers
4. Upload CSV file
5. Configure options:
   - Invoice type (Topmate/Personal)
   - Save as draft
   - Auto-send email/WhatsApp
6. System processes all rows and reports success/failure for each

### Business Profile Management

- Save commonly used business details
- Reuse profiles across multiple invoices
- Manage through API at `/api/business-profiles/`

## GST Calculation Logic

- **Same State Transaction (Intrastate):** CGST (9%) + SGST (9%) = 18% total
- **Interstate Transaction:** IGST (18%)
- State determined by comparing pincode-derived state codes
- Automatic rate calculation based on configurable GST percentage

## API Documentation

Complete API documentation available at: http://localhost:8000/docs

Key endpoints:
- `POST /api/invoices/` - Create invoice
- `GET /api/invoices/{id}/` - Get invoice details
- `GET /api/invoices/{id}/download_pdf/` - Download PDF
- `POST /api/invoices/{id}/send_email/` - Send via email
- `POST /api/invoices/{id}/send_whatsapp/` - Send via WhatsApp
- `POST /api/invoices/bulk-upload/` - Bulk create from CSV
- `GET /api/business-profiles/` - List business profiles

## Project Structure

```
Invoice_Generator/
├── backend_fastapi/              # FastAPI backend
│   ├── app/
│   │   ├── api/                  # API endpoints
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   │   ├── email_service.py  # AWS SES integration
│   │   │   ├── whatsapp_service.py
│   │   │   ├── pdf_service.py    # ReportLab PDF generation
│   │   │   ├── invoice_service.py
│   │   │   └── bulk_upload_service.py
│   │   ├── core/                 # Validators and constants
│   │   └── main.py               # FastAPI app
│   ├── alembic/                  # Database migrations
│   ├── media/                    # Generated PDFs and logos
│   ├── requirements.txt
│   └── .env                      # Configuration (not in git)
├── frontend/                     # Next.js frontend
│   ├── app/                      # App router pages
│   ├── components/               # React components
│   ├── lib/                      # API client and utilities
│   └── package.json
├── START_SERVERS.bat             # Windows startup script
└── README.md
```

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| AWS_ACCESS_KEY_ID | AWS access key for SES | Yes |
| AWS_SECRET_ACCESS_KEY | AWS secret key for SES | Yes |
| AWS_REGION | AWS region (e.g., us-east-1) | Yes |
| SES_SENDER_EMAIL | Verified sender email in SES | Yes |
| EMAIL_FROM_NAME | Display name for emails | No |
| TWILIO_ACCOUNT_SID | Twilio account SID | No |
| TWILIO_AUTH_TOKEN | Twilio auth token | No |
| TWILIO_WHATSAPP_NUMBER | Twilio WhatsApp number | No |
| SECRET_KEY | Application secret key | Yes |
| DEBUG | Debug mode (True/False) | No |
| MEDIA_ROOT | Media files directory | No |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| NEXT_PUBLIC_API_URL | Backend API URL | No (defaults to http://localhost:8000/api) |

## Troubleshooting

### Port Already in Use

**Windows:**
```bash
netstat -ano | findstr :3001
taskkill /PID <PID> /F

netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -ti:3001 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   # Windows
   pg_ctl status

   # Mac/Linux
   systemctl status postgresql
   ```

2. Test database connection:
   ```bash
   psql -U invoice_user -d invoice_db
   ```

3. Reset database:
   ```bash
   cd backend_fastapi
   alembic downgrade base
   alembic upgrade head
   ```

### Email Not Sending

1. Verify AWS SES credentials in `.env`
2. Check sender email is verified in AWS SES console
3. Ensure AWS region is correct
4. Check backend logs for error messages

### PDF Generation Issues

PDF generation uses ReportLab (pure Python), no external dependencies needed.

If logos don't appear:
1. Check `media/logos/` directory exists
2. Verify image file format (PNG, JPG, JPEG, GIF)
3. Check file permissions on media directory

### Frontend Loading Slowly

1. Clear Next.js cache:
   ```bash
   cd frontend
   rm -rf .next
   npm run dev
   ```

2. Kill duplicate Node.js processes:
   ```bash
   # Windows
   taskkill /F /IM node.exe

   # Mac/Linux
   killall node
   ```

## Performance Features

- Async operations with FastAPI and aioboto3
- Database connection pooling with SQLAlchemy
- Optimized PDF generation with ReportLab
- Next.js 14 with optimized rendering
- Component lazy loading
- Dark mode with system preference detection
- Local storage for business details caching

## Security Features

- Environment-based configuration (secrets not in code)
- Input validation with Pydantic schemas
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for API security
- AWS SES for reliable, secure email delivery

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues or questions, please open an issue on GitHub:
https://github.com/SanjeevSriram27/Invoice_Generator/issues

## License

This project is open source and available for use and modification.

## Acknowledgments

- Built with FastAPI, Next.js, and PostgreSQL
- PDF generation powered by ReportLab
- Email service powered by AWS SES
- WhatsApp integration via Twilio
