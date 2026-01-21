# Invoice Generator - FastAPI Backend

A production-ready FastAPI backend for generating GST-compliant invoices with PDF generation, multi-channel distribution (Email/WhatsApp), and bulk CSV upload support.

## Features

### Core Functionality
- **Dual Invoice Types**: Support for both Topmate standardized invoices and custom user invoices
- **GST-Compliant Calculations**: Automatic GST extraction from inclusive prices with state-based tax calculation (CGST+SGST vs IGST)
- **Atomic Invoice Numbering**: Guaranteed unique invoice numbers using PostgreSQL row-level locking
- **PDF Generation**: High-quality PDF invoices with company logos and detailed breakdowns
- **Multi-Channel Distribution**: Send invoices via Email (SMTP), WhatsApp (Twilio), or SuprSend platform
- **Bulk Upload**: Process CSV files with partial success handling (savepoint transactions)
- **Business Profiles**: Manage multiple business profiles with GSTIN, logos, and contact details
- **Draft Workflow**: Create draft invoices for review before finalization

### Technical Highlights
- **Async/Await**: Fully asynchronous for high performance under load
- **Type-Safe**: Pydantic validation for all requests and responses
- **Auto-Documentation**: Interactive API docs at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **PostgreSQL**: Production-grade database with SQLAlchemy 2.0 async ORM
- **Decimal Precision**: All financial calculations use Python's Decimal class (never float)
- **Indian Compliance**: Phone validation (E.164), GSTIN validation (15-char format), pincode validation

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.115.0 |
| ASGI Server | Uvicorn | 0.30.0 |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy (async) | 2.0.32 |
| Validation | Pydantic v2 | 2.9.0 |
| Migrations | Alembic | 1.13.2 |
| PDF Generation | ReportLab | 4.0.7 |
| Email | aiosmtplib | 3.0.2 |
| HTTP Client | httpx | 0.27.0 |
| WhatsApp | Twilio | 9.0.4 |

## Prerequisites

- Python 3.12+
- PostgreSQL 15+ (running and accessible)
- Gmail account (for SMTP email sending) OR SuprSend account
- Twilio account (optional, for WhatsApp)

## Installation

### 1. Clone the Repository

```bash
cd backend_fastapi
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE invoice_generator;
CREATE USER invoice_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_generator TO invoice_user;

# Exit psql
\q
```

### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see Environment Variables section below).

### 6. Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic upgrade head
```

This will create all necessary tables in your PostgreSQL database.

## Environment Variables

Create a `.env` file in the `backend_fastapi` directory with the following variables:

### Required Variables

```env
# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=invoice_generator
POSTGRES_USER=invoice_user
POSTGRES_PASSWORD=your_secure_password

# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Topmate Company Details (for Topmate invoices)
TOPMATE_COMPANY_NAME=Topmate Technologies Pvt Ltd
TOPMATE_GSTIN=29AAFCT0123A1Z5
TOPMATE_ADDRESS=123 Business Park, Bangalore, Karnataka
TOPMATE_PINCODE=560001
TOPMATE_STATE=KA
TOPMATE_STATE_CODE=29
TOPMATE_PHONE=+918012345678
TOPMATE_EMAIL=invoices@topmate.io
TOPMATE_WEBSITE=https://topmate.io
TOPMATE_INVOICE_PREFIX=TM-INV
```

### Optional Variables

```env
# Twilio (for WhatsApp)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# SuprSend (alternative notification platform)
SUPRSEND_WORKSPACE_KEY=your_workspace_key
SUPRSEND_WORKSPACE_SECRET=your_workspace_secret
SUPRSEND_WORKSPACE_URL=https://hub.suprsend.com
SUPRSEND_INVOICE_TEMPLATE=invoice-template-id

# GST Settings (defaults shown)
GST_RATE=18.0
CGST_RATE=9.0
SGST_RATE=9.0
IGST_RATE=18.0

# CORS Origins (frontend URLs)
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Media Storage
MEDIA_ROOT=./media
MEDIA_URL=/media/

