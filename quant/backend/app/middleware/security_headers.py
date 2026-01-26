"""
Security Headers Middleware

Adds comprehensive security headers to all HTTP responses.
Implements defense-in-depth strategy against common web vulnerabilities.

Security Headers Added:
- X-Content-Type-Options: Prevent MIME type sniffing
- X-Frame-Options: Prevent clickjacking
- X-XSS-Protection: Enable browser XSS filter
- Strict-Transport-Security: Enforce HTTPS
- Content-Security-Policy: Control resource loading
- Permissions-Policy: Restrict browser features
- Referrer-Policy: Control referrer information
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Security Benefits:
    - Prevents clickjacking attacks (X-Frame-Options)
    - Prevents MIME type confusion (X-Content-Type-Options)
    - Enables browser XSS protection (X-XSS-Protection)
    - Enforces HTTPS (HSTS)
    - Controls resource loading (CSP)
    - Restricts browser features (Permissions-Policy)
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize security headers middleware.

        Args:
            app: ASGI application
        """
        super().__init__(app)

        # Build CSP policy based on environment
        self.csp_policy = self._build_csp_policy()

    def _build_csp_policy(self) -> str:
        """
        Build Content Security Policy based on environment.

        Returns:
            CSP policy string
        """
        # Base policy (strict)
        policies = [
            "default-src 'self'",  # Only allow same-origin by default
            "script-src 'self'",  # Only allow scripts from same origin
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (needed for some frameworks)
            "img-src 'self' data: https:",  # Allow images from self, data URLs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URLs
            "connect-src 'self'",  # Allow AJAX requests to same origin
            "frame-src 'none'",  # Block all frames
            "object-src 'none'",  # Block plugins
            "base-uri 'self'",  # Restrict base tag
            "form-action 'self'",  # Only allow form submissions to same origin
            "frame-ancestors 'none'",  # Prevent embedding in iframes
        ]

        # In production, upgrade insecure requests
        if settings.ENVIRONMENT == "production":
            policies.append("upgrade-insecure-requests")

        return "; ".join(policies)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with security headers
        """
        # Process request
        response = await call_next(request)

        # Add security headers
        security_headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            # Enable XSS filter in older browsers
            "X-XSS-Protection": "1; mode=block",
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Restrict browser features
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "interest-cohort=(), payment=(), usb=()"
            ),
            # Content Security Policy
            "Content-Security-Policy": self.csp_policy,
        }

        # Add HSTS in production (enforce HTTPS)
        if settings.ENVIRONMENT == "production":
            security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Apply all security headers
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value

        # Log security header application (debug only)
        if settings.DEBUG:
            logger.debug(f"Applied security headers to {request.url.path}")

        return response


def get_security_headers() -> dict[str, str]:
    """
    Get security headers as a dictionary.

    Useful for testing or manual application.

    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": (
            "camera=(), microphone=(), geolocation=(), "
            "interest-cohort=(), payment=(), usb=()"
        ),
    }
