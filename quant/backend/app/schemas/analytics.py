"""
OpenAPI schemas for analytics endpoints.

Comprehensive documentation for complex analytics API endpoints.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


class PredictionType(str, Enum):
    """Types of predictions from ensemble model"""
    TRADE_INCREASE = "trade_increase"
    TRADE_DECREASE = "trade_decrease"
    REGIME_CHANGE = "regime_change"
    CYCLE_PEAK = "cycle_peak"
    ANOMALY = "anomaly"
    INSUFFICIENT_DATA = "insufficient_data"


class InsightSeverity(str, Enum):
    """Severity levels for insights"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelPredictionSchema(BaseModel):
    """Individual model prediction details"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "model_name": "fourier_transform",
            "prediction": 15.5,
            "confidence": 0.85,
            "supporting_evidence": {
                "dominant_period": 30,
                "phase": 0.25,
                "amplitude": 1000000
            }
        }
    })
    
    model_name: str = Field(..., description="Name of the prediction model")
    prediction: float = Field(..., description="Predicted value (e.g., trades in next 30 days)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score (0-1)")
    supporting_evidence: Dict[str, Any] = Field(..., description="Model-specific evidence")


class EnsemblePredictionRequest(BaseModel):
    """Request for ensemble prediction"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "politician_id": "123e4567-e89b-12d3-a456-426614174000",
            "prediction_horizon": 30,
            "include_insights": True
        }
    })
    
    politician_id: UUID = Field(..., description="UUID of politician to analyze")
    prediction_horizon: int = Field(30, ge=7, le=365, description="Days ahead to predict")
    include_insights: bool = Field(True, description="Include AI-generated insights")


class EnsemblePredictionResponse(BaseModel):
    """Ensemble prediction response with full details"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "politician_id": "123e4567-e89b-12d3-a456-426614174000",
            "politician_name": "Nancy Pelosi",
            "analysis_date": "2025-01-15T10:30:00Z",
            "prediction_type": "trade_increase",
            "predicted_value": 12.5,
            "confidence": 0.78,
            "model_agreement": 0.85,
            "anomaly_score": 0.15,
            "individual_predictions": [
                {
                    "model_name": "fourier_transform",
                    "prediction": 15.5,
                    "confidence": 0.85,
                    "supporting_evidence": {"dominant_period": 30}
                }
            ],
            "insights": [
                "Strong 30-day trading cycle detected",
                "Currently in accumulation phase"
            ],
            "interpretation": "Significant increase in trading activity expected"
        }
    })
    
    politician_id: str = Field(..., description="Politician UUID")
    politician_name: str = Field(..., description="Politician full name")
    analysis_date: datetime = Field(..., description="Timestamp of analysis")
    prediction_type: PredictionType = Field(..., description="Type of prediction")
    predicted_value: float = Field(..., description="Main prediction value")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence (0-1)")
    model_agreement: float = Field(..., ge=0, le=1, description="Agreement between models (0-1)")
    anomaly_score: float = Field(..., ge=0, le=1, description="Anomaly detection score (0-1)")
    individual_predictions: List[ModelPredictionSchema] = Field(..., description="Individual model predictions")
    insights: List[str] = Field(..., description="AI-generated insights")
    interpretation: str = Field(..., description="Human-readable interpretation")


class CorrelationPairRequest(BaseModel):
    """Request for pairwise correlation analysis"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "politician_ids": [
                "123e4567-e89b-12d3-a456-426614174000",
                "987e6543-e21b-12d3-a456-426614174000"
            ],
            "time_window": 365,
            "min_overlap": 10
        }
    })
    
    politician_ids: List[UUID] = Field(
        ..., 
        min_length=2, 
        max_length=10, 
        description="List of politician UUIDs to analyze (2-10)"
    )
    time_window: int = Field(365, ge=30, le=1825, description="Days of history to analyze")
    min_overlap: int = Field(10, ge=5, description="Minimum overlapping trades required")


