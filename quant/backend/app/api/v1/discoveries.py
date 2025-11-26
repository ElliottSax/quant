"""
Discoveries API Endpoints

Exposes pattern discoveries, anomalies, and experiments
found by the background discovery service.
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, UUID4

from app.core.database import get_db
from app.core.logging import get_logger

# Import from shared package
from quant_shared.models import (
    PatternDiscovery,
    AnomalyDetection,
    ModelExperiment,
    NetworkDiscovery,
    Politician,
)

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


class DiscoveryStatsResponse(BaseModel):
    """Discovery statistics."""
    total_discoveries: int
    discoveries_24h: int
    discoveries_7d: int
    total_anomalies: int
    critical_anomalies: int
    total_experiments: int
    deployment_ready_models: int
    top_patterns: List[dict]


# ============================================================================
# Discovery Endpoints
# ============================================================================

@router.get(
    "/discoveries/recent",
    response_model=List[DiscoveryResponse],
    summary="Get recent pattern discoveries",
    description="Returns recently discovered patterns sorted by date"
)
async def get_recent_discoveries(
    limit: int = Query(20, ge=1, le=100, description="Number of discoveries to return"),
    min_strength: float = Query(0.7, ge=0, le=1, description="Minimum pattern strength"),
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    deployed_only: bool = Query(False, description="Only show deployed patterns"),
    db: AsyncSession = Depends(get_db)
) -> List[DiscoveryResponse]:
    """
    Get recent pattern discoveries.

    Filters:
    - min_strength: Only show patterns above this strength
    - pattern_type: Filter by type (fourier_cycle, regime_transition, etc.)
    - deployed_only: Only show patterns deployed to production
    """

    # Build query
    stmt = (
        select(PatternDiscovery, Politician.name)
        .join(Politician, PatternDiscovery.politician_id == Politician.id)
        .where(PatternDiscovery.strength >= min_strength)
    )

    if pattern_type:
        stmt = stmt.where(PatternDiscovery.pattern_type == pattern_type)

    if deployed_only:
        stmt = stmt.where(PatternDiscovery.deployed == True)

    stmt = stmt.order_by(PatternDiscovery.discovery_date.desc()).limit(limit)

    # Execute
    result = await db.execute(stmt)
    rows = result.all()

    # Format response
    discoveries = []
    for discovery, politician_name in rows:
        discoveries.append(DiscoveryResponse(
            id=str(discovery.id),
            discovery_date=discovery.discovery_date,
            politician_id=str(discovery.politician_id),
            politician_name=politician_name,
            pattern_type=discovery.pattern_type,
            strength=discovery.strength,
            confidence=discovery.confidence,
            description=discovery.description,
            parameters=discovery.parameters,
            metadata=discovery.metadata,
            reviewed=discovery.reviewed,
            deployed=discovery.deployed,
        ))

    logger.info(f"Returned {len(discoveries)} discoveries")
    return discoveries


@router.get(
    "/discoveries/politician/{politician_id}",
    response_model=List[DiscoveryResponse],
    summary="Get discoveries for a specific politician"
)
async def get_politician_discoveries(
    politician_id: UUID4 = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db)
) -> List[DiscoveryResponse]:
    """Get all discoveries for a specific politician."""

    stmt = (
        select(PatternDiscovery, Politician.name)
        .join(Politician, PatternDiscovery.politician_id == Politician.id)
        .where(PatternDiscovery.politician_id == str(politician_id))
        .order_by(PatternDiscovery.strength.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    discoveries = []
    for discovery, politician_name in rows:
        discoveries.append(DiscoveryResponse(
            id=str(discovery.id),
            discovery_date=discovery.discovery_date,
            politician_id=str(discovery.politician_id),
            politician_name=politician_name,
            pattern_type=discovery.pattern_type,
            strength=discovery.strength,
            confidence=discovery.confidence,
            description=discovery.description,
            parameters=discovery.parameters,
            metadata=discovery.metadata,
            reviewed=discovery.reviewed,
            deployed=discovery.deployed,
        ))

    return discoveries


# ============================================================================
# Anomaly Endpoints
# ============================================================================

@router.get(
    "/anomalies/critical",
    response_model=List[AnomalyResponse],
    summary="Get critical anomalies",
    description="Returns high-severity anomalies requiring investigation"
)
async def get_critical_anomalies(
    min_severity: float = Query(0.8, ge=0, le=1, description="Minimum severity"),
    uninvestigated_only: bool = Query(True, description="Only show uninvestigated"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[AnomalyResponse]:
    """
    Get critical anomalies.

    Use this for alerts and compliance monitoring.
    """

    stmt = (
        select(AnomalyDetection, Politician.name)
        .join(Politician, AnomalyDetection.politician_id == Politician.id)
        .where(AnomalyDetection.severity >= min_severity)
    )

    if uninvestigated_only:
        stmt = stmt.where(AnomalyDetection.investigated == False)

    stmt = stmt.order_by(AnomalyDetection.severity.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    anomalies = []
    for anomaly, politician_name in rows:
        anomalies.append(AnomalyResponse(
            id=str(anomaly.id),
            detection_date=anomaly.detection_date,
            politician_id=str(anomaly.politician_id),
            politician_name=politician_name,
            anomaly_type=anomaly.anomaly_type,
            severity=anomaly.severity,
            description=anomaly.description,
            evidence=anomaly.evidence,
            investigated=anomaly.investigated,
            false_positive=anomaly.false_positive,
        ))

    logger.info(f"Returned {len(anomalies)} critical anomalies")
    return anomalies


@router.get(
    "/anomalies/politician/{politician_id}",
    response_model=List[AnomalyResponse],
    summary="Get anomalies for a specific politician"
)
async def get_politician_anomalies(
    politician_id: UUID4 = Path(..., description="Politician UUID"),
    db: AsyncSession = Depends(get_db)
) -> List[AnomalyResponse]:
    """Get all anomalies detected for a politician."""

    stmt = (
        select(AnomalyDetection, Politician.name)
        .join(Politician, AnomalyDetection.politician_id == Politician.id)
        .where(AnomalyDetection.politician_id == str(politician_id))
        .order_by(AnomalyDetection.detection_date.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()

    anomalies = []
    for anomaly, politician_name in rows:
        anomalies.append(AnomalyResponse(
            id=str(anomaly.id),
            detection_date=anomaly.detection_date,
            politician_id=str(anomaly.politician_id),
            politician_name=politician_name,
            anomaly_type=anomaly.anomaly_type,
            severity=anomaly.severity,
            description=anomaly.description,
            evidence=anomaly.evidence,
            investigated=anomaly.investigated,
            false_positive=anomaly.false_positive,
        ))

    return anomalies


# ============================================================================
# Experiment Endpoints
# ============================================================================

@router.get(
    "/experiments/recent",
    response_model=List[ExperimentResponse],
    summary="Get recent model experiments"
)
async def get_recent_experiments(
    limit: int = Query(10, ge=1, le=50),
    deployment_ready_only: bool = Query(False),
    db: AsyncSession = Depends(get_db)
) -> List[ExperimentResponse]:
    """Get recent experimental model results."""

    stmt = select(ModelExperiment)

    if deployment_ready_only:
        stmt = stmt.where(ModelExperiment.deployment_ready == True)

    stmt = stmt.order_by(ModelExperiment.experiment_date.desc()).limit(limit)

    result = await db.execute(stmt)
    experiments = result.scalars().all()

    return [
        ExperimentResponse(
            id=str(exp.id),
            experiment_date=exp.experiment_date,
            model_name=exp.model_name,
            hyperparameters=exp.hyperparameters,
            training_metrics=exp.training_metrics,
            validation_metrics=exp.validation_metrics,
            test_metrics=exp.test_metrics,
            deployment_ready=exp.deployment_ready,
            notes=exp.notes,
        )
        for exp in experiments
    ]


# ============================================================================
# Stats Endpoint
# ============================================================================

@router.get(
    "/discoveries/stats",
    response_model=DiscoveryStatsResponse,
    summary="Get discovery statistics"
)
async def get_discovery_stats(
    db: AsyncSession = Depends(get_db)
) -> DiscoveryStatsResponse:
    """Get aggregate statistics about discoveries."""

    # Total discoveries
    total_discoveries_stmt = select(func.count(PatternDiscovery.id))
    total_discoveries = (await db.execute(total_discoveries_stmt)).scalar()

    # Discoveries in last 24h
    discoveries_24h_stmt = select(func.count(PatternDiscovery.id)).where(
        PatternDiscovery.discovery_date >= datetime.now() - timedelta(days=1)
    )
    discoveries_24h = (await db.execute(discoveries_24h_stmt)).scalar()

    # Discoveries in last 7d
    discoveries_7d_stmt = select(func.count(PatternDiscovery.id)).where(
        PatternDiscovery.discovery_date >= datetime.now() - timedelta(days=7)
    )
    discoveries_7d = (await db.execute(discoveries_7d_stmt)).scalar()

    # Total anomalies
    total_anomalies_stmt = select(func.count(AnomalyDetection.id))
    total_anomalies = (await db.execute(total_anomalies_stmt)).scalar()

    # Critical anomalies
    critical_anomalies_stmt = select(func.count(AnomalyDetection.id)).where(
        AnomalyDetection.severity >= 0.8
    )
    critical_anomalies = (await db.execute(critical_anomalies_stmt)).scalar()

    # Total experiments
    total_experiments_stmt = select(func.count(ModelExperiment.id))
    total_experiments = (await db.execute(total_experiments_stmt)).scalar()

    # Deployment ready models
    deployment_ready_stmt = select(func.count(ModelExperiment.id)).where(
        ModelExperiment.deployment_ready == True
    )
    deployment_ready = (await db.execute(deployment_ready_stmt)).scalar()

    # Top pattern types
    top_patterns_stmt = (
        select(
            PatternDiscovery.pattern_type,
            func.count(PatternDiscovery.id).label('count'),
            func.avg(PatternDiscovery.strength).label('avg_strength')
        )
        .group_by(PatternDiscovery.pattern_type)
        .order_by(func.count(PatternDiscovery.id).desc())
        .limit(5)
    )
    top_patterns_result = await db.execute(top_patterns_stmt)
    top_patterns = [
        {
            'pattern_type': row[0],
            'count': row[1],
            'avg_strength': float(row[2])
        }
        for row in top_patterns_result.all()
    ]

    return DiscoveryStatsResponse(
        total_discoveries=total_discoveries or 0,
        discoveries_24h=discoveries_24h or 0,
        discoveries_7d=discoveries_7d or 0,
        total_anomalies=total_anomalies or 0,
        critical_anomalies=critical_anomalies or 0,
        total_experiments=total_experiments or 0,
        deployment_ready_models=deployment_ready or 0,
        top_patterns=top_patterns,
    )
