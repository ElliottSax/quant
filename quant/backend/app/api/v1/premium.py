"""
Premium Features API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.premium_features import premium_service
from pydantic import BaseModel

router = APIRouter()


# Request/Response models
class WatchlistCreate(BaseModel):
    name: str
    politician_ids: List[str]


class PriceAlertCreate(BaseModel):
    symbol: str
    target_price: float
    condition: str = "above"  # "above" or "below"


class ActivityAlertCreate(BaseModel):
    politician_id: str
    alert_types: List[str]  # ['new_trade', 'large_trade', 'unusual_activity']


class ReportFilters(BaseModel):
    politician_ids: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    symbols: Optional[List[str]] = None


# Middleware to check premium access
async def require_premium(
    current_user: User = Depends(get_current_active_user)
):
    """Require premium subscription"""
    has_premium = await premium_service.check_premium_access(str(current_user.id))

    if not has_premium:
        raise HTTPException(
            status_code=403,
            detail="Premium subscription required for this feature"
        )

    return current_user


@router.get("/features")
async def get_premium_features(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of available premium features
    """
    return await premium_service.get_premium_features_summary()


# Analytics Endpoints
@router.get("/analytics/patterns")
async def get_trading_patterns(
    db: AsyncSession = Depends(get_db),
    politician_id: Optional[str] = Query(None),
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(require_premium)
):
    """
    Detect advanced trading patterns
    - Unusual volume
    - Clustered trades
    - Pre-announcement activity
    """
    patterns = await premium_service.analytics.detect_trading_patterns(
        db, politician_id, days
    )

    return patterns


@router.get("/analytics/correlation/{politician_id}")
async def get_portfolio_correlation(
    politician_id: str,
    db: AsyncSession = Depends(get_db),
    days: int = Query(180, ge=30, le=730),
    current_user: User = Depends(require_premium)
):
    """
    Analyze portfolio correlation with market movements
    """
    correlation = await premium_service.analytics.analyze_portfolio_correlation(
        db, politician_id, days
    )

    return correlation


@router.get("/analytics/risk/{politician_id}")
async def get_risk_assessment(
    politician_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_premium)
):
    """
    Get comprehensive risk assessment for politician's portfolio
    """
    risk_assessment = await premium_service.analytics.assess_portfolio_risk(
        db, politician_id
    )

    return risk_assessment


# Alert Endpoints
@router.post("/alerts/price")
async def create_price_alert(
    alert: PriceAlertCreate,
    current_user: User = Depends(require_premium)
):
    """
    Create price alert for a symbol
    """
    alert_config = await premium_service.alerts.create_price_alert(
        str(current_user.id),
        alert.symbol,
        alert.target_price,
        alert.condition
    )

    return {
        "message": "Price alert created successfully",
        "alert": alert_config
    }


@router.post("/alerts/activity")
async def create_activity_alert(
    alert: ActivityAlertCreate,
    current_user: User = Depends(require_premium)
):
    """
    Create alert for politician activity
    """
    alert_config = await premium_service.alerts.create_politician_activity_alert(
        str(current_user.id),
        alert.politician_id,
        alert.alert_types
    )

    return {
        "message": "Activity alert created successfully",
        "alert": alert_config
    }


# Watchlist Endpoints
@router.post("/watchlists")
async def create_watchlist(
    watchlist: WatchlistCreate,
    current_user: User = Depends(require_premium)
):
    """
    Create custom watchlist
    """
    created_watchlist = await premium_service.portfolio.create_watchlist(
        str(current_user.id),
        watchlist.name,
        watchlist.politician_ids
    )

    return {
        "message": "Watchlist created successfully",
        "watchlist": created_watchlist
    }


@router.get("/portfolio/performance")
async def get_portfolio_performance(
    db: AsyncSession = Depends(get_db),
    politician_ids: List[str] = Query(...),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_premium)
):
    """
    Calculate portfolio performance for selected politicians
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    performance = await premium_service.portfolio.calculate_portfolio_performance(
        db, politician_ids, start_date, end_date
    )

    return performance


# Report Endpoints
@router.post("/reports/generate")
async def generate_custom_report(
    filters: ReportFilters,
    db: AsyncSession = Depends(get_db),
    format: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: User = Depends(require_premium)
):
    """
    Generate custom activity report
    """
    # Convert to dict for processing
    filter_dict = filters.dict(exclude_none=True)

    report = await premium_service.reports.generate_activity_report(
        db, filter_dict, format
    )

    return report


@router.get("/reports/export/{report_id}")
async def export_report(
    report_id: str,
    format: str = Query("csv", regex="^(csv|excel|pdf)$"),
    current_user: User = Depends(require_premium)
):
    """
    Export generated report
    """
    # In production, fetch report from database
    export_info = await premium_service.reports.export_report(
        {"report_id": report_id},
        format
    )

    return export_info


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current subscription status
    """
    has_premium = await premium_service.check_premium_access(str(current_user.id))

    return {
        "user_id": str(current_user.id),
        "has_premium": has_premium,
        "plan": "premium" if has_premium else "free",
        "features_available": 6 if has_premium else 0
    }
