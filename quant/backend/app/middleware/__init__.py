"""Middleware package."""

from app.middleware.cache_middleware import ETagMiddleware

__all__ = ["ETagMiddleware"]
