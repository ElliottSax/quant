"""
Advanced Analytics API Endpoints

Research endpoints for ensemble predictions, correlation analysis,
automated insights, and multi-politician network analysis.

**CUTTING-EDGE RESEARCH**: Multi-model ensemble, correlation detection,
automated insight generation.

Author: Claude
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field, UUID4
from uuid import UUID
import asyncio

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.cache import cache_manager
from app.core.concurrency import ml_semaphore, network_semaphore, with_concurrency_limit
from app.models.politician import Politician
from app.models.trade import Trade

# Import analytics modules
from app.ml.ensemble import EnsemblePredictor, EnsemblePrediction, PredictionType, ModelPrediction
from app.ml.correlation import CorrelationAnalyzer, CorrelationResult, NetworkMetrics, SectorAnalyzer
from app.ml.insights import InsightGenerator, Insight, InsightType, InsightSeverity, generate_executive_summary

# Import pattern analysis
from app.api.v1.patterns import (
    load_politician_trades,
    prepare_time_series,
    analyze_fourier,
    analyze_regime,
    analyze_patterns
)

logger = get_logger(__name__)
router = APIRouter()


# Helper for parallel execution when some analyses are skipped
async def _return_none():
    """Helper coroutine that returns None for skipped analyses"""
    return None


# ============================================================================
# Response Models
# ============================================================================

class ModelPredictionResponse(BaseModel):
    """Individual model prediction"""
    model_name: str
    prediction: float
    confidence: float
    supporting_evidence: Dict[str, Any]


class EnsemblePredictionResponse(BaseModel):
    """Ensemble prediction response"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    prediction_type: str
    predicted_value: float
    confidence: float = Field(..., ge=0, le=1)
    model_agreement: float = Field(..., ge=0, le=1)
    anomaly_score: float = Field(..., ge=0, le=1)
    individual_predictions: List[ModelPredictionResponse]
    insights: List[str]
    interpretation: str


class CorrelationPairResponse(BaseModel):
    """Correlation between two politicians"""
    politician1_id: str
    politician1_name: str
    politician2_id: str
    politician2_name: str
    correlation: float
    p_value: float
    significance: str  # "significant" or "not_significant"
    interpretation: str


class NetworkAnalysisResponse(BaseModel):
    """Network analysis results"""
    analysis_date: datetime
    num_politicians: int
    density: float = Field(..., description="Network connectivity (0-1)")
    clustering_coefficient: float
    average_path_length: float
    central_politicians: List[Dict[str, Any]]
    clusters: List[Dict[str, Any]]
    coordinated_groups: Dict[str, List[Tuple[str, str, float]]]


class InsightResponse(BaseModel):
    """Individual insight"""
    type: str
    severity: str
    title: str
    description: str
    confidence: float
    evidence: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime


class ComprehensiveInsightsResponse(BaseModel):
    """Complete insight analysis"""
    politician_id: str
    politician_name: str
    analysis_date: datetime
    executive_summary: str
    total_insights: int
    critical_count: int
    high_priority_count: int
    insights: List[InsightResponse]


# ============================================================================
# Ensemble Prediction Endpoints
# ============================================================================

