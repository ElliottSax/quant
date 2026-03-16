---
title: "Cointegration Trading: Finding Long-Term Pair Relationships"
description: "Master cointegration analysis for trading with Engle-Granger and Johansen tests. Build mean-reversion strategies on statistically validated relationships."
date: "2026-03-17"
author: "Dr. James Chen"
category: "Trading Strategies"
tags: ["cointegration", "pairs trading", "mean reversion", "Engle-Granger", "Johansen test"]
keywords: ["cointegration trading strategy", "Engle-Granger test trading", "Johansen cointegration"]
---
# Cointegration Trading: Finding Long-Term Pair Relationships

Cointegration is the statistical concept that underpins the most rigorous forms of [pairs trading](/blog/pairs-trading-strategy-guide) and [statistical arbitrage](/blog/crypto-statistical-arbitrage). Two price series are cointegrated when their linear combination is stationary, even though each individual series is non-stationary. In practical terms, this means the spread between the two securities tends to revert to a stable long-run equilibrium, creating a tradable signal whenever it deviates too far.

Unlike simple correlation, cointegration provides a theoretically grounded reason to expect [mean reversion](/blog/mean-reversion-strategies-guide). This guide covers the testing methodologies, implementation details, and strategy construction for cointegration-[based trading](/blog/entropy-based-trading).

## Key Takeaways

- **Cointegration implies a stable equilibrium** between two price series, not just short-term co-movement.
- **Engle-Granger is the standard two-step test** for pairwise cointegration, while Johansen handles multiple series simultaneously.
- **The hedge ratio is not static.** Use rolling estimation or Kalman filters for dynamic adaptation.
- **In-sample cointegration does not guarantee out-of-sample persistence.** Always validate on unseen data.

## Understanding Cointegration vs Correlation

The distinction between correlation and cointegration is fundamental and frequently misunderstood.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

def demonstrate_difference():
    """
    Show that correlation != cointegration with synthetic examples.
    """
    np.random.seed(42)
    n = 500

    # Case 1: Correlated but NOT cointegrated
    # Two independent random walks with correlated innovations
    eps1 = np.random.randn(n)
    eps2 = 0.8 * eps1 + 0.6 * np.random.randn(n)
    corr_not_coint_a = np.cumsum(eps1)
    corr_not_coint_b = np.cumsum(eps2)
    spread_1 = corr_not_coint_a - corr_not_coint_b

    # Case 2: Cointegrated (and correlated)
    # Series B follows Series A with a stationary spread
    common_trend = np.cumsum(np.random.randn(n) * 0.5)
    coint_a = common_trend + np.random.randn(n) * 0.3
    coint_b = 0.8 * common_trend + np.random.randn(n) * 0.3
    spread_2 = coint_a - 0.8 * coint_b

    # Test both
    corr_1 = np.corrcoef(corr_not_coint_a, corr_not_coint_b)[0, 1]
    _, p_coint_1, _ = coint(corr_not_coint_a, corr_not_coint_b)

    corr_2 = np.corrcoef(coint_a, coint_b)[0, 1]
    _, p_coint_2, _ = coint(coint_a, coint_b)

    print("Case 1: Correlated Random Walks")
    print(f"  Correlation: {corr_1:.3f}")
    print(f"  Cointegration p-value: {p_coint_1:.4f}")
    print(f"  Cointegrated: {'Yes' if p_coint_1 < 0.05 else 'No'}")

    print("\nCase 2: Cointegrated Series")
    print(f"  Correlation: {corr_2:.3f}")
    print(f"  Cointegration p-value: {p_coint_2:.4f}")
    print(f"  Cointegrated: {'Yes' if p_coint_2 < 0.05 else 'No'}")

