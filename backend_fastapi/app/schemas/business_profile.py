"""
Business Profile schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class BusinessProfileBase(BaseModel):
    """Base schema for business profile"""
    user_id: str = Field(..., min_length=1, max_length=100)
    business_name: str = Field(..., min_length=1, max_length=200)
    gstin: str = Field(..., min_length=15, max_length=15, description="15-character GSTIN")
    address: str = Field(..., min_length=1)
    pincode: str = Field(..., min_length=6, max_length=6, description="6-digit pincode")
    state: str = Field(..., min_length=2, max_length=2, description="2-letter state code")
    phone: Optional[str] = Field(None, max_length=20, description="Phone with country code")
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    logo: Optional[str] = Field(None, max_length=500, description="Logo file path or URL")

    @field_validator('gstin')
    @classmethod
    def validate_gstin_format(cls, v: str) -> str:
        """Validate GSTIN format"""
        if v:
            from app.core.validators import validate_gstin_field
            try:
                return validate_gstin_field(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v

    @field_validator('pincode')
    @classmethod
    def validate_pincode_format(cls, v: str) -> str:
        """Validate pincode format"""
        if v:
            from app.core.validators import validate_pincode_field
            try:
                return validate_pincode_field(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v

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


class BusinessProfileCreate(BusinessProfileBase):
    """Schema for creating business profile"""
    pass


class BusinessProfileUpdate(BaseModel):
    """Schema for updating business profile (all fields optional)"""
    business_name: Optional[str] = Field(None, min_length=1, max_length=200)
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    address: Optional[str] = Field(None, min_length=1)
    pincode: Optional[str] = Field(None, min_length=6, max_length=6)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    logo: Optional[str] = Field(None, max_length=500)

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

    @field_validator('pincode')
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


class BusinessProfileResponse(BusinessProfileBase):
    """Schema for business profile response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