async def _compute_ensemble_prediction(
    politician_id_str: str,
    politician_name: str,
    db: AsyncSession
) -> EnsemblePredictionResponse:
    """
    Internal function to compute ensemble prediction (cacheable).

    This is separated to enable caching while keeping the endpoint logic clean.
    """
    # Load trades and prepare time series
    trades_df = await load_politician_trades(db, politician_id_str)

    if trades_df.empty or len(trades_df) < 100:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for ensemble prediction. Need at least 100 trades, found {len(trades_df)}."
        )

    trade_frequency = prepare_time_series(trades_df)

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id_str))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    # Run all three models IN PARALLEL for better concurrency
    try:
        # Run analyses concurrently to prevent blocking, with timeout to prevent hangs
        logger.debug(f"Running parallel ML analyses for {politician.name}")
        fourier_analysis, hmm_analysis, dtw_analysis = await asyncio.wait_for(
            asyncio.gather(
                analyze_fourier(politician_id_str, db, min_strength=0.05, min_confidence=0.6, include_forecast=False),
                analyze_regime(politician_id_str, db, n_states=4),
                analyze_patterns(politician_id_str, db, window_size=30, top_k=5, similarity_threshold=0.6),
                return_exceptions=True
            ),
            timeout=60.0  # 60 second timeout for all ML operations
        )

        # Check for exceptions from parallel execution
        if isinstance(fourier_analysis, Exception):
            logger.error(f"Fourier analysis failed: {fourier_analysis}")
            raise fourier_analysis
        if isinstance(hmm_analysis, Exception):
            logger.error(f"HMM analysis failed: {hmm_analysis}")
            raise hmm_analysis
        if isinstance(dtw_analysis, Exception):
            logger.error(f"DTW analysis failed: {dtw_analysis}")
            raise dtw_analysis

        # Convert to dicts
        fourier_result = fourier_analysis.dict()
        hmm_result = hmm_analysis.dict()
        dtw_result = dtw_analysis.dict()

        # Run ensemble
        ensemble = EnsemblePredictor()
        prediction = ensemble.predict(
            fourier_result,
            hmm_result,
            dtw_result,
            trade_frequency
        )

        # Interpret prediction type
        type_descriptions = {
            PredictionType.TRADE_INCREASE: "Significant increase in trading activity expected",
            PredictionType.TRADE_DECREASE: "Significant decrease in trading activity expected",
            PredictionType.REGIME_CHANGE: "Trading regime transition imminent",
            PredictionType.CYCLE_PEAK: "Approaching peak of trading cycle",
            PredictionType.ANOMALY: "Anomalous pattern detected",
            PredictionType.INSUFFICIENT_DATA: "Insufficient cyclical patterns for prediction"
        }

        interpretation = type_descriptions.get(
            prediction.prediction_type,
            "Normal trading pattern"
        )

        # Build response
        response = EnsemblePredictionResponse(
            politician_id=str(politician.id),
            politician_name=politician.name,
            analysis_date=datetime.now(timezone.utc),
            prediction_type=prediction.prediction_type.value,
            predicted_value=prediction.value,
            confidence=prediction.confidence,
            model_agreement=prediction.model_agreement,
            anomaly_score=prediction.anomaly_score,
            individual_predictions=[
                ModelPredictionResponse(
                    model_name=p.model_name,
                    prediction=p.prediction,
                    confidence=p.confidence,
                    supporting_evidence=p.supporting_evidence
                )
                for p in prediction.predictions
            ],
            insights=prediction.insights,
            interpretation=interpretation
        )

        logger.info(f"Ensemble prediction for {politician.name}: {prediction.prediction_type.value}")

        return response

    except asyncio.TimeoutError:
        logger.error(f"Ensemble prediction timed out for {politician.name}")
        raise HTTPException(
            status_code=504,
            detail="Analysis timed out. This politician may have too much data for real-time analysis. Please try again later."
        )
    except ValueError as e:
        # Expected errors - safe to expose message
        logger.warning(f"Ensemble prediction validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors - don't expose internal details
        logger.error(f"Ensemble prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Prediction analysis failed. Please try again later or contact support if the issue persists."
        )


# ============================================================================
# Correlation Analysis Endpoints
# ============================================================================

@router.get(
    "/correlation/pairwise",
    summary="Pairwise correlation analysis",
    description="Analyze trading correlations between multiple politicians"
)
async def analyze_pairwise_correlations(
    politician_ids: List[UUID4] = Query(..., description="List of politician UUIDs (2-10)", min_length=2, max_length=10),
    db: AsyncSession = Depends(get_db)
) -> List[CorrelationPairResponse]:
    """
    Analyze pairwise trading correlations between politicians.

    **Research Applications**:
    - Detect coordinated trading
    - Find synchronized patterns
    - Identify lead-lag relationships
    - Study network effects

    **Example**: "Do Nancy and Paul Pelosi trade in sync?"
    """

    # Convert UUIDs to strings
    politician_ids_str = [str(pid) for pid in politician_ids]

    # Load all politicians
    result = await db.execute(
        select(Politician).where(Politician.id.in_(politician_ids_str))
    )
    politicians = {str(p.id): p for p in result.scalars().all()}

    if len(politicians) != len(politician_ids):
        raise HTTPException(status_code=404, detail="Some politicians not found")

    # Load trade data for each
    politician_data = {}
    for pol_id in politician_ids_str:
        trades_df = await load_politician_trades(db, pol_id)
        if not trades_df.empty:
            politician_data[pol_id] = prepare_time_series(trades_df)

    if len(politician_data) < 2:
        raise HTTPException(status_code=400, detail="Insufficient data for correlation")

    # Analyze correlations
    analyzer = CorrelationAnalyzer()
    correlations = analyzer.analyze_cycle_correlation(politician_data)

    # Build response
    responses = []
    for corr in correlations:
        pol1 = politicians[corr.politician1_id]
        pol2 = politicians[corr.politician2_id]

        significance = "significant" if corr.p_value < 0.05 else "not_significant"

        responses.append(CorrelationPairResponse(
            politician1_id=str(pol1.id),
            politician1_name=pol1.name,
            politician2_id=str(pol2.id),
            politician2_name=pol2.name,
            correlation=corr.correlation,
            p_value=corr.p_value,
            significance=significance,
            interpretation=corr.interpretation
        ))

    return responses


@router.get(
    "/network/analysis",
    response_model=NetworkAnalysisResponse,
    summary="Network analysis of politician trading",
    description="Analyze trading network structure and identify clusters of correlated politicians"
)
async def analyze_trading_network(
    min_trades: int = Query(50, ge=1, le=1000, description="Minimum trades per politician"),
    min_correlation: float = Query(0.5, ge=0, le=1, description="Minimum correlation for edges"),
    db: AsyncSession = Depends(get_db)
) -> NetworkAnalysisResponse:
    """
    Perform network analysis on politician trading patterns.

    **Network Metrics**:
    - Density: How connected the network is
    - Clustering: Tendency to form groups
    - Centrality: Most influential politicians
    - Communities: Natural groupings

    **Research Applications**:
    - Identify trading networks
    - Find central figures
    - Detect coordination
    - Study information flow

    **Example**: "Who are the central figures in the trading network?"
    """

    # Get politicians with sufficient data
    query = (
        select(Politician)
        .join(Trade)
        .group_by(Politician.id)
        .having(func.count(Trade.id) >= min_trades)
    )

    result = await db.execute(query)
    politicians = {str(p.id): p for p in result.scalars().all()}

    if len(politicians) < 3:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 3 politicians with {min_trades}+ trades"
        )

    # Load trade data
    politician_data = {}
    for pol_id in politicians.keys():
        trades_df = await load_politician_trades(db, pol_id)
        if not trades_df.empty:
            politician_data[pol_id] = prepare_time_series(trades_df)

    # Build correlation matrix
    analyzer = CorrelationAnalyzer()
    corr_matrix = analyzer.build_correlation_matrix(politician_data)

    # Build network graph
    G = analyzer.build_network_graph(corr_matrix, min_correlation=min_correlation)

    # Calculate network metrics
    metrics = analyzer.calculate_network_metrics(G)

    # Detect clusters
    clusters = analyzer.detect_clusters(corr_matrix, min_correlation=min_correlation)

    # Detect coordinated groups
    metadata = {
        pol_id: {
            'name': pol.name,
            'party': pol.party,
            'state': pol.state
        }
        for pol_id, pol in politicians.items()
    }

    coordinated = analyzer.detect_coordinated_trading(
        politician_data,
        metadata,
        correlation_threshold=min_correlation
    )

    # Format response
    response = NetworkAnalysisResponse(
        analysis_date=datetime.now(timezone.utc),
        num_politicians=len(politicians),
        density=metrics.density,
        clustering_coefficient=metrics.clustering_coefficient,
        average_path_length=metrics.average_path_length,
        central_politicians=[
            {
                'politician_id': pol_id,
                'name': politicians[pol_id].name if pol_id in politicians else pol_id,
                'centrality_score': score
            }
            for pol_id, score in metrics.central_politicians
        ],
        clusters=[
            {
                'cluster_id': cluster.cluster_id,
                'politicians': [
                    politicians[pol_id].name if pol_id in politicians else pol_id
                    for pol_id in cluster.politicians
                ],
                'avg_correlation': cluster.avg_correlation
            }
            for cluster in clusters
        ],
        coordinated_groups=coordinated
    )

    logger.info(f"Network analysis: {len(politicians)} politicians, density={metrics.density:.2f}")

    return response


