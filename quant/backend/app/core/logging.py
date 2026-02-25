"""
Logging configuration with security hardening.

Features:
- Log sanitization to prevent log injection
- Sensitive data filtering (passwords, tokens, API keys)
- Structured logging support
- Security event logging
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Set log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for errors
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # File handler for all logs (only in development)
    if settings.DEBUG:
        debug_handler = logging.FileHandler(log_dir / "debug.log")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        root_logger.addHandler(debug_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# ============================================================================
# LOG SANITIZATION - Security Hardening
# ============================================================================

# Patterns for sensitive data that should be redacted from logs
SENSITIVE_PATTERNS = [
    # Passwords
    (re.compile(r'password["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'password=***REDACTED***'),
    (re.compile(r'passwd["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'passwd=***REDACTED***'),
    (re.compile(r'pwd["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'pwd=***REDACTED***'),

    # API Keys and Tokens
    (re.compile(r'api[_-]?key["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'api_key=***REDACTED***'),
    (re.compile(r'api[_-]?secret["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'api_secret=***REDACTED***'),
    (re.compile(r'token["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'token=***REDACTED***'),
    (re.compile(r'bearer\s+[a-zA-Z0-9\-._~+/]+=*', re.IGNORECASE), 'bearer ***REDACTED***'),
    (re.compile(r'authorization["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'authorization=***REDACTED***'),

    # Secret Keys
    (re.compile(r'secret[_-]?key["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'secret_key=***REDACTED***'),
    (re.compile(r'private[_-]?key["\s:=]+[^\s,}"\']+', re.IGNORECASE), 'private_key=***REDACTED***'),

    # Credit Cards (basic pattern)
    (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), '****-****-****-****'),

    # SSN (basic pattern)
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '***-**-****'),

    # Email addresses (partial redaction)
    (re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), r'***@\2'),
]

# Patterns for log injection attacks (newlines, ANSI codes, etc.)
LOG_INJECTION_PATTERNS = [
    (re.compile(r'[\r\n]+'), ' '),  # Replace newlines with spaces
    (re.compile(r'\x1b\[[0-9;]*m'), ''),  # Remove ANSI escape codes
    (re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]'), ''),  # Remove control characters
]


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log message to prevent log injection and sensitive data exposure.

    Security protections:
    1. Removes/replaces newlines to prevent log injection
    2. Removes ANSI escape codes
    3. Removes control characters
    4. Redacts sensitive data (passwords, tokens, credit cards, etc.)

    Args:
        message: Log message to sanitize

    Returns:
        Sanitized log message

    Example:
        >>> sanitize_log_message("User login with password=secret123")
        "User login with password=***REDACTED***"

        >>> sanitize_log_message("Token: abc\\nINJECTED LOG")
        "Token: abc INJECTED LOG"  # Newline removed
    """
    if not isinstance(message, str):
        message = str(message)

    # Step 1: Prevent log injection
    for pattern, replacement in LOG_INJECTION_PATTERNS:
        message = pattern.sub(replacement, message)

    # Step 2: Redact sensitive data
    for pattern, replacement in SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)

    return message


def sanitize_dict(data: Dict[str, Any], redact_keys: set[str] | None = None) -> Dict[str, Any]:
    """
    Sanitize dictionary by redacting sensitive keys.

    Args:
        data: Dictionary to sanitize
        redact_keys: Additional keys to redact (beyond defaults)

    Returns:
        Sanitized dictionary

    Example:
        >>> sanitize_dict({"user": "john", "password": "secret"})
        {"user": "john", "password": "***REDACTED***"}
    """
    # Default sensitive keys
    default_redact_keys = {
        'password', 'passwd', 'pwd',
        'api_key', 'apikey', 'api_secret',
        'token', 'access_token', 'refresh_token',
        'secret', 'secret_key',
        'private_key', 'authorization',
        'credit_card', 'card_number', 'cvv',
        'ssn', 'social_security',
    }

    if redact_keys:
        default_redact_keys.update(redact_keys)

    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower().replace('_', '').replace('-', '')

        # Check if key contains sensitive data
        is_sensitive = any(sensitive in key_lower for sensitive in default_redact_keys)

        if is_sensitive:
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, redact_keys)
        elif isinstance(value, str):
            sanitized[key] = sanitize_log_message(value)
        else:
            sanitized[key] = value

    return sanitized


class SanitizingFilter(logging.Filter):
    """
    Logging filter that sanitizes log records before they are written.

    Automatically sanitizes:
    - Log messages
    - Exception messages
    - Extra data in log records
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize log record.

        Args:
            record: Log record to filter

        Returns:
            True (always allow record, just sanitize it)
        """
        # Sanitize main message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)

        # Sanitize exception info
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_value and hasattr(exc_value, 'args') and exc_value.args:
                # Sanitize exception message
                sanitized_args = tuple(
                    sanitize_log_message(str(arg)) if isinstance(arg, str) else arg
                    for arg in exc_value.args
                )
                exc_value.args = sanitized_args

        # Sanitize extra data
        for key in ['extra', 'args']:
            if hasattr(record, key):
                value = getattr(record, key)
                if isinstance(value, dict):
                    setattr(record, key, sanitize_dict(value))

        return True


def get_security_logger(name: str) -> logging.Logger:
    """
    Get a security-focused logger with enhanced filtering.

    Use this for logging security-sensitive events like:
    - Authentication attempts
    - Authorization failures
    - Suspicious activity
    - Data access

    Args:
        name: Logger name

    Returns:
        Logger with security sanitization
    """
    logger = logging.getLogger(f"security.{name}")

    # Add sanitizing filter if not already present
    if not any(isinstance(f, SanitizingFilter) for f in logger.filters):
        logger.addFilter(SanitizingFilter())

    return logger
