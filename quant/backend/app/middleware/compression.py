"""Response compression middleware using GZip."""

import gzip
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import get_logger

logger = get_logger(__name__)

# Minimum content length to compress (bytes)
MIN_COMPRESS_SIZE = 500

# Content types to compress
COMPRESSIBLE_TYPES = {
    "application/json",
    "text/plain",
    "text/html",
    "text/css",
    "application/javascript",
    "text/javascript",
    "application/xml",
    "text/xml",
}


class GZipMiddleware(BaseHTTPMiddleware):
    """
    GZip compression middleware for responses.

    Compresses responses when:
    - Client accepts gzip encoding
    - Response content type is compressible
    - Response size exceeds minimum threshold

    Performance Impact:
    - Reduces bandwidth by 60-80% for JSON responses
    - Minor CPU overhead for compression
    - Significant improvement for slow connections
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = MIN_COMPRESS_SIZE,
        compression_level: int = 6,
        exclude_paths: set[str] | None = None,
    ):
        """
        Initialize GZip middleware.

        Args:
            app: ASGI application
            minimum_size: Minimum content size to compress (default: 500 bytes)
            compression_level: GZip compression level 1-9 (default: 6)
            exclude_paths: Paths to exclude from compression
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.exclude_paths = exclude_paths or set()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with GZip compression.

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Compressed or original response
        """
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)

        # Get response
        response = await call_next(request)

        # Check content type
        content_type = response.headers.get("Content-Type", "")
        base_content_type = content_type.split(";")[0].strip()

        if base_content_type not in COMPRESSIBLE_TYPES:
            return response

        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Check minimum size
        if len(body) < self.minimum_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress
        compressed_body = gzip.compress(body, compresslevel=self.compression_level)

        # Only use compressed if it's actually smaller
        if len(compressed_body) >= len(body):
            logger.debug(f"Compression not beneficial for {request.url.path}")
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Log compression ratio
        ratio = (1 - len(compressed_body) / len(body)) * 100
        logger.debug(f"Compressed {request.url.path}: {len(body)} -> {len(compressed_body)} ({ratio:.1f}% reduction)")

        # Create compressed response
        headers = dict(response.headers)
        headers["Content-Encoding"] = "gzip"
        headers["Content-Length"] = str(len(compressed_body))
        headers["Vary"] = "Accept-Encoding"

        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )
