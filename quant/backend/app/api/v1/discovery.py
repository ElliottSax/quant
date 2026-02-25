"""
Discovery Integration API Endpoints

Exposes data from the discovery project through quant's API.
Provides predictions, analysis, and alerts from ML trading analysis.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.discovery_integration import discovery_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class SignalDetail(BaseModel):
    """Individual signal detail."""
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


class MLScores(BaseModel):
    """ML model scores."""
    logistic: Optional[int] = None
    random_forest: Optional[int] = None
    gradient_boost: Optional[int] = None


class PredictionSignals(BaseModel):
    """All signals for a prediction."""
    cyclical: Optional[dict] = None
    regime: Optional[dict] = None
    pattern: Optional[dict] = None
    motif: Optional[dict] = None
    ml: Optional[dict] = None


class StockPrediction(BaseModel):
    """Stock prediction from discovery ML models."""
    ticker: str
    prediction: str
    confidence: float
    signals: Optional[PredictionSignals] = None
    patterns_found: Optional[List[str]] = None
    regime: Optional[str] = None
    cycle_info: Optional[dict] = None
    ml_scores: Optional[dict] = None
    timestamp: Optional[str] = None
    source: Optional[str] = "discovery"


class CycleAnalysis(BaseModel):
    """24x7 cycle analysis result."""
    summary: dict
    results: List[dict]
    filename: Optional[str] = None
    timestamp: Optional[str] = None


class DiscoverySummary(BaseModel):
    """Summary of available discovery data."""
    available: bool
    predictions_count: int
    top_predictions: List[dict]
    latest_analysis_timestamp: Optional[str] = None
    data_path: str


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/status",
    response_model=DiscoverySummary,
    summary="Get discovery integration status"
)
async def get_discovery_status():
    """
    Check if discovery data is available and get summary.

    Returns:
        Summary of available predictions and analysis data.
    """
    summary = discovery_service.get_summary()
    return DiscoverySummary(**summary)


@router.get(
    "/predictions",
    response_model=List[StockPrediction],
    summary="Get ML stock predictions"
)
async def get_predictions(
    limit: int = Query(20, ge=1, le=100, description="Max predictions to return"),
    min_confidence: float = Query(0.0, ge=0, le=1, description="Minimum confidence"),
    prediction_type: Optional[str] = Query(None, pattern="^(UP|DOWN)$", description="Filter by UP/DOWN")
):
    """
    Get ML predictions from discovery analysis.

    Predictions are based on:
    - Cyclical patterns in politician trading
    - Regime detection (activity levels)
    - DTW pattern matching
    - Ensemble ML models (logistic, random forest, gradient boost)

    Returns:
        List of stock predictions with confidence scores and signals.
    """
    predictions = discovery_service.get_latest_predictions()

    if not predictions:
        logger.warning("No predictions available from discovery")
        return []

    # Filter by confidence
    predictions = [p for p in predictions if p.get('confidence', 0) >= min_confidence]

    # Filter by prediction type
    if prediction_type:
        predictions = [p for p in predictions if p.get('prediction') == prediction_type]

    # Sort by confidence
    predictions.sort(key=lambda x: x.get('confidence', 0), reverse=True)

    return [StockPrediction(**p) for p in predictions[:limit]]


@router.get(
    "/predictions/multi-horizon",
    summary="Get multi-horizon predictions"
)
async def get_multi_horizon_predictions():
    """
    Get predictions across multiple time horizons (7d, 14d, 30d).
    """
    predictions = discovery_service.get_multi_horizon_predictions()

    if not predictions:
        return {"message": "Multi-horizon predictions not available", "data": {}}

    return {"data": predictions}


@router.get(
    "/predictions/{ticker}",
    response_model=StockPrediction,
    summary="Get prediction for a specific stock"
)
async def get_stock_prediction(ticker: str):
    """
    Get ML prediction for a specific stock ticker.

    Returns detailed signals including:
    - Cyclical analysis (trade cycles, seasonality)
    - Regime analysis (activity levels)
    - Pattern matching results
    - ML model predictions
    """
    prediction = discovery_service.get_stock_prediction(ticker)

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction found for ticker {ticker.upper()}"
        )

    return StockPrediction(**prediction)


@router.get(
    "/analysis/cycles",
    response_model=List[CycleAnalysis],
    summary="Get 24x7 cycle analysis"
)
async def get_cycle_analysis(
    limit: int = Query(10, ge=1, le=50, description="Max analyses to return")
):
    """
    Get recent 24x7 cycle analysis results.

    Each analysis includes:
    - Sentiment breakdown (positive/negative/neutral)
    - Volume statistics
    - Pattern detection results
    - Worker processing summary
    """
    analyses = discovery_service.get_cycle_analysis(limit=limit)

    if not analyses:
        return []

    return [CycleAnalysis(**a) for a in analyses]


@router.get(
    "/analytics",
    summary="Get pipeline analytics"
)
async def get_pipeline_analytics():
    """
    Get aggregated analytics from discovery pipeline.

    Includes:
    - Top traded stocks
    - Sector distribution
    - Most active politicians
    - Transaction type distribution
    """
    analytics = discovery_service.get_pipeline_analytics()

    return {
        "analytics": analytics,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/trades",
    summary="Get recent trades from discovery"
)
async def get_discovery_trades(
    limit: int = Query(50, ge=1, le=200, description="Max trades to return"),
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    politician: Optional[str] = Query(None, description="Filter by politician name")
):
    """
    Get recent politician trades from discovery pipeline.
    """
    trades = discovery_service.get_pipeline_trades(limit=limit * 2)  # Get extra for filtering

    if ticker:
        trades = [t for t in trades if t.get('ticker', '').upper() == ticker.upper()]

    if politician:
        trades = [
            t for t in trades
            if politician.lower() in t.get('politician_name', '').lower()
        ]

    return {
        "trades": trades[:limit],
        "count": len(trades[:limit]),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/alerts",
    summary="Get recent alerts"
)
async def get_discovery_alerts(
    limit: int = Query(20, ge=1, le=100, description="Max alerts to return")
):
    """
    Get recent trading alerts from discovery.

    Alert types include:
    - Large transactions (>$500K, >$1M)
    - Politician activity
    - Ticker alerts for popular stocks
    """
    alerts = discovery_service.get_alerts(limit=limit)

    return {
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": datetime.utcnow().isoformat()
    }
