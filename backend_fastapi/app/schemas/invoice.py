"""
Invoice schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Literal
from decimal import Decimal
from datetime import date, datetime
from app.schemas.invoice_item import InvoiceItemCreate, InvoiceItemResponse


class InvoiceBase(BaseModel):
    """Base schema for invoice"""
    invoice_type: Literal['topmate', 'user'] = Field(..., description="Invoice type: topmate or user")
    user_id: str = Field(..., min_length=1, max_length=100)

    # Dates
    invoice_date: date = Field(default_factory=date.today, description="Invoice date (defaults to today)")
    due_date: Optional[date] = None

    # Seller details (required for user invoices, auto-filled for topmate)
    seller_name: Optional[str] = Field(None, max_length=200)
    seller_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    seller_address: Optional[str] = None
    seller_pincode: Optional[str] = Field(None, min_length=6, max_length=6)
    seller_state: Optional[str] = Field(None, min_length=2, max_length=2)
    seller_phone: Optional[str] = Field(None, max_length=20)
    seller_email: Optional[str] = Field(None, max_length=100)
    seller_website: Optional[str] = Field(None, max_length=200)
    seller_logo: Optional[str] = None  # Base64 image data (can be very long)

    # Buyer details (always required)
    buyer_name: str = Field(..., min_length=1, max_length=200)
    buyer_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    buyer_address: str = Field(..., min_length=1)
    buyer_pincode: str = Field(..., min_length=6, max_length=6)
    buyer_state: str = Field(..., min_length=2, max_length=2)
    buyer_phone: Optional[str] = Field(None, max_length=20)
    buyer_email: Optional[str] = Field(None, max_length=100)
    buyer_logo: Optional[str] = None  # Base64 image data (can be very long)

    # Settings
    gst_rate: Decimal = Field(Decimal('18.00'), description="GST rate percentage (default 18%)")
    is_draft: bool = Field(False, description="Whether invoice is a draft")

    # Additional
    notes: Optional[str] = None
    payment_terms: Optional[str] = None

    @field_validator('seller_gstin', 'buyer_gstin')
    @classmethod
    def validate_gstin_format(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None and validate GSTIN format"""
        # Convert empty string to None
        if v == '' or v is None:
            return None
        # Validate if value exists
        from app.core.validators import validate_gstin_field
        try:
            return validate_gstin_field(v)
        except ValueError as e:
            raise ValueError(str(e))

    @field_validator('seller_pincode', 'buyer_pincode')
    @classmethod
    def validate_pincode_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate pincode format"""
        if v:
            from app.core.validators import validate_pincode_field
            try:
                return validate_pincode_field(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v

    @field_validator('seller_phone', 'buyer_phone')
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


class InvoiceCreate(InvoiceBase):
    """
    Schema for creating invoice

    Note: unit_price in items should be GST-INCLUSIVE (as sent from frontend)
    The backend will extract the base price.
    """
    items: List[InvoiceItemCreate] = Field(..., min_length=1, description="At least one item required")

    @model_validator(mode='before')
    @classmethod
    def clear_seller_for_topmate(cls, data):
        """
        For Topmate invoices, clear any seller details sent from frontend
        This prevents validation errors on invalid/saved seller data
        """
        if isinstance(data, dict) and data.get('invoice_type') == 'topmate':
            # Clear seller fields for Topmate invoices - they'll be auto-filled by service
            data['seller_name'] = None
            data['seller_gstin'] = None
            data['seller_address'] = None
            data['seller_pincode'] = None
            data['seller_state'] = None
            data['seller_phone'] = None
            data['seller_email'] = None
            data['seller_website'] = None
            data['seller_logo'] = None
        return data

    @model_validator(mode='after')
    def validate_seller_details(self):
        """
        Validate seller details based on invoice type
        - topmate invoices: seller details auto-filled from settings (already cleared)
        - user invoices: seller details required
        """
        if self.invoice_type == 'user':
            required_fields = [
                ('seller_name', 'Seller name'),
                ('seller_gstin', 'Seller GSTIN'),
                ('seller_address', 'Seller address'),
                ('seller_pincode', 'Seller pincode'),
                ('seller_state', 'Seller state')
            ]

            for field_name, field_label in required_fields:
                if not getattr(self, field_name):
                    raise ValueError(f"{field_label} is required for user invoices")

        return self


class InvoiceUpdate(BaseModel):
    """
    Schema for updating invoice (only allowed for drafts)
    All fields optional
    """
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Seller
    seller_name: Optional[str] = Field(None, max_length=200)
    seller_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    seller_address: Optional[str] = None
    seller_pincode: Optional[str] = Field(None, min_length=6, max_length=6)
    seller_state: Optional[str] = Field(None, min_length=2, max_length=2)
    seller_phone: Optional[str] = Field(None, max_length=20)
    seller_email: Optional[str] = Field(None, max_length=100)
    seller_website: Optional[str] = Field(None, max_length=200)

    # Buyer
    buyer_name: Optional[str] = Field(None, max_length=200)
    buyer_gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    buyer_address: Optional[str] = None
    buyer_pincode: Optional[str] = Field(None, min_length=6, max_length=6)
    buyer_state: Optional[str] = Field(None, min_length=2, max_length=2)
    buyer_phone: Optional[str] = Field(None, max_length=20)
    buyer_email: Optional[str] = Field(None, max_length=100)

    # Items
    items: Optional[List[InvoiceItemCreate]] = Field(None, min_length=1)

    # Settings
    gst_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """
    Schema for invoice response (full details)

    Note: All Decimal fields are serialized as strings for JSON compatibility
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str

    # Financial (calculated by backend)
    subtotal: Decimal = Field(..., description="Subtotal (base price without tax)")
    cgst: Decimal = Field(..., description="Central GST (intrastate)")
    sgst: Decimal = Field(..., description="State GST (intrastate)")
    igst: Decimal = Field(..., description="Integrated GST (interstate)")
    total: Decimal = Field(..., description="Grand total")
    is_interstate: bool = Field(..., description="Whether transaction is interstate")

    # PDF
    pdf_url: Optional[str] = None
    pdf_file: Optional[str] = None

    # Items
    items: List[InvoiceItemResponse] = []

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('subtotal', 'cgst', 'sgst', 'igst', 'total', 'gst_rate', mode='before')
    @classmethod
    def serialize_decimal(cls, v):
        """Ensure Decimal fields are serialized as strings for JSON compatibility"""
        if isinstance(v, Decimal):
            return str(v)
        return v


