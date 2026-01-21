"""
Invoice Item schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from typing import Optional
from datetime import datetime


class InvoiceItemBase(BaseModel):
    """Base schema for invoice item"""
    description: str = Field(..., min_length=1, max_length=500)
    hsn_sac: str = Field(..., min_length=1, max_length=15, description="HSN/SAC code")
    quantity: Decimal = Field(..., gt=0, description="Quantity (must be positive)")
    unit_price: Decimal = Field(..., gt=0, description="Unit price INCLUDING GST from frontend")


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating invoice item (used in nested invoice creation)"""
    pass


class InvoiceItemUpdate(BaseModel):
    """Schema for updating invoice item"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    hsn_sac: Optional[str] = Field(None, min_length=1, max_length=15)
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)


class InvoiceItemResponse(InvoiceItemBase):
    """
    Schema for invoice item response
    Note: unit_price in response is the BASE price (GST extracted)
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    serial_number: int
    amount: Decimal = Field(..., description="Total amount for this item (quantity * unit_price)")
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('unit_price', 'amount', mode='before')
    @classmethod
    def serialize_decimal(cls, v):
        """Ensure Decimal fields are serialized as strings for JSON compatibility"""
        if isinstance(v, Decimal):
            return str(v)
        return v
