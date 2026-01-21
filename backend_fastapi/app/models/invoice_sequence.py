"""
InvoiceNumberSequence model - Manages atomic invoice number generation
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from app.models.base import Base


class InvoiceNumberSequence(Base):
    """
    Manages invoice number sequences
    - One sequence for Topmate (global)
    - One sequence per user for self-use invoices
    Equivalent to Django's InvoiceNumberSequence model
    """
    __tablename__ = 'invoice_number_sequences'
    __table_args__ = (
        UniqueConstraint('sequence_type', 'user_id', name='uq_sequence_type_user'),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    sequence_type = Column(
        String(10),
        nullable=False,
        comment="'topmate' or 'user'"
    )
    user_id = Column(
        String(100),
        nullable=True,
        comment="User ID for user-specific sequences"
    )
    current_number = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        if self.sequence_type == 'topmate':
            return f"<InvoiceNumberSequence(type='topmate', current={self.current_number})>"
        return f"<InvoiceNumberSequence(type='user', user_id='{self.user_id}', current={self.current_number})>"