class InvoiceListResponse(BaseModel):
    """
    Lightweight schema for invoice list endpoint
    Only includes essential fields for performance
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    invoice_type: str
    user_id: str
    buyer_name: str
    total: Decimal
    invoice_date: date
    is_draft: bool
    created_at: datetime

    @field_validator('total', mode='before')
    @classmethod
    def serialize_decimal(cls, v):
        """Ensure Decimal fields are serialized as strings"""
        if isinstance(v, Decimal):
            return str(v)
        return v


class InvoiceSummaryResponse(BaseModel):
    """Schema for invoice summary statistics"""
    total_invoices: int = Field(..., description="Total number of invoices")
    draft_invoices: int = Field(..., description="Number of draft invoices")
    finalized_invoices: int = Field(..., description="Number of finalized invoices")
    total_amount: Decimal = Field(..., description="Sum of all invoice totals")
    topmate_invoices: int = Field(..., description="Number of Topmate invoices")
    user_invoices: int = Field(..., description="Number of user invoices")

    @field_validator('total_amount', mode='before')
    @classmethod
    def serialize_decimal(cls, v):
        """Ensure Decimal fields are serialized as strings"""
        if isinstance(v, Decimal):
            return str(v)
        return v


class SendEmailRequest(BaseModel):
    """Schema for email sending request"""
    recipient_email: Optional[str] = Field(None, description="Override buyer email")
    subject: Optional[str] = Field(None, description="Custom email subject")
    message: Optional[str] = Field(None, description="Custom email message")


class SendWhatsAppRequest(BaseModel):
    """Schema for WhatsApp sending request"""
    recipient_phone: Optional[str] = Field(None, description="Override buyer phone")
    message: Optional[str] = Field(None, description="Custom WhatsApp message")