demonstrate_difference()
```

## Engle-Granger Two-Step Test

The Engle-Granger method is the standard pairwise cointegration test, proceeding in two stages: (1) estimate the cointegrating regression, and (2) test the residuals for stationarity.

```python
def engle_granger_test(
    series_a: pd.Series,
    series_b: pd.Series,
    significance: float = 0.05,
) -> dict:
    """
    Full Engle-Granger cointegration test with detailed output.

    Steps:
    1. Regress A on B (OLS) to find hedge ratio (beta)
    2. Compute residuals (spread)
    3. Test residuals for stationarity (ADF)
    """
    # Step 1: Cointegrating regression
    X = add_constant(series_b)
    model = OLS(series_a, X).fit()

    alpha = model.params.iloc[0]  # intercept
    beta = model.params.iloc[1]   # hedge ratio

    # Step 2: Compute residuals
    spread = series_a - beta * series_b - alpha

    # Step 3: ADF test on residuals
    # Use critical values for cointegration (not standard ADF)
    adf_stat, adf_pvalue, _, _, critical_values, _ = adfuller(spread, autolag="AIC")

    # Also run the built-in cointegration test for verification
    coint_stat, coint_pvalue, _ = coint(series_a, series_b)

    # Half-life of mean reversion
    spread_lag = spread.shift(1)
    delta = spread.diff()
    valid = ~(spread_lag.isna() | delta.isna())
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression()
    lr.fit(spread_lag[valid].values.reshape(-1, 1), delta[valid].values)
    theta = lr.coef_[0]
    half_life = -np.log(2) / np.log(1 + theta) if theta < 0 else np.inf

    is_cointegrated = coint_pvalue < significance

    result = {
        "cointegrated": is_cointegrated,
        "coint_pvalue": coint_pvalue,
        "coint_statistic": coint_stat,
        "adf_statistic": adf_stat,
        "adf_pvalue": adf_pvalue,
        "hedge_ratio": beta,
        "intercept": alpha,
        "r_squared": model.rsquared,
        "spread": spread,
        "half_life": half_life,
        "critical_values": critical_values,
    }

    print(f"Cointegration Test Results:")
    print(f"  Hedge ratio (beta): {beta:.4f}")
    print(f"  ADF statistic: {adf_stat:.4f}")
    print(f"  p-value: {coint_pvalue:.4f}")
    print(f"  Half-life: {half_life:.1f} days")
    print(f"  Cointegrated: {is_cointegrated}")

    return result
```

## Johansen Cointegration Test

For systems of three or more securities, the Johansen test identifies the number of cointegrating relationships and their associated vectors.

```python
from statsmodels.tsa.vector_ar.vecm import coint_johansen

def johansen_test(
    prices: pd.DataFrame,
    det_order: int = 0,
    k_ar_diff: int = 1,
    significance_level: str = "5%",
) -> dict:
    """
    Johansen cointegration test for multiple price series.

    Args:
        prices: DataFrame with each column a price series
        det_order: -1 (no deterministic), 0 (constant), 1 (trend)
        k_ar_diff: number of lagged differences in VECM

    Returns:
        Number of cointegrating relationships and vectors
    """
    result = coint_johansen(prices.dropna(), det_order, k_ar_diff)

    # Trace test
    sig_idx = {"1%": 2, "5%": 1, "10%": 0}[significance_level]
    trace_stats = result.lr1          # Trace statistics
    trace_crits = result.cvt[:, sig_idx]  # Critical values

    # Maximum eigenvalue test
    eigen_stats = result.lr2
    eigen_crits = result.cvm[:, sig_idx]

    n_coint_trace = sum(trace_stats > trace_crits)
    n_coint_eigen = sum(eigen_stats > eigen_crits)

    # Cointegrating vectors (eigenvectors)
    vectors = result.evec

    print(f"Johansen Test Results ({significance_level} significance):")
    print(f"  Trace test: {n_coint_trace} cointegrating relationships")
    print(f"  Max-eigenvalue test: {n_coint_eigen} cointegrating relationships")
    print(f"\n  Trace Statistics vs Critical Values:")
    for i, (stat, crit) in enumerate(zip(trace_stats, trace_crits)):
        sig = "*" if stat > crit else ""
        print(f"    r <= {i}: {stat:.4f} vs {crit:.4f} {sig}")

    print(f"\n  Cointegrating Vectors:")
    for i in range(min(n_coint_trace, 3)):
        vec = vectors[:, i]
        normalized = vec / vec[0]
        labels = prices.columns.tolist()
        vec_str = " + ".join([f"{w:.4f}*{l}" for w, l in zip(normalized, labels)])
        print(f"    Vector {i+1}: {vec_str}")

    return {
        "n_cointegrating_trace": n_coint_trace,
        "n_cointegrating_eigen": n_coint_eigen,
        "trace_statistics": trace_stats,
        "trace_critical_values": trace_crits,
        "eigen_statistics": eigen_stats,
        "eigen_critical_values": eigen_crits,
        "eigenvectors": vectors,
        "eigenvalues": result.eig,
    }
```

## Dynamic Hedge Ratio with Rolling OLS

Static hedge ratios estimated on historical data degrade over time. Rolling OLS adapts the ratio to changing market conditions.

```python
class RollingHedgeRatio:
    """
    Compute hedge ratios using a rolling regression window.
    """

    def __init__(self, window: int = 60):
        self.window = window

    def compute(
        self, series_a: pd.Series, series_b: pd.Series
    ) -> pd.DataFrame:
        """
        Rolling OLS hedge ratio with R-squared tracking.
        """
        results = []

        for i in range(self.window, len(series_a)):
            window_a = series_a.iloc[i - self.window:i]
            window_b = series_b.iloc[i - self.window:i]

            X = add_constant(window_b)
            model = OLS(window_a, X).fit()

            results.append({
                "date": series_a.index[i],
                "hedge_ratio": model.params.iloc[1],
                "intercept": model.params.iloc[0],
                "r_squared": model.rsquared,
                "std_error": model.bse.iloc[1],
            })

        df = pd.DataFrame(results).set_index("date")
        return df

    def compute_spread(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        hedge_df: pd.DataFrame,
    ) -> pd.Series:
        """Compute spread using dynamic hedge ratio."""
        common = hedge_df.index.intersection(series_a.index)
        spread = (
            series_a.loc[common]
            - hedge_df.loc[common, "hedge_ratio"] * series_b.loc[common]
            - hedge_df.loc[common, "intercept"]
        )
        return spread
```

## Building the Complete Strategy

Combine all components into a tradeable strategy with proper risk controls.

```python
class CointegrationStrategy:
    """
    Complete cointegration trading strategy.
    """

    def __init__(
        self,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        stop_z: float = 4.0,
        zscore_lookback: int = 60,
        hedge_lookback: int = 60,
        recoint_period: int = 63,  # Re-test cointegration quarterly
    ):
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        self.zscore_lookback = zscore_lookback
        self.hedge_lookback = hedge_lookback
        self.recoint_period = recoint_period

    def run(
        self, prices_a: pd.Series, prices_b: pd.Series
    ) -> pd.DataFrame:
        """Execute the full strategy pipeline."""

        # 1. Compute rolling hedge ratio
        rhr = RollingHedgeRatio(self.hedge_lookback)
        hedge_df = rhr.compute(prices_a, prices_b)

        # 2. Compute spread
        spread = rhr.compute_spread(prices_a, prices_b, hedge_df)

        # 3. Compute z-score
        spread_mean = spread.rolling(self.zscore_lookback).mean()
        spread_std = spread.rolling(self.zscore_lookback).std()
        zscore = (spread - spread_mean) / spread_std

        # 4. Generate signals with periodic cointegration check
        signals = pd.Series(0.0, index=zscore.index)
        position = 0
        last_coint_check = 0
        coint_valid = True

        for i in range(1, len(zscore)):
            z = zscore.iloc[i]

            # Periodic cointegration re-validation
            if i - last_coint_check >= self.recoint_period:
                window_a = prices_a.loc[:zscore.index[i]].iloc[-252:]
                window_b = prices_b.loc[:zscore.index[i]].iloc[-252:]
                if len(window_a) >= 100:
                    _, p, _ = coint(window_a, window_b)
                    coint_valid = p < 0.10  # Relaxed for re-check
                    last_coint_check = i

            if not coint_valid:
                position = 0  # Exit if cointegration breaks
            elif position == 0:
                if z < -self.entry_z:
                    position = 1
                elif z > self.entry_z:
                    position = -1
            elif position == 1:
                if z > -self.exit_z or z > self.stop_z:
                    position = 0
            elif position == -1:
                if z < self.exit_z or z < -self.stop_z:
                    position = 0

            signals.iloc[i] = position

        # 5. Compute returns
        hr = hedge_df["hedge_ratio"]
        ret_a = prices_a.pct_change()
        ret_b = prices_b.pct_change()

        common = signals.index
        strategy_ret = signals * (
            ret_a.loc[common] - hr.loc[common] * ret_b.loc[common]
        ) / (1 + hr.loc[common].abs())

        return pd.DataFrame({
            "signal": signals,
            "zscore": zscore,
            "spread": spread,
            "hedge_ratio": hr,
            "strategy_return": strategy_ret,
            "cumulative": (1 + strategy_ret.fillna(0)).cumprod(),
        })
