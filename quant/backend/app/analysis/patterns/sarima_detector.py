"""
SARIMA (Seasonal ARIMA) pattern detector.

Detects seasonal patterns using Seasonal AutoRegressive Integrated Moving Average models.
SARIMA can identify recurring patterns at fixed intervals (annual, quarterly, monthly).
"""

from datetime import date, timedelta
from typing import Optional
import uuid

import numpy as np
import pandas as pd
from pmdarima import auto_arima
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

from app.analysis.patterns.base import (
    Frequency,
    Pattern,
    PatternDetector,
    PatternOccurrence,
    PatternType,
    ValidationMetrics,
)
from app.analysis.validation.validator import (
    ConsistencyAnalyzer,
    RecentPerformanceAnalyzer,
    StatisticalTester,
    WalkForwardValidator,
)


class SARIMADetector(PatternDetector):
    """
    Detect seasonal patterns using SARIMA models.

    SARIMA (Seasonal ARIMA) is specified as ARIMA(p,d,q)(P,D,Q,s):
    - (p,d,q): Non-seasonal AR, differencing, MA orders
    - (P,D,Q): Seasonal AR, differencing, MA orders
    - s: Seasonal period length

    This detector identifies:
    - Annual seasonality (252 trading days)
    - Quarterly seasonality (63 trading days)
    - Monthly seasonality (21 trading days)
    """

    # Seasonal periods to test (in trading days)
    SEASONAL_PERIODS = {
        'annual': 252,
        'quarterly': 63,
        'monthly': 21,
    }

    def __init__(
        self,
        min_seasonal_strength: float = 0.3,
        max_p: int = 3,
        max_q: int = 3,
        max_P: int = 2,
        max_Q: int = 2,
        **kwargs,
    ):
        """
        Initialize SARIMA detector.

        Args:
            min_seasonal_strength: Minimum seasonal strength to consider (0-1)
            max_p: Maximum non-seasonal AR order
            max_q: Maximum non-seasonal MA order
            max_P: Maximum seasonal AR order
            max_Q: Maximum seasonal MA order
            **kwargs: Additional arguments passed to PatternDetector
        """
        super().__init__(**kwargs)
        self.min_seasonal_strength = min_seasonal_strength
        self.max_p = max_p
        self.max_q = max_q
        self.max_P = max_P
        self.max_Q = max_Q

    async def detect(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[Pattern]:
        """
        Detect seasonal patterns in ticker data using SARIMA.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (default: 10 years ago)
            end_date: End date (default: today)

        Returns:
            List of validated seasonal patterns
        """
        # Default date range: 10 years
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365 * 10)

        # Fetch market data
        data = await self.fetch_market_data(ticker, start_date, end_date)

        if len(data) < 500:  # Need at least ~2 years of data
            return []

        detected_patterns = []

        # Test each seasonal period
        for period_name, period_length in self.SEASONAL_PERIODS.items():
            # Skip if not enough data for this seasonality
            if len(data) < period_length * 3:
                continue

            try:
                pattern = await self._detect_seasonal_pattern(
                    ticker=ticker,
                    data=data,
                    period_name=period_name,
                    period_length=period_length,
                )

                if pattern is not None:
                    detected_patterns.append(pattern)

            except Exception as e:
                # Log error but continue with other periods
                print(f"Error detecting {period_name} pattern for {ticker}: {e}")
                continue

        return detected_patterns

    async def _detect_seasonal_pattern(
        self,
        ticker: str,
        data: pd.DataFrame,
        period_name: str,
        period_length: int,
    ) -> Optional[Pattern]:
        """
        Detect seasonal pattern for a specific period.

        Args:
            ticker: Stock ticker
            data: Historical price data
            period_name: Name of period ('annual', 'quarterly', 'monthly')
            period_length: Length of period in trading days

        Returns:
            Pattern if detected and validated, None otherwise
        """
        # 1. Check for seasonality using decomposition
        seasonal_strength = self._calculate_seasonal_strength(
            data['Close'],
            period=period_length,
        )

        if seasonal_strength < self.min_seasonal_strength:
            return None  # No significant seasonality

        # 2. Fit SARIMA model with auto parameter selection
        try:
            model = auto_arima(
                data['Close'],
                seasonal=True,
                m=period_length,
                max_p=self.max_p,
                max_q=self.max_q,
                max_P=self.max_P,
                max_Q=self.max_Q,
                max_d=2,
                max_D=1,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
            )
        except Exception:
            return None  # Model fitting failed

        # Extract seasonal component
        seasonal_component = self._extract_seasonal_component(
            data['Close'],
            period=period_length,
        )

        # 3. Identify peak and trough periods
        occurrences = self._identify_occurrences(
            data=data,
            seasonal_component=seasonal_component,
            period_length=period_length,
        )

        if len(occurrences) < self.min_occurrences:
            return None  # Not enough historical occurrences

        # 4. Validate pattern
        validation_metrics = self.validate_pattern_with_data(
            data=data,
            occurrences=occurrences,
            period_length=period_length,
        )

        if not self.meets_minimum_criteria(validation_metrics):
            return None  # Failed validation

        # 5. Calculate reliability and confidence
        reliability_score = self.calculate_reliability_score(validation_metrics)
        confidence = self.calculate_confidence(
            validation_metrics.p_value,
            validation_metrics.effect_size,
        )

        # 6. Determine next occurrence
        next_occurrence = self._predict_next_occurrence(
            occurrences=occurrences,
            period_length=period_length,
        )

        # 7. Create pattern object
        frequency_map = {
            'annual': Frequency.ANNUAL,
            'quarterly': Frequency.QUARTERLY,
            'monthly': Frequency.MONTHLY,
        }

        pattern = Pattern(
            pattern_id=str(uuid.uuid4()),
            pattern_type=PatternType.SEASONAL,
            name=f"{ticker} - {period_name.capitalize()} Seasonal Pattern",
            description=self._generate_description(
                ticker=ticker,
                period_name=period_name,
                seasonal_strength=seasonal_strength,
                model=model,
                occurrences=occurrences,
            ),
            ticker=ticker,
            cycle_length_days=period_length,
            frequency=frequency_map[period_name],
            next_occurrence=next_occurrence,
            validation_metrics=validation_metrics,
            reliability_score=reliability_score,
            confidence=confidence,
            historical_occurrences=occurrences,
            first_detected=occurrences[0].start_date if occurrences else None,
            last_validated=date.today(),
            economic_rationale=self._generate_economic_rationale(period_name),
            parameters={
                'sarima_order': model.order,
                'seasonal_order': model.seasonal_order,
                'aic': model.aic(),
                'seasonal_strength': seasonal_strength,
                'period_length': period_length,
            },
        )

        return pattern

    def _calculate_seasonal_strength(
        self,
        series: pd.Series,
        period: int,
    ) -> float:
        """
        Calculate strength of seasonal component.

        Uses STL decomposition to separate trend, seasonal, and residual components.
        Seasonal strength = 1 - Var(Residual) / Var(Seasonal + Residual)

        Args:
            series: Time series data
            period: Seasonal period length

        Returns:
            Seasonal strength (0-1), higher = stronger seasonality
        """
        if len(series) < period * 2:
            return 0.0

        try:
            # STL decomposition
            decomposition = seasonal_decompose(
                series,
                model='additive',
                period=period,
                extrapolate_trend='freq',
            )

            seasonal = decomposition.seasonal
            resid = decomposition.resid

            # Remove NaNs
            seasonal = seasonal.dropna()
            resid = resid.dropna()

            if len(seasonal) == 0 or len(resid) == 0:
                return 0.0

            # Calculate seasonal strength
            var_resid = np.var(resid)
            var_seasonal_resid = np.var(seasonal + resid)

            if var_seasonal_resid == 0:
                return 0.0

            strength = max(0.0, 1 - var_resid / var_seasonal_resid)
            return strength

        except Exception:
            return 0.0

    def _extract_seasonal_component(
        self,
        series: pd.Series,
        period: int,
    ) -> pd.Series:
        """
        Extract seasonal component from time series.

        Args:
            series: Time series data
            period: Seasonal period length

        Returns:
            Seasonal component
        """
        decomposition = seasonal_decompose(
            series,
            model='additive',
            period=period,
            extrapolate_trend='freq',
        )

        return decomposition.seasonal

    def _identify_occurrences(
        self,
        data: pd.DataFrame,
        seasonal_component: pd.Series,
        period_length: int,
    ) -> list[PatternOccurrence]:
        """
        Identify historical pattern occurrences from seasonal component.

        Args:
            data: Price data
            seasonal_component: Extracted seasonal component
            period_length: Length of seasonal period

        Returns:
            List of pattern occurrences
        """
        occurrences = []

        # Find peaks in seasonal component (strongest positive seasonality)
        # Use a rolling window to identify local maxima
        window_size = period_length // 4  # Quarter of the cycle

        seasonal_rolling_max = seasonal_component.rolling(
            window=window_size,
            center=True,
        ).max()

        # Identify peaks: points where value equals rolling max
        is_peak = (seasonal_component == seasonal_rolling_max) & (seasonal_component > 0)
        peak_indices = seasonal_component[is_peak].index

        # Group peaks into cycles
        current_cycle_start = None
        current_cycle_returns = []

        for i, idx in enumerate(peak_indices):
            if current_cycle_start is None:
                current_cycle_start = idx
                current_cycle_returns = []

            # Check if this peak is in a new cycle
            days_since_start = (idx - current_cycle_start).days

            if days_since_start >= period_length * 0.8:
                # New cycle - record previous occurrence
                if len(current_cycle_returns) > 0:
                    cycle_return = np.sum(current_cycle_returns)
                    occurrences.append(
                        PatternOccurrence(
                            start_date=current_cycle_start.date(),
                            end_date=idx.date(),
                            return_pct=cycle_return,
                            confidence=80.0,  # Base confidence
                        )
                    )

                current_cycle_start = idx
                current_cycle_returns = []

            # Accumulate returns in this cycle
            if idx in data.index:
                current_cycle_returns.append(data.loc[idx, 'returns'])

        return occurrences

    def validate_pattern(
        self,
        pattern: Pattern,
        data: pd.DataFrame,
    ) -> ValidationMetrics:
        """
        Validate SARIMA pattern using walk-forward analysis.

        Args:
            pattern: Pattern to validate
            data: Historical price data

        Returns:
            Validation metrics
        """
        return self.validate_pattern_with_data(
            data=data,
            occurrences=pattern.historical_occurrences,
            period_length=pattern.cycle_length_days,
        )

    def validate_pattern_with_data(
        self,
        data: pd.DataFrame,
        occurrences: list[PatternOccurrence],
        period_length: int,
    ) -> ValidationMetrics:
        """
        Validate pattern with provided occurrences.

        Args:
            data: Price data
            occurrences: Historical occurrences
            period_length: Cycle length

        Returns:
            Validation metrics
        """
        # Create signal function for walk-forward validation
        def signal_fn(df: pd.DataFrame) -> pd.Series:
            """Generate binary signal from occurrences."""
            signal = pd.Series(0, index=df.index)

            for occ in occurrences:
                # Mark dates within occurrence window as active
                mask = (df.index.date >= occ.start_date) & (df.index.date <= occ.end_date)
                signal[mask] = 1

            return signal

        # Walk-forward validation
        validator = WalkForwardValidator()
        wf_result = validator.validate(data, signal_fn)

        # Statistical tests
        pattern_returns = []
        baseline_returns = []

        signal = signal_fn(data)
        pattern_returns = data.loc[signal == 1, 'returns'].dropna().values
        baseline_returns = data.loc[signal == 0, 'returns'].dropna().values

        if len(pattern_returns) == 0 or len(baseline_returns) == 0:
            # Cannot perform statistical tests
            p_value = 1.0
            effect_size = 0.0
        else:
            t_stat, p_value = StatisticalTester.t_test(
                pattern_returns,
                baseline_returns,
            )
            effect_size = self.calculate_effect_size(pattern_returns, baseline_returns)

        # Statistical power
        statistical_power = StatisticalTester.calculate_statistical_power(
            effect_size=effect_size,
            sample_size=len(pattern_returns),
        )

        # Consistency
        consistency_score = ConsistencyAnalyzer.calculate_consistency_score(
            occurrences=occurrences,
            total_periods=len(data) // period_length,
        )

        # Recent performance
        recent_performance = RecentPerformanceAnalyzer.calculate_recent_performance(
            occurrences=[
                {
                    'start_date': occ.start_date,
                    'return_pct': occ.return_pct,
                }
                for occ in occurrences
            ],
            lookback_count=3,
        )

        last_occurrence_date = max([occ.end_date for occ in occurrences]) if occurrences else None

        # Years of data
        years_of_data = (data.index[-1] - data.index[0]).days / 365.25

        return ValidationMetrics(
            p_value=p_value,
            effect_size=effect_size,
            statistical_power=statistical_power,
            walk_forward_efficiency=wf_result.walk_forward_efficiency,
            in_sample_return=wf_result.in_sample_return,
            out_sample_return=wf_result.out_sample_return,
            consistency_score=consistency_score,
            sample_size=len(occurrences),
            years_of_data=years_of_data,
            recent_performance=recent_performance,
            last_occurrence_date=last_occurrence_date,
            sharpe_ratio=wf_result.sharpe_ratio,
            max_drawdown=wf_result.max_drawdown,
            win_rate=wf_result.win_rate,
        )

    def _predict_next_occurrence(
        self,
        occurrences: list[PatternOccurrence],
        period_length: int,
    ) -> date:
        """
        Predict next pattern occurrence.

        Args:
            occurrences: Historical occurrences
            period_length: Cycle length in days

        Returns:
            Predicted date of next occurrence
        """
        if not occurrences:
            return date.today() + timedelta(days=period_length)

        # Use most recent occurrence + period length
        last_occurrence = max(occurrences, key=lambda x: x.end_date)
        next_date = last_occurrence.end_date + timedelta(days=period_length)

        # Adjust if next occurrence is in the past
        while next_date < date.today():
            next_date += timedelta(days=period_length)

        return next_date

    def _generate_description(
        self,
        ticker: str,
        period_name: str,
        seasonal_strength: float,
        model: any,
        occurrences: list[PatternOccurrence],
    ) -> str:
        """Generate human-readable pattern description."""
        avg_return = np.mean([occ.return_pct for occ in occurrences])
        avg_return_pct = avg_return * 100

        description = (
            f"Seasonal {period_name} pattern detected in {ticker} with "
            f"{seasonal_strength:.1%} seasonal strength. "
            f"Historical occurrences show average return of {avg_return_pct:+.2f}% "
            f"during active periods. "
            f"Pattern has occurred {len(occurrences)} times over the analyzed period."
        )

        return description

    def _generate_economic_rationale(self, period_name: str) -> str:
        """Generate economic rationale for seasonal pattern."""
        rationales = {
            'annual': (
                "Annual seasonality may be driven by tax-loss harvesting (December), "
                "January Effect (small cap rally), earnings season patterns, "
                "or institutional rebalancing cycles."
            ),
            'quarterly': (
                "Quarterly patterns often align with earnings announcements, "
                "end-of-quarter window dressing by fund managers, "
                "or economic data release schedules."
            ),
            'monthly': (
                "Monthly seasonality may result from options expiration, "
                "mutual fund flows, systematic rebalancing, "
                "or Turn-of-Month effects."
            ),
        }

        return rationales.get(period_name, "Seasonal pattern with cyclical behavior.")
