"""
Walk-forward validation and statistical testing framework.

This module provides rigorous validation methodology to ensure detected patterns
are statistically significant and not the result of data mining or curve-fitting.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.utils import resample


@dataclass
class WalkForwardResult:
    """Results from walk-forward validation."""

    in_sample_return: float
    out_sample_return: float
    walk_forward_efficiency: float
    num_windows: int
    window_results: list[dict]
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float


class WalkForwardValidator:
    """
    Walk-forward validation to prevent overfitting.

    Methodology:
    1. Split data into multiple windows (in-sample + out-sample)
    2. "Train" pattern detection on in-sample data
    3. Test on out-sample (forward) data
    4. Calculate Walk-Forward Efficiency (WFE) = out-sample / in-sample performance

    WFE > 0.5 is considered acceptable (out-sample performs at least 50% as well as in-sample)
    WFE > 0.8 is excellent
    WFE >= 1.0 is exceptional (out-sample equals or exceeds in-sample)
    """

    def __init__(
        self,
        in_sample_period_days: int = 730,  # 2 years
        out_sample_period_days: int = 90,  # 3 months
        min_windows: int = 3,
    ):
        """
        Initialize walk-forward validator.

        Args:
            in_sample_period_days: Length of in-sample training period
            out_sample_period_days: Length of out-sample testing period
            min_windows: Minimum number of walk-forward windows required
        """
        self.in_sample_period = timedelta(days=in_sample_period_days)
        self.out_sample_period = timedelta(days=out_sample_period_days)
        self.min_windows = min_windows

    def validate(
        self,
        data: pd.DataFrame,
        pattern_signal_fn: Callable[[pd.DataFrame], pd.Series],
    ) -> WalkForwardResult:
        """
        Perform walk-forward validation.

        Args:
            data: Historical price data with 'returns' column
            pattern_signal_fn: Function that takes data and returns binary signal
                              (1 = pattern active, 0 = pattern inactive)

        Returns:
            Walk-forward validation results
        """
        if 'returns' not in data.columns:
            raise ValueError("Data must contain 'returns' column")

        windows = self._create_windows(data)

        if len(windows) < self.min_windows:
            raise ValueError(
                f"Insufficient data for {self.min_windows} walk-forward windows. "
                f"Got {len(windows)} windows."
            )

        window_results = []
        in_sample_returns = []
        out_sample_returns = []

        for i, (in_sample_data, out_sample_data) in enumerate(windows, 1):
            # Generate signals for both periods
            in_sample_signal = pattern_signal_fn(in_sample_data)
            out_sample_signal = pattern_signal_fn(out_sample_data)

            # Calculate returns when pattern is active
            in_ret = self._calculate_pattern_return(in_sample_data, in_sample_signal)
            out_ret = self._calculate_pattern_return(out_sample_data, out_sample_signal)

            window_results.append({
                'window': i,
                'in_sample_start': in_sample_data.index[0],
                'in_sample_end': in_sample_data.index[-1],
                'out_sample_start': out_sample_data.index[0],
                'out_sample_end': out_sample_data.index[-1],
                'in_sample_return': in_ret,
                'out_sample_return': out_ret,
            })

            in_sample_returns.append(in_ret)
            out_sample_returns.append(out_ret)

        # Calculate aggregate metrics
        avg_in_sample = np.mean(in_sample_returns)
        avg_out_sample = np.mean(out_sample_returns)

        # Walk-Forward Efficiency
        if avg_in_sample > 0:
            wfe = avg_out_sample / avg_in_sample
        else:
            wfe = 0.0

        # Calculate all returns with pattern signal for risk metrics
        all_signal = pattern_signal_fn(data)
        pattern_returns = data.loc[all_signal == 1, 'returns'].dropna()

        sharpe = self._calculate_sharpe_ratio(pattern_returns)
        max_dd = self._calculate_max_drawdown(pattern_returns)
        win_rate = (pattern_returns > 0).sum() / len(pattern_returns) if len(pattern_returns) > 0 else 0

        return WalkForwardResult(
            in_sample_return=avg_in_sample,
            out_sample_return=avg_out_sample,
            walk_forward_efficiency=wfe,
            num_windows=len(windows),
            window_results=window_results,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
        )

    def _create_windows(
        self,
        data: pd.DataFrame,
    ) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Create walk-forward windows.

        Returns:
            List of (in_sample_data, out_sample_data) tuples
        """
        windows = []
        start_date = data.index[0]
        end_date = data.index[-1]

        current_date = start_date

        while True:
            in_sample_end = current_date + self.in_sample_period
            out_sample_end = in_sample_end + self.out_sample_period

            # Check if we have enough data for this window
            if out_sample_end > end_date:
                break

            # Extract data for this window
            in_sample_data = data.loc[current_date:in_sample_end]
            out_sample_data = data.loc[in_sample_end:out_sample_end]

            if len(in_sample_data) >= 100 and len(out_sample_data) >= 20:
                windows.append((in_sample_data, out_sample_data))

            # Move to next window (50% overlap)
            current_date += self.in_sample_period / 2

        return windows

    def _calculate_pattern_return(
        self,
        data: pd.DataFrame,
        signal: pd.Series,
    ) -> float:
        """
        Calculate average return when pattern is active.

        Args:
            data: Price data with returns
            signal: Binary signal (1 = active, 0 = inactive)

        Returns:
            Average return during pattern occurrences
        """
        # Align signal with data
        signal = signal.reindex(data.index, fill_value=0)

        # Get returns when pattern is active
        pattern_returns = data.loc[signal == 1, 'returns'].dropna()

        if len(pattern_returns) == 0:
            return 0.0

        return pattern_returns.mean()

    def _calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02,
    ) -> float:
        """
        Calculate annualized Sharpe ratio.

        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Annualized Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Annualize
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1
        excess_returns = returns - daily_rf

        sharpe = excess_returns.mean() / returns.std() * np.sqrt(252)
        return sharpe

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown.

        Args:
            returns: Daily returns

        Returns:
            Maximum drawdown (positive number)
        """
        if len(returns) == 0:
            return 0.0

        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        return abs(drawdown.min())


class StatisticalTester:
    """Statistical hypothesis testing for pattern significance."""

    @staticmethod
    def t_test(
        pattern_returns: np.ndarray,
        baseline_returns: np.ndarray,
    ) -> tuple[float, float]:
        """
        Perform independent samples t-test.

        Tests null hypothesis: pattern returns = baseline returns

        Args:
            pattern_returns: Returns during pattern occurrences
            baseline_returns: Returns during baseline periods

        Returns:
            (t_statistic, p_value)
        """
        t_stat, p_value = stats.ttest_ind(
            pattern_returns,
            baseline_returns,
            equal_var=False,  # Welch's t-test
        )
        return t_stat, p_value

    @staticmethod
    def chi_square_test(
        pattern_win_rate: float,
        pattern_count: int,
        baseline_win_rate: float,
    ) -> tuple[float, float]:
        """
        Chi-square test for win rate significance.

        Tests if pattern win rate is significantly different from baseline.

        Args:
            pattern_win_rate: Win rate during pattern (0-1)
            pattern_count: Number of pattern occurrences
            baseline_win_rate: Baseline win rate (0-1)

        Returns:
            (chi2_statistic, p_value)
        """
        # Observed frequencies
        pattern_wins = int(pattern_win_rate * pattern_count)
        pattern_losses = pattern_count - pattern_wins

        # Expected frequencies (if pattern had baseline win rate)
        expected_wins = baseline_win_rate * pattern_count
        expected_losses = pattern_count - expected_wins

        observed = np.array([pattern_wins, pattern_losses])
        expected = np.array([expected_wins, expected_losses])

        chi2, p_value = stats.chisquare(observed, expected)
        return chi2, p_value

    @staticmethod
    def bootstrap_confidence_interval(
        returns: np.ndarray,
        confidence_level: float = 0.95,
        n_bootstrap: int = 10000,
    ) -> tuple[float, float]:
        """
        Calculate bootstrap confidence interval for mean return.

        Args:
            returns: Array of returns
            confidence_level: Confidence level (0-1)
            n_bootstrap: Number of bootstrap samples

        Returns:
            (lower_bound, upper_bound)
        """
        bootstrap_means = []

        for _ in range(n_bootstrap):
            sample = resample(returns, replace=True)
            bootstrap_means.append(np.mean(sample))

        alpha = 1 - confidence_level
        lower = np.percentile(bootstrap_means, alpha / 2 * 100)
        upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)

        return lower, upper

    @staticmethod
    def calculate_statistical_power(
        effect_size: float,
        sample_size: int,
        alpha: float = 0.05,
    ) -> float:
        """
        Calculate statistical power (1 - Type II error rate).

        Uses Cohen's d effect size.

        Args:
            effect_size: Cohen's d
            sample_size: Number of observations
            alpha: Significance level

        Returns:
            Statistical power (0-1)
        """
        from scipy.stats import norm

        # Critical value for two-tailed test
        z_alpha = norm.ppf(1 - alpha / 2)

        # Non-centrality parameter
        ncp = effect_size * np.sqrt(sample_size / 2)

        # Power = P(reject H0 | H1 is true)
        power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)

        return power


class ConsistencyAnalyzer:
    """Analyze pattern consistency over time."""

    @staticmethod
    def calculate_consistency_score(
        occurrences: list,
        total_periods: int,
    ) -> float:
        """
        Calculate consistency score based on occurrence frequency.

        Args:
            occurrences: List of pattern occurrences
            total_periods: Total number of periods analyzed

        Returns:
            Consistency score (0-1)
        """
        if total_periods == 0:
            return 0.0

        occurrence_rate = len(occurrences) / total_periods

        # Higher score for patterns that occur frequently and reliably
        # 80%+ occurrence rate = 1.0
        # 60-80% = 0.8-1.0
        # 40-60% = 0.6-0.8
        # <40% = proportional

        if occurrence_rate >= 0.8:
            return 1.0
        elif occurrence_rate >= 0.6:
            return 0.8 + (occurrence_rate - 0.6) * 1.0
        elif occurrence_rate >= 0.4:
            return 0.6 + (occurrence_rate - 0.4) * 1.0
        else:
            return occurrence_rate * 1.5

    @staticmethod
    def analyze_temporal_stability(
        occurrences: list[dict],
    ) -> dict:
        """
        Analyze if pattern performance is stable over time.

        Args:
            occurrences: List of occurrence dicts with 'date' and 'return_pct'

        Returns:
            Dict with stability metrics
        """
        if len(occurrences) < 3:
            return {
                'stable': False,
                'trend': None,
                'variance': None,
            }

        # Sort by date
        sorted_occs = sorted(occurrences, key=lambda x: x['start_date'])

        # Split into early and late periods
        mid_point = len(sorted_occs) // 2
        early_returns = [occ['return_pct'] for occ in sorted_occs[:mid_point]]
        late_returns = [occ['return_pct'] for occ in sorted_occs[mid_point:]]

        # Compare means
        early_mean = np.mean(early_returns)
        late_mean = np.mean(late_returns)

        # T-test for difference
        t_stat, p_value = stats.ttest_ind(early_returns, late_returns)

        # Calculate trend (linear regression over time)
        returns_array = np.array([occ['return_pct'] for occ in sorted_occs])
        time_array = np.arange(len(returns_array))

        if len(time_array) > 1:
            slope, intercept, r_value, p_val, std_err = stats.linregress(time_array, returns_array)
            trend = 'improving' if slope > 0 else 'declining'
        else:
            trend = None

        # Variance (lower is more stable)
        variance = np.var([occ['return_pct'] for occ in sorted_occs])

        return {
            'stable': p_value > 0.05,  # No significant difference between periods
            'early_mean': early_mean,
            'late_mean': late_mean,
            'trend': trend,
            'variance': variance,
            'trend_p_value': p_val if len(time_array) > 1 else None,
        }


class RecentPerformanceAnalyzer:
    """Analyze recent pattern performance."""

    @staticmethod
    def calculate_recent_performance(
        occurrences: list[dict],
        lookback_count: int = 3,
    ) -> float:
        """
        Calculate average return over last N occurrences.

        Args:
            occurrences: List of occurrence dicts with 'return_pct'
            lookback_count: Number of recent occurrences to analyze

        Returns:
            Average return of recent occurrences
        """
        if len(occurrences) == 0:
            return 0.0

        # Sort by date (most recent first)
        sorted_occs = sorted(
            occurrences,
            key=lambda x: x['start_date'],
            reverse=True,
        )

        # Get last N occurrences
        recent = sorted_occs[:lookback_count]

        if len(recent) == 0:
            return 0.0

        return np.mean([occ['return_pct'] for occ in recent])

    @staticmethod
    def check_recent_confirmation(
        occurrences: list[dict],
        max_days_ago: int = 365,
    ) -> bool:
        """
        Check if pattern has occurred recently.

        Args:
            occurrences: List of occurrence dicts
            max_days_ago: Maximum days since last occurrence

        Returns:
            True if pattern occurred within last N days
        """
        if len(occurrences) == 0:
            return False

        # Get most recent occurrence
        most_recent = max(occurrences, key=lambda x: x['start_date'])
        days_ago = (date.today() - most_recent['start_date']).days

        return days_ago <= max_days_ago
