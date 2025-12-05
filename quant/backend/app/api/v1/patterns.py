"""
Pattern Analysis API Endpoints

Research endpoints for exploring cyclical patterns in politician trading data.
Provides access to Fourier analysis, HMM regime detection, and DTW pattern matching.

**RESEARCH USE ONLY**: This API is for academic research and transparency.
Not for trading signals or financial advice.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from enum import Enum

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade

logger = get_logger(__name__)
router = APIRouter()

# Import cyclical models (optional - gracefully degrade if ML libs unavailable)
try:
    from app.ml.cyclical import (
        FourierCyclicalDetector,
        RegimeDetector,
        DynamicTimeWarpingMatcher,
        CyclicalExperimentTracker
    )
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML libraries not available: {e}. Pattern analysis endpoints will be disabled.")
    ML_AVAILABLE = False
    FourierCyclicalDetector = None
    RegimeDetector = None
    DynamicTimeWarpingMatcher = None
    CyclicalExperimentTracker = None


# ============================================================================
# Response Models
# ============================================================================

class CycleInfo(BaseModel):
    """Information about a detected cycle"""
    period_days: float = Field(..., description="Cycle period in days")
    strength: float = Field(..., description="FFT power spectrum strength")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    category: str = Field(..., description="Cycle category (weekly, monthly, etc.)")
    frequency: float = Field(..., description="Cycle frequency")


class FourierAnalysisResponse(BaseModel):
    """Response from Fourier cycle detection"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    total_trades: int
    date_range_start: date
    date_range_end: date
    dominant_cycles: List[CycleInfo]
    total_cycles_found: int
    forecast_30d: Optional[List[float]] = Field(None, description="30-day forecast")
    summary: str = Field(..., description="Human-readable summary")


class RegimeInfo(BaseModel):
    """Information about a trading regime"""
    regime_id: int
    name: str
    avg_return: float
    volatility: float
    frequency: float = Field(..., description="% of time in this regime")
    sample_size: int


class RegimeAnalysisResponse(BaseModel):
    """Response from HMM regime detection"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    current_regime: int
    current_regime_name: str
    regime_confidence: float = Field(..., ge=0, le=1)
    expected_duration_days: float
    regimes: List[RegimeInfo]
    transition_probabilities: Dict[str, float] = Field(
        ..., description="Probabilities of transitioning to other regimes"
    )
    summary: str


class PatternMatch(BaseModel):
    """A similar historical pattern"""
    match_date: str
    similarity_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    outcome_30d_trades: Optional[float] = None
    outcome_90d_trades: Optional[float] = None


class DTWAnalysisResponse(BaseModel):
    """Response from DTW pattern matching"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    current_pattern_days: int
    matches_found: int
    top_matches: List[PatternMatch]
    prediction_30d: float = Field(..., description="Predicted trade change in 30 days")
    prediction_confidence: float = Field(..., ge=0, le=1)
    summary: str


class ComprehensiveAnalysisResponse(BaseModel):
    """Combined analysis from all three models"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    fourier: FourierAnalysisResponse
    hmm: RegimeAnalysisResponse
    dtw: DTWAnalysisResponse
    key_insights: List[str] = Field(..., description="Top 3-5 actionable insights")


class AnalysisType(str, Enum):
    """Type of pattern analysis"""
    fourier = "fourier"
    hmm = "hmm"
    dtw = "dtw"
    comprehensive = "comprehensive"


# ============================================================================
# Helper Functions
# ============================================================================

async def load_politician_trades(
    db: AsyncSession,
    politician_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> pd.DataFrame:
    """Load trades for a politician into a pandas DataFrame"""

    # Build query
    query = (
        select(Trade, Politician)
        .join(Politician, Trade.politician_id == Politician.id)
        .where(Trade.politician_id == politician_id)
    )

    if start_date:
        query = query.where(Trade.transaction_date >= start_date)
    if end_date:
        query = query.where(Trade.transaction_date <= end_date)

    query = query.order_by(Trade.transaction_date)

    # Execute
    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return pd.DataFrame()

    # Convert to DataFrame
    data = []
    for trade, politician in rows:
        data.append({
            'transaction_date': trade.transaction_date,
            'ticker': trade.ticker,
            'transaction_type': trade.transaction_type,
            'amount': (trade.amount_min + trade.amount_max) / 2 if trade.amount_min and trade.amount_max else None,
            'politician_name': politician.name
        })

    df = pd.DataFrame(data)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    return df


def prepare_time_series(df: pd.DataFrame, freq: str = 'D') -> pd.Series:
    """Convert trades DataFrame to time series"""

    if df.empty:
        return pd.Series(dtype=float)

    # Create daily trade frequency
    trade_freq = df.groupby('transaction_date').size()

    # Create full date range
    date_range = pd.date_range(
        start=df['transaction_date'].min(),
        end=df['transaction_date'].max(),
        freq=freq
    )

    # Reindex to include all dates
    ts = trade_freq.reindex(date_range, fill_value=0)

    return ts


# ============================================================================
# Endpoints
# ============================================================================

@router.get(
    "/politicians",
    summary="List all politicians with available data",
    description="Get list of politicians who have trades available for pattern analysis"
)
async def list_politicians_with_data(
    db: AsyncSession = Depends(get_db),
    min_trades: int = Query(10, description="Minimum number of trades required")
) -> List[Dict[str, Any]]:
    """List politicians with sufficient data for analysis"""

    query = (
        select(
            Politician.id,
            Politician.name,
            Politician.party,
            Politician.state,
            Politician.chamber,
            func.count(Trade.id).label('trade_count'),
            func.min(Trade.transaction_date).label('first_trade'),
            func.max(Trade.transaction_date).label('last_trade')
        )
        .join(Trade, Trade.politician_id == Politician.id)
        .group_by(Politician.id, Politician.name, Politician.party, Politician.state, Politician.chamber)
        .having(func.count(Trade.id) >= min_trades)
        .order_by(func.count(Trade.id).desc())
    )

    result = await db.execute(query)
    rows = result.all()

    politicians = []
    for row in rows:
        politicians.append({
            'id': str(row.id),
            'name': row.name,
            'party': row.party,
            'state': row.state,
            'chamber': row.chamber,
            'trade_count': row.trade_count,
            'first_trade': row.first_trade.isoformat(),
            'last_trade': row.last_trade.isoformat(),
            'days_active': (row.last_trade - row.first_trade).days,
            'suitable_for_analysis': {
                'fourier': row.trade_count >= 30,
                'hmm': row.trade_count >= 100,
                'dtw': row.trade_count >= 90
            }
        })

    return politicians


@router.get(
    "/analyze/{politician_id}/fourier",
    response_model=FourierAnalysisResponse,
    summary="Fourier cycle analysis",
    description="Detect periodic trading cycles using Fourier Transform. Identifies weekly, monthly, quarterly, and annual patterns."
)
async def analyze_fourier(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db),
    min_strength: float = Query(0.05, ge=0, le=1, description="Minimum cycle strength"),
    min_confidence: float = Query(0.6, ge=0, le=1, description="Minimum confidence threshold"),
    include_forecast: bool = Query(True, description="Include 30-day forecast")
) -> FourierAnalysisResponse:
    """
    Run Fourier analysis to detect cyclical trading patterns.

    This endpoint uses Fast Fourier Transform (FFT) to identify dominant periodic patterns
    in a politician's trading history. Useful for detecting systematic trading behaviors.

    **Research Applications**:
    - Detect regular trading schedules
    - Identify potential insider trading windows
    - Compare cycles across politicians
    - Study correlation with market events

    **Example**: "Does Nancy Pelosi trade on a monthly cycle aligned with earnings seasons?"
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML libraries not available. Pattern analysis is currently disabled."
        )

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")

    # Load trades
    trades_df = await load_politician_trades(db, politician_id)

    if trades_df.empty or len(trades_df) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for Fourier analysis. Found {len(trades_df)} trades, need at least 30."
        )

    # Prepare time series
    trade_frequency = prepare_time_series(trades_df)

    # Run Fourier analysis
    try:
        detector = FourierCyclicalDetector(
            min_strength=min_strength,
            min_confidence=min_confidence
        )
        result = detector.detect_cycles(
            trade_frequency,
            sampling_rate='daily',
            return_details=include_forecast
        )

        # Build response
        cycles = [CycleInfo(**cycle) for cycle in result['dominant_cycles']]

        forecast = None
        if include_forecast and 'cycle_forecast' in result:
            forecast = result['cycle_forecast']['forecast']

        response = FourierAnalysisResponse(
            politician_id=str(politician.id),
            politician_name=politician.name,
            analysis_date=datetime.utcnow(),
            total_trades=len(trades_df),
            date_range_start=trades_df['transaction_date'].min().date(),
            date_range_end=trades_df['transaction_date'].max().date(),
            dominant_cycles=cycles,
            total_cycles_found=result['total_cycles_found'],
            forecast_30d=forecast,
            summary=detector.get_cycle_summary()
        )

        logger.info(f"Fourier analysis completed for {politician.name}: {result['total_cycles_found']} cycles found")

        return response

    except Exception as e:
        logger.error(f"Fourier analysis failed for {politician_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/analyze/{politician_id}/regime",
    response_model=RegimeAnalysisResponse,
    summary="HMM regime detection",
    description="Identify distinct trading regimes (bull, bear, volatile, calm) using Hidden Markov Models"
)
async def analyze_regime(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db),
    n_states: int = Query(4, ge=2, le=6, description="Number of hidden states/regimes")
) -> RegimeAnalysisResponse:
    """
    Run HMM regime detection to classify trading behavior into distinct states.

    Uses Hidden Markov Models to identify periods of different trading behavior.
    For example: aggressive buying vs defensive selling vs holding periods.

    **Research Applications**:
    - Identify shifts in trading strategy
    - Correlate regime changes with market events
    - Predict upcoming regime transitions
    - Study behavioral patterns

    **Example**: "When does Dan Crenshaw switch from buying to selling?"
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML libraries not available. Pattern analysis is currently disabled."
        )

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")

    # Load trades
    trades_df = await load_politician_trades(db, politician_id)

    if trades_df.empty or len(trades_df) < 100:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for HMM analysis. Found {len(trades_df)} trades, need at least 100."
        )

    # Prepare time series
    trade_frequency = prepare_time_series(trades_df)
    returns = trade_frequency.diff().fillna(0)

    # Run HMM analysis
    try:
        detector = RegimeDetector(n_states=n_states)
        result = detector.fit_and_predict(returns)

        # Build response
        regimes = [
            RegimeInfo(
                regime_id=int(state),
                name=chars['name'],
                avg_return=chars['avg_return'],
                volatility=chars['volatility'],
                frequency=chars['frequency'],
                sample_size=chars['sample_size']
            )
            for state, chars in result['regime_characteristics'].items()
        ]

        # Get transition probabilities for current regime
        transitions = detector.get_regime_transition_probabilities(result['current_regime'])

        response = RegimeAnalysisResponse(
            politician_id=str(politician.id),
            politician_name=politician.name,
            analysis_date=datetime.utcnow(),
            current_regime=result['current_regime'],
            current_regime_name=result['current_regime_name'],
            regime_confidence=float(result['regime_probabilities'][result['current_regime']]),
            expected_duration_days=float(result['expected_duration'][result['current_regime']]),
            regimes=regimes,
            transition_probabilities=transitions,
            summary=detector.get_regime_summary(result)
        )

        logger.info(f"HMM analysis completed for {politician.name}: current regime is {result['current_regime_name']}")

        return response

    except Exception as e:
        logger.error(f"HMM analysis failed for {politician_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/analyze/{politician_id}/patterns",
    response_model=DTWAnalysisResponse,
    summary="DTW pattern matching",
    description="Find similar historical trading patterns using Dynamic Time Warping"
)
async def analyze_patterns(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db),
    window_size: int = Query(30, ge=7, le=90, description="Pattern window size in days"),
    top_k: int = Query(5, ge=1, le=20, description="Number of top matches to return"),
    similarity_threshold: float = Query(0.6, ge=0, le=1, description="Minimum similarity threshold")
) -> DTWAnalysisResponse:
    """
    Find historical patterns similar to current trading behavior using DTW.

    Dynamic Time Warping finds periods in history when the politician traded similarly
    to their recent behavior, then shows what happened next.

    **Research Applications**:
    - Predict future trading based on historical patterns
    - Identify recurring behaviors
    - Detect anomalous periods (no historical matches)
    - Study pattern evolution over time

    **Example**: "Has Paul Pelosi's current trading pattern happened before? What followed?"
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML libraries not available. Pattern analysis is currently disabled."
        )

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail=f"Politician {politician_id} not found")

    # Load trades
    trades_df = await load_politician_trades(db, politician_id)

    if trades_df.empty or len(trades_df) < window_size + 90:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for DTW analysis. Need at least {window_size + 90} trades."
        )

    # Prepare time series
    trade_frequency = prepare_time_series(trades_df)

    # Run DTW analysis
    try:
        matcher = DynamicTimeWarpingMatcher(similarity_threshold=similarity_threshold)

        matches = matcher.find_similar_patterns(
            current_pattern=trade_frequency,
            historical_data=trade_frequency,
            window_size=window_size,
            top_k=top_k
        )

        prediction = matcher.predict_from_matches(matches, horizon=30)

        # Build response
        pattern_matches = [
            PatternMatch(
                match_date=str(match['match_date'])[:10],
                similarity_score=match['similarity_score'],
                confidence=match['confidence'],
                outcome_30d_trades=match.get('outcome_30d', {}).get('total_return'),
                outcome_90d_trades=match.get('outcome_90d', {}).get('total_return')
            )
            for match in matches
        ]

        response = DTWAnalysisResponse(
            politician_id=str(politician.id),
            politician_name=politician.name,
            analysis_date=datetime.utcnow(),
            current_pattern_days=window_size,
            matches_found=len(matches),
            top_matches=pattern_matches,
            prediction_30d=prediction['predicted_return'],
            prediction_confidence=prediction['confidence'],
            summary=matcher.get_pattern_summary(matches, horizon=30)
        )

        logger.info(f"DTW analysis completed for {politician.name}: {len(matches)} patterns found")

        return response

    except Exception as e:
        logger.error(f"DTW analysis failed for {politician_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/analyze/{politician_id}/comprehensive",
    response_model=ComprehensiveAnalysisResponse,
    summary="Run all pattern analyses",
    description="Execute Fourier, HMM, and DTW analyses simultaneously for complete insight"
)
async def analyze_comprehensive(
    politician_id: str = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db)
) -> ComprehensiveAnalysisResponse:
    """
    Run all three analysis models and provide integrated insights.

    Combines Fourier cycle detection, HMM regime classification, and DTW pattern
    matching to provide a comprehensive view of trading behavior.

    **Research Applications**:
    - Complete behavioral profile
    - Cross-validate findings across models
    - Generate multi-dimensional insights
    - Holistic pattern understanding

    **Example**: "Give me the complete analysis of Nancy Pelosi's trading patterns"
    """
    if not ML_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ML libraries not available. Pattern analysis is currently disabled."
        )

    # Run all three analyses
    fourier_result = await analyze_fourier(politician_id, db)
    hmm_result = await analyze_regime(politician_id, db)
    dtw_result = await analyze_patterns(politician_id, db)

    # Generate key insights
    insights = []

    # Insight 1: Dominant cycle
    if fourier_result.dominant_cycles:
        top_cycle = fourier_result.dominant_cycles[0]
        insights.append(
            f"Trades on a {top_cycle.period_days:.0f}-day {top_cycle.category} cycle "
            f"with {top_cycle.confidence*100:.0f}% confidence"
        )

    # Insight 2: Current regime
    insights.append(
        f"Currently in '{hmm_result.current_regime_name}' regime "
        f"(expected to last {hmm_result.expected_duration_days:.0f} more days)"
    )

    # Insight 3: Pattern prediction
    if dtw_result.matches_found > 0:
        insights.append(
            f"Historical patterns predict {dtw_result.prediction_30d:+.1f} trade change in next 30 days "
            f"({dtw_result.prediction_confidence*100:.0f}% confidence)"
        )

    # Insight 4: Trade intensity
    insights.append(
        f"Total of {fourier_result.total_trades} trades over "
        f"{(fourier_result.date_range_end - fourier_result.date_range_start).days} days"
    )

    # Insight 5: Pattern consistency
    if fourier_result.dominant_cycles:
        strength = fourier_result.dominant_cycles[0].strength
        if strength > 0.8:
            insights.append("Highly regular trading pattern (strength > 0.8) suggests systematic approach")
        elif strength < 0.5:
            insights.append("Irregular trading pattern (strength < 0.5) suggests opportunistic approach")

    response = ComprehensiveAnalysisResponse(
        politician_id=politician_id,
        politician_name=fourier_result.politician_name,
        analysis_date=datetime.utcnow(),
        fourier=fourier_result,
        hmm=hmm_result,
        dtw=dtw_result,
        key_insights=insights[:5]  # Top 5
    )

    logger.info(f"Comprehensive analysis completed for {fourier_result.politician_name}")

    return response


@router.get(
    "/compare",
    summary="Compare patterns across politicians",
    description="Compare cyclical patterns and regimes across multiple politicians"
)
async def compare_politicians(
    politician_ids: List[str] = Query(..., description="List of politician UUIDs to compare"),
    db: AsyncSession = Depends(get_db),
    analysis_type: AnalysisType = Query(AnalysisType.fourier, description="Type of analysis to compare")
) -> Dict[str, Any]:
    """
    Compare pattern analysis results across multiple politicians.

    **Research Applications**:
    - Find politicians with similar trading patterns
    - Identify coordinated trading behavior
    - Study party-based differences
    - Detect systematic patterns

    **Example**: "Do Pelosi family members have synchronized trading cycles?"
    """

    if len(politician_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 politicians for comparison")

    results = {}

    for pol_id in politician_ids:
        try:
            if analysis_type == AnalysisType.fourier:
                results[pol_id] = await analyze_fourier(pol_id, db)
            elif analysis_type == AnalysisType.hmm:
                results[pol_id] = await analyze_regime(pol_id, db)
            elif analysis_type == AnalysisType.dtw:
                results[pol_id] = await analyze_patterns(pol_id, db)
            else:
                results[pol_id] = await analyze_comprehensive(pol_id, db)
        except HTTPException:
            results[pol_id] = None

    # Calculate comparison metrics
    comparison = {
        'politicians': results,
        'comparison_date': datetime.utcnow().isoformat(),
        'analysis_type': analysis_type.value
    }

    # Add correlation metrics if Fourier
    if analysis_type == AnalysisType.fourier:
        cycles = {}
        for pol_id, result in results.items():
            if result and result.dominant_cycles:
                cycles[pol_id] = result.dominant_cycles[0].period_days

        if len(cycles) > 1:
            comparison['cycle_correlation'] = {
                'cycles': cycles,
                'interpretation': "Similar cycle periods suggest potential coordination" if
                    max(cycles.values()) - min(cycles.values()) < 7 else
                    "Distinct cycles suggest independent strategies"
            }

    logger.info(f"Comparison completed for {len(politician_ids)} politicians")

    return comparison