# ============================================================================
# Automated Insights Endpoints
# ============================================================================

@router.get(
    "/insights/{politician_id}",
    response_model=ComprehensiveInsightsResponse,
    summary="Generate automated insights",
    description="AI-generated insights from comprehensive pattern analysis"
)
async def generate_insights(
    politician_id: UUID4 = Path(..., description="Politician UUID"),
    confidence_threshold: float = Query(0.7, ge=0, le=1, description="Minimum confidence"),
    db: AsyncSession = Depends(get_db)
) -> ComprehensiveInsightsResponse:
    """
    Generate comprehensive automated insights using all analytics.

    This endpoint:
    - Runs all pattern analyses
    - Generates ensemble predictions
    - Detects anomalies
    - Produces natural language insights
    - Prioritizes by severity and confidence

    **Insight Types**:
    - Pattern detection
    - Anomaly alerts
    - Predictions
    - Risk assessments
    - Correlations

    **Severity Levels**:
    - Critical: Requires immediate investigation
    - High: Priority findings
    - Medium: Notable patterns
    - Low: Minor observations
    - Info: General information

    **Research Applications**:
    - Automated screening
    - Priority identification
    - Report generation
    - Executive summaries

    **Example**: "Give me the top insights for Nancy Pelosi"
    """

    # Convert UUID to string
    politician_id_str = str(politician_id)

    # Load politician
    result = await db.execute(select(Politician).where(Politician.id == politician_id_str))
    politician = result.scalar_one_or_none()

    if not politician:
        raise HTTPException(status_code=404, detail="Politician not found")

    # Load trades
    trades_df = await load_politician_trades(db, politician_id_str)

    if trades_df.empty or len(trades_df) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient data for insights. Need at least 30 trades."
        )

    try:
        # Run all analyses IN PARALLEL for better concurrency
        logger.debug(f"Running parallel ML analyses for insights: {politician.name}")

        # Prepare async tasks (conditionally include HMM and DTW based on data requirements)
        tasks = [
            analyze_fourier(politician_id_str, db, min_strength=0.05, min_confidence=0.6, include_forecast=False)
        ]

        # Only run HMM if sufficient data
        if len(trades_df) >= 100:
            tasks.append(analyze_regime(politician_id_str, db, n_states=4))
        else:
            tasks.append(_return_none())  # Placeholder that returns None

        # Only run DTW if sufficient data
        if len(trades_df) >= 90:
            tasks.append(analyze_patterns(politician_id_str, db, window_size=30, top_k=5, similarity_threshold=0.6))
        else:
            tasks.append(_return_none())  # Placeholder that returns None

        # Run analyses concurrently with timeout to prevent hangs
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=60.0  # 60 second timeout for all ML operations
        )
        fourier_analysis = results[0]
        hmm_analysis = results[1] if len(results) > 1 else None
        dtw_analysis = results[2] if len(results) > 2 else None

        # Check for exceptions
        if isinstance(fourier_analysis, Exception):
            logger.error(f"Fourier analysis failed: {fourier_analysis}")
            raise fourier_analysis
        if isinstance(hmm_analysis, Exception):
            logger.error(f"HMM analysis failed: {hmm_analysis}")
            hmm_analysis = None  # Continue without HMM
        if isinstance(dtw_analysis, Exception):
            logger.error(f"DTW analysis failed: {dtw_analysis}")
            dtw_analysis = None  # Continue without DTW

        # Sector analysis (run in thread to not block)
        sector_analyzer = SectorAnalyzer()
        sector_prefs = await asyncio.to_thread(sector_analyzer.analyze_sector_preference, trades_df)

        # Generate insights
        insight_gen = InsightGenerator(confidence_threshold=confidence_threshold)

        insights = insight_gen.generate_comprehensive_insights(
            fourier_result=fourier_analysis.dict(),
            hmm_result=hmm_analysis.dict() if hmm_analysis else {},
            dtw_result=dtw_analysis.dict() if dtw_analysis else {},
            sector_analysis={'sector_preference': sector_prefs},
            politician_metadata={'name': politician.name}
        )

        # Generate executive summary
        exec_summary = generate_executive_summary(insights)

        # Count by severity
        critical_count = sum(1 for i in insights if i.severity == InsightSeverity.CRITICAL)
        high_count = sum(1 for i in insights if i.severity == InsightSeverity.HIGH)

        # Build response
        response = ComprehensiveInsightsResponse(
            politician_id=str(politician.id),
            politician_name=politician.name,
            analysis_date=datetime.now(timezone.utc),
            executive_summary=exec_summary,
            total_insights=len(insights),
            critical_count=critical_count,
            high_priority_count=high_count,
            insights=[
                InsightResponse(
                    type=i.type.value,
                    severity=i.severity.value,
                    title=i.title,
                    description=i.description,
                    confidence=i.confidence,
                    evidence=i.evidence,
                    recommendations=i.recommendations,
                    timestamp=i.timestamp
                )
                for i in insights
            ]
        )

        logger.info(f"Generated {len(insights)} insights for {politician.name} ({critical_count} critical, {high_count} high)")

        return response

    except asyncio.TimeoutError:
        logger.error(f"Insight generation timed out for {politician.name}")
        raise HTTPException(
            status_code=504,
            detail="Insight generation timed out. This politician may have too much data for real-time analysis. Please try again later."
        )
    except ValueError as e:
        # Expected errors - safe to expose message
        logger.warning(f"Insight generation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors - don't expose internal details
        logger.error(f"Insight generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Insight generation failed. Please try again later or contact support if the issue persists."
        )


@router.get(
    "/anomaly-detection/{politician_id}",
    summary="Anomaly detection",
    description="Detect anomalous trading patterns requiring investigation"
)
async def detect_anomalies(
    politician_id: UUID4 = Path(..., description="Politician UUID"),
    anomaly_threshold: float = Query(0.7, ge=0, le=1, description="Anomaly score threshold"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Detect anomalous trading patterns.

    **Anomaly Indicators**:
    - No historical precedent (DTW)
    - Off-cycle trading (Fourier)
    - Unusual regime (HMM)
    - Model disagreement (Ensemble)

    **Research Applications**:
    - Compliance monitoring
    - Fraud detection
    - Unusual activity alerts
    - Investigation prioritization

    **Example**: "Is Nancy Pelosi's current trading anomalous?"
    """

    insights_response = await generate_insights(
        politician_id=politician_id,
        confidence_threshold=0.6,
        db=db
    )

    # Filter for anomaly insights
    anomalies = [
        i for i in insights_response.insights
        if i.type == InsightType.ANOMALY.value and i.confidence >= anomaly_threshold
    ]

    # Also check ensemble anomaly score
    try:
        ensemble_response = await get_ensemble_prediction(politician_id, db)
        has_high_anomaly_score = ensemble_response.anomaly_score >= anomaly_threshold
    except:
        has_high_anomaly_score = False

    return {
        'politician_id': str(politician_id),
        'politician_name': insights_response.politician_name,
        'analysis_date': datetime.now(timezone.utc),
        'anomaly_detected': len(anomalies) > 0 or has_high_anomaly_score,
        'anomaly_count': len(anomalies),
        'ensemble_anomaly_score': ensemble_response.anomaly_score if has_high_anomaly_score else 0,
        'anomalies': anomalies,
        'requires_investigation': len(anomalies) > 0 and any(
            a.severity in [InsightSeverity.CRITICAL.value, InsightSeverity.HIGH.value]
            for a in anomalies
        )
    }
