"""
Invoice API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os

from app.database import get_db
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceSummaryResponse,
    SendEmailRequest,
    SendWhatsAppRequest,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.invoice_service import InvoiceService
from app.services.pdf_service import PDFService
from app.core.exceptions import (
    InvoiceNotFoundException,
    PDFGenerationException,
)


router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_invoice_service(db: AsyncSession = Depends(get_db)) -> InvoiceService:
    """Dependency to get invoice service"""
    return InvoiceService(db)


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.get("/", response_model=PaginatedResponse[InvoiceListResponse])
async def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    invoice_type: Optional[str] = Query(None, description="Filter by invoice type (topmate/user)"),
    is_draft: Optional[bool] = Query(None, description="Filter by draft status"),
    request: Request = None,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    List invoices with pagination and filters

    Returns paginated results in Django REST Framework format:
    - **count**: Total number of invoices
    - **next**: URL to next page (null if last page)
    - **previous**: URL to previous page (null if first page)
    - **results**: List of invoices for current page

    Filters:
    - **user_id**: Filter by user ID
    - **invoice_type**: Filter by type (topmate/user)
    - **is_draft**: Filter by draft status
    """
    # Calculate offset
    offset = (page - 1) * page_size

    # Build filter criteria
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if invoice_type:
        filters['invoice_type'] = invoice_type
    if is_draft is not None:
        filters['is_draft'] = is_draft

    # Get invoices and total count
    invoices = await service.list_invoices(
        skip=offset,
        limit=page_size,
        **filters
    )

    total = await service.count_invoices(**filters)

    # Build pagination URLs
    base_url = str(request.url).split('?')[0] if request else ""
    query_params = dict(request.query_params) if request else {}

    next_url = None
    if (page * page_size) < total:
        query_params['page'] = page + 1
        next_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in query_params.items())}"

    prev_url = None
    if page > 1:
        query_params['page'] = page - 1
        prev_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in query_params.items())}"

    return PaginatedResponse(
        count=total,
        next=next_url,
        previous=prev_url,
        results=invoices
    )


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: Request,
    invoice_data: InvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Create a new invoice

    The invoice will be created with:
    - Unique invoice number (auto-generated atomically)
    - GST-inclusive prices converted to base prices
    - Tax calculations (CGST+SGST or IGST based on states)
    - Optional PDF generation (if not draft)

    Request body should include:
    - **invoice_type**: 'topmate' or 'user'
    - **user_id**: User creating the invoice
    - **invoice_date**: Invoice date
    - **buyer details**: name, address, pincode, state, etc.
    - **seller details**: Required for 'user' invoices, auto-filled for 'topmate'
    - **items**: List of invoice items (at least 1 required)
    - **gst_rate**: GST rate percentage (default 18%)
    - **is_draft**: Whether to create as draft (default false)
    """
    invoice = await service.create_invoice(invoice_data.model_dump())

    return invoice


@router.get("/summary/", response_model=InvoiceSummaryResponse)
async def get_summary(
    user_id: str = Query(..., description="User ID to get summary for"),
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Get invoice summary statistics for a user

    Returns:
    - Total number of invoices
    - Number of draft invoices
    - Number of finalized invoices
    - Total amount across all invoices
    - Number of Topmate invoices
    - Number of user invoices
    """
    summary = await service.get_summary(user_id)

    return summary


