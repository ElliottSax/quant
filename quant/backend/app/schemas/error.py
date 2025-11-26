"""Standardized error response schemas."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """Detailed error information for a specific field or issue."""

    field: Optional[str] = Field(None, description="Field name if error is field-specific")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")


class ErrorResponse(BaseModel):
    """Standardized error response format."""

    error: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp when error occurred"
    )
    path: Optional[str] = Field(None, description="Request path where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    errors: Optional[list[ErrorDetail]] = Field(None, description="List of specific errors")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Request validation failed",
                "status_code": 422,
                "timestamp": "2025-01-20T10:30:00Z",
                "path": "/api/v1/auth/register",
                "errors": [
                    {
                        "field": "password",
                        "message": "Password must contain at least one uppercase letter",
                        "code": "password_strength"
                    }
                ]
            }
        }


def create_error_response(
    error: str,
    message: str,
    status_code: int,
    path: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    errors: Optional[list[ErrorDetail]] = None
) -> ErrorResponse:
    """
    Create a standardized error response.

    Args:
        error: Error type/category
        message: Human-readable error message
        status_code: HTTP status code
        path: Request path where error occurred
        details: Additional error details
        errors: List of specific errors

    Returns:
        ErrorResponse with standardized format
    """
    return ErrorResponse(
        error=error,
        message=message,
        status_code=status_code,
        path=path,
        details=details,
        errors=errors
    )
