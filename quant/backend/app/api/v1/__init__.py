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

# Discovery integration router (pulls from discovery project)
try:
    from app.api.v1 import discovery
    api_router.include_router(discovery.router, prefix="/discovery", tags=["discovery-integration"])
    logger.info("Discovery integration endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Discovery integration disabled: {e}")

# WebSocket router for real-time updates (includes enhanced features)
try:
    from app.api.v1 import websocket
    api_router.include_router(websocket.router, tags=["websocket"])
    logger.info("WebSocket endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"WebSocket endpoints disabled: {e}")

# Backtesting router (standalone - only requires yfinance)
try:
    from app.api.v1 import backtesting
    api_router.include_router(backtesting.router, tags=["backtesting"])
    logger.info("Backtesting endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Backtesting endpoints disabled: {e}")

# Affiliate broker integration (standalone - no dependencies)
try:
    from app.api.v1 import affiliate
    api_router.include_router(affiliate.router, tags=["affiliate"])
    logger.info("Affiliate broker endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Affiliate broker endpoints disabled: {e}")

# Portfolio Backtesting router (standalone - only requires yfinance + numpy/pandas)
try:
    from app.api.v1 import portfolio_backtesting
    api_router.include_router(portfolio_backtesting.router, tags=["portfolio-backtesting"])
    logger.info("Portfolio backtesting endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Portfolio backtesting endpoints disabled: {e}")

# Finnhub router (standalone - only requires aiohttp)
try:
    from app.api.v1 import finnhub
    api_router.include_router(finnhub.router, tags=["finnhub"])
    logger.info("Finnhub endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Finnhub endpoints disabled: {e}")

# ML-dependent features (optional)
try:
    from app.api.v1 import (
        patterns,
        analytics,
        signals,
        sentiment,
        portfolio,
        reports
    )
    api_router.include_router(patterns.router, prefix="/patterns", tags=["pattern-analysis"])
    api_router.include_router(analytics.router, prefix="/analytics", tags=["advanced-analytics"])
    api_router.include_router(signals.router, tags=["trading-signals"])
    api_router.include_router(sentiment.router, tags=["sentiment-analysis"])
    api_router.include_router(portfolio.router, tags=["portfolio-optimization"])
    api_router.include_router(reports.router, tags=["automated-reporting"])
    logger.info("ML-dependent features loaded successfully")
except ImportError as e:
    logger.warning(f"ML-dependent features disabled due to missing dependencies: {e}")

# Advanced Analytics (Task #14)
try:
    from app.api.v1 import advanced_analytics
    api_router.include_router(advanced_analytics.router, tags=["advanced-analytics-v2"])
    logger.info("Advanced analytics endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Advanced analytics endpoints disabled: {e}")

# Premium Features (Task #10)
try:
    from app.api.v1 import alerts, subscriptions, portfolios
    api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
    api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
    api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
    logger.info("Premium features endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Premium features endpoints disabled: {e}")

# Stock Prediction Features (2026-02-24)
# Provides ML predictions, technical indicators, pattern detection
# SECURED VERSION: Requires authentication and implements rate limiting
try:
    from app.api.v1 import prediction_secure
    api_router.include_router(prediction_secure.router, tags=["stock-prediction"])
    logger.info("Secured stock prediction endpoints loaded successfully")
except ImportError as e:
    logger.warning(f"Stock prediction endpoints disabled due to missing dependencies: {e}")
    logger.info("To enable: pip install yfinance alpha_vantage twelvedata finnhub-python pandas-ta")
    # Fallback to unsecured endpoints if secure version fails
    try:
        from app.api.v1 import prediction
        api_router.include_router(prediction.router, tags=["stock-prediction-legacy"])
        logger.warning("Using UNSECURED prediction endpoints (NOT RECOMMENDED)")
    except ImportError:
        pass