@router.get("/{invoice_id}/", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Retrieve invoice by ID

    Returns full invoice details including all items.
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    return invoice


@router.put("/{invoice_id}/", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Update an existing invoice

    Note: Only draft invoices can be updated. Finalized invoices are immutable.

    All fields in the request body are optional. Only provided fields will be updated.
    """
    invoice = await service.update_invoice(
        invoice_id,
        invoice_data.model_dump(exclude_unset=True)
    )

    return invoice


@router.delete("/{invoice_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Delete an invoice

    This will also delete all associated invoice items (cascade delete).
    """
    await service.delete_invoice(invoice_id)

    return None


# ============================================================================
# PDF Endpoints
# ============================================================================

@router.get("/{invoice_id}/download_pdf/")
async def download_pdf(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Download invoice PDF

    If PDF doesn't exist, it will be generated automatically.

    Returns PDF file with appropriate headers for download.
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Generate PDF if not exists
    if not invoice.pdf_file:
        pdf_service = PDFService()
        await pdf_service.generate_pdf(invoice)
        await db.commit()
        await db.refresh(invoice)

    # Build PDF path
    if invoice.pdf_file:
        # Extract filename from path
        filename = invoice.pdf_file.split('/')[-1]
        pdf_path = os.path.join("media", "invoices", filename)
    else:
        raise PDFGenerationException("Failed to generate PDF")

    # Check if file exists
    if not os.path.exists(pdf_path):
        raise PDFGenerationException(f"PDF file not found: {pdf_path}")

    # Return file response
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{invoice.invoice_number}.pdf"
    )


@router.post("/{invoice_id}/generate_pdf/", response_model=InvoiceResponse)
async def generate_pdf(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate invoice PDF

    Forces regeneration of the PDF file even if it already exists.

    Returns updated invoice with new PDF path.
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Generate PDF
    pdf_service = PDFService()
    await pdf_service.generate_pdf(invoice)

    await db.commit()
    await db.refresh(invoice)

    return invoice


# ============================================================================
# Action Endpoints
# ============================================================================

@router.post("/{invoice_id}/finalize/", response_model=InvoiceResponse)
async def finalize_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Finalize a draft invoice

    This action:
    1. Sets is_draft = False (makes invoice immutable)
    2. Generates PDF if not already generated

    Finalized invoices cannot be modified or deleted.
    """
    invoice = await service.finalize_invoice(invoice_id)

    return invoice


@router.post("/{invoice_id}/send_email/", response_model=SuccessResponse)
async def send_email(
    invoice_id: int,
    email_data: Optional[SendEmailRequest] = None,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Send invoice via email (SMTP)

    Uses configured SMTP server to send invoice PDF to buyer.

    Optional overrides:
    - **recipient_email**: Override buyer email
    - **subject**: Custom email subject
    - **message**: Custom email message
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Check buyer email
    recipient = email_data.recipient_email if email_data else None
    if not recipient and not invoice.buyer_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buyer email not provided"
        )

    # Import email service (avoid circular import)
    from app.services.email_service import EmailService
    email_service = EmailService()

    # Send email
    await email_service.send_invoice_email(
        invoice,
        recipient_email=recipient,
        subject=email_data.subject if email_data else None,
        message=email_data.message if email_data else None
    )

    return SuccessResponse(message="Email sent successfully")


@router.post("/{invoice_id}/share_whatsapp/", response_model=SuccessResponse)
async def share_whatsapp(
    invoice_id: int,
    whatsapp_data: Optional[SendWhatsAppRequest] = None,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Send invoice via WhatsApp (Twilio)

    Uses Twilio WhatsApp Business API to send invoice.

    Optional overrides:
    - **recipient_phone**: Override buyer phone
    - **message**: Custom WhatsApp message
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Import WhatsApp service
    from app.services.whatsapp_service import WhatsAppService
    whatsapp_service = WhatsAppService()

    # Send WhatsApp
    result = await whatsapp_service.send_invoice_whatsapp(
        invoice,
        recipient_phone=whatsapp_data.recipient_phone if whatsapp_data else None,
        message=whatsapp_data.message if whatsapp_data else None
    )

    return SuccessResponse(
        message="WhatsApp sent successfully",
        data=result
    )


@router.post("/{invoice_id}/send_email_suprsend/", response_model=SuccessResponse)
async def send_email_suprsend(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Send invoice via SuprSend email

    Uses SuprSend notification platform to send email.
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Import SuprSend service
    from app.services.suprsend_service import SuprSendService
    suprsend_service = SuprSendService()

    # Send email via SuprSend
    await suprsend_service.send_invoice_email(invoice)

    return SuccessResponse(message="Email sent via SuprSend")


@router.post("/{invoice_id}/send_whatsapp_suprsend/", response_model=SuccessResponse)
async def send_whatsapp_suprsend(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Send invoice via SuprSend WhatsApp

    Uses SuprSend notification platform to send WhatsApp message.
    """
    invoice = await service.get_invoice(invoice_id)

    if not invoice:
        raise InvoiceNotFoundException(invoice_id)

    # Import SuprSend service
    from app.services.suprsend_service import SuprSendService
    suprsend_service = SuprSendService()

    # Send WhatsApp via SuprSend
    await suprsend_service.send_invoice_whatsapp(invoice)

    return SuccessResponse(message="WhatsApp sent via SuprSend")


# ============================================================================
# Bulk Upload Endpoint
# ============================================================================

@router.post("/bulk-upload/")
async def bulk_upload(
    csv_file: UploadFile = File(..., description="CSV file with invoice data"),
    invoice_type: str = Query(..., description="Invoice type: topmate or user"),
    user_id: str = Query(..., description="User ID creating invoices"),
    create_as_draft: bool = Query(False, description="Create invoices as drafts"),
    send_email: bool = Query(False, description="Send email after creation"),
    send_whatsapp: bool = Query(False, description="Send WhatsApp after creation"),
    gst_rate: float = Query(18.0, description="GST rate percentage"),
    # Seller details (for user invoices)
    seller_name: Optional[str] = Query(None),
    seller_gstin: Optional[str] = Query(None),
    seller_address: Optional[str] = Query(None),
    seller_pincode: Optional[str] = Query(None),
    seller_state: Optional[str] = Query(None),
    seller_phone: Optional[str] = Query(None),
    seller_email: Optional[str] = Query(None),
    seller_website: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk upload invoices from CSV file

    CSV format should have headers:
    - receiver_name
    - receiver_address
    - pincode
    - phone
    - email
    - gstin
    - product_descriptions (pipe-separated: "Product 1|Product 2")
    - hsn_sac_codes (pipe-separated: "998314|998315")
    - quantities (pipe-separated: "1|2")
    - total_values (pipe-separated: "11800.00|5900.00")
    - notes (optional)
    - payment_terms (optional)

    Returns:
    - **successful**: Number of successful invoice creations
    - **failed**: Number of failed invoice creations
    - **successes**: List of successful invoices
    - **failures**: List of failed invoices with error messages

    Note: Implements partial success - some rows may succeed while others fail.
    """
    # Import bulk upload service
    from app.services.bulk_upload_service import BulkUploadService

    # Create bulk upload service
    bulk_service = BulkUploadService(
        db=db,
        csv_file=csv_file,
        user_id=user_id,
        invoice_type=invoice_type,
        create_as_draft=create_as_draft,
        send_email=send_email,
        send_whatsapp=send_whatsapp,
        gst_rate=gst_rate,
        seller_details={
            'name': seller_name,
            'gstin': seller_gstin,
            'address': seller_address,
            'pincode': seller_pincode,
            'state': seller_state,
            'phone': seller_phone,
            'email': seller_email,
            'website': seller_website,
        }
    )

    # Process CSV
    result = await bulk_service.process()

    return result
