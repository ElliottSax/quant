---
title: "Python Data Analysis for Trading: pandas and NumPy Guide"
description: "Master pandas and NumPy for trading data analysis. Learn time series manipulation, return calculations, rolling statistics, and performance metrics."
date: "2026-03-24"
author: "Dr. James Chen"
category: "Python & Automation"
tags: ["python", "pandas", "numpy", "data analysis", "quantitative trading"]
keywords: ["python data analysis trading", "pandas trading", "numpy financial analysis"]
---

# Python Data Analysis for Trading: pandas and NumPy Guide

Every quantitative trading workflow begins with data. Before indicators are calculated, strategies are backtested, or signals are generated, raw market data must be loaded, cleaned, transformed, and analyzed. pandas and NumPy form the computational foundation for this work in Python, providing the data structures and operations that handle time series manipulation, return calculations, statistical analysis, and performance measurement.

This guide covers the essential pandas and NumPy operations for trading analysis, from loading and cleaning data through computing the performance metrics that evaluate strategy viability.

## Setting Up the Environment

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Display settings for better readability
pd.set_option('display.max_columns', 20)
pd.set_option('display.float_format', '{:.4f}'.format)
```

## Loading and Cleaning Market Data

### From CSV Files

```python
# Standard OHLCV data loading
df = pd.read_csv(
    'SPY_daily.csv',
    parse_dates=['Date'],
    index_col='Date'
)

# Ensure proper column names
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Sort by date (ascending)
df = df.sort_index()

# Check for and handle missing data
print(f"Missing values:\n{df.isnull().sum()}")
df = df.fillna(method='ffill')  # Forward fill (carry last known value)

# Remove duplicate indices
df = df[~df.index.duplicated(keep='first')]

# Verify data integrity
assert df.index.is_monotonic_increasing, "Data is not sorted by date"
assert not df.isnull().any().any(), "Missing values remain"
```

### From APIs (yfinance)

```python
import yfinance as yf

# Download single ticker
spy = yf.download('SPY', start='2015-01-01', end='2025-12-31')

# Download multiple tickers
tickers = ['SPY', 'QQQ', 'IWM', 'TLT', 'GLD']
prices = yf.download(tickers, start='2015-01-01', end='2025-12-31')['Close']

# Resample to different frequencies
weekly = spy.resample('W').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

monthly = spy.resample('ME').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})
```

## Return Calculations

### Types of Returns

```python
# Simple (arithmetic) returns
df['Simple_Return'] = df['Close'].pct_change()

# Log (continuous) returns
df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))

# Cumulative returns
df['Cumulative_Return'] = (1 + df['Simple_Return']).cumprod() - 1

# Multi-period returns (e.g., 5-day, 20-day, 60-day)
df['Return_5d'] = df['Close'].pct_change(5)
df['Return_20d'] = df['Close'].pct_change(20)
df['Return_60d'] = df['Close'].pct_change(60)
```

### Why Log Returns Are Used in Quantitative Analysis

Log returns have mathematical properties that make them preferable for statistical analysis:
1. **Additivity:** Multi-period log returns sum across time (simple returns do not)
2. **Symmetry:** A +10% log return and -10% log return cancel exactly
3. **Normality:** Log returns are closer to normally distributed than simple returns
4. **Continuous compounding:** Log returns represent continuously compounded rates

For portfolio construction and multi-period analysis, use log returns. For reporting performance to end users, convert back to simple returns.

## Rolling Statistics

Rolling calculations are fundamental to trading analysis, as they provide a moving window view of statistical properties over time.

```python
# Rolling mean and standard deviation
window = 20
df['Rolling_Mean'] = df['Simple_Return'].rolling(window).mean()
df['Rolling_Std'] = df['Simple_Return'].rolling(window).std()
df['Rolling_Vol'] = df['Simple_Return'].rolling(window).std() * np.sqrt(252)

# Rolling Sharpe Ratio (annualized)
risk_free_daily = 0.04 / 252  # 4% annual risk-free rate
df['Rolling_Sharpe'] = (
    (df['Simple_Return'].rolling(window).mean() - risk_free_daily) /
    df['Simple_Return'].rolling(window).std()
) * np.sqrt(252)

# Rolling correlation between two assets
df['Correlation_SPY_QQQ'] = (
    df['SPY_Return'].rolling(60).corr(df['QQQ_Return'])
)

# Rolling beta
df['Rolling_Beta'] = (
    df['Stock_Return'].rolling(60).cov(df['Market_Return']) /
    df['Market_Return'].rolling(60).var()
)

