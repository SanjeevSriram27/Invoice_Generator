"""
Business Profile API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from app.database import get_db
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse,
)
from app.core.exceptions import BusinessProfileNotFoundException


router = APIRouter(prefix="/business-profiles", tags=["business-profiles"])


@router.get("/", response_model=List[BusinessProfileResponse])
async def list_business_profiles(
    user_id: Optional[str] = Query(None, description="Filter by user_id"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    List business profiles with optional filtering

    - **user_id**: Filter profiles by user ID
    - **skip**: Pagination offset
    - **limit**: Maximum results per page
    """
    query = select(BusinessProfile)

    # Apply filter if user_id provided
    if user_id:
        query = query.where(BusinessProfile.user_id == user_id)

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(BusinessProfile.created_at.desc())

    result = await db.execute(query)
    profiles = result.scalars().all()

    return profiles


@router.get("/by_user/", response_model=List[BusinessProfileResponse])
async def get_profiles_by_user(
    user_id: str = Query(..., description="User ID to filter by"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all business profiles for a specific user

    This endpoint matches Django's `by_user` action endpoint.

    - **user_id**: Required user ID parameter
    """
    query = select(BusinessProfile).where(
        BusinessProfile.user_id == user_id
    ).order_by(BusinessProfile.created_at.desc())

    result = await db.execute(query)
    profiles = result.scalars().all()

    return profiles


@router.post("/", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_business_profile(
    profile_data: BusinessProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new business profile

    - **user_id**: User ID (required)
    - **business_name**: Business name (required)
    - **gstin**: 15-character GSTIN (required)
    - **address**: Business address (required)
    - **pincode**: 6-digit pincode (required)
    - **state**: 2-letter state code (required)
    - **phone**: Phone number with country code (optional)
    - **email**: Business email (optional)
    - **website**: Business website URL (optional)
    - **logo**: Logo file path or URL (optional)
    """
    # Create new business profile
    profile = BusinessProfile(**profile_data.model_dump())

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    return profile


@router.get("/{profile_id}/", response_model=BusinessProfileResponse)
async def get_business_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a business profile by ID

    - **profile_id**: Business profile ID
    """
    query = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise BusinessProfileNotFoundException(str(profile_id))

    return profile


@router.put("/{profile_id}/", response_model=BusinessProfileResponse)
async def update_business_profile(
    profile_id: int,
    profile_data: BusinessProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing business profile

    All fields are optional. Only provided fields will be updated.

    - **profile_id**: Business profile ID to update
    """
    # Get existing profile
    query = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise BusinessProfileNotFoundException(str(profile_id))

    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return profile


@router.delete("/{profile_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a business profile

    - **profile_id**: Business profile ID to delete
    """
    # Get existing profile
    query = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise BusinessProfileNotFoundException(str(profile_id))

    # Delete profile
    await db.delete(profile)
    await db.commit()

    return None
