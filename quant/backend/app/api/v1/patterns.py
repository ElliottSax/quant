"""Pattern detection API endpoints."""

from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.pattern import PatternModel
from app.models.pattern_occurrence import PatternOccurrence

router = APIRouter()


@router.get("/patterns")
async def get_patterns(
    pattern_type: Optional[
        Literal[
            "seasonal",
            "calendar",
            "cycle",
            "regime",
            "behavioral",
            "politician",
            "earnings",
            "economic",
        ]
    ] = Query(default=None, description="Filter by pattern type"),
    ticker: Optional[str] = Query(default=None, description="Filter by ticker symbol"),
    min_reliability: float = Query(
        default=70.0,
        ge=0,
        le=100,
        description="Minimum reliability score",
    ),
    is_active: bool = Query(default=True, description="Filter active patterns only"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Results offset"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get detected patterns with optional filters.

    Returns list of patterns that meet the specified criteria, ordered by
    reliability score (highest first).
    """
    query = select(PatternModel).options(
        selectinload(PatternModel.occurrences)
    )

    # Apply filters
    if pattern_type:
        query = query.where(PatternModel.pattern_type == pattern_type)

    if ticker:
        query = query.where(PatternModel.ticker == ticker)

    query = query.where(PatternModel.reliability_score >= min_reliability)

    if is_active:
        query = query.where(PatternModel.is_active == True)

    # Order by reliability score (highest first)
    query = query.order_by(PatternModel.reliability_score.desc())

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    patterns = result.scalars().all()

    return {
        "patterns": [pattern.to_dict() for pattern in patterns],
        "count": len(patterns),
        "limit": limit,
        "offset": offset,
        "filters": {
            "pattern_type": pattern_type,
            "ticker": ticker,
            "min_reliability": min_reliability,
            "is_active": is_active,
        },
    }


@router.get("/patterns/{pattern_id}")
async def get_pattern(
    pattern_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get detailed information about a specific pattern.

    Includes full validation metrics, historical occurrences, and economic rationale.
    """
    query = select(PatternModel).options(
        selectinload(PatternModel.occurrences)
    ).where(PatternModel.pattern_id == pattern_id)

    result = await db.execute(query)
    pattern = result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Get occurrences
    occurrences = [occ.to_dict() for occ in pattern.occurrences]

    pattern_dict = pattern.to_dict()
    pattern_dict["occurrences"] = occurrences

    return pattern_dict


@router.get("/patterns/upcoming")
async def get_upcoming_patterns(
    days_ahead: int = Query(default=30, ge=1, le=365, description="Look ahead days"),
    min_reliability: float = Query(default=70.0, ge=0, le=100),
    ticker: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get patterns with upcoming occurrences.

    Returns patterns that are expected to occur within the specified timeframe,
    ordered by next occurrence date (soonest first).
    """
    from datetime import date, timedelta

    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    query = select(PatternModel).options(
        selectinload(PatternModel.occurrences)
    )

    # Filter conditions
    query = query.where(
        PatternModel.is_active == True,
        PatternModel.next_occurrence.isnot(None),
        PatternModel.next_occurrence >= today,
        PatternModel.next_occurrence <= end_date,
        PatternModel.reliability_score >= min_reliability,
    )

    if ticker:
        query = query.where(PatternModel.ticker == ticker)

    # Order by next occurrence (soonest first)
    query = query.order_by(PatternModel.next_occurrence.asc()).limit(limit)

    result = await db.execute(query)
    patterns = result.scalars().all()

    return {
        "patterns": [pattern.to_dict() for pattern in patterns],
        "count": len(patterns),
        "timeframe": {
            "start": today.isoformat(),
            "end": end_date.isoformat(),
            "days": days_ahead,
        },
        "filters": {
            "min_reliability": min_reliability,
            "ticker": ticker,
        },
    }


@router.get("/patterns/{pattern_id}/occurrences")
async def get_pattern_occurrences(
    pattern_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get historical occurrences for a specific pattern.

    Returns list of past occurrences with performance metrics, ordered by
    date (most recent first).
    """
    # First verify pattern exists
    pattern_query = select(PatternModel).where(
        PatternModel.pattern_id == pattern_id
    )
    pattern_result = await db.execute(pattern_query)
    pattern = pattern_result.scalar_one_or_none()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Get occurrences
    query = (
        select(PatternOccurrence)
        .where(PatternOccurrence.pattern_id == pattern.id)
        .order_by(PatternOccurrence.end_date.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    occurrences = result.scalars().all()

    return {
        "pattern_id": pattern_id,
        "pattern_name": pattern.name,
        "occurrences": [occ.to_dict() for occ in occurrences],
        "count": len(occurrences),
        "limit": limit,
        "offset": offset,
    }


@router.get("/patterns/ticker/{ticker}")
async def get_patterns_for_ticker(
    ticker: str,
    min_reliability: float = Query(default=60.0, ge=0, le=100),
    is_active: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get all patterns detected for a specific ticker.

    Returns all pattern types (seasonal, calendar, etc.) that have been
    detected for the specified stock.
    """
    query = select(PatternModel).options(
        selectinload(PatternModel.occurrences)
    )

    query = query.where(
        PatternModel.ticker == ticker,
        PatternModel.reliability_score >= min_reliability,
    )

    if is_active:
        query = query.where(PatternModel.is_active == True)

    query = query.order_by(PatternModel.reliability_score.desc())

    result = await db.execute(query)
    patterns = result.scalars().all()

    # Group by pattern type
    patterns_by_type = {}
    for pattern in patterns:
        ptype = pattern.pattern_type
        if ptype not in patterns_by_type:
            patterns_by_type[ptype] = []
        patterns_by_type[ptype].append(pattern.to_dict())

    return {
        "ticker": ticker,
        "total_patterns": len(patterns),
        "patterns_by_type": patterns_by_type,
        "filters": {
            "min_reliability": min_reliability,
            "is_active": is_active,
        },
    }


@router.get("/patterns/top-reliable")
async def get_top_reliable_patterns(
    limit: int = Query(default=20, ge=1, le=100),
    pattern_type: Optional[
        Literal[
            "seasonal",
            "calendar",
            "cycle",
            "regime",
            "behavioral",
            "politician",
            "earnings",
            "economic",
        ]
    ] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get top patterns by reliability score.

    Returns the most reliable patterns across all tickers, useful for
    identifying the strongest market anomalies.
    """
    query = select(PatternModel).options(
        selectinload(PatternModel.occurrences)
    )

    query = query.where(PatternModel.is_active == True)

    if pattern_type:
        query = query.where(PatternModel.pattern_type == pattern_type)

    query = query.order_by(PatternModel.reliability_score.desc()).limit(limit)

    result = await db.execute(query)
    patterns = result.scalars().all()

    return {
        "patterns": [pattern.to_dict() for pattern in patterns],
        "count": len(patterns),
        "filters": {
            "pattern_type": pattern_type,
        },
    }


@router.get("/patterns/stats/summary")
async def get_pattern_statistics(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get summary statistics about detected patterns.

    Provides overview of pattern detection system: total patterns, average
    reliability, breakdown by type, etc.
    """
    from sqlalchemy import func

    # Total active patterns
    total_query = select(func.count(PatternModel.id)).where(
        PatternModel.is_active == True
    )
    total_result = await db.execute(total_query)
    total_patterns = total_result.scalar()

    # Average reliability score
    avg_reliability_query = select(
        func.avg(PatternModel.reliability_score)
    ).where(PatternModel.is_active == True)
    avg_result = await db.execute(avg_reliability_query)
    avg_reliability = avg_result.scalar() or 0.0

    # Patterns by type
    type_query = (
        select(
            PatternModel.pattern_type,
            func.count(PatternModel.id).label("count"),
        )
        .where(PatternModel.is_active == True)
        .group_by(PatternModel.pattern_type)
    )
    type_result = await db.execute(type_query)
    patterns_by_type = {row[0]: row[1] for row in type_result}

    # Upcoming patterns (next 30 days)
    from datetime import date, timedelta

    today = date.today()
    upcoming_30d = today + timedelta(days=30)

    upcoming_query = select(func.count(PatternModel.id)).where(
        PatternModel.is_active == True,
        PatternModel.next_occurrence.isnot(None),
        PatternModel.next_occurrence >= today,
        PatternModel.next_occurrence <= upcoming_30d,
    )
    upcoming_result = await db.execute(upcoming_query)
    upcoming_count = upcoming_result.scalar()

    # High reliability patterns (>= 80)
    high_reliability_query = select(func.count(PatternModel.id)).where(
        PatternModel.is_active == True,
        PatternModel.reliability_score >= 80,
    )
    high_rel_result = await db.execute(high_reliability_query)
    high_reliability_count = high_rel_result.scalar()

    return {
        "total_active_patterns": total_patterns,
        "average_reliability_score": round(avg_reliability, 2),
        "patterns_by_type": patterns_by_type,
        "upcoming_patterns_30d": upcoming_count,
        "high_reliability_patterns": high_reliability_count,
    }
