"""
Custom exceptions for the invoice application
"""
from fastapi import HTTPException, status


class InvoiceNotFoundException(HTTPException):
    """Raised when invoice is not found"""
    def __init__(self, invoice_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with id {invoice_id} not found"
        )


class BusinessProfileNotFoundException(HTTPException):
    """Raised when business profile is not found"""
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business profile {identifier} not found"
        )


class InvoiceNotDraftException(HTTPException):
    """Raised when attempting to modify a finalized invoice"""
    def __init__(self, invoice_number: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice {invoice_number} is finalized and cannot be modified"
        )


class InvalidInvoiceDataException(HTTPException):
    """Raised when invoice data is invalid"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class PDFGenerationException(HTTPException):
    """Raised when PDF generation fails"""
    def __init__(self, detail: str = "Failed to generate PDF"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class EmailSendException(HTTPException):
    """Raised when email sending fails"""
    def __init__(self, detail: str = "Failed to send email"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class WhatsAppSendException(HTTPException):
    """Raised when WhatsApp message sending fails"""
    def __init__(self, detail: str = "Failed to send WhatsApp message"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