```

## Performance Metrics for Pair Strategies

Pair strategies need specialized metrics beyond standard Sharpe ratios.

```python
def pair_performance_report(results: pd.DataFrame) -> dict:
    """Generate pair-trading-specific performance metrics."""
    ret = results["strategy_return"].dropna()
    signals = results["signal"]

    # Trade counting
    signal_changes = signals.diff().abs()
    roundtrips = (signal_changes > 0).sum() // 2

    # Time in market
    time_in_market = (signals != 0).mean()

    # Average trade duration
    trades = []
    start = None
    for i in range(len(signals)):
        if signals.iloc[i] != 0 and start is None:
            start = i
        elif signals.iloc[i] == 0 and start is not None:
            trades.append(i - start)
            start = None
    avg_duration = np.mean(trades) if trades else 0

    report = {
        "annual_return": ret.mean() * 252,
        "annual_vol": ret.std() * np.sqrt(252),
        "sharpe_ratio": ret.mean() / ret.std() * np.sqrt(252) if ret.std() > 0 else 0,
        "total_roundtrips": roundtrips,
        "avg_trade_duration_days": avg_duration,
        "time_in_market": time_in_market,
        "max_drawdown": (
            (results["cumulative"].cummax() - results["cumulative"])
            / results["cumulative"].cummax()
        ).max(),
    }
    return report
```

## FAQ

### How often should I re-test cointegration for existing pairs?

Re-test at least quarterly (every 63 trading days) using a rolling window of at least 1 year. If the p-value rises above 0.10, begin tightening position sizes. If it rises above 0.20, close the position. Cointegration breakdowns are often preceded by fundamental changes like mergers, regulatory shifts, or business model pivots.

### Can cointegration work with ETFs instead of individual stocks?

ETFs are actually excellent candidates for cointegration trading because they track well-defined baskets with stable compositions. Pairs like XLE/USO (energy), GLD/GDX (gold), or IWM/IWN (small cap value/growth) often exhibit strong cointegration. ETF pairs also have lower borrowing costs and better liquidity than individual stock pairs.

### What is the minimum data length needed to test for cointegration?

At minimum, use 2 years (approximately 500 trading days) for cointegration testing. The Engle-Granger test has low power (high false-negative rate) on short samples. Longer samples (3-5 years) provide more reliable results but risk including structural breaks. A practical approach is to test on 3-5 years of data and validate on the most recent 1 year.

### How does the hedge ratio relate to beta in CAPM?

The cointegration hedge ratio is analogous to but distinct from CAPM beta. CAPM beta is estimated from returns and measures systematic risk exposure. The cointegration hedge ratio is estimated from price levels and represents the long-run equilibrium relationship. For cointegration trading, always use the price-level hedge ratio, not the returns-based beta.

### What causes cointegration to break down?

The most common causes are: (1) fundamental divergence such as a merger, spin-off, or major strategic change, (2) sector rotation where one stock moves to a different peer group, (3) liquidity changes such as one stock becoming thinly traded, and (4) regulatory changes that affect one company disproportionately. Monitor news flow and corporate actions for your pairs in addition to statistical re-testing.
