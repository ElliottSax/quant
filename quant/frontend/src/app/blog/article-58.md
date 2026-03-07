---
title: Untitled
date: 2026-03-06
author: Stack Guide
category: strategies
tags: []
lastmod: 2026-03-06
description: Comprehensive guide to untitled---
# Bollinger Bands Strategy: Complete Backtest
Learn more: [backtesting strategies](/guides/backtesting)
---

## 1. Why Bollinger Bands Still Matter in 2024  

The **bollinger bands indicator**—three lines that encapsulate price volatility—was created by John Bollinger in the 1980s. Despite the rise of machine‑learning models, Bollinger Bands remain a favorite among retail traders and quantitative analysts because:

Learn more: [trading algorithms](/strategies)

| Benefit | Explanation |
|--------|--------------|
| **Dynamic support/resistance** | The bands expand when volatility spikes and contract during calm markets, automatically adapting to regime changes. |
| **Mean‑reversion signal** | Prices that wander far outside the outer band often revert toward the middle band (a simple moving average). |
| **Simplicity** | Only three parameters (period, σ‑multiplier, and SMA type) are needed, making it easy to combine with other signals. |

Learn more: [risk management](/guides/risk)

In this article we’ll build a **complete backtest** of a classic **bollinger bands trading** system, evaluate its performance on two major markets, and discuss the risk‑management overlay needed to make the strategy viable for retail traders and quants alike.

**Related**: [Untitled](/article-53)

---

## 2. Anatomy of the Bollinger Bands Indicator  

| Component | Formula | Typical Setting |
|-----------|---------|-----------------|
| **Middle Band (MB)** | `SMA(price, N)` | N = 20 (20‑day simple moving average) |
| **Upper Band (UB)** | `MB + K * σ(price, N)` | K = 2 (2 standard deviations) |
| **Lower Band (LB)** | `MB - K * σ(price, N)` | K = 2 |

*σ* denotes the rolling standard deviation of closing prices over the same window *N*. When price touches or breaches the UB/LB, the market is considered **over‑bought** or **over‑sold**, respectively. The MB acts as a mean‑reversion anchor.

---

## 3. Defining the Classic Bollinger Bands Strategy  

The most widely taught **bollinger bands strategy** follows a simple set of entry/exit rules:

| Rule | Condition | Action |
|------|-----------|--------|
| **Long Entry** | Close ≤ LB (price closes at or below the lower band) | Buy 1 unit |
| **Short Entry** | Close ≥ UB (price closes at or above the upper band) | Sell short 1 unit |
| **Exit Long** | Close ≥ MB (price crosses above the middle band) | Close long position |
| **Exit Short** | Close ≤ MB (price crosses below the middle band) | Close short position |
| **Stop‑Loss** | 2 × ATR(14) away from entry price (optional) | Force exit |

The strategy assumes **mean‑reversion**: after a price excursion beyond a band, the probability of a pull‑back toward the SMA is higher than a continuation.  

> **Note:** The stop‑loss is a risk‑management overlay, not part of the pure Bollinger rule set. It dramatically improves the risk‑adjusted return, as we’ll see later.

---

## 4. Data Selection & Pre‑Processing  

### 4.1. Instruments  

| Symbol | Asset Class | Reason for Inclusion |
|--------|-------------|----------------------|
| `SPY` | US Equity ETF (S&P 500) | Highly liquid, long‑term data (2000‑2023) |
| `EURUSD=X` | FX pair (Euro/USD) | Represents a non‑equity, 24‑hour market with different volatility dynamics |

### 4.2. Timeframe  

- **Daily candles** from **2000‑01‑03** to **2023‑12‑29** (6,164 trading days for SPY, 5,981 for EURUSD).  
- We exclude the COVID‑19 crash week (2020‑03‑09 to 2020‑03‑20) in one sensitivity test to see how the strategy fares under extreme stress.

### 4.3. Feature Engineering  

```python
import yfinance as yf
import pandas as pd
import numpy as np

def add_bollinger(df, n=20, k=2):
    df['MB'] = df['Close'].rolling(window=n).mean()
    df['STD'] = df['Close'].rolling(window=n).std()
    df['UB'] = df['MB'] + k * df['STD']
    df['LB'] = df['MB'] - k * df['STD']
    return df

**Related**: [Untitled](/article-48)

def add_atr(df, n=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=n).mean()
    return df

# Load data
spy = yf.download('SPY', start='2000-01-01', end='2024-01-01')
eurusd = yf.download('EURUSD=X', start='2000-01-01', end='2024-01-01')

# Build indicator columns
for df in (spy, eurusd):
    df = add_bollinger(df)
    df = add_atr(df)
```

The resulting DataFrame now contains every variable needed for the backtest.

---

## 5. Backtesting Methodology  

### 5.1. Engine Overview  

| Component | Description |
|-----------|-------------|
| **Signal Generation** | Vectorized logic that flags long/short entries and exits based on the bands. |
| **Position Tracking** | One‑unit position size (long = +1, short = –1, flat = 0). |
| **PnL Calculation** | Daily P&L = position * (today’s close – yesterday’s close). |
| **Transaction Costs** | Fixed commission of 0.005 % per trade (typical for retail brokers) plus a slippage of 0.5 % of the spread for FX. |
| **Risk‑adjusted Metrics** | CAGR, Sharpe (Rf = 0 %), Sortino, maximum drawdown, Calmar, and profit factor. |

###  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 5.2. Pseudocode  

```python
def run_backtest(df):
    df = df.copy()
    df['Signal'] = 0               # 1 = long, -1 = short, 0 = flat

**Related**: [Untitled](/article-43)

    # Entry rules
    df.loc[df['Close'] <= df['LB'], 'Signal'] = 1
    df.loc[df['Close'] >= df['UB'], 'Signal'] = -1

    # Exit rules (override entry)
    df.loc[(df['Signal'].shift() == 1) & (df['Close'] >= df['MB']), 'Signal'] = 0
    df.loc[(df['Signal'].shift() == -1) & (df['Close'] <= df['MB']), 'Signal'] = 0

    # Forward‑fill position until an exit signal appears
    df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)

    # Stop‑loss: if price moves 2×ATR against the trade, flip to flat
    df['StopLong'] = (df['Close'] < df['EntryPrice'] - 2*df['ATR'])
    df['StopShort'] = (df['Close'] > df['EntryPrice'] + 2*df['ATR'])
    # (implementation details omitted for brevity)

    # Daily returns
    df['Return'] = df['Position'].shift() * df['Close'].pct_change()
    df['Return'] -= 0.00005   # commission per trade (approx.)

    # Equity curve
    df['Equity'] = (1 + df['Return']).cumprod()
    return df
```

The code is deliberately concise

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

**Related**: [Untitled](/article-13)

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-43)
- [Untitled](/article-13)
- [Untitled](/article-53)
- [Untitled](/article-48)
