"""
Discoveries API Endpoints

Exposes pattern discoveries, anomalies, and experiments
found by automated ML analysis of trading data.
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

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
    """Pattern discovery is not implemented. Returns nothing.

    This function used to INVENT its results: it read real politicians out of the
    database, then assigned each one a pattern type, a "strength" and a "confidence"
    drawn from random.uniform, and returned them as analytical findings about named
    people. The randomness was seeded from the politician id, so the same person always
    got the same fabricated discovery and it looked stable across requests — which made
    it more convincing, not less false.

    It survived because the politicians table is empty in production, so the loop never
    ran. That is luck, not a safeguard: populating the table would have started
    publishing invented analysis about real individuals.

    Returning an empty list rather than raising keeps existing callers working while
    guaranteeing nothing fabricated leaves this service. A real implementation must
    compute from trade data and carry its own statistics.
    """
    return []


async def _generate_anomalies_from_data(
    db: AsyncSession,
    min_severity: float = 0.5,
    limit: int = 20
) -> List[AnomalyResponse]:
    """Anomaly detection is not implemented. Returns nothing.

    As with discoveries above, this assigned random.uniform "severity" and
    "detection_confidence" scores to real named politicians and returned them as
    detections. No detector existed behind any of it.
    """
    return []


def _generate_experiments() -> List[ExperimentResponse]:
    """ML experiment tracking is not implemented. Returns nothing.

    This returned a hardcoded roster of model names with invented accuracy and status
    fields, presented as a record of experiments that were never run.
    """
    return []


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
