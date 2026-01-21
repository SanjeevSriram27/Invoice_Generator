"""
Common schemas for API responses
"""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List
from datetime import datetime


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response matching Django REST Framework format

    Example:
        {
            "count": 100,
            "next": "http://localhost:8000/api/invoices/?page=2",
            "previous": null,
            "results": [...]
        }
    """
    count: int = Field(..., description="Total number of items")
    next: Optional[str] = Field(None, description="URL to next page")
    previous: Optional[str] = Field(None, description="URL to previous page")
    results: List[T] = Field(..., description="List of items for current page")


class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    detail: str
    error_code: Optional[str] = None


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps"""
    created_at: datetime
    updated_at: Optional[datetime] = None
