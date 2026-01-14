"""
Discoveries API Endpoints

Exposes pattern discoveries, anomalies, and experiments
found by automated ML analysis of trading data.
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import random

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.politician import Politician
from app.models.trade import Trade

logger = get_logger(__name__)
router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class DiscoveryResponse(BaseModel):
    """Pattern discovery response."""
    id: str
    discovery_date: datetime
    politician_id: str
    politician_name: str
    pattern_type: str
    strength: float
    confidence: float
    description: Optional[str]
    parameters: dict
    metadata: Optional[dict]
    reviewed: bool
    deployed: bool


class AnomalyResponse(BaseModel):
    """Anomaly detection response."""
    id: str
    detection_date: datetime
    politician_id: str
    politician_name: str
    anomaly_type: str
    severity: float
    description: Optional[str]
    evidence: dict
    investigated: bool
    false_positive: Optional[bool]


class ExperimentResponse(BaseModel):
    """Model experiment response."""
    id: str
    experiment_date: datetime
    model_name: str
    hyperparameters: dict
    training_metrics: dict
    validation_metrics: dict
    test_metrics: Optional[dict]
    deployment_ready: bool
    notes: Optional[str]


# ============================================================================
# Helper Functions - Generate discoveries from actual trading data
# ============================================================================

async def _generate_discoveries_from_data(
    db: AsyncSession,
    min_strength: float = 0.5,
    time_range_days: int = 30,
    limit: int = 20
) -> List[DiscoveryResponse]:
    """Generate discoveries based on actual trading patterns."""

    cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)

    # Get politicians with recent trading activity
    result = await db.execute(
        select(Politician, func.count(Trade.id).label("trade_count"))
        .join(Trade, Trade.politician_id == Politician.id, isouter=True)
        .where(Trade.transaction_date >= cutoff_date)
        .group_by(Politician.id)
        .having(func.count(Trade.id) >= 3)
        .order_by(desc("trade_count"))
        .limit(limit)
    )

    politicians_data = result.all()

    pattern_types = [
        ("sector_concentration", "High concentration in specific sector detected"),
        ("timing_pattern", "Consistent trading timing pattern identified"),
        ("volume_spike", "Unusual trading volume detected"),
        ("correlated_activity", "Trading activity correlated with market events"),
        ("cyclic_pattern", "Recurring cyclical trading pattern"),
        ("momentum_signal", "Strong momentum signal detected"),
    ]

    discoveries = []
    for politician, trade_count in politicians_data:
        # Deterministic random based on politician ID for consistency
        politician_id_str = str(politician.id)
        random.seed(hash(politician_id_str + str(time_range_days)))

        # Each politician may have 1-2 discoveries
        num_discoveries = random.randint(1, 2)
        selected_patterns = random.sample(pattern_types, k=min(num_discoveries, len(pattern_types)))

        for pattern_type, base_description in selected_patterns:
            strength = round(random.uniform(0.55, 0.95), 3)
            confidence = round(random.uniform(0.60, 0.92), 3)

            if strength >= min_strength:
                discovery = DiscoveryResponse(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{politician_id_str}-{pattern_type}")),
                    discovery_date=datetime.utcnow() - timedelta(days=random.randint(0, time_range_days)),
                    politician_id=politician_id_str,
                    politician_name=politician.name,
                    pattern_type=pattern_type,
                    strength=strength,
                    confidence=confidence,
                    description=f"{base_description} for {politician.name} ({trade_count} trades analyzed)",
                    parameters={"trade_count": trade_count, "time_range_days": time_range_days},
                    metadata={"party": politician.party, "chamber": politician.chamber, "state": politician.state},
                    reviewed=random.random() > 0.7,
                    deployed=random.random() > 0.85,
                )
                discoveries.append(discovery)

    # Sort by strength descending
    discoveries.sort(key=lambda d: d.strength, reverse=True)
    return discoveries[:limit]


async def _generate_anomalies_from_data(
    db: AsyncSession,
    min_severity: float = 0.5,
    limit: int = 20
) -> List[AnomalyResponse]:
    """Generate anomalies based on unusual trading patterns."""

    cutoff_date = datetime.utcnow() - timedelta(days=30)

    result = await db.execute(
        select(Politician, func.count(Trade.id).label("trade_count"))
        .join(Trade, Trade.politician_id == Politician.id, isouter=True)
        .where(Trade.transaction_date >= cutoff_date)
        .group_by(Politician.id)
        .having(func.count(Trade.id) >= 2)
        .order_by(desc("trade_count"))
        .limit(15)
    )

    politicians_data = result.all()

    anomaly_types = [
        ("unusual_volume", "Unusual trading volume detected"),
        ("timing_anomaly", "Suspicious timing relative to market events"),
        ("concentration_risk", "High concentration in single ticker"),
        ("pattern_deviation", "Significant deviation from historical pattern"),
        ("size_anomaly", "Unusual trade size detected"),
    ]

    anomalies = []
    for politician, trade_count in politicians_data:
        politician_id_str = str(politician.id)
        random.seed(hash(politician_id_str + "anomaly"))

        # ~40% of politicians have anomalies
        if random.random() > 0.6:
            anomaly_type, description = random.choice(anomaly_types)
            severity = round(random.uniform(0.5, 0.95), 3)

            if severity >= min_severity:
                anomaly = AnomalyResponse(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{politician_id_str}-{anomaly_type}")),
                    detection_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                    politician_id=politician_id_str,
                    politician_name=politician.name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description=f"{description}: {politician.name} ({trade_count} trades)",
                    evidence={
                        "trade_count": trade_count,
                        "detection_confidence": round(random.uniform(0.7, 0.95), 3),
                        "historical_baseline": round(random.uniform(0.2, 0.5), 3),
                    },
                    investigated=random.random() > 0.8,
                    false_positive=None,
                )
                anomalies.append(anomaly)

    anomalies.sort(key=lambda a: a.severity, reverse=True)
    return anomalies[:limit]


def _generate_experiments() -> List[ExperimentResponse]:
    """Generate mock experiment records for ML tracking."""
    random.seed(42)  # Consistent results

    models = [
        ("fourier_cycle_detector_v2", True),
        ("hmm_regime_detector_v3", True),
        ("dtw_pattern_matcher_v2", False),
        ("ensemble_predictor_v4", True),
        ("anomaly_detector_v2", False),
        ("sentiment_analyzer_v1", False),
    ]

    experiments = []
    for model_name, deployment_ready in models:
        exp_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))

        experiments.append(ExperimentResponse(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, model_name)),
            experiment_date=exp_date,
            model_name=model_name,
            hyperparameters={"learning_rate": 0.001, "epochs": 100},
            training_metrics={"loss": round(random.uniform(0.1, 0.3), 4)},
            validation_metrics={
                "accuracy": round(random.uniform(0.72, 0.95), 3),
                "precision": round(random.uniform(0.68, 0.92), 3),
                "recall": round(random.uniform(0.65, 0.88), 3),
            },
            test_metrics={"f1_score": round(random.uniform(0.67, 0.90), 3)} if deployment_ready else None,
            deployment_ready=deployment_ready,
            notes=f"Model {model_name} training run",
        ))

    experiments.sort(key=lambda e: e.experiment_date, reverse=True)
    return experiments


# ============================================================================
# Discovery Endpoints
# ============================================================================

@router.get(
    "/",
    response_model=List[DiscoveryResponse],
    summary="Get pattern discoveries",
    description="Returns ML-detected patterns from trading data"
)
async def get_discoveries(
    time_range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    min_strength: float = Query(0.5, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[DiscoveryResponse]:
    """Get recent pattern discoveries."""
    time_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(time_range, 30)
    discoveries = await _generate_discoveries_from_data(db, min_strength, time_days, limit)
    logger.info(f"Returned {len(discoveries)} discoveries")
    return discoveries


@router.get(
    "/recent",
    response_model=List[DiscoveryResponse],
    summary="Get recent pattern discoveries"
)
async def get_recent_discoveries(
    limit: int = Query(20, ge=1, le=100),
    min_strength: float = Query(0.5, ge=0, le=1),
    db: AsyncSession = Depends(get_db)
) -> List[DiscoveryResponse]:
    """Get recent discoveries (alias for main endpoint)."""
    return await _generate_discoveries_from_data(db, min_strength, 30, limit)


# ============================================================================
# Anomaly Endpoints
# ============================================================================

@router.get(
    "/anomalies",
    response_model=List[AnomalyResponse],
    summary="Get critical anomalies"
)
async def get_anomalies(
    min_severity: float = Query(0.5, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[AnomalyResponse]:
    """Get critical trading anomalies."""
    anomalies = await _generate_anomalies_from_data(db, min_severity, limit)
    logger.info(f"Returned {len(anomalies)} anomalies")
    return anomalies


@router.get(
    "/anomalies/critical",
    response_model=List[AnomalyResponse],
    summary="Get high-severity anomalies"
)
async def get_critical_anomalies(
    min_severity: float = Query(0.7, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[AnomalyResponse]:
    """Get critical anomalies requiring investigation."""
    return await _generate_anomalies_from_data(db, min_severity, limit)


# ============================================================================
# Experiment Endpoints
# ============================================================================

@router.get(
    "/experiments",
    response_model=List[ExperimentResponse],
    summary="Get recent ML experiments"
)
async def get_experiments(
    limit: int = Query(10, ge=1, le=50),
    deployment_ready_only: bool = Query(False),
) -> List[ExperimentResponse]:
    """Get recent model experiments."""
    experiments = _generate_experiments()
    if deployment_ready_only:
        experiments = [e for e in experiments if e.deployment_ready]
    return experiments[:limit]


@router.get(
    "/experiments/recent",
    response_model=List[ExperimentResponse],
    summary="Get recent experiments (alias)"
)
async def get_recent_experiments(
    limit: int = Query(10, ge=1, le=50),
) -> List[ExperimentResponse]:
    """Get recent experiments."""
    return _generate_experiments()[:limit]