# Debug Mode
DEBUG=False
```

### Getting Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → 2-Step Verification → App passwords
4. Generate a new app password for "Mail"
5. Use this 16-character password as `EMAIL_HOST_PASSWORD`

## Running the Server

### Development Mode (with auto-reload)

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at:
- API Base URL: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Documentation

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Try out API endpoints directly from the browser
  - See request/response schemas
  - Test authentication and file uploads

- **ReDoc**: http://localhost:8000/redoc
  - Clean, readable API documentation
  - Better for understanding the full API structure

### Key Endpoints

#### Health Check
```
GET /health
```
Returns server status and database connectivity.

#### Business Profiles
```
GET    /api/business-profiles/              List all business profiles
POST   /api/business-profiles/              Create new business profile
GET    /api/business-profiles/{id}/         Get business profile by ID
PUT    /api/business-profiles/{id}/         Update business profile
DELETE /api/business-profiles/{id}/         Delete business profile
GET    /api/business-profiles/by_user/      Get profiles by user_id
```

#### Invoices
```
GET    /api/invoices/                       List invoices (with filters)
POST   /api/invoices/                       Create new invoice
GET    /api/invoices/summary/               Get invoice statistics
GET    /api/invoices/{id}/                  Get invoice by ID
PUT    /api/invoices/{id}/                  Update invoice (draft only)
DELETE /api/invoices/{id}/                  Delete invoice
GET    /api/invoices/{id}/download_pdf/     Download invoice PDF
POST   /api/invoices/{id}/generate_pdf/     Regenerate invoice PDF
POST   /api/invoices/{id}/finalize/         Finalize draft invoice
POST   /api/invoices/{id}/send_email/       Send invoice via Email (SMTP)
POST   /api/invoices/{id}/share_whatsapp/   Send invoice via WhatsApp (Twilio)
POST   /api/invoices/{id}/send_email_suprsend/     Send via SuprSend Email
POST   /api/invoices/{id}/send_whatsapp_suprsend/  Send via SuprSend WhatsApp
POST   /api/invoices/bulk-upload/           Bulk upload invoices from CSV
```

### Example Requests

#### Create a Topmate Invoice

```bash
curl -X POST "http://localhost:8000/api/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_type": "topmate",
    "user_id": "user_123",
    "invoice_date": "2026-01-14",
    "buyer_name": "John Doe",
    "buyer_address": "456 Customer Street, Mumbai",
    "buyer_pincode": "400001",
    "buyer_state": "MH",
    "buyer_phone": "+919876543210",
    "buyer_email": "john@example.com",
    "buyer_gstin": "27AAFCT0123A1Z5",
    "items": [
      {
        "description": "Consulting Service",
        "hsn_sac": "998314",
        "quantity": 1,
        "unit_price": "11800.00"
      }
    ],
    "gst_rate": 18.0,
    "is_draft": false,
    "notes": "Payment due within 30 days",
    "payment_terms": "Net 30"
  }'
```

#### Create a User Invoice

```bash
curl -X POST "http://localhost:8000/api/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_type": "user",
    "user_id": "user_456",
    "invoice_date": "2026-01-14",
    "seller_name": "My Business Ltd",
    "seller_gstin": "29AAFCT9876B1Z5",
    "seller_address": "789 Business Road, Bangalore",
    "seller_pincode": "560001",
    "seller_state": "KA",
    "seller_phone": "+918123456789",
    "seller_email": "billing@mybusiness.com",
    "buyer_name": "Customer Corp",
    "buyer_address": "321 Client Avenue, Delhi",
    "buyer_pincode": "110001",
    "buyer_state": "DL",
    "buyer_email": "accounts@customer.com",
    "items": [
      {
        "description": "Product A",
        "hsn_sac": "998315",
        "quantity": 3,
        "unit_price": "5900.00"
      }
    ],
    "gst_rate": 18.0,
    "is_draft": false
  }'
