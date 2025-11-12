"""Monitoring and observability setup."""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


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
