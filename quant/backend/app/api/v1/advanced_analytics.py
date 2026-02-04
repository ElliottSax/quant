"""
Advanced Analytics API Endpoints

Comprehensive analytics endpoints including:
- Options analysis (gamma exposure, flow, unusual activity)
- Enhanced sentiment analysis (multi-source)
- Pattern recognition (clustering, timing, correlation)
- Predictive modeling
- Risk scoring

Author: Claude
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field, UUID4
from uuid import UUID
import asyncio

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.cache import cache_manager
from app.models.politician import Politician
from app.models.trade import Trade
from app.models.analytics import (
    OptionsAnalysisCache,
    SentimentAnalysisCache,
    PatternRecognitionResult,
    CorrelationAnalysisCache,
    PredictiveModelResult,
    RiskScoreCache
)

from app.services.options_analyzer import (
    get_options_analyzer,
    OptionsAnalysisResult,
    OptionsFlowSentiment
)
from app.services.enhanced_sentiment import (
    get_enhanced_sentiment_analyzer,
    AggregatedSentiment,
    SentimentSource
)
from app.services.pattern_recognizer import (
    get_pattern_recognizer,
    PatternRecognitionResult as PatternResult
)

logger = get_logger(__name__)
router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class OptionsGammaExposureResponse(BaseModel):
    """Gamma exposure analysis response"""
    ticker: str
    timestamp: datetime
    total_gamma: float
    net_gamma: float
    gamma_flip_price: Optional[float]
    market_stance: str
    key_strikes: List[tuple]
    explanation: str
    cached: bool = False


class OptionsFlowResponse(BaseModel):
    """Options flow analysis response"""
    ticker: str
    timestamp: datetime
    call_volume: int
    put_volume: int
    call_put_ratio: float
    net_premium_flow: float
    sentiment: str
    confidence: float
    notable_strikes: List[float]


class UnusualActivityResponse(BaseModel):
    """Unusual options activity response"""
    ticker: str
    timestamp: datetime
    activity_type: str
    description: str
    option_type: str
    strike: float
    expiration: date
    volume: int
    open_interest: int
    unusual_score: float


class CompleteOptionsAnalysisResponse(BaseModel):
    """Complete options analysis"""
    ticker: str
    timestamp: datetime
    gamma_exposure: Optional[OptionsGammaExposureResponse]
    options_flow: Optional[OptionsFlowResponse]
    unusual_activities: List[UnusualActivityResponse]
    overall_sentiment: str
    confidence: float
    summary: str


class SentimentAnalysisResponse(BaseModel):
    """Sentiment analysis response"""
    entity_id: Optional[str]
    entity_name: Optional[str]
    entity_type: str  # "politician" or "ticker"
    timestamp: datetime
    overall_score: float
    overall_category: str
    confidence: float
    source_breakdown: Dict[str, float]
    items_analyzed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    trend_24h: Optional[float]
    summary: str
    cached: bool = False


class PatternClusterResponse(BaseModel):
    """Trading cluster response"""
    cluster_id: int
    politicians: List[str]
    politician_ids: List[str]
    avg_correlation: float
    trade_overlap: float
    common_tickers: List[str]
    cluster_size: int
    confidence: float
    description: str


class CorrelatedTradingResponse(BaseModel):
    """Correlated trading pattern"""
    politician_ids: List[str]
    politician_names: List[str]
    correlation_score: float
    common_trades: int
    time_window_days: int
    common_tickers: List[str]
    pattern_strength: str
    statistical_significance: float


class PatternRecognitionResponse(BaseModel):
    """Pattern recognition response"""
    timestamp: datetime
    clusters: List[PatternClusterResponse]
    correlated_patterns: List[CorrelatedTradingResponse]
    total_patterns_detected: int
    summary: str


class PoliticianCorrelationMatrixResponse(BaseModel):
    """Correlation matrix for politicians"""
    timestamp: datetime
    lookback_days: int
    matrix: Dict[str, Dict[str, float]]  # politician_id -> {politician_id -> correlation}
    top_correlations: List[Dict[str, Any]]
    summary: str


class PredictionResponse(BaseModel):
    """Prediction response"""
    politician_id: str
    politician_name: str
    model_name: str
    prediction_type: str
    predicted_value: float
    confidence: float
    forecast_days: Optional[int]
    explanation: str
    timestamp: datetime


class RiskScoreResponse(BaseModel):
    """Risk score response"""
    politician_id: str
    politician_name: str
    overall_risk_score: float
    volatility_score: float
    consistency_score: float
    timing_risk_score: float
    risk_category: str
    risk_factors: Dict[str, Any]
    explanation: str
    timestamp: datetime


# ============================================================================
# Options Analysis Endpoints
# ============================================================================

@router.post(
    "/analytics/options/gamma-exposure",
    response_model=OptionsGammaExposureResponse,
    summary="Calculate Gamma Exposure (GEX)",
    description="Analyze gamma exposure for a ticker to understand market maker positioning"
)
async def calculate_gamma_exposure(
    ticker: str = Query(..., description="Stock ticker symbol"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate Gamma Exposure (GEX) for a ticker

    GEX represents the total gamma exposure that market makers have,
    which influences price movement and volatility.
    """
    logger.info(f"Calculating gamma exposure for {ticker}")

    # Check cache first
    cache_query = (
        select(OptionsAnalysisCache)
        .where(
            and_(
                OptionsAnalysisCache.ticker == ticker,
                OptionsAnalysisCache.analysis_date >= datetime.now() - timedelta(minutes=30)
            )
        )
        .order_by(desc(OptionsAnalysisCache.analysis_date))
        .limit(1)
    )

    result = await db.execute(cache_query)
    cached = result.scalar_one_or_none()

    if cached and cached.total_gamma is not None:
        logger.info(f"Using cached gamma exposure for {ticker}")
        return OptionsGammaExposureResponse(
            ticker=ticker,
            timestamp=cached.analysis_date,
            total_gamma=cached.total_gamma,
            net_gamma=cached.net_gamma or 0.0,
            gamma_flip_price=cached.gamma_flip_price,
            market_stance=cached.market_stance or "neutral",
            key_strikes=[],  # Simplified
            explanation=cached.full_analysis.get("gamma_exposure", {}).get("explanation", "") if cached.full_analysis else "",
            cached=True
        )

    # Analyze
    analyzer = get_options_analyzer()
    analysis = await analyzer.analyze_symbol(ticker, include_flow=False, include_unusual=False)

    # Store in cache
    cache_entry = OptionsAnalysisCache(
        ticker=ticker,
        analysis_date=datetime.now(),
        total_gamma=analysis.gamma_exposure.total_gamma if analysis.gamma_exposure else None,
        net_gamma=analysis.gamma_exposure.net_gamma if analysis.gamma_exposure else None,
        gamma_flip_price=analysis.gamma_exposure.gamma_flip_price if analysis.gamma_exposure else None,
        market_stance=analysis.gamma_exposure.market_stance if analysis.gamma_exposure else None,
        overall_sentiment=analysis.overall_sentiment.value,
        confidence=analysis.confidence,
        full_analysis=analysis.dict()
    )

    db.add(cache_entry)
    await db.commit()

    if not analysis.gamma_exposure:
        raise HTTPException(status_code=404, detail=f"No gamma exposure data available for {ticker}")

    return OptionsGammaExposureResponse(
        ticker=ticker,
        timestamp=analysis.timestamp,
        total_gamma=analysis.gamma_exposure.total_gamma,
        net_gamma=analysis.gamma_exposure.net_gamma,
        gamma_flip_price=analysis.gamma_exposure.gamma_flip_price,
        market_stance=analysis.gamma_exposure.market_stance,
        key_strikes=analysis.gamma_exposure.key_gamma_strikes,
        explanation=analysis.gamma_exposure.explanation,
        cached=False
    )


