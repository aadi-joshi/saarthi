"""
SUVIDHA 2026 - Main FastAPI Application
Smart Urban Virtual Interactive Digital Helpdesk Assistant
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import logging

from app.config import settings
from app.database import init_db, close_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import RequestLoggingMiddleware

# Import routers
from app.routers import auth, billing, grievance, connection, document, notification, analytics, admin

# Configure logging
logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING)
logger = logging.getLogger("suvidha")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    logger.info("Starting SUVIDHA Backend...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down SUVIDHA Backend...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Smart Urban Virtual Interactive Digital Helpdesk Assistant
    
    A comprehensive digital kiosk system for civic utility services including:
    - **Electricity** - Bill payment, new connections, complaints
    - **Gas** - Bill payment, new connections, leak reporting
    - **Water** - Bill payment, new connections, supply issues
    - **Municipal Services** - Property tax, waste management, street lights
    
    ### Features
    - OTP-based citizen authentication
    - Multi-language support (English, Hindi)
    - Accessibility features
    - Offline transaction support
    - Real-time notifications
    - Admin dashboard with analytics
    
    ### Security
    - OAuth2 + JWT authentication
    - AES encryption for PII
    - Rate limiting
    - Audit logging with hash chain
    
    Built for C-DAC SUVIDHA 2026 Hackathon
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else error["loc"][0]
        errors.append({
            "field": field,
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SUVIDHA Backend"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Smart Urban Virtual Interactive Digital Helpdesk Assistant",
        "documentation": "/docs" if settings.DEBUG else "Documentation available in production mode",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(grievance.router, prefix="/api/v1")
app.include_router(connection.router, prefix="/api/v1")
app.include_router(document.router, prefix="/api/v1")
app.include_router(notification.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
