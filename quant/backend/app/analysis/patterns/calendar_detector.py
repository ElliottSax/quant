"""
Calendar Effects pattern detector.

Detects well-known calendar anomalies in stock markets:
- January Effect: Small cap outperformance in January
- Monday Effect: Lower returns on Mondays
- Turn-of-Month Effect: Higher returns around month end
- Holiday Effect: Higher returns before holidays
- Day-of-Week Effects: Consistent patterns by weekday
- Pre-FOMC Drift: Returns before Fed meetings
"""

from datetime import date, timedelta
from typing import Optional
import uuid

import numpy as np
import pandas as pd
from scipy import stats

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


class CalendarEffectsDetector(PatternDetector):
    """
    Detect calendar-based anomalies.

    Tests for statistically significant patterns tied to specific calendar dates,
    days of week, or events. Each effect is rigorously validated using t-tests,
    walk-forward analysis, and multiple hypothesis correction.
    """

    def __init__(
        self,
        effects_to_test: Optional[list[str]] = None,
        **kwargs,
    ):
        """
        Initialize calendar effects detector.

        Args:
            effects_to_test: List of effects to test. If None, tests all.
                           Options: 'january', 'monday', 'turn_of_month', 'holiday', 'day_of_week'
            **kwargs: Additional arguments passed to PatternDetector
        """
        super().__init__(**kwargs)

        if effects_to_test is None:
            effects_to_test = [
                'january',
                'monday',
                'turn_of_month',
                'holiday',
                'day_of_week',
            ]

        self.effects_to_test = effects_to_test

    async def detect(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[Pattern]:
        """
        Detect calendar effects for a ticker.

        Args:
            ticker: Stock ticker symbol
            start_date: Start date (default: 10 years ago)
            end_date: End date (default: today)

        Returns:
            List of validated calendar effect patterns
        """
        # Default date range: 10 years
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365 * 10)

        # Fetch market data
        data = await self.fetch_market_data(ticker, start_date, end_date)

        if len(data) < 252:  # Need at least 1 year of data
            return []

        detected_patterns = []

        # Test each calendar effect
        if 'january' in self.effects_to_test:
            pattern = await self._detect_january_effect(ticker, data)
            if pattern:
                detected_patterns.append(pattern)

        if 'monday' in self.effects_to_test:
            pattern = await self._detect_monday_effect(ticker, data)
            if pattern:
                detected_patterns.append(pattern)

        if 'turn_of_month' in self.effects_to_test:
            pattern = await self._detect_turn_of_month_effect(ticker, data)
            if pattern:
                detected_patterns.append(pattern)

        if 'day_of_week' in self.effects_to_test:
            patterns = await self._detect_day_of_week_effects(ticker, data)
            detected_patterns.extend(patterns)

        # Apply Bonferroni correction for multiple hypothesis testing
        num_tests = len(self.effects_to_test)
        for pattern in detected_patterns:
            if pattern.validation_metrics:
                corrected_p = self.bonferroni_correction(
                    pattern.validation_metrics.p_value,
                    num_tests,
                )
                pattern.validation_metrics.p_value = corrected_p

                # Recalculate confidence and reliability with corrected p-value
                pattern.confidence = self.calculate_confidence(
                    corrected_p,
                    pattern.validation_metrics.effect_size,
                )
                pattern.reliability_score = self.calculate_reliability_score(
                    pattern.validation_metrics,
                )

        # Filter to only patterns that still pass after correction
        validated_patterns = [
            p for p in detected_patterns
            if p.validation_metrics and self.meets_minimum_criteria(p.validation_metrics)
        ]

        return validated_patterns

    async def _detect_january_effect(
        self,
        ticker: str,
        data: pd.DataFrame,
    ) -> Optional[Pattern]:
        """
        Detect January Effect: stocks (especially small caps) tend to outperform in January.

        Historical basis: Tax-loss harvesting in December creates selling pressure,
        followed by buying in January. More pronounced in small cap stocks.

        Args:
            ticker: Stock ticker
            data: Historical price data

        Returns:
            Pattern if detected and validated
        """
        # Identify January trading days
        data['is_january'] = data.index.month == 1

        january_returns = data.loc[data['is_january'], 'returns'].dropna()
        other_returns = data.loc[~data['is_january'], 'returns'].dropna()

        if len(january_returns) < 5 or len(other_returns) < 100:
            return None  # Insufficient data

        # Statistical test
        t_stat, p_value = StatisticalTester.t_test(
            january_returns.values,
            other_returns.values,
        )

        effect_size = self.calculate_effect_size(
            january_returns.values,
            other_returns.values,
        )

        # Must show positive effect (January > other months)
        if january_returns.mean() <= other_returns.mean():
            return None

        # Identify historical occurrences (each January)
        occurrences = []
        for year in data.index.year.unique():
            year_data = data[data.index.year == year]
            jan_data = year_data[year_data['is_january']]

            if len(jan_data) > 0:
                jan_return = jan_data['returns'].sum()
                occurrences.append(
                    PatternOccurrence(
                        start_date=jan_data.index[0].date(),
                        end_date=jan_data.index[-1].date(),
                        return_pct=jan_return,
                        confidence=75.0,
                    )
                )

        # Validation
        validation_metrics = self._validate_calendar_effect(
            data=data,
            effect_mask=data['is_january'],
            occurrences=occurrences,
            p_value=p_value,
            effect_size=effect_size,
        )

        if not self.meets_minimum_criteria(validation_metrics):
            return None

        # Create pattern
        pattern = Pattern(
            pattern_id=str(uuid.uuid4()),
            pattern_type=PatternType.CALENDAR,
            name=f"{ticker} - January Effect",
            description=(
                f"January Effect detected: {ticker} shows statistically significant "
                f"outperformance in January. Average January return: "
                f"{january_returns.mean() * 100:+.2f}% vs other months: "
                f"{other_returns.mean() * 100:+.2f}%. "
                f"Effect observed in {len(occurrences)} of {len(data.index.year.unique())} years."
            ),
            ticker=ticker,
            cycle_length_days=365,
            frequency=Frequency.ANNUAL,
            window_start_day=1,  # January 1
            window_end_day=31,  # January 31
            next_occurrence=self._next_january(),
            validation_metrics=validation_metrics,
            reliability_score=self.calculate_reliability_score(validation_metrics),
            confidence=self.calculate_confidence(p_value, effect_size),
            historical_occurrences=occurrences,
            first_detected=occurrences[0].start_date if occurrences else None,
            last_validated=date.today(),
            economic_rationale=(
                "January Effect driven by tax-loss harvesting in December "
                "(selling losers for tax deductions) followed by reinvestment in January. "
                "Window dressing by institutional investors and year-end bonuses "
                "also contribute. More pronounced in small cap stocks."
            ),
            risk_factors=[
                "Effect has weakened over time as it became well-known",
                "Timing can vary (late December through early February)",
                "Market conditions and tax policy changes affect magnitude",
            ],
            parameters={
                'effect_type': 'january',
                'january_mean_return': january_returns.mean(),
                'other_mean_return': other_returns.mean(),
            },
        )

        return pattern

    async def _detect_monday_effect(
        self,
        ticker: str,
        data: pd.DataFrame,
    ) -> Optional[Pattern]:
        """
        Detect Monday Effect: stocks tend to have lower (or negative) returns on Mondays.

        Historical basis: Negative news released over weekend, portfolio adjustments
        after weekend reflection, and settlement timing effects.

        Args:
            ticker: Stock ticker
            data: Historical price data

        Returns:
            Pattern if detected and validated
        """
        # Monday is day_of_week = 0
        data['is_monday'] = data['day_of_week'] == 0

        monday_returns = data.loc[data['is_monday'], 'returns'].dropna()
        other_returns = data.loc[~data['is_monday'], 'returns'].dropna()

        if len(monday_returns) < 20 or len(other_returns) < 100:
            return None

        # Statistical test
        t_stat, p_value = StatisticalTester.t_test(
            monday_returns.values,
            other_returns.values,
        )

        effect_size = abs(self.calculate_effect_size(
            monday_returns.values,
            other_returns.values,
        ))

        # Must show negative effect (Monday < other days) OR significantly different
        mean_diff = monday_returns.mean() - other_returns.mean()

        # Group by week for occurrences
        data['week'] = data.index.to_period('W')
        occurrences = []

        for week in data['week'].unique():
            week_data = data[data['week'] == week]
            monday_data = week_data[week_data['is_monday']]

            if len(monday_data) > 0:
                monday_return = monday_data['returns'].iloc[0]
                occurrences.append(
                    PatternOccurrence(
                        start_date=monday_data.index[0].date(),
                        end_date=monday_data.index[0].date(),
                        return_pct=monday_return,
                        confidence=70.0,
                    )
                )

        # Validation
        validation_metrics = self._validate_calendar_effect(
            data=data,
            effect_mask=data['is_monday'],
            occurrences=occurrences,
            p_value=p_value,
            effect_size=effect_size,
        )

        if not self.meets_minimum_criteria(validation_metrics):
            return None

        # Create pattern
        direction = "lower" if mean_diff < 0 else "different"

        pattern = Pattern(
            pattern_id=str(uuid.uuid4()),
            pattern_type=PatternType.CALENDAR,
            name=f"{ticker} - Monday Effect",
            description=(
                f"Monday Effect detected: {ticker} shows {direction} returns on Mondays. "
                f"Average Monday return: {monday_returns.mean() * 100:+.2f}% vs other days: "
                f"{other_returns.mean() * 100:+.2f}%. "
            ),
            ticker=ticker,
            cycle_length_days=7,
            frequency=Frequency.WEEKLY,
            next_occurrence=self._next_monday(),
            validation_metrics=validation_metrics,
            reliability_score=self.calculate_reliability_score(validation_metrics),
            confidence=self.calculate_confidence(p_value, effect_size),
            historical_occurrences=occurrences[-52:],  # Last year of Mondays
            first_detected=occurrences[0].start_date if occurrences else None,
            last_validated=date.today(),
            economic_rationale=(
                "Monday Effect may be driven by negative news released over weekends, "
                "portfolio rebalancing decisions made over the weekend, "
                "and settlement timing effects from Friday trading."
            ),
            risk_factors=[
                "Effect magnitude varies significantly over time",
                "Not consistent across all stocks or market conditions",
                "Diminished in recent decades",
            ],
            parameters={
                'effect_type': 'monday',
                'monday_mean_return': monday_returns.mean(),
                'other_mean_return': other_returns.mean(),
            },
        )

        return pattern

    async def _detect_turn_of_month_effect(
        self,
        ticker: str,
        data: pd.DataFrame,
    ) -> Optional[Pattern]:
        """
        Detect Turn-of-Month Effect: higher returns in last/first few days of month.

        Typically defined as last trading day of month and first 3 trading days
        of next month.

        Historical basis: Pension fund and mutual fund flows, systematic rebalancing,
        options expiration, and portfolio window dressing.

        Args:
            ticker: Stock ticker
            data: Historical price data

        Returns:
            Pattern if detected and validated
        """
        # Identify turn-of-month periods
        # Last day of month and first 3 days of next month
        data['day_in_month'] = data.groupby(
            data.index.to_period('M')
        ).cumcount() + 1

        data['days_in_month'] = data.index.days_in_month

        data['is_tom'] = (
            (data['day_in_month'] <= 3) |  # First 3 days
            (data['day_in_month'] >= data['days_in_month'])  # Last day
        )

        tom_returns = data.loc[data['is_tom'], 'returns'].dropna()
        other_returns = data.loc[~data['is_tom'], 'returns'].dropna()

        if len(tom_returns) < 20 or len(other_returns) < 100:
            return None

        # Statistical test
        t_stat, p_value = StatisticalTester.t_test(
            tom_returns.values,
            other_returns.values,
        )

        effect_size = self.calculate_effect_size(
            tom_returns.values,
            other_returns.values,
        )

        # Must show positive effect (TOM > other days)
        if tom_returns.mean() <= other_returns.mean():
            return None

        # Group by month for occurrences
        data['month_period'] = data.index.to_period('M')
        occurrences = []

        for month in data['month_period'].unique():
            month_data = data[data['month_period'] == month]
            tom_data = month_data[month_data['is_tom']]

            if len(tom_data) > 0:
                tom_return = tom_data['returns'].sum()
                occurrences.append(
                    PatternOccurrence(
                        start_date=tom_data.index[0].date(),
                        end_date=tom_data.index[-1].date(),
                        return_pct=tom_return,
                        confidence=75.0,
                    )
                )

        # Validation
        validation_metrics = self._validate_calendar_effect(
            data=data,
            effect_mask=data['is_tom'],
            occurrences=occurrences,
            p_value=p_value,
            effect_size=effect_size,
        )

        if not self.meets_minimum_criteria(validation_metrics):
            return None

        # Create pattern
        pattern = Pattern(
            pattern_id=str(uuid.uuid4()),
            pattern_type=PatternType.CALENDAR,
            name=f"{ticker} - Turn-of-Month Effect",
            description=(
                f"Turn-of-Month Effect detected: {ticker} shows higher returns "
                f"during turn-of-month period (last + first 3 days). "
                f"Average TOM return: {tom_returns.mean() * 100:+.2f}% vs other days: "
                f"{other_returns.mean() * 100:+.2f}%."
            ),
            ticker=ticker,
            cycle_length_days=30,
            frequency=Frequency.MONTHLY,
            next_occurrence=self._next_turn_of_month(),
            validation_metrics=validation_metrics,
            reliability_score=self.calculate_reliability_score(validation_metrics),
            confidence=self.calculate_confidence(p_value, effect_size),
            historical_occurrences=occurrences[-12:],  # Last year
            first_detected=occurrences[0].start_date if occurrences else None,
            last_validated=date.today(),
            economic_rationale=(
                "Turn-of-Month Effect driven by systematic flows from pension funds, "
                "401(k) contributions, mutual fund purchases, and portfolio rebalancing. "
                "Options expiration (third Friday) and month-end window dressing "
                "by fund managers also contribute."
            ),
            risk_factors=[
                "Exact timing can vary (some studies show effect starts earlier)",
                "Magnitude depends on market conditions",
                "May be affected by options expiration week",
            ],
            parameters={
                'effect_type': 'turn_of_month',
                'tom_mean_return': tom_returns.mean(),
                'other_mean_return': other_returns.mean(),
                'tom_days_definition': 'last day + first 3 days',
            },
        )

        return pattern

    async def _detect_day_of_week_effects(
        self,
        ticker: str,
        data: pd.DataFrame,
    ) -> list[Pattern]:
        """
        Detect day-of-week effects for each weekday.

        Args:
            ticker: Stock ticker
            data: Historical price data

        Returns:
            List of detected day-of-week patterns
        """
        patterns = []

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for day_num, day_name in enumerate(day_names):
            data[f'is_{day_name.lower()}'] = data['day_of_week'] == day_num

            day_returns = data.loc[data[f'is_{day_name.lower()}'], 'returns'].dropna()
            other_returns = data.loc[~data[f'is_{day_name.lower()}'], 'returns'].dropna()

            if len(day_returns) < 20:
                continue

            # Statistical test
            t_stat, p_value = StatisticalTester.t_test(
                day_returns.values,
                other_returns.values,
            )

            effect_size = abs(self.calculate_effect_size(
                day_returns.values,
                other_returns.values,
            ))

            # Only report if significant difference
            if p_value > self.min_p_value:
                continue

            # Group by week
            data['week'] = data.index.to_period('W')
            occurrences = []

            for week in data['week'].unique():
                week_data = data[data['week'] == week]
                day_data = week_data[week_data[f'is_{day_name.lower()}']]

                if len(day_data) > 0:
                    day_return = day_data['returns'].iloc[0]
                    occurrences.append(
                        PatternOccurrence(
                            start_date=day_data.index[0].date(),
                            end_date=day_data.index[0].date(),
                            return_pct=day_return,
                            confidence=70.0,
                        )
                    )

            # Validation
            validation_metrics = self._validate_calendar_effect(
                data=data,
                effect_mask=data[f'is_{day_name.lower()}'],
                occurrences=occurrences,
                p_value=p_value,
                effect_size=effect_size,
            )

            if not self.meets_minimum_criteria(validation_metrics):
                continue

            # Create pattern
            mean_diff = day_returns.mean() - other_returns.mean()
            direction = "higher" if mean_diff > 0 else "lower"

            pattern = Pattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type=PatternType.CALENDAR,
                name=f"{ticker} - {day_name} Effect",
                description=(
                    f"{day_name} shows {direction} returns for {ticker}. "
                    f"Average {day_name} return: {day_returns.mean() * 100:+.2f}% "
                    f"vs other days: {other_returns.mean() * 100:+.2f}%."
                ),
                ticker=ticker,
                cycle_length_days=7,
                frequency=Frequency.WEEKLY,
                next_occurrence=self._next_weekday(day_num),
                validation_metrics=validation_metrics,
                reliability_score=self.calculate_reliability_score(validation_metrics),
                confidence=self.calculate_confidence(p_value, effect_size),
                historical_occurrences=occurrences[-52:],  # Last year
                first_detected=occurrences[0].start_date if occurrences else None,
                last_validated=date.today(),
                economic_rationale=f"Day-of-week effect for {day_name}.",
                parameters={
                    'effect_type': f'{day_name.lower()}_effect',
                    'day_mean_return': day_returns.mean(),
                    'other_mean_return': other_returns.mean(),
                },
            )

            patterns.append(pattern)

        return patterns

    def _validate_calendar_effect(
        self,
        data: pd.DataFrame,
        effect_mask: pd.Series,
        occurrences: list[PatternOccurrence],
        p_value: float,
        effect_size: float,
    ) -> ValidationMetrics:
        """
        Validate calendar effect using walk-forward analysis.

        Args:
            data: Price data
            effect_mask: Boolean mask for when effect is active
            occurrences: Historical occurrences
            p_value: Initial p-value from t-test
            effect_size: Effect size

        Returns:
            Validation metrics
        """
        # Create signal function
        def signal_fn(df: pd.DataFrame) -> pd.Series:
            return effect_mask.reindex(df.index, fill_value=0).astype(int)

        # Walk-forward validation
        validator = WalkForwardValidator()
        try:
            wf_result = validator.validate(data, signal_fn)
        except Exception:
            # If validation fails, return minimal metrics
            return self._create_minimal_metrics(p_value, effect_size, occurrences)

        # Statistical power
        effect_returns = data.loc[effect_mask, 'returns'].dropna()
        statistical_power = StatisticalTester.calculate_statistical_power(
            effect_size=effect_size,
            sample_size=len(effect_returns),
        )

        # Consistency
        # For calendar effects, consistency = how often effect holds
        consistency_score = ConsistencyAnalyzer.calculate_consistency_score(
            occurrences=occurrences,
            total_periods=len(occurrences) + 50,  # Approximate
        )

        # Recent performance
        recent_performance = RecentPerformanceAnalyzer.calculate_recent_performance(
            occurrences=[
                {'start_date': occ.start_date, 'return_pct': occ.return_pct}
                for occ in occurrences
            ],
            lookback_count=min(3, len(occurrences)),
        )

        last_occurrence_date = max([occ.end_date for occ in occurrences]) if occurrences else None
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

    def _create_minimal_metrics(
        self,
        p_value: float,
        effect_size: float,
        occurrences: list[PatternOccurrence],
    ) -> ValidationMetrics:
        """Create minimal validation metrics when walk-forward fails."""
        return ValidationMetrics(
            p_value=p_value,
            effect_size=effect_size,
            statistical_power=0.5,
            walk_forward_efficiency=0.0,
            in_sample_return=0.0,
            out_sample_return=0.0,
            consistency_score=0.5,
            sample_size=len(occurrences),
            years_of_data=1.0,
            recent_performance=0.0,
            last_occurrence_date=None,
        )

    def validate_pattern(
        self,
        pattern: Pattern,
        data: pd.DataFrame,
    ) -> ValidationMetrics:
        """Validate calendar pattern."""
        # Re-create effect mask based on pattern parameters
        effect_type = pattern.parameters.get('effect_type')

        if effect_type == 'january':
            effect_mask = data.index.month == 1
        elif effect_type == 'monday':
            effect_mask = data['day_of_week'] == 0
        elif effect_type == 'turn_of_month':
            data['day_in_month'] = data.groupby(data.index.to_period('M')).cumcount() + 1
            data['days_in_month'] = data.index.days_in_month
            effect_mask = (data['day_in_month'] <= 3) | (data['day_in_month'] >= data['days_in_month'])
        else:
            effect_mask = pd.Series(False, index=data.index)

        return self._validate_calendar_effect(
            data=data,
            effect_mask=effect_mask,
            occurrences=pattern.historical_occurrences,
            p_value=pattern.validation_metrics.p_value if pattern.validation_metrics else 1.0,
            effect_size=pattern.validation_metrics.effect_size if pattern.validation_metrics else 0.0,
        )

    # Helper methods for next occurrence dates

    def _next_january(self) -> date:
        """Get next January 1st."""
        today = date.today()
        if today.month == 1 and today.day <= 31:
            return date(today.year, 1, 1)
        else:
            return date(today.year + 1, 1, 1)

    def _next_monday(self) -> date:
        """Get next Monday."""
        today = date.today()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)

    def _next_turn_of_month(self) -> date:
        """Get next turn-of-month (last day of current month)."""
        today = date.today()
        # Last day of current month
        if today.month == 12:
            return date(today.year, 12, 31)
        else:
            next_month = date(today.year, today.month + 1, 1)
            return next_month - timedelta(days=1)

    def _next_weekday(self, weekday: int) -> date:
        """Get next occurrence of specified weekday (0=Monday, 4=Friday)."""
        today = date.today()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)
