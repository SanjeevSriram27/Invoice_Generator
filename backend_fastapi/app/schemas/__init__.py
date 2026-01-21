"""
Pydantic schemas for request/response validation
"""
from app.schemas.common import (
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
    TimestampMixin,
)
from app.schemas.business_profile import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.schemas.invoice_item import (
    InvoiceItemCreate,
    InvoiceItemUpdate,
    InvoiceItemResponse,
)
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceSummaryResponse,
    SendEmailRequest,
    SendWhatsAppRequest,
)
from app.schemas.bulk_upload import (
    BulkInvoiceCSVRow,
    BulkUploadSuccessItem,
    BulkUploadFailureItem,
    BulkUploadResult,
    BulkUploadSettings,
)

__all__ = [
    # Common
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "TimestampMixin",
    # Business Profile
    "BusinessProfileCreate",
    "BusinessProfileUpdate",
    "BusinessProfileResponse",
    # Invoice Item
    "InvoiceItemCreate",
    "InvoiceItemUpdate",
    "InvoiceItemResponse",
    # Invoice
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse",
    "InvoiceListResponse",
    "InvoiceSummaryResponse",
    "SendEmailRequest",
    "SendWhatsAppRequest",
    # Bulk Upload
    "BulkInvoiceCSVRow",
    "BulkUploadSuccessItem",
    "BulkUploadFailureItem",
    "BulkUploadResult",
    "BulkUploadSettings",
]
