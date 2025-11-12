"""Politicians API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Politician, Trade
from app.schemas import PoliticianResponse, PoliticianWithTrades

router = APIRouter()


@router.get("/", response_model=dict)
async def list_politicians(
    skip: int = 0,
    limit: int = 100,
    chamber: str | None = None,
    party: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    List all politicians with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        chamber: Filter by chamber (senate/house)
        party: Filter by party
        db: Database session

    Returns:
        List of politicians with pagination info
    """
    # Limit the maximum number of results
    limit = min(limit, 100)

    # Build query
    query = select(Politician)

    # Apply filters
    if chamber:
        query = query.where(Politician.chamber == chamber.lower())
    if party:
        query = query.where(Politician.party == party)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Add pagination and ordering
    query = query.order_by(Politician.name).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    politicians = result.scalars().all()

    # Convert to response models
    politician_responses = [PoliticianResponse.model_validate(p) for p in politicians]

    return {
        "politicians": politician_responses,
        "total": total,
        "skip": skip,
        "limit": limit,
        "filters": {"chamber": chamber, "party": party},
    }


@router.get("/{politician_id}", response_model=PoliticianWithTrades)
async def get_politician(
    politician_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PoliticianWithTrades:
    """
    Get a specific politician by ID with trade statistics.

    Args:
        politician_id: Politician UUID
        db: Database session

    Returns:
        Politician details with trade count and recent trade date
    """
    # Get politician
    query = select(Politician).where(Politician.id == politician_id)
    result = await db.execute(query)
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    # Get trade statistics
    trade_count_query = select(func.count()).where(Trade.politician_id == politician_id)
    trade_count_result = await db.execute(trade_count_query)
    trade_count = trade_count_result.scalar_one()

    # Get most recent trade date
    recent_trade_query = (
        select(func.max(Trade.transaction_date))
        .where(Trade.politician_id == politician_id)
    )
    recent_trade_result = await db.execute(recent_trade_query)
    recent_trade_date = recent_trade_result.scalar_one_or_none()

    # Create response
    politician_dict = {
        "id": politician.id,
        "name": politician.name,
        "chamber": politician.chamber,
        "party": politician.party,
        "state": politician.state,
        "bioguide_id": politician.bioguide_id,
        "created_at": politician.created_at,
        "updated_at": politician.updated_at,
        "trade_count": trade_count,
        "recent_trade_date": recent_trade_date,
    }

    return PoliticianWithTrades(**politician_dict)
