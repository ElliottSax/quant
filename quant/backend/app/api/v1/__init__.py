"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import (
    trades,
    politicians,
    stats,
    auth,
    patterns,
    export,
    analytics,
    signals,
    backtesting,
    sentiment
)

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(politicians.router, prefix="/politicians", tags=["politicians"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(patterns.router, prefix="/patterns", tags=["pattern-analysis"])
api_router.include_router(export.router, prefix="/export", tags=["data-export"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["advanced-analytics"])

# New high-priority features
api_router.include_router(signals.router, tags=["trading-signals"])
api_router.include_router(backtesting.router, tags=["backtesting"])
api_router.include_router(sentiment.router, tags=["sentiment-analysis"])
