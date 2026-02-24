"""
Database models for stock predictions.

Stores ML predictions, technical indicators, and trading signals.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Float, Integer, DateTime, JSON, Index, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class PredictionDirection(str, enum.Enum):
    """Prediction direction enum."""
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


class SignalType(str, enum.Enum):
    """Trading signal type enum."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ModelType(str, enum.Enum):
    """ML model type enum."""
    LSTM = "LSTM"
    XGBOOST = "XGBOOST"
    RANDOM_FOREST = "RANDOM_FOREST"
    ENSEMBLE = "ENSEMBLE"
    RULE_BASED = "RULE_BASED"
    RL_AGENT = "RL_AGENT"


class StockPrediction(Base):
    """
    Stock price predictions from ML models.

    Stores predictions for future price movements with confidence scores.
    Used for tracking model accuracy over time.
    """
    __tablename__ = "stock_predictions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Prediction details
    prediction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False)  # How many days ahead

    # Model information
    model_type: Mapped[ModelType] = mapped_column(SQLEnum(ModelType), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(50))

    # Prediction values
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_price: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_direction: Mapped[PredictionDirection] = mapped_column(
        SQLEnum(PredictionDirection),
        nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0

    # Additional predictions (JSON array)
    predicted_prices: Mapped[Optional[dict]] = mapped_column(JSON)  # Array of future prices

    # Technical features used
    features: Mapped[Optional[dict]] = mapped_column(JSON)

    # Actual outcome (filled later)
    actual_price: Mapped[Optional[float]] = mapped_column(Float)
    actual_direction: Mapped[Optional[PredictionDirection]] = mapped_column(
        SQLEnum(PredictionDirection)
    )
    accuracy: Mapped[Optional[float]] = mapped_column(Float)  # Calculated after validation

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'prediction_date'),
        Index('idx_model_type', 'model_type'),
        Index('idx_created_at', 'created_at'),
    )


class TechnicalIndicators(Base):
    """
    Technical indicators calculated for stocks.

    Stores indicator values for historical analysis and backtesting.
    """
    __tablename__ = "technical_indicators"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Price data
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    # Momentum indicators
    rsi: Mapped[Optional[float]] = mapped_column(Float)
    macd: Mapped[Optional[float]] = mapped_column(Float)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float)
    macd_hist: Mapped[Optional[float]] = mapped_column(Float)
    stoch_k: Mapped[Optional[float]] = mapped_column(Float)
    stoch_d: Mapped[Optional[float]] = mapped_column(Float)

    # Trend indicators
    sma_20: Mapped[Optional[float]] = mapped_column(Float)
    sma_50: Mapped[Optional[float]] = mapped_column(Float)
    sma_200: Mapped[Optional[float]] = mapped_column(Float)
    ema_12: Mapped[Optional[float]] = mapped_column(Float)
    ema_26: Mapped[Optional[float]] = mapped_column(Float)
    adx: Mapped[Optional[float]] = mapped_column(Float)

    # Volatility indicators
    bb_upper: Mapped[Optional[float]] = mapped_column(Float)
    bb_middle: Mapped[Optional[float]] = mapped_column(Float)
    bb_lower: Mapped[Optional[float]] = mapped_column(Float)
    atr: Mapped[Optional[float]] = mapped_column(Float)

    # Volume indicators
    obv: Mapped[Optional[float]] = mapped_column(Float)
    vwap: Mapped[Optional[float]] = mapped_column(Float)

    # Additional indicators (JSON)
    other_indicators: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_symbol_date_unique', 'symbol', 'date', unique=True),
    )


class TradingSignal(Base):
    """
    Trading signals generated by various strategies.

    Stores buy/sell/hold recommendations with reasoning.
    """
    __tablename__ = "trading_signals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Signal details
    signal_type: Mapped[SignalType] = mapped_column(SQLEnum(SignalType), nullable=False)
    signal_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Source information
    strategy_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[Optional[ModelType]] = mapped_column(SQLEnum(ModelType))

    # Signal strength
    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    strength: Mapped[Optional[str]] = mapped_column(String(20))  # "weak", "moderate", "strong"

    # Price information
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    target_price: Mapped[Optional[float]] = mapped_column(Float)
    stop_loss: Mapped[Optional[float]] = mapped_column(Float)

    # Reasoning
    reasoning: Mapped[Optional[str]] = mapped_column(String(500))
    technical_signals: Mapped[Optional[dict]] = mapped_column(JSON)
    patterns_detected: Mapped[Optional[dict]] = mapped_column(JSON)

    # Performance tracking
    executed: Mapped[bool] = mapped_column(default=False)
    execution_price: Mapped[Optional[float]] = mapped_column(Float)
    outcome: Mapped[Optional[str]] = mapped_column(String(20))  # "profit", "loss", "neutral"
    profit_loss: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Indexes
    __table_args__ = (
        Index('idx_symbol_signal_date', 'symbol', 'signal_date'),
        Index('idx_signal_type', 'signal_type'),
        Index('idx_strategy', 'strategy_name'),
    )


class PatternDetection(Base):
    """
    Candlestick and chart patterns detected in stock data.

    Stores pattern occurrences for analysis and backtesting.
    """
    __tablename__ = "pattern_detections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    detection_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Pattern information
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "CDLHAMMER", etc.
    pattern_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pattern_category: Mapped[str] = mapped_column(String(50))  # "bullish_reversal", etc.

    # Pattern strength
    strength: Mapped[str] = mapped_column(String(20))  # "weak", "moderate", "strong"
    direction: Mapped[str] = mapped_column(String(20))  # "bullish", "bearish", "neutral"
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Price at detection
    price_at_detection: Mapped[float] = mapped_column(Float, nullable=False)

    # Pattern details (JSON)
    pattern_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Outcome tracking
    price_after_1d: Mapped[Optional[float]] = mapped_column(Float)
    price_after_5d: Mapped[Optional[float]] = mapped_column(Float)
    price_after_10d: Mapped[Optional[float]] = mapped_column(Float)
    pattern_success: Mapped[Optional[bool]] = mapped_column()

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_pattern_type', 'pattern_type'),
        Index('idx_pattern_date', 'symbol', 'detection_date'),
    )


class ModelPerformance(Base):
    """
    Track ML model performance metrics over time.

    Stores accuracy, precision, recall, and other metrics for model monitoring.
    """
    __tablename__ = "model_performance"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Model information
    model_type: Mapped[ModelType] = mapped_column(SQLEnum(ModelType), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    # Time period
    evaluation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Performance metrics
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)

    # Prediction statistics
    total_predictions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_predictions: Mapped[int] = mapped_column(Integer, nullable=False)

    # Direction accuracy
    direction_accuracy: Mapped[float] = mapped_column(Float)

    # Additional metrics (JSON)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_model_eval', 'model_type', 'evaluation_date'),
    )
