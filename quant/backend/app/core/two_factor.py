"""Two-Factor Authentication utilities using TOTP."""

import base64
import io
import json
import secrets
from typing import TYPE_CHECKING

import pyotp
import qrcode

from app.core.config import settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.models.user import User

logger = get_logger(__name__)

# Number of backup codes to generate
BACKUP_CODE_COUNT = 10
BACKUP_CODE_LENGTH = 8


def generate_totp_secret() -> str:
    """Generate a new TOTP secret."""
    return pyotp.random_base32()


def get_totp(secret: str) -> pyotp.TOTP:
    """Get TOTP instance for a secret."""
    return pyotp.TOTP(secret)


def verify_totp(secret: str, token: str) -> bool:
    """
    Verify a TOTP token.

    Args:
        secret: TOTP secret
        token: 6-digit token to verify

    Returns:
        True if token is valid, False otherwise
    """
    try:
        totp = get_totp(secret)
        # valid_window=1 allows for 30 seconds of clock drift
        return totp.verify(token, valid_window=1)
    except Exception as e:
        logger.warning(f"TOTP verification failed: {e}")
        return False


def generate_provisioning_uri(secret: str, username: str) -> str:
    """
    Generate the provisioning URI for authenticator apps.

    Args:
        secret: TOTP secret
        username: User's username or email

    Returns:
        otpauth:// URI
    """
    totp = get_totp(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name=settings.PROJECT_NAME
    )


def generate_qr_code_base64(provisioning_uri: str) -> str:
    """
    Generate a QR code as base64 encoded PNG.

    Args:
        provisioning_uri: The otpauth:// URI

    Returns:
        Base64 encoded PNG image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_backup_codes() -> list[str]:
    """
    Generate a set of backup codes for 2FA recovery.

    Returns:
        List of backup codes
    """
    return [
        secrets.token_hex(BACKUP_CODE_LENGTH // 2).upper()
        for _ in range(BACKUP_CODE_COUNT)
    ]


def hash_backup_codes(codes: list[str]) -> str:
    """
    Store backup codes as JSON string.
    In production, consider hashing each code individually.

    Args:
        codes: List of backup codes

    Returns:
        JSON string of codes (for basic storage)
    """
    # Note: For enhanced security, hash each code with bcrypt
    # Here we store as JSON for simplicity; codes are single-use
    return json.dumps(codes)


def verify_backup_code(stored_codes_json: str, provided_code: str) -> tuple[bool, str | None]:
    """
    Verify a backup code and return updated codes list.

    Args:
        stored_codes_json: JSON string of remaining backup codes
        provided_code: Code provided by user

    Returns:
        Tuple of (is_valid, updated_codes_json or None)
    """
    try:
        codes = json.loads(stored_codes_json)
        normalized_code = provided_code.upper().replace("-", "").replace(" ", "")

        if normalized_code in codes:
            # Remove used code
            codes.remove(normalized_code)
            logger.info(f"Backup code used, {len(codes)} remaining")
            return True, json.dumps(codes) if codes else None

        return False, None
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse backup codes: {e}")
        return False, None


def get_remaining_backup_codes_count(stored_codes_json: str | None) -> int:
    """Get the count of remaining backup codes."""
    if not stored_codes_json:
        return 0
    try:
        codes = json.loads(stored_codes_json)
        return len(codes)
    except (json.JSONDecodeError, TypeError):
        return 0
