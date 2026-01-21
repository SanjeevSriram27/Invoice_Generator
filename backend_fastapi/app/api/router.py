"""
Main API router that aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.business_profiles import router as business_profiles_router
from app.api.invoices import router as invoices_router


# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(business_profiles_router)
api_router.include_router(invoices_router)
