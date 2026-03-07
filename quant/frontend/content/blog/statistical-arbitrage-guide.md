---
title: "Statistical Arbitrage: Quantitative Pair Trading Systems"
description: "Build statistical arbitrage systems with Python. Pair selection, spread modeling, entry/exit signals, and risk management for mean-reversion strategies."
date: "2026-03-16"
author: "Dr. James Chen"
category: "Trading Strategies"
tags: ["statistical arbitrage", "pairs trading", "mean reversion", "quantitative trading", "spread trading"]
keywords: ["statistical arbitrage", "pairs trading strategy", "quantitative pair trading"]
---

# Statistical Arbitrage: Quantitative Pair Trading Systems

Statistical arbitrage exploits temporary pricing dislocations between related securities. When two historically correlated stocks diverge beyond what fundamentals justify, a stat arb strategy goes long the underperformer and short the outperformer, profiting as the spread reverts to its historical mean.

This is one of the oldest and most robust quantitative strategies, used by hedge funds from D.E. Shaw to Renaissance Technologies. The edge comes not from predicting direction but from identifying pairs whose spread is mean-reverting, sizing positions correctly, and managing the risk of permanent divergence.

## Key Takeaways

- **Pair selection is the critical step.** Cointegrated pairs outperform correlated pairs because cointegration implies a stable long-run equilibrium.
- **The spread, not individual prices, is the signal.** All entry/exit logic operates on the standardized spread (z-score).
- **Risk management must account for regime breaks.** Stop losses on the spread prevent catastrophic losses when pairs permanently diverge.
- **Transaction costs and borrowing fees** materially impact profitability and must be included in backtests.

## Pair Selection: Finding Tradable Pairs

The universe of potential pairs grows quadratically with the number of stocks. Screen efficiently by starting with sector/industry constraints.

```python
import numpy as np
import pandas as pd
from itertools import combinations
from statsmodels.tsa.stattools import coint

def find_cointegrated_pairs(
    prices: pd.DataFrame,
    significance: float = 0.05,
    min_correlation: float = 0.7,
) -> pd.DataFrame:
    """
    Screen all pairs for cointegration using Engle-Granger test.
    Pre-filter by correlation to reduce computation.

    Args:
        prices: DataFrame with tickers as columns, dates as index
        significance: p-value threshold for cointegration
        min_correlation: minimum correlation for pre-filter

    Returns:
        DataFrame of cointegrated pairs with test statistics
    """
    tickers = prices.columns.tolist()
    n = len(tickers)

    # Pre-filter: correlation matrix
    returns = prices.pct_change().dropna()
    corr_matrix = returns.corr()

    results = []
    pairs_tested = 0

    for i, j in combinations(range(n), 2):
        # Skip low-correlation pairs
        if abs(corr_matrix.iloc[i, j]) < min_correlation:
            continue

        pairs_tested += 1
        ticker_a, ticker_b = tickers[i], tickers[j]

        # Engle-Granger cointegration test
        score, pvalue, _ = coint(prices[ticker_a], prices[ticker_b])

        if pvalue < significance:
            # Compute hedge ratio via OLS
            from numpy.polynomial.polynomial import polyfit
            beta = np.polyfit(prices[ticker_b], prices[ticker_a], 1)[0]

            # Spread statistics
            spread = prices[ticker_a] - beta * prices[ticker_b]
            half_life = compute_half_life(spread)

            results.append({
                "ticker_a": ticker_a,
                "ticker_b": ticker_b,
                "coint_pvalue": pvalue,
                "coint_statistic": score,
                "correlation": corr_matrix.iloc[i, j],
                "hedge_ratio": beta,
                "half_life": half_life,
                "spread_std": spread.std(),
            })

    pairs_df = pd.DataFrame(results)
    if len(pairs_df) > 0:
        pairs_df = pairs_df.sort_values("coint_pvalue")

    print(f"Tested {pairs_tested} pairs, found {len(pairs_df)} cointegrated")
    return pairs_df


def compute_half_life(spread: pd.Series) -> float:
    """
    Compute mean-reversion half-life using OLS on spread changes.
    Half-life = -ln(2) / ln(1 + theta), where theta is AR(1) coefficient.
    """
    spread_lag = spread.shift(1)
    spread_diff = spread.diff()

    # Drop NaN
    valid = ~(spread_lag.isna() | spread_diff.isna())
    y = spread_diff[valid].values
    x = spread_lag[valid].values.reshape(-1, 1)

    # OLS: delta_spread = theta * spread_lag + epsilon
    from sklearn.linear_model import LinearRegression
    reg = LinearRegression()
    reg.fit(x, y)
    theta = reg.coef_[0]

    if theta >= 0:
        return np.inf  # Not mean-reverting

    half_life = -np.log(2) / np.log(1 + theta)
    return half_life
```