class CorrelationPairResponse(BaseModel):
    """Correlation analysis between two politicians"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "politician1_id": "123e4567-e89b-12d3-a456-426614174000",
            "politician1_name": "Nancy Pelosi",
            "politician2_id": "987e6543-e21b-12d3-a456-426614174000",
            "politician2_name": "Dan Crenshaw",
            "correlation": 0.72,
            "p_value": 0.0001,
            "significance": "significant",
            "interpretation": "Strong positive correlation detected",
            "common_tickers": ["NVDA", "AAPL", "MSFT"],
            "overlap_count": 45
        }
    })
    
    politician1_id: str = Field(..., description="First politician UUID")
    politician1_name: str = Field(..., description="First politician name")
    politician2_id: str = Field(..., description="Second politician UUID")
    politician2_name: str = Field(..., description="Second politician name")
    correlation: float = Field(..., ge=-1, le=1, description="Correlation coefficient (-1 to 1)")
    p_value: float = Field(..., ge=0, le=1, description="Statistical p-value")
    significance: str = Field(..., description="Statistical significance level")
    interpretation: str = Field(..., description="Human-readable interpretation")
    common_tickers: Optional[List[str]] = Field(None, description="Common traded tickers")
    overlap_count: Optional[int] = Field(None, description="Number of overlapping trades")


class NetworkMetricsResponse(BaseModel):
    """Network analysis metrics"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "analysis_date": "2025-01-15T10:30:00Z",
            "num_politicians": 247,
            "density": 0.35,
            "clustering_coefficient": 0.62,
            "average_path_length": 2.8,
            "central_politicians": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Nancy Pelosi",
                    "centrality": 0.89,
                    "degree": 45
                }
            ],
            "clusters": [
                {
                    "cluster_id": 1,
                    "size": 15,
                    "theme": "Technology stocks",
                    "members": ["Nancy Pelosi", "Dan Crenshaw"]
                }
            ]
        }
    })
    
    analysis_date: datetime = Field(..., description="Timestamp of analysis")
    num_politicians: int = Field(..., ge=0, description="Total politicians in network")
    density: float = Field(..., ge=0, le=1, description="Network connectivity (0-1)")
    clustering_coefficient: float = Field(..., ge=0, le=1, description="Network clustering metric")
    average_path_length: float = Field(..., ge=0, description="Average connection distance")
    central_politicians: List[Dict[str, Any]] = Field(..., description="Most central/influential politicians")
    clusters: List[Dict[str, Any]] = Field(..., description="Detected trading clusters/groups")


class InsightSchema(BaseModel):
    """AI-generated insight"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "type": "pattern",
            "severity": "warning",
            "confidence": 0.85,
            "title": "Unusual Trading Pattern Detected",
            "description": "Significant increase in options trading detected",
            "recommendation": "Investigate recent legislative activity",
            "supporting_data": {
                "trade_count": 45,
                "volume": 5000000,
                "period": "2025-01"
            }
        }
    })
    
    type: str = Field(..., description="Type of insight (pattern, anomaly, trend)")
    severity: InsightSeverity = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in insight (0-1)")
    title: str = Field(..., description="Brief title")
    description: str = Field(..., description="Detailed description")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation")
    supporting_data: Dict[str, Any] = Field(..., description="Supporting data/evidence")


class SectorAnalysisResponse(BaseModel):
    """Sector-based analysis results"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "sector": "Technology",
            "total_volume": 25000000,
            "trade_count": 450,
            "politician_count": 89,
            "top_tickers": [
                {"symbol": "NVDA", "volume": 5000000, "trades": 120},
                {"symbol": "AAPL", "volume": 4500000, "trades": 95}
            ],
            "trend": "bullish",
            "momentum": 0.75,
            "insights": [
                "Technology sector showing increased institutional interest"
            ]
        }
    })
    
    sector: str = Field(..., description="Sector name")
    total_volume: float = Field(..., ge=0, description="Total trading volume")
    trade_count: int = Field(..., ge=0, description="Number of trades")
    politician_count: int = Field(..., ge=0, description="Number of politicians trading")
    top_tickers: List[Dict[str, Any]] = Field(..., description="Most traded tickers in sector")
    trend: str = Field(..., description="Overall trend (bullish/bearish/neutral)")
    momentum: float = Field(..., ge=-1, le=1, description="Momentum indicator (-1 to 1)")
    insights: List[str] = Field(..., description="Sector-specific insights")


class ExecutiveSummaryResponse(BaseModel):
    """Executive summary of analytics"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": "2025-Q1",
            "key_findings": [
                "Unusual activity in semiconductor stocks",
                "Coordinated trading patterns among tech committee members"
            ],
            "risk_assessment": {
                "level": "medium",
                "factors": ["High concentration", "Timing patterns"]
            },
            "recommendations": [
                "Monitor semiconductor legislation",
                "Track tech committee member trades"
            ],
            "metrics": {
                "total_volume": 150000000,
                "active_politicians": 187,
                "anomaly_count": 12
            }
        }
    })
    
    period: str = Field(..., description="Analysis period")
    key_findings: List[str] = Field(..., description="Key findings and discoveries")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    metrics: Dict[str, Any] = Field(..., description="Summary metrics")