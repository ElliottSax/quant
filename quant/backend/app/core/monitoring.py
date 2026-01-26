"""Monitoring and observability setup."""

import time
import psutil
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MonitoringService:
    """Centralized monitoring and metrics service"""

    def __init__(self):
        self.start_time = time.time()

        # Prometheus metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )

        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )

        self.active_requests = Gauge(
            'http_requests_active',
            'Active HTTP requests'
        )

        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )

        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )

        self.error_count = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'endpoint']
        )

        # System metrics
        self.cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage')
        self.disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage')

    def track_request(self, method: str, endpoint: str, status_code: int):
        """Track HTTP request"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()

    def track_cache_hit(self, cache_type: str = 'redis'):
        """Track cache hit"""
        self.cache_hits.labels(cache_type=cache_type).inc()

    def track_cache_miss(self, cache_type: str = 'redis'):
        """Track cache miss"""
        self.cache_misses.labels(cache_type=cache_type).inc()

    def track_error(self, error_type: str, endpoint: str):
        """Track error"""
        self.error_count.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()

    def update_system_metrics(self):
        """Update system resource metrics"""
        try:
            self.cpu_usage.set(psutil.cpu_percent(interval=1))
            self.memory_usage.set(psutil.virtual_memory().percent)
            self.disk_usage.set(psutil.disk_usage('/').percent)
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return {
            'uptime_seconds': time.time() - self.start_time,
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'active_requests': self.active_requests._value.get(),
        }

    def export_prometheus_metrics(self) -> Response:
        """Export metrics in Prometheus format"""
        self.update_system_metrics()
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )


# Global monitoring service
monitoring_service = MonitoringService()


def setup_sentry() -> None:
    """
    Initialize Sentry monitoring.

    Only initializes if SENTRY_DSN is configured.
    """
    if not settings.SENTRY_DSN:
        logger.info("Sentry DSN not configured - monitoring disabled")
        return

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            # Set traces_sample_rate to 1.0 to capture 100% of transactions
            # Adjust this value in production
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
            profiles_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            # Release tracking
            release=f"quant@{settings.VERSION}",
            # Send default PII (personally identifiable information)
            send_default_pii=False,
            # Additional options
            attach_stacktrace=True,
            # Before send hook to filter sensitive data
            before_send=filter_sensitive_data,
        )

        logger.info(
            f"Sentry monitoring initialized for environment: {settings.SENTRY_ENVIRONMENT}"
        )

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def filter_sensitive_data(event: dict, hint: dict) -> dict | None:
    """
    Filter sensitive data before sending to Sentry.

    Args:
        event: Sentry event dictionary
        hint: Additional context

    Returns:
        Filtered event or None to drop the event
    """
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]

        # Redact authorization headers
        if "Authorization" in headers:
            headers["Authorization"] = "[Filtered]"
        if "authorization" in headers:
            headers["authorization"] = "[Filtered]"

        # Redact cookie headers
        if "Cookie" in headers:
            headers["Cookie"] = "[Filtered]"
        if "cookie" in headers:
            headers["cookie"] = "[Filtered]"

    # Remove sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        query_string = event["request"]["query_string"]

        # Filter common sensitive parameters
        sensitive_params = ["password", "token", "api_key", "secret"]
        for param in sensitive_params:
            if param in query_string.lower():
                event["request"]["query_string"] = "[Filtered]"
                break

    # Remove sensitive data from extra context
    if "extra" in event:
        extra = event["extra"]
        sensitive_keys = ["password", "token", "secret", "api_key", "access_token", "refresh_token"]

        for key in list(extra.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                extra[key] = "[Filtered]"

    return event


def capture_exception(exception: Exception, **extra_context) -> None:
    """
    Manually capture an exception to Sentry.

    Args:
        exception: Exception to capture
        **extra_context: Additional context to attach
    """
    if not settings.SENTRY_DSN:
        return

    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)

        sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", **extra_context) -> None:
    """
    Manually capture a message to Sentry.

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **extra_context: Additional context to attach
    """
    if not settings.SENTRY_DSN:
        return

    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)

        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: str | None = None, username: str | None = None) -> None:
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username,
    })


def clear_user_context() -> None:
    """Clear user context from Sentry."""
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.set_user(None)