@router.get(
    "/analytics/options/{ticker}",
    response_model=CompleteOptionsAnalysisResponse,
    summary="Complete Options Analysis",
    description="Comprehensive options analysis including GEX, flow, and unusual activity"
)
async def analyze_options(
    ticker: str = Path(..., description="Stock ticker symbol"),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete options analysis for a ticker

    Includes:
    - Gamma exposure (GEX)
    - Options flow (calls vs puts)
    - Unusual activity detection
    """
    logger.info(f"Complete options analysis for {ticker}")

    analyzer = get_options_analyzer()
    analysis = await analyzer.analyze_symbol(ticker)

    # Convert to response
    gamma_exp = None
    if analysis.gamma_exposure:
        gamma_exp = OptionsGammaExposureResponse(
            ticker=ticker,
            timestamp=analysis.timestamp,
            total_gamma=analysis.gamma_exposure.total_gamma,
            net_gamma=analysis.gamma_exposure.net_gamma,
            gamma_flip_price=analysis.gamma_exposure.gamma_flip_price,
            market_stance=analysis.gamma_exposure.market_stance,
            key_strikes=analysis.gamma_exposure.key_gamma_strikes,
            explanation=analysis.gamma_exposure.explanation
        )

    flow = None
    if analysis.options_flow:
        flow = OptionsFlowResponse(
            ticker=ticker,
            timestamp=analysis.timestamp,
            call_volume=analysis.options_flow.total_call_volume,
            put_volume=analysis.options_flow.total_put_volume,
            call_put_ratio=analysis.options_flow.call_put_ratio,
            net_premium_flow=analysis.options_flow.net_premium_flow,
            sentiment=analysis.options_flow.sentiment.value,
            confidence=analysis.options_flow.confidence,
            notable_strikes=analysis.options_flow.notable_strikes
        )

    unusual = [
        UnusualActivityResponse(
            ticker=ticker,
            timestamp=u.timestamp,
            activity_type=u.activity_type.value,
            description=u.description,
            option_type=u.option_type.value,
            strike=u.strike,
            expiration=u.expiration,
            volume=u.volume,
            open_interest=u.open_interest,
            unusual_score=u.unusual_score
        )
        for u in analysis.unusual_activities
    ]

    # Store in cache
    cache_entry = OptionsAnalysisCache(
        ticker=ticker,
        analysis_date=datetime.now(),
        total_gamma=analysis.gamma_exposure.total_gamma if analysis.gamma_exposure else None,
        net_gamma=analysis.gamma_exposure.net_gamma if analysis.gamma_exposure else None,
        gamma_flip_price=analysis.gamma_exposure.gamma_flip_price if analysis.gamma_exposure else None,
        market_stance=analysis.gamma_exposure.market_stance if analysis.gamma_exposure else None,
        call_volume=analysis.options_flow.total_call_volume if analysis.options_flow else None,
        put_volume=analysis.options_flow.total_put_volume if analysis.options_flow else None,
        call_put_ratio=analysis.options_flow.call_put_ratio if analysis.options_flow else None,
        net_premium_flow=analysis.options_flow.net_premium_flow if analysis.options_flow else None,
        flow_sentiment=analysis.options_flow.sentiment.value if analysis.options_flow else None,
        overall_sentiment=analysis.overall_sentiment.value,
        confidence=analysis.confidence,
        full_analysis=analysis.dict()
    )

    db.add(cache_entry)
    await db.commit()

    return CompleteOptionsAnalysisResponse(
        ticker=ticker,
        timestamp=analysis.timestamp,
        gamma_exposure=gamma_exp,
        options_flow=flow,
        unusual_activities=unusual,
        overall_sentiment=analysis.overall_sentiment.value,
        confidence=analysis.confidence,
        summary=analysis.summary
    )


# ============================================================================
# Sentiment Analysis Endpoints
# ============================================================================

@router.get(
    "/analytics/sentiment/politician/{politician_id}",
    response_model=SentimentAnalysisResponse,
    summary="Politician Sentiment Analysis",
    description="Multi-source sentiment analysis for a politician"
)
async def analyze_politician_sentiment(
    politician_id: UUID4 = Path(..., description="Politician UUID"),
    lookback_days: int = Query(7, ge=1, le=30, description="Days to look back"),
    sources: Optional[List[str]] = Query(None, description="Specific sources to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment for a politician from multiple sources

    Sources:
    - NewsAPI
    - GDELT
    - Social media (if configured)
    - Congressional records
    """
    logger.info(f"Analyzing sentiment for politician {politician_id}")

    # Get politician
    pol_query = select(Politician).where(Politician.id == politician_id)
    result = await db.execute(pol_query)
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    # Check cache
    cache_query = (
        select(SentimentAnalysisCache)
        .where(
            and_(
                SentimentAnalysisCache.politician_id == politician_id,
                SentimentAnalysisCache.analysis_date >= datetime.now() - timedelta(hours=1)
            )
        )
        .order_by(desc(SentimentAnalysisCache.analysis_date))
        .limit(1)
    )

    cache_result = await db.execute(cache_query)
    cached = cache_result.scalar_one_or_none()

    if cached:
        logger.info(f"Using cached sentiment for {politician.name}")
        return SentimentAnalysisResponse(
            entity_id=str(politician_id),
            entity_name=politician.name,
            entity_type="politician",
            timestamp=cached.analysis_date,
            overall_score=cached.overall_score,
            overall_category=cached.overall_category,
            confidence=cached.confidence,
            source_breakdown=cached.source_breakdown,
            items_analyzed=cached.items_analyzed,
            positive_count=cached.positive_count,
            negative_count=cached.negative_count,
            neutral_count=cached.neutral_count,
            trend_24h=cached.trend_24h,
            summary=cached.full_analysis.get("summary", "") if cached.full_analysis else "",
            cached=True
        )

    # Analyze
    analyzer = get_enhanced_sentiment_analyzer()

    source_list = None
    if sources:
        source_list = [SentimentSource(s) for s in sources]

    sentiment = await analyzer.analyze_politician(
        politician_id=str(politician_id),
        politician_name=politician.name,
        lookback_days=lookback_days,
        sources=source_list
    )

    # Store in cache
    cache_entry = SentimentAnalysisCache(
        politician_id=politician_id,
        analysis_date=datetime.now(),
        overall_score=sentiment.overall_score,
        overall_category=sentiment.overall_category.value,
        confidence=sentiment.confidence,
        items_analyzed=sentiment.items_analyzed,
        positive_count=sentiment.positive_count,
        negative_count=sentiment.negative_count,
        neutral_count=sentiment.neutral_count,
        source_breakdown=sentiment.source_breakdown,
        trend_24h=sentiment.trend_24h,
        full_analysis=sentiment.dict()
    )

    db.add(cache_entry)
    await db.commit()

    return SentimentAnalysisResponse(
        entity_id=str(politician_id),
        entity_name=politician.name,
        entity_type="politician",
        timestamp=sentiment.timestamp,
        overall_score=sentiment.overall_score,
        overall_category=sentiment.overall_category.value,
        confidence=sentiment.confidence,
        source_breakdown=sentiment.source_breakdown,
        items_analyzed=sentiment.items_analyzed,
        positive_count=sentiment.positive_count,
        negative_count=sentiment.negative_count,
        neutral_count=sentiment.neutral_count,
        trend_24h=sentiment.trend_24h,
        summary=sentiment.summary,
        cached=False
    )


@router.get(
    "/analytics/sentiment/ticker/{ticker}",
    response_model=SentimentAnalysisResponse,
    summary="Ticker Sentiment Analysis",
    description="Multi-source sentiment analysis for a stock ticker"
)
async def analyze_ticker_sentiment(
    ticker: str = Path(..., description="Stock ticker symbol"),
    lookback_days: int = Query(7, ge=1, le=30, description="Days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment for a stock ticker from multiple sources
    """
    logger.info(f"Analyzing sentiment for ticker {ticker}")

    # Analyze
    analyzer = get_enhanced_sentiment_analyzer()
    sentiment = await analyzer.analyze_ticker(
        ticker=ticker,
        lookback_days=lookback_days
    )

    # Store in cache
    cache_entry = SentimentAnalysisCache(
        ticker=ticker,
        analysis_date=datetime.now(),
        overall_score=sentiment.overall_score,
        overall_category=sentiment.overall_category.value,
        confidence=sentiment.confidence,
        items_analyzed=sentiment.items_analyzed,
        positive_count=sentiment.positive_count,
        negative_count=sentiment.negative_count,
        neutral_count=sentiment.neutral_count,
        source_breakdown=sentiment.source_breakdown,
        trend_24h=sentiment.trend_24h,
        full_analysis=sentiment.dict()
    )

    db.add(cache_entry)
    await db.commit()

    return SentimentAnalysisResponse(
        entity_id=ticker,
        entity_name=ticker,
        entity_type="ticker",
        timestamp=sentiment.timestamp,
        overall_score=sentiment.overall_score,
        overall_category=sentiment.overall_category.value,
        confidence=sentiment.confidence,
        source_breakdown=sentiment.source_breakdown,
        items_analyzed=sentiment.items_analyzed,
        positive_count=sentiment.positive_count,
        negative_count=sentiment.negative_count,
        neutral_count=sentiment.neutral_count,
        trend_24h=sentiment.trend_24h,
        summary=sentiment.summary,
        cached=False
    )


# ============================================================================
# Pattern Recognition Endpoints
# ============================================================================

@router.get(
    "/analytics/patterns",
    response_model=PatternRecognitionResponse,
    summary="Pattern Recognition Analysis",
    description="Detect trading patterns, clusters, and correlations"
)
async def analyze_patterns(
    lookback_days: int = Query(90, ge=30, le=365, description="Days to analyze"),
    min_cluster_size: int = Query(3, ge=2, le=10, description="Minimum cluster size"),
    min_correlation: float = Query(0.6, ge=0.3, le=1.0, description="Minimum correlation"),
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive pattern recognition analysis

    Detects:
    - Trading clusters (politicians who trade similarly)
    - Correlated trading patterns
    - Timing patterns
    - Sector rotations
    """
    logger.info("Running pattern recognition analysis")

    recognizer = get_pattern_recognizer()
    patterns = await recognizer.analyze_patterns(
        db=db,
        lookback_days=lookback_days,
        min_cluster_size=min_cluster_size,
        min_correlation=min_correlation
    )

    # Convert to response
    clusters = [
        PatternClusterResponse(
            cluster_id=c.cluster_id,
            politicians=c.politicians,
            politician_ids=c.politician_ids,
            avg_correlation=c.avg_correlation,
            trade_overlap=c.trade_overlap,
            common_tickers=c.common_tickers,
            cluster_size=c.cluster_size,
            confidence=c.confidence,
            description=c.description
        )
        for c in patterns.clusters
    ]

    correlated = [
        CorrelatedTradingResponse(
            politician_ids=p.politician_ids,
            politician_names=p.politician_names,
            correlation_score=p.correlation_score,
            common_trades=p.common_trades,
            time_window_days=p.time_window_days,
            common_tickers=p.common_tickers,
            pattern_strength=p.pattern_strength,
            statistical_significance=p.statistical_significance
        )
        for p in patterns.correlated_patterns
    ]

    return PatternRecognitionResponse(
        timestamp=patterns.timestamp,
        clusters=clusters,
        correlated_patterns=correlated,
        total_patterns_detected=len(clusters) + len(correlated),
        summary=patterns.summary
    )


@router.get(
    "/analytics/correlations/politicians",
    response_model=PoliticianCorrelationMatrixResponse,
    summary="Politician Correlation Matrix",
    description="Cross-politician correlation analysis"
)
async def politician_correlation_matrix(
    lookback_days: int = Query(90, ge=30, le=365, description="Days to analyze"),
    min_trades: int = Query(5, ge=1, le=20, description="Minimum trades required"),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate correlation matrix between politicians

    Shows which politicians tend to make similar trades
    """
    logger.info("Calculating politician correlation matrix")

    # This is a simplified placeholder
    # Real implementation would calculate pairwise correlations

    return PoliticianCorrelationMatrixResponse(
        timestamp=datetime.now(),
        lookback_days=lookback_days,
        matrix={},
        top_correlations=[],
        summary="Correlation matrix calculation - implementation pending"
    )


# ============================================================================
# Export router
# ============================================================================

__all__ = ["router"]
