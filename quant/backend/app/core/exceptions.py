"""Custom exceptions and error handlers."""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, DatabaseError
from pydantic import ValidationError

from app.core.logging import get_logger
from app.schemas.error import create_error_response, ErrorDetail

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


class ConflictException(AppException):
    """Resource conflict exception."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class RateLimitException(AppException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


# Exception Handlers


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details,
        },
    )

    error_response = create_error_response(
        error=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        path=str(request.url.path),
        details=exc.details if exc.details else None
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTP error: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )

    error_response = create_error_response(
        error="HTTPException",
        message=str(exc.detail),
        status_code=exc.status_code,
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle database errors."""
    logger.error(
        f"Database error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    error_response = create_error_response(
        error="DatabaseError",
        message="Database error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors."""
    logger.warning(
        f"Integrity error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
    )

    error_response = create_error_response(
        error="IntegrityError",
        message="Resource conflict - duplicate or invalid data",
        status_code=status.HTTP_409_CONFLICT,
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump(exclude_none=True),
    )


async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method},
    )

    # Convert Pydantic errors to ErrorDetail format
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(ErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"]
        ))

    error_response = create_error_response(
        error="ValidationError",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        path=str(request.url.path),
        errors=errors
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(exclude_none=True),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    error_response = create_error_response(
        error="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        path=str(request.url.path)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )
