---
title: "Python Stock Data Analysis: Complete Guide with pandas"
description: "Master stock data analysis in Python using pandas. Learn data fetching, cleaning, technical indicators, and portfolio analytics with production code examples."
date: "2026-03-10"
author: "Dr. James Chen"
category: "Data Science"
tags: ["python", "pandas", "stock analysis", "data science", "financial data"]
keywords: ["python stock data analysis", "pandas financial analysis", "stock market python"]
---
# Python Stock Data Analysis: Complete Guide with pandas

Stock [data analysis](/blog/python-data-analysis-trading) forms the foundation of every [quantitative trading](/blog/crypto-quant-trading-strategies) strategy. Whether you are building a simple [moving average crossover](/blog/moving-average-crossover-strategy) or a sophisticated [machine learning](/blog/machine-learning-trading) model, your ability to load, clean, transform, and analyze financial time series data determines the quality of your downstream results.

In this guide, we walk through the complete workflow for stock data analysis using Python and pandas, from fetching raw OHLCV data to computing portfolio-level analytics. Every code example here is production-tested and reflects patterns used in institutional quant workflows.

## Key Takeaways

- **pandas is the workhorse** for financial data manipulation, offering vectorized operations that outperform row-by-row iteration by 100x or more.
- **Data quality matters more than model complexity.** Corporate actions, missing values, and timezone inconsistencies silently corrupt backtest results.
- **Returns analysis should use log returns** for multi-period aggregation and statistical modeling.
- **Resampling and rolling windows** are essential for multi-timeframe analysis and [feature engineering](/blog/feature-engineering-trading).

## Setting Up Your Environment

Before diving into analysis, install the core dependencies. We use `yfinance` for free data access, though production systems typically connect to providers like Polygon.io, Alpaca, or Bloomberg.

```python
# requirements.txt
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.18
matplotlib>=3.7.0
scipy>=1.10.0
```

```python
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Fetch historical data
def fetch_stock_data(
    ticker: str,
    start: str = "2020-01-01",
    end: str | None = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch OHLCV data with proper index handling.
    Returns DataFrame with DatetimeIndex (timezone-naive).
    """
    end = end or datetime.now().strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start, end=end, interval=interval)

    # Normalize timezone-aware index to timezone-naive
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Flatten multi-level columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df

# Example usage
aapl = fetch_stock_data("AAPL", start="2022-01-01")
print(f"Shape: {aapl.shape}")
print(f"Date range: {aapl.index[0]} to {aapl.index[-1]}")
print(aapl.tail())
```

## Data Cleaning and Validation

Raw market data frequently contains gaps, outliers, and corporate action artifacts. A robust cleaning pipeline prevents these issues from propagating into your analysis.

```python
def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean OHLCV data: handle missing values, detect outliers,
    and validate price relationships.
    """
    df = df.copy()

    # 1. Drop rows where all OHLCV are NaN
    df.dropna(how="all", subset=["Open", "High", "Low", "Close"], inplace=True)

    # 2. Forward-fill small gaps (up to 3 days for holidays)
    df.ffill(limit=3, inplace=True)

    # 3. Validate OHLC relationships
    # High should be >= Open, Close, Low
    invalid_high = df["High"] < df[["Open", "Close"]].max(axis=1)
    # Low should be <= Open, Close, High
    invalid_low = df["Low"] > df[["Open", "Close"]].min(axis=1)

    if invalid_high.sum() > 0:
        print(f"Warning: {invalid_high.sum()} rows with invalid High")
        df.loc[invalid_high, "High"] = df.loc[
            invalid_high, ["Open", "Close", "High"]
        ].max(axis=1)

    # 4. Detect extreme daily returns (potential data errors)
    returns = df["Close"].pct_change()
    extreme = returns.abs() > 0.50  # 50% single-day move
    if extreme.sum() > 0:
        print(f"Warning: {extreme.sum()} extreme daily returns detected")

    return df

aapl_clean = clean_ohlcv(aapl)
```

## Computing Returns

Returns are the fundamental unit of financial analysis. Use log returns for statistical modeling and simple returns for portfolio aggregation.

