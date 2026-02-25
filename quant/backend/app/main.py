"""Main FastAPI application."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.logging import setup_logging, get_logger
from app.core.rate_limit import RateLimitMiddleware
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    database_error_handler,
    integrity_error_handler,
    validation_error_handler,
    general_exception_handler,
)
from app.api.v1 import api_router

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Set up monitoring
from app.core.monitoring import setup_sentry
setup_sentry()

# Validate configuration on startup
from app.core.config_validator import validate_config_on_startup
validate_config_on_startup()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting up Quant Analytics Platform...")
    try:
        await init_db()
        logger.info("Database initialized successfully")

        # Initialize cache manager
        from app.core.cache import cache_manager
        await cache_manager.connect()
        logger.info("Cache manager initialized")

        # Initialize token blacklist
        from app.core.token_blacklist import token_blacklist
        await token_blacklist.connect()
        logger.info("Token blacklist initialized")

        # Initialize audit logging
        from app.core.audit import audit_logger
        from app.core.database import get_db
        async for db in get_db():
            audit_logger.db = db
            break

    except Exception as e:
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Quant Analytics Platform...")

    # Close cache connection
    from app.core.cache import cache_manager
    await cache_manager.close()

    # Close token blacklist connection
    from app.core.token_blacklist import token_blacklist
    await token_blacklist.close()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Track government stock trades with statistical rigor",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Set up CORS with stricter configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "If-None-Match"],
    expose_headers=["ETag", "Cache-Control"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add security headers middleware (Week 3 Security Hardening)
# Protects against: clickjacking, XSS, MIME sniffing, etc.
from app.middleware import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)
logger.info("Security headers middleware enabled")

# Add GZip compression middleware
# Performance impact: 60-80% bandwidth reduction for JSON responses
from app.middleware import GZipMiddleware
app.add_middleware(
    GZipMiddleware,
    minimum_size=500,
    compression_level=6,
)
logger.info("GZip compression middleware enabled")

# Add ETag caching middleware for GET requests
# Performance impact: 70-90% bandwidth reduction for repeated requests
from app.middleware import ETagMiddleware
app.add_middleware(
    ETagMiddleware,
    cache_max_age=300,  # 5 minutes default cache
    exclude_paths={"/docs", "/redoc", "/openapi.json", "/health"},
)
logger.info("ETag caching middleware enabled")

# Add enhanced rate limiting with per-user limits
from app.core.rate_limit_enhanced import EnhancedRateLimitMiddleware, EnhancedRateLimiter
rate_limiter = EnhancedRateLimiter(
    default_limit=60,
    window_seconds=60,
    enable_user_limits=True,
    enable_ip_limits=True
)
app.add_middleware(EnhancedRateLimitMiddleware, rate_limiter=rate_limiter)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {
        "message": "Quant Analytics Platform API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Checks:
    - Database connectivity
    - Redis cache connectivity
    - Token blacklist connectivity
    - Service status

    Returns:
        Health status including all service dependencies
    """
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": "unknown",
            "cache": "unknown",
            "token_blacklist": "unknown",
        }
    }

    all_healthy = True

    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Health check failed - database error: {e}")
        health_status["services"]["database"] = "error"
        all_healthy = False

    # Check Redis cache
    try:
        from app.core.cache import cache_manager
        if cache_manager.enabled and cache_manager.redis_client:
            await cache_manager.redis_client.ping()
            health_status["services"]["cache"] = "connected"
        else:
            health_status["services"]["cache"] = "disabled"
    except Exception as e:
        logger.error(f"Health check failed - cache error: {e}")
        health_status["services"]["cache"] = "error"
        all_healthy = False

    # Check token blacklist
    try:
        from app.core.token_blacklist import token_blacklist
        if token_blacklist.enabled and token_blacklist.redis_client:
            await token_blacklist.redis_client.ping()
            health_status["services"]["token_blacklist"] = "connected"
        else:
            health_status["services"]["token_blacklist"] = "disabled"
    except Exception as e:
        logger.error(f"Health check failed - token blacklist error: {e}")
        health_status["services"]["token_blacklist"] = "error"
        # Not critical for overall health
        logger.warning("Token blacklist error is non-critical")

    # Set overall status
    health_status["status"] = "healthy" if all_healthy else "degraded"

    # Return 503 if unhealthy
    if not all_healthy:
        raise HTTPException(
            status_code=503,
            detail=health_status
        )

    return health_status
