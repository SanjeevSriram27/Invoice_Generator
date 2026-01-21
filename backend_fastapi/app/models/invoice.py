"""
Invoice and InvoiceItem models - Main invoice entities
"""
from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, Numeric, Boolean, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal

from app.models.base import Base


class Invoice(Base):
    """
    Main Invoice model
    Represents a complete invoice (Topmate or User-generated)
    Equivalent to Django's Invoice model
    """
    __tablename__ = 'invoices'
    __table_args__ = (
        Index('idx_invoice_user_created', 'user_id', 'created_at'),
        Index('idx_invoice_number', 'invoice_number', unique=True),
        Index('idx_invoice_type', 'invoice_type'),
    )

    id = Column(BigInteger, primary_key=True, index=True)

    # Invoice identification
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_type = Column(
        String(10),
        nullable=False,
        index=True,
        comment="'topmate' or 'user'"
    )
    user_id = Column(
        String(100),
        nullable=False,
        index=True,
        comment="User ID who generated the invoice"
    )

    # Dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)

    # Seller details (Issued By)
    seller_name = Column(String(255), nullable=False)
    seller_gstin = Column(String(15), nullable=False)
    seller_address = Column(Text, nullable=False)
    seller_pincode = Column(String(6), nullable=False)
    seller_state = Column(String(2), nullable=False)
    seller_phone = Column(String(15), nullable=True)
    seller_email = Column(String(100), nullable=True)
    seller_logo = Column(String(500), nullable=True)
    seller_website = Column(String(200), nullable=True)

    # Seller bank details
    seller_bank_name = Column(String(200), nullable=True)
    seller_account_number = Column(String(50), nullable=True)
    seller_ifsc_code = Column(String(11), nullable=True)
    seller_account_holder_name = Column(String(200), nullable=True)
    seller_branch = Column(String(200), nullable=True)

    # Buyer details (Issued To)
    buyer_name = Column(String(255), nullable=False)
    buyer_gstin = Column(String(15), nullable=True)
    buyer_address = Column(Text, nullable=False)
    buyer_pincode = Column(String(6), nullable=False)
    buyer_state = Column(String(2), nullable=False)
    buyer_phone = Column(String(15), nullable=True)
    buyer_email = Column(String(100), nullable=True)
    buyer_logo = Column(String(500), nullable=True)

    # Financial details
    subtotal = Column(Numeric(12, 2), nullable=False)
    cgst = Column(Numeric(12, 2), nullable=False, default=0)
    sgst = Column(Numeric(12, 2), nullable=False, default=0)
    igst = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False)

    # Tax flags
    is_interstate = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if IGST applicable, False if CGST+SGST"
    )
    gst_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=18.00,
        comment="GST rate percentage (e.g., 18.00 for 18%)"
    )

    # Additional fields
    notes = Column(Text, nullable=True)
    payment_terms = Column(String(255), nullable=True)

    # PDF storage
    pdf_url = Column(String(500), nullable=True)
    pdf_file = Column(String(500), nullable=True)

    # Metadata
    is_draft = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="selectin"  # Eager load items
    )

    def calculate_taxes(self, gst_rate_percent: Decimal = None):
        """
        Calculate GST based on seller and buyer states
        Updates cgst, sgst, igst, and total fields
        """
        if gst_rate_percent is None:
            gst_rate_percent = self.gst_rate

        gst_rate = gst_rate_percent / Decimal('100')

        if self.seller_state == self.buyer_state:
            # Same state: CGST + SGST (split GST equally)
            self.is_interstate = False
            half_rate = gst_rate / Decimal('2')
            self.cgst = (self.subtotal * half_rate).quantize(Decimal('0.01'))
            self.sgst = (self.subtotal * half_rate).quantize(Decimal('0.01'))
            self.igst = Decimal('0.00')
        else:
            # Different states: IGST (full GST rate)
            self.is_interstate = True
            self.igst = (self.subtotal * gst_rate).quantize(Decimal('0.01'))
            self.cgst = Decimal('0.00')
            self.sgst = Decimal('0.00')

        self.total = self.subtotal + self.cgst + self.sgst + self.igst

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', buyer='{self.buyer_name}')>"


class InvoiceItem(Base):
    """
    Line items for an invoice
    Multiple items per invoice
    Equivalent to Django's InvoiceItem model
    """
    __tablename__ = 'invoice_items'
    __table_args__ = (
        Index('idx_invoice_item_invoice_id', 'invoice_id'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    invoice_id = Column(
        BigInteger,
        ForeignKey('invoices.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    serial_number = Column(Integer, nullable=False, comment="S.No. in the invoice")
    description = Column(Text, nullable=False)
    hsn_sac = Column(
        String(15),
        nullable=False,
        comment="HSN (goods) or SAC (services) code"
    )
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

    def calculate_amount(self):
        """Calculate amount from quantity and unit_price"""
        self.amount = (self.quantity * self.unit_price).quantize(Decimal('0.01'))

    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, invoice_id={self.invoice_id}, serial={self.serial_number})>"
