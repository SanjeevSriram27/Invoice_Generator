"""
Base model and common mixins for SQLAlchemy models
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

# Create base class
Base = declarative_base()


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps
    Replaces Django's auto_now_add and auto_now
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
