"""API v1 routes."""

from fastapi import APIRouter
import logging

# Core imports (no ML dependencies)
from app.api.v1 import (
    trades,
    politicians,
    stats,
    auth,
    export
)

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include core routers (always available)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(politicians.router, prefix="/politicians", tags=["politicians"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(export.router, prefix="/export", tags=["data-export"])

# Market data router (no ML dependencies, uses yfinance)
try:
    from app.api.v1 import market_data
    api_router.include_router(market_data.router, tags=["market-data"])
    logger.info("Market data endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Market data endpoints disabled: {e}")

# Discoveries router (no ML dependencies, generates from data)
try:
    from app.api.v1 import discoveries
    api_router.include_router(discoveries.router, prefix="/discoveries", tags=["discoveries"])
    logger.info("Discoveries endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Discoveries endpoints disabled: {e}")

# ML-dependent features (optional)
try:
    from app.api.v1 import (
        patterns,
        analytics,
        signals,
        backtesting,
        sentiment,
        portfolio,
        reports
    )
    api_router.include_router(patterns.router, prefix="/patterns", tags=["pattern-analysis"])
    api_router.include_router(analytics.router, prefix="/analytics", tags=["advanced-analytics"])
    api_router.include_router(signals.router, tags=["trading-signals"])
    api_router.include_router(backtesting.router, tags=["backtesting"])
    api_router.include_router(sentiment.router, tags=["sentiment-analysis"])
    api_router.include_router(portfolio.router, tags=["portfolio-optimization"])
    api_router.include_router(reports.router, tags=["automated-reporting"])
    logger.info("ML-dependent features loaded successfully")
except ImportError as e:
    logger.warning(f"ML-dependent features disabled due to missing dependencies: {e}")
