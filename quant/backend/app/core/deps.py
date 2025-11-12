"""Dependencies for FastAPI endpoints."""

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)

# Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        Current user

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify token
    user_id = verify_token(token, token_type="access")
    if not user_id:
        logger.warning("Invalid or expired token")
        raise UnauthorizedException("Invalid or expired token")

    # Get user from database
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        logger.warning(f"Invalid user ID in token: {user_id}")
        raise UnauthorizedException("Invalid token")

    query = select(User).where(User.id == user_uuid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise UnauthorizedException("User not found")

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user_id}")
        raise UnauthorizedException("Inactive user")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Current active user

    Raises:
        ForbiddenException: If user is not active
    """
    if not current_user.is_active:
        raise ForbiddenException("Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current user from token

    Returns:
        Current superuser

    Raises:
        ForbiddenException: If user is not a superuser
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Non-superuser attempted superuser action: {current_user.username}"
        )
        raise ForbiddenException("Insufficient privileges")
    return current_user


# Optional authentication dependency (doesn't fail if no token)
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Get current user if token is provided, otherwise return None.

    Args:
        credentials: HTTP authorization credentials (optional)
        db: Database session

    Returns:
        Current user if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except (UnauthorizedException, ForbiddenException):
        return None