# Expanding (cumulative) statistics
df['Expanding_Mean'] = df['Simple_Return'].expanding().mean()
df['Expanding_Sharpe'] = (
    (df['Simple_Return'].expanding().mean() - risk_free_daily) /
    df['Simple_Return'].expanding().std()
) * np.sqrt(252)
```

## Performance Metrics with NumPy

```python
def calculate_performance_metrics(returns, risk_free_rate=0.04):
    """
    Calculate comprehensive performance metrics from a return series.

    Parameters:
    - returns: pandas Series of daily returns
    - risk_free_rate: annual risk-free rate (default 4%)
    """
    trading_days = 252
    rf_daily = risk_free_rate / trading_days

    # Basic statistics
    total_return = (1 + returns).prod() - 1
    n_years = len(returns) / trading_days
    cagr = (1 + total_return) ** (1 / n_years) - 1

    # Risk metrics
    annual_vol = returns.std() * np.sqrt(trading_days)
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(trading_days)

    # Drawdown analysis
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    avg_drawdown = drawdown[drawdown < 0].mean()

    # Drawdown duration
    underwater = drawdown < 0
    dd_groups = (~underwater).cumsum()[underwater]
    if len(dd_groups) > 0:
        max_dd_duration = dd_groups.value_counts().max()
    else:
        max_dd_duration = 0

    # Risk-adjusted metrics
    sharpe = (returns.mean() - rf_daily) / returns.std() * np.sqrt(trading_days)
    sortino = (returns.mean() - rf_daily) / downside_returns.std() * np.sqrt(trading_days)
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else np.inf

    # Win/loss statistics
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    win_rate = len(wins) / len(returns)
    profit_factor = wins.sum() / abs(losses.sum()) if len(losses) > 0 else np.inf

    # Skewness and kurtosis
    skewness = returns.skew()
    kurtosis = returns.kurtosis()

    return {
        'Total Return': f'{total_return:.2%}',
        'CAGR': f'{cagr:.2%}',
        'Annual Volatility': f'{annual_vol:.2%}',
        'Sharpe Ratio': f'{sharpe:.2f}',
        'Sortino Ratio': f'{sortino:.2f}',
        'Calmar Ratio': f'{calmar:.2f}',
        'Max Drawdown': f'{max_drawdown:.2%}',
        'Avg Drawdown': f'{avg_drawdown:.2%}',
        'Max DD Duration (days)': max_dd_duration,
        'Win Rate': f'{win_rate:.2%}',
        'Profit Factor': f'{profit_factor:.2f}',
        'Skewness': f'{skewness:.2f}',
        'Excess Kurtosis': f'{kurtosis:.2f}',
    }
```

## Time Series Operations for Trading

### Lag and Lead Operations

```python
# Create lagged features (previous period values)
for lag in [1, 5, 10, 20]:
    df[f'Return_Lag_{lag}'] = df['Simple_Return'].shift(lag)

# Create future returns for labeling (target variable)
df['Future_Return_1d'] = df['Simple_Return'].shift(-1)
df['Future_Return_5d'] = df['Close'].pct_change(5).shift(-5)
```

### Regime Detection with NumPy

```python
def detect_volatility_regime(returns, short_window=20, long_window=120):
    """Classify market into high/low volatility regimes."""
    short_vol = returns.rolling(short_window).std() * np.sqrt(252)
    long_vol = returns.rolling(long_window).std() * np.sqrt(252)

    regime = np.where(short_vol > long_vol, 'High Vol', 'Low Vol')
    return pd.Series(regime, index=returns.index)

df['Vol_Regime'] = detect_volatility_regime(df['Simple_Return'])
```

### Cross-Sectional Analysis (Multiple Assets)

```python
# Rank assets by momentum
def rank_by_momentum(prices, lookback=60):
    """Rank assets by momentum score (return over lookback period)."""
    returns = prices.pct_change(lookback).iloc[-1]
    ranks = returns.rank(ascending=False)
    return returns, ranks

# Calculate pairwise correlations
correlation_matrix = prices.pct_change().dropna().corr()

# Portfolio-level return
weights = np.array([0.3, 0.3, 0.2, 0.1, 0.1])  # SPY, QQQ, IWM, TLT, GLD
portfolio_returns = (prices.pct_change().dropna() * weights).sum(axis=1)
```

## Key Takeaways

- pandas provides the DataFrame structure essential for organizing OHLCV data, calculating returns, and computing rolling statistics for trading analysis.
- NumPy enables vectorized mathematical operations that are 10-100x faster than Python loops, critical for performance metrics and large-scale computations.
- Log returns are preferred for statistical analysis due to their additivity and symmetry; simple returns are used for performance reporting.
- Rolling calculations (mean, standard deviation, correlation, beta) provide time-varying statistical estimates that capture changing market conditions.
- A comprehensive performance analysis includes risk-adjusted metrics (Sharpe, Sortino, Calmar), drawdown analysis, and distributional characteristics (skewness, kurtosis).
- Data cleaning (handling missing values, duplicate removal, data integrity checks) should always precede any analysis.

## Frequently Asked Questions

### How do I handle missing data in financial time series?

Forward-fill (`ffill`) is the standard approach for market data, as it carries the last known price forward. This is appropriate because a stock that does not trade on a given day (holiday, halt) is still worth its last traded price. Never use backward-fill or interpolation for market data, as these introduce look-ahead bias. For volume data, fill missing values with 0 (no trading occurred).

### What is the difference between pandas rolling and expanding?

Rolling calculations use a fixed-size window (e.g., the last 20 observations), producing a time-varying statistic. Expanding calculations use all available data from the start up to the current observation, producing a cumulative statistic. Rolling is used for short-term technical analysis (moving averages, rolling volatility), while expanding is used for cumulative performance metrics (cumulative return, cumulative Sharpe ratio).

### How large a dataset can pandas handle efficiently?

pandas handles millions of rows efficiently for most financial data operations. A 20-year tick-level dataset for a single instrument (approximately 50-100 million rows) is manageable on modern hardware with 16+ GB RAM. For datasets exceeding available memory, use chunked processing (`pd.read_csv(chunksize=N)`), Dask for parallel out-of-core computation, or filter the data to the relevant subset before loading into pandas.

### Should I use pandas or NumPy for financial calculations?

Use pandas for data organization, time series alignment, and labeled operations (accessing by date, column name). Use NumPy for computation-heavy operations where speed matters and labeled indexing is not needed. In practice, most trading analysis uses pandas as the primary interface, with NumPy operating behind the scenes for mathematical operations. When performance is critical (real-time systems), convert to NumPy arrays for the computation-intensive portions.
