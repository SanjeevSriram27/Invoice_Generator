"""
Bulk upload schemas for CSV processing
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal


class BulkInvoiceCSVRow(BaseModel):
    """
    Schema for a single row in bulk invoice CSV

    CSV Headers (from Django):
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
    """
    receiver_name: str = Field(..., min_length=1, description="Buyer name")
    receiver_address: str = Field(..., min_length=1, description="Buyer address")
    pincode: str = Field(..., min_length=6, max_length=6, description="Buyer pincode")
    phone: Optional[str] = Field(None, description="Buyer phone")
    email: Optional[str] = Field(None, description="Buyer email")
    gstin: Optional[str] = Field(None, description="Buyer GSTIN")

    # Pipe-separated item fields
    product_descriptions: str = Field(..., min_length=1, description="Pipe-separated descriptions")
    hsn_sac_codes: str = Field(..., min_length=1, description="Pipe-separated HSN/SAC codes")
    quantities: str = Field(..., min_length=1, description="Pipe-separated quantities")
    total_values: str = Field(..., min_length=1, description="Pipe-separated total values (GST-inclusive)")

    # Optional
    notes: Optional[str] = Field(None, description="Invoice notes")
    payment_terms: Optional[str] = Field(None, description="Payment terms")

    @field_validator('pincode')
    @classmethod
    def validate_pincode_format(cls, v: str) -> str:
        """Validate pincode format"""
        from app.core.validators import validate_pincode_field
        try:
            return validate_pincode_field(v)
        except ValueError as e:
            raise ValueError(str(e))

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate and format phone number"""
        if v:
            from app.core.validators import validate_phone_field
            try:
                return validate_phone_field(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v

    @field_validator('gstin')
    @classmethod
    def validate_gstin_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate GSTIN format"""
        if v:
            from app.core.validators import validate_gstin_field
            try:
                return validate_gstin_field(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v


class BulkUploadSuccessItem(BaseModel):
    """Schema for successful invoice creation in bulk upload"""
    row_number: int = Field(..., description="Row number in CSV (1-based)")
    invoice_id: int = Field(..., description="Created invoice ID")
    invoice_number: str = Field(..., description="Generated invoice number")
    buyer_name: str = Field(..., description="Buyer name")
    total: Decimal = Field(..., description="Invoice total")

    @field_validator('total', mode='before')
    @classmethod
    def serialize_decimal(cls, v):
        """Ensure Decimal fields are serialized as strings"""
        if isinstance(v, Decimal):
            return str(v)
        return v


class BulkUploadFailureItem(BaseModel):
    """Schema for failed invoice creation in bulk upload"""
    row_number: int = Field(..., description="Row number in CSV (1-based)")
    buyer_name: Optional[str] = Field(None, description="Buyer name if available")
    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class BulkUploadResult(BaseModel):
    """
    Schema for bulk upload result

    Implements partial success - some rows may succeed while others fail
    """
    successful: int = Field(..., description="Number of successful invoices")
    failed: int = Field(..., description="Number of failed invoices")
    total_rows: int = Field(..., description="Total rows processed")

    successes: List[BulkUploadSuccessItem] = Field(
        default_factory=list,
        description="List of successful invoice creations"
    )
    failures: List[BulkUploadFailureItem] = Field(
        default_factory=list,
        description="List of failed invoice creations"
    )

    processing_time_seconds: Optional[float] = Field(
        None,
        description="Total processing time in seconds"
    )


class BulkUploadSettings(BaseModel):
    """Settings for bulk upload operation"""
    invoice_type: str = Field(..., description="Invoice type: topmate or user")
    user_id: str = Field(..., description="User ID creating the invoices")
    create_as_draft: bool = Field(False, description="Create invoices as drafts")
    send_email: bool = Field(False, description="Send email after creation")
    send_whatsapp: bool = Field(False, description="Send WhatsApp after creation")
    gst_rate: Decimal = Field(Decimal('18.00'), description="GST rate percentage")

    # Seller details (for user invoices)
    seller_name: Optional[str] = None
    seller_gstin: Optional[str] = None
    seller_address: Optional[str] = None
    seller_pincode: Optional[str] = None
    seller_state: Optional[str] = None
    seller_phone: Optional[str] = None
    seller_email: Optional[str] = None
    seller_website: Optional[str] = None
