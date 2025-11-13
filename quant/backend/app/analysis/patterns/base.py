"""
Base classes and types for pattern detection.

This module provides the foundational abstractions for the pattern detection system,
enabling hedge fund-level cyclical pattern recognition with statistical rigor.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Any, Optional

import numpy as np
import pandas as pd


class PatternType(Enum):
    """Types of cyclical patterns that can be detected."""

    SEASONAL = "seasonal"  # SARIMA-detected seasonal patterns
    CALENDAR = "calendar"  # Calendar effects (January, Monday, etc.)
    CYCLE = "cycle"  # Fourier-detected dominant cycles
    REGIME = "regime"  # HMM-detected market regimes
    BEHAVIORAL = "behavioral"  # DTW-detected behavioral patterns
    POLITICIAN = "politician"  # Patterns correlated with politician trades
    EARNINGS = "earnings"  # Earnings cycle patterns
    ECONOMIC = "economic"  # Economic cycle patterns (GDP, Fed meetings, etc.)


class Frequency(Enum):
    """Frequency of pattern occurrence."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


@dataclass
class PatternOccurrence:
    """A single historical occurrence of a pattern."""

    start_date: date
    end_date: date
    return_pct: float  # Return during this occurrence
    confidence: float  # Confidence score for this specific occurrence
    volume_change: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class ValidationMetrics:
    """Comprehensive validation metrics for a pattern."""

    # Statistical significance
    p_value: float
    effect_size: float  # Cohen's d or similar
    statistical_power: float

    # Walk-forward validation
    walk_forward_efficiency: float  # Out-of-sample / In-sample performance
    in_sample_return: float
    out_sample_return: float

    # Robustness
    consistency_score: float  # How consistent across time periods
    sample_size: int  # Number of occurrences
    years_of_data: float

    # Recent performance
    recent_performance: float  # Last 3 occurrences average
    last_occurrence_date: Optional[date] = None

    # Risk metrics
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None


