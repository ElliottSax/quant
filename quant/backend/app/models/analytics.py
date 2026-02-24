"""
Analytics Models

Database models for storing advanced analytics results including:
- Options analysis results
- Sentiment analysis cache
- Pattern recognition results
- Predictive model outputs

Author: Claude
"""

import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, Date, Numeric, Text, ForeignKey, func, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.common import UUID, JSONType

if TYPE_CHECKING:
    from app.models.politician import Politician


class OptionsAnalysisCache(Base):
    """Cache for options analysis results"""

    __tablename__ = "options_analysis_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Gamma Exposure
    total_gamma: Mapped[Optional[float]] = mapped_column(Float)
    net_gamma: Mapped[Optional[float]] = mapped_column(Float)
    gamma_flip_price: Mapped[Optional[float]] = mapped_column(Float)
    market_stance: Mapped[Optional[str]] = mapped_column(String(20))

    # Options Flow
    call_volume: Mapped[Optional[int]] = mapped_column()
    put_volume: Mapped[Optional[int]] = mapped_column()
    call_put_ratio: Mapped[Optional[float]] = mapped_column(Float)
    net_premium_flow: Mapped[Optional[float]] = mapped_column(Float)
    flow_sentiment: Mapped[Optional[str]] = mapped_column(String(20))

    # Overall
    overall_sentiment: Mapped[Optional[str]] = mapped_column(String(20))
    confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Full analysis results (JSON)
    full_analysis: Mapped[Optional[dict]] = mapped_column(JSONType())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Indexes
    __table_args__ = (
        Index("idx_options_ticker_date", "ticker", "analysis_date"),
    )

    def __repr__(self) -> str:
        return f"<OptionsAnalysisCache {self.ticker} {self.analysis_date}>"


class SentimentAnalysisCache(Base):
    """Cache for sentiment analysis results"""

    __tablename__ = "sentiment_analysis_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Can be either politician or ticker sentiment
    politician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        index=True,
    )
    ticker: Mapped[Optional[str]] = mapped_column(String(10), index=True)

    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Aggregated results
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_category: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Breakdown
    items_analyzed: Mapped[int] = mapped_column(nullable=False)
    positive_count: Mapped[int] = mapped_column(nullable=False)
    negative_count: Mapped[int] = mapped_column(nullable=False)
    neutral_count: Mapped[int] = mapped_column(nullable=False)

    # Source breakdown (JSON)
    source_breakdown: Mapped[dict] = mapped_column(JSONType(), nullable=False)

    # Trend
    trend_24h: Mapped[Optional[float]] = mapped_column(Float)

    # Full results (JSON)
    full_analysis: Mapped[Optional[dict]] = mapped_column(JSONType())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationship
    politician: Mapped[Optional["Politician"]] = relationship("Politician")

    # Indexes
    __table_args__ = (
        Index("idx_sentiment_politician_date", "politician_id", "analysis_date"),
        Index("idx_sentiment_ticker_date", "ticker", "analysis_date"),
    )

    def __repr__(self) -> str:
        entity = self.politician_id or self.ticker
        return f"<SentimentAnalysisCache {entity} {self.analysis_date}>"


class PatternRecognitionResult(Base):
    """Stored pattern recognition results"""

    __tablename__ = "pattern_recognition_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Pattern type
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Involved politicians (JSON array of UUIDs)
    politician_ids: Mapped[list] = mapped_column(JSONType(), nullable=False)

    # Pattern details (JSON)
    pattern_data: Mapped[dict] = mapped_column(JSONType(), nullable=False)

    # Metrics
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    significance: Mapped[Optional[float]] = mapped_column(Float)

    # Description
    description: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Indexes
    __table_args__ = (
        Index("idx_pattern_type_date", "pattern_type", "analysis_date"),
    )

    def __repr__(self) -> str:
        return f"<PatternRecognitionResult {self.pattern_type} {self.analysis_date}>"


class CorrelationAnalysisCache(Base):
    """Cache for correlation analysis results"""

    __tablename__ = "correlation_analysis_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Correlation type
    correlation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # "politician_politician", "politician_sector", "cross_politician"

    # Entities involved
    entity1_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    entity2_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)

    # Correlation value
    correlation: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[Optional[float]] = mapped_column(Float)

    # Time window
    lookback_days: Mapped[int] = mapped_column(nullable=False)

    # Additional metrics (JSON)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONType())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Indexes
    __table_args__ = (
        Index("idx_correlation_type_date", "correlation_type", "analysis_date"),
        Index("idx_correlation_entities", "entity1_id", "entity2_id"),
    )

    def __repr__(self) -> str:
        return f"<CorrelationAnalysisCache {self.correlation_type} {self.correlation:.3f}>"


class PredictiveModelResult(Base):
    """Predictive model results and forecasts"""

    __tablename__ = "predictive_model_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Prediction
    prediction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    prediction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # "trade_likelihood", "risk_score", "return_forecast", etc.

    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Prediction horizon
    forecast_days: Mapped[Optional[int]] = mapped_column()
    target_date: Mapped[Optional[date]] = mapped_column(Date)

    # Features used (JSON)
    features: Mapped[Optional[dict]] = mapped_column(JSONType())

    # Model metrics
    model_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    model_metrics: Mapped[Optional[dict]] = mapped_column(JSONType())

    # Explanation
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationship
    politician: Mapped["Politician"] = relationship("Politician")

    # Indexes
    __table_args__ = (
        Index("idx_prediction_politician_date", "politician_id", "prediction_date"),
        Index("idx_prediction_model_date", "model_name", "prediction_date"),
    )

    def __repr__(self) -> str:
        return f"<PredictiveModelResult {self.model_name} {self.politician_id} {self.prediction_date}>"


class RiskScoreCache(Base):
    """Risk scores for politicians"""

    __tablename__ = "risk_score_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    politician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        ForeignKey("politicians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Risk scores
    overall_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )  # 0-100

    volatility_score: Mapped[float] = mapped_column(Float, nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False)
    timing_risk_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Risk category
    risk_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # "low", "medium", "high", "very_high"

    # Contributing factors (JSON)
    risk_factors: Mapped[dict] = mapped_column(JSONType(), nullable=False)

    # Explanation
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationship
    politician: Mapped["Politician"] = relationship("Politician")

    # Indexes
    __table_args__ = (
        Index("idx_risk_politician_date", "politician_id", "analysis_date"),
        Index("idx_risk_score", "overall_risk_score"),
    )

    def __repr__(self) -> str:
        return f"<RiskScoreCache {self.politician_id} {self.overall_risk_score:.1f}>"