## Spread Construction and Z-Score Signal

The spread between the paired securities, standardized as a z-score, drives all trading decisions.

```python
class PairSpread:
    """
    Manage spread construction, z-score computation,
    and signal generation for a pair.
    """

    def __init__(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        lookback: int = 60,
        entry_z: float = 2.0,
        exit_z: float = 0.5,
        stop_z: float = 4.0,
    ):
        self.prices_a = prices_a
        self.prices_b = prices_b
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z

    def compute_hedge_ratio(self, method: str = "rolling_ols") -> pd.Series:
        """Compute dynamic hedge ratio."""
        if method == "rolling_ols":
            # Rolling OLS hedge ratio
            ratios = []
            for i in range(self.lookback, len(self.prices_a)):
                window_a = self.prices_a.iloc[i - self.lookback:i]
                window_b = self.prices_b.iloc[i - self.lookback:i]
                beta = np.polyfit(window_b, window_a, 1)[0]
                ratios.append(beta)
            return pd.Series(
                ratios,
                index=self.prices_a.index[self.lookback:],
            )
        else:
            # Static hedge ratio (full sample)
            beta = np.polyfit(self.prices_b, self.prices_a, 1)[0]
            return pd.Series(beta, index=self.prices_a.index)

    def compute_spread(self, hedge_ratio: pd.Series | float = None) -> pd.Series:
        """Compute the spread (residual) between the pair."""
        if hedge_ratio is None:
            hedge_ratio = self.compute_hedge_ratio()

        if isinstance(hedge_ratio, pd.Series):
            aligned_a = self.prices_a.loc[hedge_ratio.index]
            aligned_b = self.prices_b.loc[hedge_ratio.index]
            spread = aligned_a - hedge_ratio * aligned_b
        else:
            spread = self.prices_a - hedge_ratio * self.prices_b
        return spread

    def compute_zscore(self, spread: pd.Series) -> pd.Series:
        """Rolling z-score of the spread."""
        mean = spread.rolling(self.lookback).mean()
        std = spread.rolling(self.lookback).std()
        zscore = (spread - mean) / std
        return zscore

    def generate_signals(self, zscore: pd.Series) -> pd.Series:
        """
        Generate trading signals from z-score.
        +1: long spread (long A, short B)
        -1: short spread (short A, long B)
         0: no position
        """
        signals = pd.Series(0, index=zscore.index)

        position = 0
        for i in range(1, len(zscore)):
            z = zscore.iloc[i]

            if position == 0:
                # Entry signals
                if z < -self.entry_z:
                    position = 1   # Long spread
                elif z > self.entry_z:
                    position = -1  # Short spread
            elif position == 1:
                # Exit or stop for long spread
                if z > -self.exit_z or z > self.stop_z:
                    position = 0
            elif position == -1:
                # Exit or stop for short spread
                if z < self.exit_z or z < -self.stop_z:
                    position = 0

            signals.iloc[i] = position

        return signals
```

## Backtesting the Pair Strategy

A proper backtest accounts for transaction costs, margin requirements, and slippage.

```python
def backtest_pair(
    prices_a: pd.Series,
    prices_b: pd.Series,
    signals: pd.Series,
    hedge_ratio: pd.Series,
    capital: float = 100_000,
    transaction_cost_bps: float = 10,
    borrow_cost_annual_bps: float = 50,
) -> pd.DataFrame:
    """
    Backtest a pairs trading strategy with realistic costs.
    """
    # Align all series
    common_idx = signals.dropna().index
    signals = signals.loc[common_idx]
    pa = prices_a.loc[common_idx]
    pb = prices_b.loc[common_idx]
    hr = hedge_ratio.loc[common_idx] if isinstance(hedge_ratio, pd.Series) else hedge_ratio

    # Returns
    ret_a = pa.pct_change()
    ret_b = pb.pct_change()

    # Strategy returns: long A, short B when signal = 1 (opposite for -1)
    if isinstance(hr, pd.Series):
        strategy_returns = signals * (ret_a - hr * ret_b) / (1 + hr.abs())
    else:
        strategy_returns = signals * (ret_a - hr * ret_b) / (1 + abs(hr))

    # Transaction costs (on signal changes)
    signal_changes = signals.diff().abs()
    tc = signal_changes * transaction_cost_bps / 10_000

    # Borrow costs (when short)
    daily_borrow = borrow_cost_annual_bps / 10_000 / 252
    borrow_cost = signals.abs() * daily_borrow

    # Net returns
    net_returns = strategy_returns - tc - borrow_cost

    # Build results
    results = pd.DataFrame({
        "signal": signals,
        "gross_return": strategy_returns,
        "transaction_cost": tc,
        "borrow_cost": borrow_cost,
        "net_return": net_returns,
        "cumulative": (1 + net_returns).cumprod(),
    })

    # Summary statistics
    annual_return = net_returns.mean() * 252
    annual_vol = net_returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0

    total_trades = (signal_changes > 0).sum()
    total_costs = (tc + borrow_cost).sum()

    print(f"Annual Return: {annual_return:.2%}")
    print(f"Annual Vol: {annual_vol:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Total Trades: {total_trades}")
    print(f"Total Costs: {total_costs:.4f}")

    return results
```

