"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Any, TYPE_CHECKING

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.user import User

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Account lockout settings
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token.

    Args:
        subject: Token subject (typically user ID)
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str, version: int = 0) -> str:
    """
    Create JWT refresh token with version for rotation.

    Args:
        subject: Token subject (typically user ID)
        version: Refresh token version (incremented on rotation)

    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "ver": version  # Add version for rotation
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(
    token: str,
    token_type: str = "access",
    expected_version: int | None = None
) -> tuple[str | None, int | None]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token to verify
        token_type: Expected token type ('access' or 'refresh')
        expected_version: Expected token version (for refresh tokens)

    Returns:
        Tuple of (user_id, version) if valid, (None, None) otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        token_sub: str = payload.get("sub")
        token_exp: int = payload.get("exp")
        token_typ: str = payload.get("type")
        token_ver: int = payload.get("ver", 0)

        if not token_sub or not token_exp or token_typ != token_type:
            logger.warning(f"Invalid token payload: type={token_typ}, expected={token_type}")
            return None, None

        # Check version if provided (for refresh tokens)
        if expected_version is not None and token_ver != expected_version:
            logger.warning(f"Token version mismatch: {token_ver} != {expected_version}")
            return None, None

        # Check if token is expired
        if datetime.fromtimestamp(token_exp, tz=timezone.utc) < datetime.now(timezone.utc):
            logger.warning("Token has expired")
            return None, None

        return token_sub, token_ver

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None, None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_account_locked(user: "User") -> bool:
    """
    Check if user account is locked.

    Args:
        user: User to check

    Returns:
        True if account is locked, False otherwise
    """
    if user.locked_until is None:
        return False

    try:
        locked_until_utc = _ensure_utc(user.locked_until)
        if datetime.now(timezone.utc) >= locked_until_utc:
            # Lockout expired
            return False
        return True
    except (AttributeError, TypeError):
        # Handle edge cases where locked_until is not a proper datetime
        logger.warning(f"Invalid locked_until value for user: {type(user.locked_until)}")
        return False


def get_lockout_time_remaining(user: "User") -> int:
    """
    Get remaining lockout time in seconds.

    Args:
        user: User to check

    Returns:
        Remaining lockout time in seconds
    """
    if user.locked_until is None:
        return 0

    try:
        locked_until_utc = _ensure_utc(user.locked_until)
        remaining = (locked_until_utc - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(remaining))
    except (AttributeError, TypeError):
        return 0


async def handle_failed_login(user: "User", db: "AsyncSession") -> None:
    """
    Handle failed login attempt and apply lockout if necessary.

    Args:
        user: User who failed to login
        db: Database session
    """
    user.failed_login_attempts += 1

    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        # Lock the account
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        logger.warning(
            f"Account locked due to {user.failed_login_attempts} failed attempts: {user.username}"
        )
    else:
        logger.info(
            f"Failed login attempt {user.failed_login_attempts}/{MAX_FAILED_ATTEMPTS} for user: {user.username}"
        )

    await db.commit()


async def reset_failed_login_attempts(user: "User", db: "AsyncSession") -> None:
    """
    Reset failed login attempts on successful login.

    Args:
        user: User who logged in successfully
        db: Database session
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()