```

#### Download Invoice PDF

```bash
curl -o invoice.pdf "http://localhost:8000/api/invoices/1/download_pdf/"
```

#### Get Invoice Summary

```bash
curl "http://localhost:8000/api/invoices/summary/?user_id=user_123"
```

Response:
```json
{
  "total_invoices": 10,
  "draft_invoices": 2,
  "finalized_invoices": 8,
  "total_amount": "118000.00",
  "topmate_invoices": 5,
  "user_invoices": 5
}
```

## Business Logic

### GST Price Extraction

The frontend sends GST-inclusive prices (the final amount customer pays). The backend automatically extracts the base price:

**Formula**: `base_price = price_with_gst / (1 + gst_rate)`

**Example**:
- Frontend sends: ₹11,800 (total amount including GST)
- GST rate: 18%
- Backend calculates: ₹11,800 ÷ 1.18 = ₹10,000 (base price)
- GST amount: ₹10,000 × 0.18 = ₹1,800
- Verification: ₹10,000 + ₹1,800 = ₹11,800 ✓

### State-Based Tax Calculation

Indian GST rules require different tax applications based on buyer-seller location:

**Intrastate (Same State)**:
- CGST (Central GST): 9% of base amount
- SGST (State GST): 9% of base amount
- Total GST: 18%

**Interstate (Different States)**:
- IGST (Integrated GST): 18% of base amount
- CGST: 0%
- SGST: 0%

Example:
```
Seller: Karnataka (KA), Buyer: Karnataka (KA)
Subtotal: ₹10,000
CGST: ₹900 (9%)
SGST: ₹900 (9%)
Total: ₹11,800

Seller: Karnataka (KA), Buyer: Maharashtra (MH)
Subtotal: ₹10,000
IGST: ₹1,800 (18%)
Total: ₹11,800
```

### Atomic Invoice Numbering

To prevent duplicate invoice numbers under concurrent requests, the system uses PostgreSQL row-level locking:

```python
async with db.begin_nested():  # Create savepoint
    query = select(InvoiceNumberSequence).where(...).with_for_update()  # Lock row
    sequence = await db.execute(query)
    sequence.current_number += 1
    await db.flush()
```

**Invoice Number Formats**:
- Topmate: `TM-INV-000001`, `TM-INV-000002`, etc.
- User: `INV-{USER_HASH}-0001`, `INV-{USER_HASH}-0002`, etc.

### Bulk Upload Partial Success

The bulk CSV upload uses savepoint transactions to ensure partial success:

```python
for row in csv_rows:
    async with db.begin_nested():  # Savepoint for this row
        try:
            create_invoice(row)
            # Savepoint committed on success
        except Exception:
            # Savepoint rolled back
            # Other rows unaffected
```

If row 5 fails, rows 1-4 and 6-10 still succeed.

## CSV Format for Bulk Upload

The bulk upload endpoint accepts CSV files with the following headers:

```csv
receiver_name,receiver_address,pincode,phone,email,gstin,product_descriptions,hsn_sac_codes,quantities,total_values,notes,payment_terms
John Doe,"123 Street, Mumbai",400001,9876543210,john@example.com,27AAFCT0123A1Z5,Consulting Service,998314,1,11800.00,Payment due in 30 days,Net 30
Jane Smith,"456 Avenue, Delhi",110001,9876543211,jane@example.com,,Product A|Product B,998315|998316,2|1,11800.00|5900.00,,
```

**Notes**:
- Multiple items separated by pipe (`|`) character
- GSTIN is optional
- Phone will be auto-formatted to E.164 format
- Total values should be GST-inclusive

**Upload Example**:

```bash
curl -X POST "http://localhost:8000/api/invoices/bulk-upload/" \
  -F "csv_file=@invoices.csv" \
  -F "invoice_type=topmate" \
  -F "user_id=user_123" \
  -F "gst_rate=18.0" \
  -F "create_as_draft=false" \
  -F "send_email=false" \
  -F "send_whatsapp=false"
```

## Project Structure

```
backend_fastapi/
├── app/
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Pydantic Settings configuration
│   ├── database.py                # SQLAlchemy async engine
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── base.py               # Base model with timestamps
│   │   ├── business_profile.py   # BusinessProfile model
│   │   ├── invoice.py            # Invoice + InvoiceItem models
│   │   └── invoice_sequence.py   # Atomic numbering model
│   │
│   ├── schemas/                   # Pydantic validation schemas
│   │   ├── business_profile.py   # Business profile schemas
│   │   ├── invoice.py            # Invoice request/response schemas
│   │   ├── invoice_item.py       # Invoice item schemas
│   │   ├── bulk_upload.py        # Bulk upload schemas
│   │   └── common.py             # Pagination, base schemas
│   │
│   ├── api/                       # Route handlers
│   │   ├── router.py             # Main router aggregator
│   │   ├── business_profiles.py  # 6 business profile endpoints
│   │   └── invoices.py           # 13 invoice endpoints
│   │
│   ├── services/                  # Business logic layer
│   │   ├── pdf_service.py        # PDF generation (ReportLab)
│   │   ├── invoice_service.py    # Invoice CRUD + numbering
│   │   ├── bulk_upload_service.py # CSV processing
│   │   ├── email_service.py      # SMTP email (aiosmtplib)
│   │   ├── whatsapp_service.py   # Twilio WhatsApp
│   │   └── suprsend_service.py   # SuprSend notifications
│   │
│   └── core/                      # Core utilities
│       ├── validators.py         # Phone, GSTIN, pincode validation
│       ├── constants.py          # Indian states, state codes
│       └── exceptions.py         # Custom exception classes
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── media/                         # File storage
│   ├── logos/                    # Business logos
│   └── invoices/                 # Generated PDFs
│
├── .env                          # Environment variables (create this)
├── .env.example                  # Example environment file
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
└── README.md                     # This file
```

## Testing

### Manual Testing

Start the server and use the interactive docs at http://localhost:8000/docs to test endpoints.

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List invoices
curl "http://localhost:8000/api/invoices/"

# Get invoice by ID
curl "http://localhost:8000/api/invoices/1/"

# Download PDF
curl -o invoice.pdf "http://localhost:8000/api/invoices/1/download_pdf/"
```

### Testing with Python

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8000/health")
        print(response.json())

        # Create invoice
        invoice_data = {
            "invoice_type": "topmate",
            "user_id": "test_user",
            "invoice_date": "2026-01-14",
            "buyer_name": "Test Buyer",
            "buyer_address": "Test Address",
            "buyer_pincode": "560001",
            "buyer_state": "KA",
            "items": [{
                "description": "Test Service",
                "hsn_sac": "998314",
                "quantity": 1,
                "unit_price": "11800.00"
            }],
            "gst_rate": 18.0
        }

        response = await client.post(
            "http://localhost:8000/api/invoices/",
            json=invoice_data
        )
        print(response.json())

asyncio.run(test_api())
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
FATAL: password authentication failed for user "invoice_user"
```

**Solution**: Check your `.env` file has correct `POSTGRES_PASSWORD`.

#### 2. Port Already in Use

```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution**: Kill existing process or use different port:
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -9 python

# Or use different port
python -m uvicorn app.main:app --port 8001
```

#### 3. Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution**: Make sure you're in the `backend_fastapi` directory and virtual environment is activated.

#### 4. Alembic Migration Errors

```
Target database is not up to date
```

**Solution**: Run migrations:
```bash
alembic upgrade head
```

#### 5. PDF Generation Fails

```
FileNotFoundError: [Errno 2] No such file or directory: './media/invoices/'
```

**Solution**: Create media directories:
```bash
mkdir -p media/invoices media/logos
```

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

This will:
- Show detailed error messages
- Enable SQL query logging
- Show stack traces in responses

## Performance Considerations

### Database Connection Pooling

SQLAlchemy uses connection pooling by default. Adjust pool size for production:

```python
# app/database.py
engine = create_async_engine(
    settings.database_url,
    pool_size=20,        # Max connections
    max_overflow=10,     # Extra connections during peak
    pool_pre_ping=True   # Check connections before use
)
```

### Concurrent Request Handling

Use multiple Uvicorn workers for production:

```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### PDF Generation Performance

PDF generation is CPU-intensive and runs in a ThreadPoolExecutor to avoid blocking the async event loop. The default pool size is 4 workers. Adjust in `app/services/pdf_service.py` if needed.

## Migration from Django

If you're migrating from the Django backend:

1. **Database**: The SQLAlchemy models preserve Django table names (`invoices_invoice`, `invoices_invoiceitem`, etc.) for compatibility
2. **API Contract**: All endpoints maintain the same request/response format as Django REST Framework
3. **Business Logic**: GST calculations, invoice numbering, and PDF generation are identical
4. **Frontend**: No frontend changes required - same API endpoints and response structures

## Contributing

When contributing to this project:

1. Follow PEP 8 style guidelines
2. Use type hints for all function parameters and return values
3. Add docstrings to all public functions and classes
4. Update this README if adding new features
5. Test all endpoints before submitting pull requests

## License

[Your License Here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Changelog

### Version 2.0.0 (2026-01-14)
- Complete conversion from Django to FastAPI
- Migrated from SQLite to PostgreSQL
- Implemented async/await throughout
- Added interactive API documentation
- Improved performance with async database operations
- Enhanced error handling and validation

---

Built with FastAPI, PostgreSQL, and ❤️
