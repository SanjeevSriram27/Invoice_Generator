"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application

    Runs on startup and shutdown
    """
    # Startup
    print("=" * 80)
    print("Starting Invoice Generator FastAPI Backend")
    print("=" * 80)

    # Create tables if they don't exist (for development)
    # In production, use Alembic migrations instead
    async with engine.begin() as conn:
        # Don't create tables automatically - use Alembic migrations
        # await conn.run_sync(Base.metadata.create_all)
        print("Database connection established")

    # Ensure media directories exist
    media_dirs = [
        os.path.join(settings.media_root, "logos"),
        os.path.join(settings.media_root, "invoices")
    ]
    for dir_path in media_dirs:
        os.makedirs(dir_path, exist_ok=True)

    print(f"Media directories ensured: {settings.media_root}")
    print(f"CORS origins: {settings.cors_origins}")
    print("=" * 80)

    yield

    # Shutdown
    print("=" * 80)
    print("Shutting down Invoice Generator FastAPI Backend")
    print("=" * 80)


# Create FastAPI application
app = FastAPI(
    title="Invoice Generator API",
    description="FastAPI backend for invoice generation with GST calculations, PDF generation, and multi-channel distribution",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for media (logos, PDFs)
# Ensure media directory exists
os.makedirs(settings.media_root, exist_ok=True)

app.mount(
    settings.media_url,
    StaticFiles(directory=settings.media_root),
    name="media"
)


# Include API routers
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Invoice Generator API - FastAPI Backend",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "api_base": "/api",
        "endpoints": {
            "business_profiles": "/api/business-profiles/",
            "invoices": "/api/invoices/"
        },
        "status": "running"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }


# Exception handlers
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # Log the validation error for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Validation error on {request.url}: {exc.errors()}")

    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # Handle input field if it exists and is serializable
        if "input" in error:
            try:
                error_dict["input"] = str(error["input"])
            except:
                error_dict["input"] = None
        errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "body": None  # Don't include body as it may contain non-serializable objects
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Run with: python app/main.py
    # Or use: uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