```python
def compute_returns(
    prices: pd.Series, method: str = "log"
) -> pd.Series:
    """Compute returns from a price series."""
    if method == "log":
        return np.log(prices / prices.shift(1))
    elif method == "simple":
        return prices.pct_change()
    else:
        raise ValueError(f"Unknown method: {method}")

# Daily log returns
aapl_clean["log_return"] = compute_returns(aapl_clean["Close"], "log")
aapl_clean["simple_return"] = compute_returns(aapl_clean["Close"], "simple")

# Multi-period returns via log return aggregation
weekly_log_return = aapl_clean["log_return"].rolling(5).sum()
monthly_log_return = aapl_clean["log_return"].rolling(21).sum()

# Annualized statistics
annual_return = aapl_clean["log_return"].mean() * 252
annual_vol = aapl_clean["log_return"].std() * np.sqrt(252)
sharpe = annual_return / annual_vol

print(f"Annualized Return: {annual_return:.2%}")
print(f"Annualized Volatility: {annual_vol:.2%}")
print(f"Sharpe Ratio: {sharpe:.2f}")
```

## Technical Indicators with pandas

Rolling window operations in pandas map directly to most technical indicators. Here is a reusable indicator library.

```python
class TechnicalIndicators:
    """Vectorized technical indicators using pandas."""

    @staticmethod
    def sma(series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window).mean()

    @staticmethod
    def ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def bollinger_bands(
        series: pd.Series, window: int = 20, num_std: float = 2.0
    ) -> pd.DataFrame:
        sma = series.rolling(window).mean()
        std = series.rolling(window).std()
        return pd.DataFrame({
            "upper": sma + num_std * std,
            "middle": sma,
            "lower": sma - num_std * std,
        })

    @staticmethod
    def rsi(series: pd.Series, window: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/window, min_periods=window).mean()
        avg_loss = loss.ewm(alpha=1/window, min_periods=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def atr(
        high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
    ) -> pd.Series:
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        return tr.rolling(window).mean()

# Apply indicators
ti = TechnicalIndicators()
aapl_clean["SMA_20"] = ti.sma(aapl_clean["Close"], 20)
aapl_clean["SMA_50"] = ti.sma(aapl_clean["Close"], 50)
aapl_clean["RSI_14"] = ti.rsi(aapl_clean["Close"], 14)
bb = ti.bollinger_bands(aapl_clean["Close"])
aapl_clean = pd.concat([aapl_clean, bb], axis=1)
```

## Multi-Asset Portfolio Analysis

Real trading involves analyzing multiple assets simultaneously. pandas makes this straightforward with multi-column DataFrames.

```python
def build_portfolio_data(
    tickers: list[str], start: str = "2022-01-01"
) -> pd.DataFrame:
    """Fetch and align close prices for multiple tickers."""
    frames = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker, start=start)
        frames[ticker] = df["Close"]

    portfolio = pd.DataFrame(frames).dropna()
    return portfolio

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
prices = build_portfolio_data(tickers)

# Correlation matrix
returns = prices.pct_change().dropna()
corr_matrix = returns.corr()
print("Correlation Matrix:")
print(corr_matrix.round(3))

# Rolling correlation between two assets
rolling_corr = returns["AAPL"].rolling(60).corr(returns["MSFT"])

# Equal-weight portfolio
weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
portfolio_return = (returns * weights).sum(axis=1)
cumulative = (1 + portfolio_return).cumprod()

# Portfolio statistics
port_annual_return = portfolio_return.mean() * 252
port_annual_vol = portfolio_return.std() * np.sqrt(252)
port_sharpe = port_annual_return / port_annual_vol

# Maximum drawdown
rolling_max = cumulative.cummax()
drawdown = (cumulative - rolling_max) / rolling_max
max_drawdown = drawdown.min()

print(f"\nPortfolio Return: {port_annual_return:.2%}")
print(f"Portfolio Vol: {port_annual_vol:.2%}")
print(f"Portfolio Sharpe: {port_sharpe:.2f}")
print(f"Max Drawdown: {max_drawdown:.2%}")
```

## Resampling for Multi-Timeframe Analysis

