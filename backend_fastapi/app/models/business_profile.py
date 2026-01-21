"""
BusinessProfile model - User's business details for self-use invoices
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class BusinessProfile(Base):
    """
    Stores business profile for 'self-use' invoices
    One profile per user
    Equivalent to Django's BusinessProfile model
    """
    __tablename__ = 'business_profiles'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    business_name = Column(String(255), nullable=False)
    gstin = Column(
        String(15),
        nullable=False,
        comment="15-digit GST Identification Number"
    )
    address = Column(Text, nullable=False)
    pincode = Column(String(6), nullable=False)
    state = Column(String(2), nullable=False)  # Indian state code
    phone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    logo = Column(
        String(500),
        nullable=True,
        comment="Path to business logo file"
    )
    website = Column(
        String(200),
        nullable=True,
        comment="Business website or profile URL"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<BusinessProfile(id={self.id}, name='{self.business_name}', gstin='{self.gstin}')>"
