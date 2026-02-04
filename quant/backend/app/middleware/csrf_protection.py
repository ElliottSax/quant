"""
CSRF Protection Middleware

Protects against Cross-Site Request Forgery attacks.
"""

import secrets
import hmac
import hashlib
from typing import Callable, Optional
from datetime import datetime, timedelta, timezone

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.datastructures import Headers

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection using double-submit cookie pattern.

    How it works:
    1. Server generates CSRF token and sets it as cookie
    2. Client reads token and includes in request header
    3. Server validates token matches cookie

    Safe methods (GET, HEAD, OPTIONS) are exempt.
    """

    def __init__(
        self,
        app: ASGIApp,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        exempt_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.exempt_paths = exempt_paths or [
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
            "/api/v1/monitoring/metrics",
            "/health"
        ]
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with CSRF protection"""

        # Skip exempt paths
        if self._is_exempt(request.url.path):
            return await call_next(request)

        # Safe methods don't need CSRF protection
        if request.method in self.safe_methods:
            response = await call_next(request)
            # Set CSRF cookie for subsequent requests
            if self.cookie_name not in request.cookies:
                csrf_token = self._generate_token()
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=True,
                    secure=settings.ENVIRONMENT == "production",
                    samesite="strict",
                    max_age=86400  # 24 hours
                )
            return response

        # For unsafe methods, validate CSRF token
        csrf_cookie = request.cookies.get(self.cookie_name)
        csrf_header = request.headers.get(self.header_name)

        if not csrf_cookie or not csrf_header:
            logger.warning(
                f"CSRF token missing: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "has_cookie": bool(csrf_cookie),
                    "has_header": bool(csrf_header)
                }
            )
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing"
            )

        # Validate token
        if not self._validate_token(csrf_cookie, csrf_header):
            logger.warning(
                f"CSRF token mismatch: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path
                }
            )
            raise HTTPException(
                status_code=403,
                detail="CSRF token invalid"
            )

        # Token valid, proceed with request
        response = await call_next(request)

        # Rotate token after use
        new_token = self._generate_token()
        response.set_cookie(
            key=self.cookie_name,
            value=new_token,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="strict",
            max_age=86400
        )

        return response

    def _generate_token(self) -> str:
        """Generate a secure CSRF token"""
        return secrets.token_urlsafe(32)

    def _validate_token(self, cookie_token: str, header_token: str) -> bool:
        """
        Validate CSRF token using constant-time comparison.

        Args:
            cookie_token: Token from cookie
            header_token: Token from header

        Returns:
            True if tokens match
        """
        return hmac.compare_digest(cookie_token, header_token)

    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)


class CSRFTokenGenerator:
    """
    Utility for generating CSRF tokens in views.

    Use this when you need to manually generate tokens
    (e.g., for form rendering).
    """

    @staticmethod
    def generate() -> str:
        """Generate a new CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_signed_token(secret: str) -> str:
        """
        Create a signed CSRF token.

        Args:
            secret: Secret key for signing

        Returns:
            Signed token
        """
        token = secrets.token_urlsafe(32)
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))

        # Create signature
        message = f"{token}:{timestamp}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{token}:{timestamp}:{signature}"

    @staticmethod
    def verify_signed_token(
        signed_token: str,
        secret: str,
        max_age: int = 3600
    ) -> bool:
        """
        Verify a signed CSRF token.

        Args:
            signed_token: Token to verify
            secret: Secret key for verification
            max_age: Maximum token age in seconds

        Returns:
            True if valid
        """
        try:
            parts = signed_token.split(":")
            if len(parts) != 3:
                return False

            token, timestamp_str, signature = parts

            # Verify timestamp
            timestamp = int(timestamp_str)
            now = int(datetime.now(timezone.utc).timestamp())
            if now - timestamp > max_age:
                return False

            # Verify signature
            message = f"{token}:{timestamp_str}"
            expected_signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error(f"CSRF token verification failed: {e}")
            return False