Converting daily data to weekly or monthly bars is essential for strategies that operate across timeframes.

```python
def resample_ohlcv(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """
    Resample OHLCV data to a lower frequency.
    freq: 'W' (weekly), 'ME' (monthly), 'QE' (quarterly)
    """
    resampled = df.resample(freq).agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    })
    return resampled.dropna()

weekly = resample_ohlcv(aapl_clean, "W")
monthly = resample_ohlcv(aapl_clean, "ME")

print(f"Daily bars: {len(aapl_clean)}")
print(f"Weekly bars: {len(weekly)}")
print(f"Monthly bars: {len(monthly)}")
```

## Performance Analysis: Drawdowns and Risk Metrics

Production systems need comprehensive risk analytics beyond simple Sharpe ratios.

```python
def performance_report(returns: pd.Series) -> dict:
    """Generate a comprehensive performance report."""
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max

    # Drawdown duration
    is_drawdown = drawdown < 0
    drawdown_groups = (~is_drawdown).cumsum()
    dd_durations = is_drawdown.groupby(drawdown_groups).sum()

    report = {
        "total_return": cumulative.iloc[-1] - 1,
        "annualized_return": returns.mean() * 252,
        "annualized_vol": returns.std() * np.sqrt(252),
        "sharpe_ratio": (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
        "sortino_ratio": (returns.mean() * 252) / (
            returns[returns < 0].std() * np.sqrt(252)
        ),
        "max_drawdown": drawdown.min(),
        "max_dd_duration_days": int(dd_durations.max()) if len(dd_durations) > 0 else 0,
        "calmar_ratio": (returns.mean() * 252) / abs(drawdown.min()),
        "skewness": returns.skew(),
        "kurtosis": returns.kurtosis(),
        "var_95": returns.quantile(0.05),
        "cvar_95": returns[returns <= returns.quantile(0.05)].mean(),
        "positive_days_pct": (returns > 0).mean(),
    }
    return report

report = performance_report(aapl_clean["simple_return"].dropna())
for k, v in report.items():
    if isinstance(v, float):
        print(f"{k}: {v:.4f}")
    else:
        print(f"{k}: {v}")
```

## Production Considerations

When moving from notebooks to production pipelines, several practices become critical.

### Data Storage

Store cleaned data in Parquet format rather than CSV. Parquet preserves dtypes, compresses well, and reads 5-10x faster for columnar access patterns.

```python
# Save to parquet
aapl_clean.to_parquet("data/aapl_daily.parquet")

# Read back (preserves DatetimeIndex and dtypes)
df = pd.read_parquet("data/aapl_daily.parquet")
```

### Memory Optimization

For large universes (thousands of symbols), downcast numeric types to reduce memory usage by 50-70%.

```python
def optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast numeric columns to reduce memory."""
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    return df
```

## FAQ

### What is the best Python library for stock data analysis?

pandas is the industry standard for tabular financial data. It provides vectorized operations, time series resampling, rolling windows, and seamless integration with NumPy, scikit-learn, and visualization libraries. For tick-level data exceeding available RAM, consider polars or Dask.

### How do I handle missing data in stock price series?

Forward-fill small gaps (1-3 days for holidays and weekends), but flag or remove extended gaps. Never interpolate prices, as this creates artificial data points that bias backtests. Always validate that your forward-fill does not cross corporate action boundaries like stock splits.

### Should I use log returns or simple returns?

Use log returns for statistical modeling (they are additive across time periods and approximately normally distributed). Use simple returns for portfolio-level aggregation (they are additive across assets). Never mix the two in the same calculation.

### How much historical data do I need for reliable analysis?

For daily strategies, a minimum of 3-5 years provides enough data for meaningful statistical tests and covers multiple market regimes. For intraday strategies, 1-2 years is typically sufficient due to the higher sample count. Always ensure your data spans at least one bear market cycle.

### How do I adjust for stock splits and dividends?

Use adjusted close prices for return calculations and backtesting. Raw (unadjusted) prices are only useful for intraday analysis of the current day. The `yfinance` library returns adjusted prices by default in the "Close" column, but verify this with your data provider.