## Portfolio of Pairs

Diversifying across multiple pairs reduces idiosyncratic risk and smooths the equity curve.

```python
def build_pairs_portfolio(
    pairs_list: list[dict],
    prices_df: pd.DataFrame,
    max_pairs: int = 10,
    capital_per_pair: float = 10_000,
) -> pd.DataFrame:
    """
    Construct a portfolio of pair trades with equal capital allocation.

    Args:
        pairs_list: list of dicts with ticker_a, ticker_b, hedge_ratio
        prices_df: DataFrame of all prices
        max_pairs: maximum simultaneous pairs
    """
    all_returns = []

    for pair in pairs_list[:max_pairs]:
        ps = PairSpread(
            prices_df[pair["ticker_a"]],
            prices_df[pair["ticker_b"]],
        )
        spread = ps.compute_spread(pair["hedge_ratio"])
        zscore = ps.compute_zscore(spread)
        signals = ps.generate_signals(zscore)

        ret_a = prices_df[pair["ticker_a"]].pct_change()
        ret_b = prices_df[pair["ticker_b"]].pct_change()
        pair_return = signals * (ret_a - pair["hedge_ratio"] * ret_b) / (1 + abs(pair["hedge_ratio"]))
        all_returns.append(pair_return)

    # Equal-weight combination
    returns_df = pd.DataFrame(all_returns).T
    portfolio_return = returns_df.mean(axis=1)

    sharpe = portfolio_return.mean() / portfolio_return.std() * np.sqrt(252)
    print(f"Portfolio Sharpe: {sharpe:.2f}")
    print(f"Active pairs: {returns_df.count(axis=1).mean():.1f}")

    return portfolio_return
```

## Risk Management

Pairs that were cointegrated can break apart permanently due to fundamental changes (mergers, sector shifts, earnings surprises).

```python
def pair_risk_monitor(
    spread: pd.Series,
    zscore: pd.Series,
    max_zscore: float = 4.0,
    max_half_life: float = 60,
    recoint_window: int = 126,
) -> dict:
    """
    Monitor pair health and flag deterioration.
    """
    current_z = zscore.iloc[-1]
    current_hl = compute_half_life(spread.iloc[-recoint_window:])

    # Re-test cointegration on recent window
    # (requires original price series)
    warnings = []

    if abs(current_z) > max_zscore:
        warnings.append(f"Z-score extreme: {current_z:.2f}")

    if current_hl > max_half_life:
        warnings.append(f"Half-life too long: {current_hl:.0f} days")

    if current_hl == np.inf:
        warnings.append("Spread is no longer mean-reverting")

    return {
        "current_zscore": current_z,
        "current_half_life": current_hl,
        "warnings": warnings,
        "healthy": len(warnings) == 0,
    }
```

## FAQ

### What is the difference between correlation and cointegration for pairs trading?

Correlation measures the linear relationship between returns (short-term co-movement). Cointegration measures whether two price series share a long-run equilibrium. Two stocks can be highly correlated but not cointegrated (they trend together but can drift apart permanently), or cointegrated but not always highly correlated (short-term divergences revert). Cointegration is the stronger and more useful condition for pairs trading because it implies the spread is stationary and mean-reverting.

### What is a good half-life for a pairs trade?

A half-life of 5-30 trading days is ideal for daily strategies. Shorter half-lives (under 5 days) may not provide enough time to enter and exit profitably after costs. Longer half-lives (over 60 days) tie up capital and expose you to regime change risk. The half-life also determines your lookback window for z-score normalization: use approximately 3-4 times the half-life.

### How do I manage the risk of pairs breaking apart?

Implement three layers of protection: (1) hard stop losses at 3-4 standard deviations on the z-score, (2) periodic re-testing of cointegration on a rolling window (e.g., quarterly), and (3) position limits that cap exposure to any single pair at 10-15% of portfolio capital. If cointegration breaks down, close the position regardless of current P&L.

### How many pairs should I trade simultaneously?

Diversification across 8-15 pairs significantly reduces the variance of returns compared to trading a single pair. Beyond 20 pairs, the marginal diversification benefit diminishes and operational complexity increases. Ensure pairs are drawn from different sectors to avoid concentration in a single risk factor.
