"""
Subscription-related dependencies for rate limiting and feature access
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.subscription import SubscriptionService


async def check_backtest_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Check if user has remaining backtest quota for their tier.
    Raises HTTPException if quota exceeded.
    """
    usage = await SubscriptionService.check_usage(db, current_user.id)

    if not usage["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly backtest limit reached ({usage['used']}/{usage['limit']}). "
            f"Upgrade to premium for more backtests.",
            headers={"Retry-After": "2592000"},  # 30 days
        )

    return current_user


async def check_premium_access(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if user has premium or higher subscription.
    Raises HTTPException if user is on free tier.
    """
    if not current_user.is_premium():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a premium subscription. "
            "Upgrade to unlock advanced strategies and analysis.",
        )
    return current_user


async def check_enterprise_access(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if user has enterprise subscription.
    Raises HTTPException if user doesn't have enterprise tier.
    """
    if not current_user.is_enterprise():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature is only available for enterprise customers.",
        )
    return current_user


async def optional_user(
    current_user: User | None = Depends(get_current_user),
) -> User | None:
    """
    Get current user if available, otherwise None.
    Used for endpoints that work with or without authentication.
    """
    return current_user
