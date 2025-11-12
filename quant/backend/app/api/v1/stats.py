"""Statistics API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "30d",
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get politician performance leaderboard.

    Args:
        period: Time period (7d, 30d, 90d, 1y)
        limit: Maximum number of records to return
        db: Database session

    Returns:
        Leaderboard data
    """
    # TODO: Implement actual statistics calculation
    return {
        "leaderboard": [],
        "period": period,
        "limit": limit,
    }


@router.get("/sectors")
async def get_sector_stats(
    period: str = "30d",
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get sector trading statistics.

    Args:
        period: Time period
        db: Database session

    Returns:
        Sector statistics
    """
    # TODO: Implement actual statistics calculation
    return {
        "sectors": [],
        "period": period,
    }