@dataclass
class Pattern:
    """
    A detected cyclical pattern with full statistical validation.

    Represents a reliable, statistically validated cyclical pattern that occurs
    predictably in the market. Each pattern includes comprehensive validation
    metrics, historical occurrences, and economic rationale.
    """

    # Identity
    pattern_id: str  # Unique identifier
    pattern_type: PatternType
    name: str  # Human-readable name (e.g., "January Effect - Small Cap")
    description: str  # Detailed explanation

    # Target
    ticker: Optional[str] = None  # Specific ticker, or None for market-wide
    sector: Optional[str] = None
    market_cap: Optional[str] = None  # "small", "mid", "large"

    # Timing
    cycle_length_days: int = 0  # Length of one complete cycle
    frequency: Optional[Frequency] = None
    next_occurrence: Optional[date] = None
    window_start_day: Optional[int] = None  # Day of year/month when pattern starts
    window_end_day: Optional[int] = None

    # Statistical validation
    validation_metrics: Optional[ValidationMetrics] = None
    reliability_score: float = 0.0  # Composite score 0-100
    confidence: float = 0.0  # Statistical confidence 0-100

    # Historical data
    historical_occurrences: list[PatternOccurrence] = field(default_factory=list)
    first_detected: Optional[date] = None
    last_validated: Optional[date] = None

    # Explanation
    economic_rationale: Optional[str] = None  # Why this pattern exists
    risk_factors: list[str] = field(default_factory=list)

    # Politician signal correlation
    politician_correlation: Optional[float] = None  # Correlation with politician trades
    recent_politician_activity: Optional[dict[str, Any]] = None

    # Metadata
    detected_at: datetime = field(default_factory=datetime.utcnow)
    detector_version: str = "1.0.0"
    parameters: dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Check if pattern is currently active (within occurrence window)."""
        if self.next_occurrence is None:
            return False

        today = date.today()
        # Consider active if within 7 days of next occurrence
        days_until = (self.next_occurrence - today).days
        return -7 <= days_until <= 7

    def is_reliable(self, min_score: float = 70.0) -> bool:
        """Check if pattern meets minimum reliability threshold."""
        return self.reliability_score >= min_score

    def has_politician_confirmation(self, min_correlation: float = 0.3) -> bool:
        """Check if pattern is confirmed by politician trading activity."""
        if self.politician_correlation is None:
            return False
        return self.politician_correlation >= min_correlation

    def get_expected_return(self) -> Optional[float]:
        """Get expected return based on historical performance."""
        if not self.validation_metrics:
            return None

        # Use out-of-sample return if available, otherwise in-sample
        return self.validation_metrics.out_sample_return

    def get_risk_adjusted_score(self) -> float:
        """Get reliability score adjusted for risk (Sharpe ratio)."""
        if not self.validation_metrics or self.validation_metrics.sharpe_ratio is None:
            return self.reliability_score

        # Adjust reliability score by Sharpe ratio
        sharpe_adjustment = min(self.validation_metrics.sharpe_ratio / 2.0, 1.0)
        return self.reliability_score * (0.7 + 0.3 * sharpe_adjustment)


class PatternDetector(ABC):
    """
    Abstract base class for all pattern detectors.

    Each pattern detector implements a specific algorithm (SARIMA, Calendar Effects, etc.)
    to identify cyclical patterns in market data. All detectors must implement rigorous
    statistical validation and reliability scoring.
    """

    def __init__(
        self,
        min_occurrences: int = 10,
        min_years: float = 5.0,
        min_p_value: float = 0.05,
        min_wfe: float = 0.5,
        require_recent_confirmation: bool = True,
    ):
        """
        Initialize pattern detector with validation parameters.

        Args:
            min_occurrences: Minimum number of historical occurrences required
            min_years: Minimum years of data required
            min_p_value: Maximum p-value for statistical significance
            min_wfe: Minimum walk-forward efficiency (out/in sample performance)
            require_recent_confirmation: Whether pattern must work in recent data
        """
        self.min_occurrences = min_occurrences
        self.min_years = min_years
        self.min_p_value = min_p_value
        self.min_wfe = min_wfe
        self.require_recent_confirmation = require_recent_confirmation

    @abstractmethod
    async def detect(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[Pattern]:
        """
        Detect patterns for a given ticker.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date for analysis (None = use all available data)
            end_date: End date for analysis (None = use today)

        Returns:
            List of detected patterns that pass validation
        """
        pass

    @abstractmethod
    def validate_pattern(self, pattern: Pattern, data: pd.DataFrame) -> ValidationMetrics:
        """
        Validate a pattern using walk-forward analysis and statistical tests.

        Args:
            pattern: Pattern to validate
            data: Historical price data

        Returns:
            Comprehensive validation metrics
        """
        pass

    def calculate_reliability_score(self, metrics: ValidationMetrics) -> float:
        """
        Calculate composite reliability score (0-100) from validation metrics.

        Scoring breakdown:
        - Statistical Significance: 30% (p-value, effect size, power)
        - Walk-Forward Efficiency: 25% (out-of-sample performance)
        - Sample Size: 20% (number of occurrences, years of data)
        - Recent Performance: 15% (last 3 occurrences)
        - Consistency: 10% (stability across time)

        Args:
            metrics: Validation metrics

        Returns:
            Reliability score from 0-100
        """
        score = 0.0

        # 1. Statistical Significance (30 points)
        if metrics.p_value <= 0.001:
            score += 30
        elif metrics.p_value <= 0.01:
            score += 25
        elif metrics.p_value <= 0.05:
            score += 20
        else:
            score += max(0, 20 * (1 - metrics.p_value / 0.05))

        # Effect size bonus
        if metrics.effect_size > 0.8:  # Large effect
            score += 5
        elif metrics.effect_size > 0.5:  # Medium effect
            score += 3

        score = min(score, 30)  # Cap at 30

        # 2. Walk-Forward Efficiency (25 points)
        if metrics.walk_forward_efficiency >= 1.0:  # Out-sample >= In-sample
            score += 25
        elif metrics.walk_forward_efficiency >= 0.8:
            score += 20
        elif metrics.walk_forward_efficiency >= 0.5:
            score += 15
        else:
            score += max(0, 15 * metrics.walk_forward_efficiency / 0.5)

        score = min(score, 55)  # Cap cumulative at 55

        # 3. Sample Size (20 points)
        occurrence_score = min(20, metrics.sample_size * 2)  # 1 point per occurrence, cap at 20
        years_score = min(10, metrics.years_of_data)  # 1 point per year, cap at 10
        score += (occurrence_score * 0.6 + years_score * 0.4)

        score = min(score, 75)  # Cap cumulative at 75

        # 4. Recent Performance (15 points)
        if metrics.recent_performance > 0:
            # Scale based on recent returns
            recent_score = min(15, metrics.recent_performance * 100)
            score += recent_score

        score = min(score, 90)  # Cap cumulative at 90

        # 5. Consistency (10 points)
        score += metrics.consistency_score * 10

        return min(100.0, score)

    def calculate_confidence(self, p_value: float, effect_size: float) -> float:
        """
        Calculate statistical confidence (0-100) from p-value and effect size.

        Args:
            p_value: Statistical p-value
            effect_size: Cohen's d or similar effect size metric

        Returns:
            Confidence score from 0-100
        """
        # Base confidence from p-value
        if p_value <= 0.001:
            confidence = 99.0
        elif p_value <= 0.01:
            confidence = 95.0
        elif p_value <= 0.05:
            confidence = 90.0
        else:
            confidence = max(0, 90 * (1 - p_value / 0.05))

        # Adjust by effect size
        if effect_size < 0.2:  # Small effect
            confidence *= 0.8
        elif effect_size < 0.5:  # Medium effect
            confidence *= 0.9
        # Large effect (>0.8) gets no penalty

        return min(100.0, confidence)

    def meets_minimum_criteria(self, metrics: ValidationMetrics) -> bool:
        """
        Check if pattern meets minimum validation criteria.

        Args:
            metrics: Validation metrics to check

        Returns:
            True if pattern passes all minimum thresholds
        """
        # Statistical significance
        if metrics.p_value > self.min_p_value:
            return False

        # Walk-forward efficiency
        if metrics.walk_forward_efficiency < self.min_wfe:
            return False

        # Sample size
        if metrics.sample_size < self.min_occurrences:
            return False

        if metrics.years_of_data < self.min_years:
            return False

        # Recent confirmation (if required)
        if self.require_recent_confirmation:
            if metrics.last_occurrence_date is None:
                return False

            days_since = (date.today() - metrics.last_occurrence_date).days
            if days_since > 365:  # No occurrence in last year
                return False

            if metrics.recent_performance <= 0:  # Recent occurrences unprofitable
                return False

        return True

    async def fetch_market_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """
        Fetch historical market data for pattern detection.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with OHLCV data and returns
        """
        import yfinance as yf

        # Fetch data from Yahoo Finance
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,  # Adjust for splits/dividends
        )

        if data.empty:
            raise ValueError(f"No data available for {ticker}")

        # Calculate returns
        data['returns'] = data['Close'].pct_change()
        data['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))

        # Add date features
        data['day_of_week'] = data.index.dayofweek
        data['day_of_month'] = data.index.day
        data['month'] = data.index.month
        data['quarter'] = data.index.quarter
        data['day_of_year'] = data.index.dayofyear

        return data

    def calculate_effect_size(
        self,
        pattern_returns: np.ndarray,
        baseline_returns: np.ndarray,
    ) -> float:
        """
        Calculate Cohen's d effect size.

        Args:
            pattern_returns: Returns during pattern occurrences
            baseline_returns: Returns during baseline periods

        Returns:
            Cohen's d effect size
        """
        mean_diff = np.mean(pattern_returns) - np.mean(baseline_returns)
        pooled_std = np.sqrt(
            (np.var(pattern_returns) + np.var(baseline_returns)) / 2
        )

        if pooled_std == 0:
            return 0.0

        return mean_diff / pooled_std

    def bonferroni_correction(self, p_value: float, num_tests: int) -> float:
        """
        Apply Bonferroni correction for multiple hypothesis testing.

        Args:
            p_value: Original p-value
            num_tests: Number of independent tests performed

        Returns:
            Corrected p-value
        """
        return min(1.0, p_value * num_tests)
