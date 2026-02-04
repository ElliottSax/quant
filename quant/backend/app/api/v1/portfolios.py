"""
Portfolio Tracking API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.portfolio_service import portfolio_service
from app.services.subscription_service import subscription_service

router = APIRouter()


# Request/Response models
class WatchlistCreate(BaseModel):
    """Request model for creating a watchlist."""

    name: str = Field(..., min_length=1, max_length=255)
    politician_ids: List[str] = Field(..., min_items=1)
    description: Optional[str] = None
    is_public: bool = False


class WatchlistUpdate(BaseModel):
    """Request model for updating a watchlist."""

    name: Optional[str] = None
    politician_ids: Optional[List[str]] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    sort_order: Optional[int] = None


class WatchlistResponse(BaseModel):
    """Response model for watchlist."""

    id: str
    user_id: str
    name: str
    politician_ids: List[str]
    description: Optional[str]
    is_public: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


async def require_premium(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Require premium subscription for portfolio features."""
    has_premium = await subscription_service.check_premium_access(db, str(current_user.id))

    if not has_premium:
        raise HTTPException(
            status_code=403,
            detail="Premium subscription required for portfolio tracking"
        )

    return current_user


@router.post("/watchlists", response_model=WatchlistResponse, status_code=201)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Create a custom watchlist.

    **Premium feature**: Requires premium subscription.
    """
    watchlist = await portfolio_service.create_watchlist(
        db=db,
        user_id=str(current_user.id),
        name=watchlist_data.name,
        politician_ids=watchlist_data.politician_ids,
        description=watchlist_data.description,
        is_public=watchlist_data.is_public,
    )

    return WatchlistResponse.from_orm(watchlist)


@router.get("/watchlists", response_model=List[WatchlistResponse])
async def get_watchlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get all watchlists for the current user.

    **Premium feature**: Requires premium subscription.
    """
    watchlists = await portfolio_service.get_user_watchlists(
        db=db,
        user_id=str(current_user.id),
    )

    return [WatchlistResponse.from_orm(w) for w in watchlists]


@router.get("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get a specific watchlist.

    **Premium feature**: Requires premium subscription.
    """
    watchlists = await portfolio_service.get_user_watchlists(
        db=db,
        user_id=str(current_user.id),
    )

    watchlist = next((w for w in watchlists if str(w.id) == watchlist_id), None)

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    return WatchlistResponse.from_orm(watchlist)


@router.patch("/watchlists/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: str,
    watchlist_update: WatchlistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Update a watchlist.

    **Premium feature**: Requires premium subscription.
    """
    # Get update data
    update_data = watchlist_update.dict(exclude_none=True)

    watchlist = await portfolio_service.update_watchlist(
        db=db,
        watchlist_id=watchlist_id,
        user_id=str(current_user.id),
        **update_data
    )

    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    return WatchlistResponse.from_orm(watchlist)


@router.delete("/watchlists/{watchlist_id}", status_code=204)
async def delete_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Delete a watchlist.

    **Premium feature**: Requires premium subscription.
    """
    deleted = await portfolio_service.delete_watchlist(
        db=db,
        watchlist_id=watchlist_id,
        user_id=str(current_user.id),
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    return None


@router.get("/{politician_id}/snapshot")
async def get_portfolio_snapshot(
    politician_id: str,
    snapshot_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get portfolio snapshot for a politician.

    **Premium feature**: Requires premium subscription.
    """
    portfolio = await portfolio_service.calculate_portfolio_snapshot(
        db=db,
        politician_id=politician_id,
        snapshot_date=snapshot_date,
    )

    return {
        "politician_id": str(portfolio.politician_id),
        "snapshot_date": portfolio.snapshot_date.isoformat(),
        "total_value": float(portfolio.total_value),
        "holdings": portfolio.holdings,
        "sector_allocation": portfolio.sector_allocation,
        "concentration_score": float(portfolio.concentration_score)
        if portfolio.concentration_score
        else None,
    }


@router.get("/{politician_id}/history")
async def get_portfolio_history(
    politician_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get portfolio history for a politician.

    **Premium feature**: Requires premium subscription.
    """
    portfolios = await portfolio_service.get_portfolio_history(
        db=db,
        politician_id=politician_id,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "politician_id": politician_id,
        "snapshots": [
            {
                "snapshot_date": p.snapshot_date.isoformat(),
                "total_value": float(p.total_value),
                "holdings_count": len(p.holdings),
                "concentration_score": float(p.concentration_score)
                if p.concentration_score
                else None,
            }
            for p in portfolios
        ],
    }


@router.get("/{politician_id}/report")
async def get_portfolio_report(
    politician_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get comprehensive portfolio report for a politician.

    **Premium feature**: Requires premium subscription.
    """
    report = await portfolio_service.get_portfolio_report(
        db=db,
        politician_id=politician_id,
    )

    return report


@router.get("/performance/calculate")
async def calculate_portfolio_performance(
    politician_ids: List[str] = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Calculate portfolio performance for selected politicians.

    **Premium feature**: Requires premium subscription.
    """
    performance = await portfolio_service.calculate_portfolio_performance(
        db=db,
        politician_ids=politician_ids,
        start_date=start_date,
        end_date=end_date,
    )

    return performance
