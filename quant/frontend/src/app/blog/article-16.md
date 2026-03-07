---
title: Untitled
date: 2026-03-06
author: Stack Guide
category: strategies
tags: []
lastmod: 2026-03-06
description: Comprehensive guide to untitled---
# Mean Reversion Strategy: Backtest & Implementation
*Target audience: retail traders and quantitative enthusiasts*
---

## Introduction  

The **mean reversion trading strategy** is one of the oldest and most intuitive ideas in quantitative finance. It rests on the observation that many price series tend to drift toward a statistical “average” after periods of deviation. When a security’s price moves far enough away from that average, a mean‑reverting trader expects it to swing back, creating a potential profit opportunity.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we will:

1. Explain the theoretical underpinnings of mean reversion.  
2. Walk through a concrete **mean reversion backtest** using real market data.  
3. Show how to interpret backtest metrics (CAGR, Sharpe, max drawdown, etc.).  
4. Discuss risk‑management tools that protect a portfolio when the market stays away from the mean.  
5. Provide a practical implementation checklist for both retail traders and quants.  

Learn more: [trading algorithms](/strategies)

All code snippets are in Python and rely on open‑source libraries (`pandas`, `numpy`, `yfinance`, `matplotlib`). Feel free to copy, adapt, and run the examples on your own machine.  

Learn more: [risk management](/guides/risk)

---  

## Core Concepts of a Mean Reversion Trading Strategy  

| Concept | Why it matters | Typical quantitative test |
|---------|----------------|---------------------------|
| **Stationarity** | A mean‑reverting series has a constant mean and variance over time. | Augmented Dickey‑Fuller (ADF) test on price or log‑price returns. |
| **Half‑life** | The speed at which a deviation decays back to the mean; informs signal lag. | Estimate using the Ornstein‑Uhlenbeck (OU) process: `half_life = -log(2)/λ`. |
| **Reversion Indicator** | Turns raw price data into a standardized signal (e.g., Z‑score). | Z‑score = `(price - rolling_mean) / rolling_std`. |
| **Entry/Exit Rules** | Define when to open and close positions based on the indicator. | Long when Z‑score ≤ –2, short when Z‑score ≥ +2, exit at |Z‑score| ≤ 0.5. |

The **mean reversion backtest** we’ll build follows these steps:

1. Pull historical price data.  
2. Compute a rolling mean and standard deviation.  
3. Generate a Z‑score (our **reversion indicator**).  
4. Create position signals from the Z‑score thresholds.  
5. Simulate daily P&L, accounting for slippage and transaction costs.  

**Related**: [Untitled](/article-66)

---  

## Choosing the Right Reversion Indicator  

While many traders simply use a Z‑score, other popular **reversion indicators** include:

| Indicator | Formula | Typical Use‑Case |
|-----------|---------|------------------|
| **Bollinger Bands** | Upper = MA + 2·σ, Lower = MA – 2·σ | Visual confirmation; triggers when price touches bands. |
| **Relative Strength Index (RSI)** | 100 – 100/(1 + RS) | Over‑bought/over‑sold extremes (≥70 or ≤30) often revert. |
| **Commodity Channel Index (CCI)** | (Price – MA) / (0.015·Mean Deviation) | Detects extreme price deviations. |
| **Kalman Filter** | Adaptive estimate of mean and variance | Handles non‑stationary regimes. |

For the purpose of this tutorial we’ll stick with the **Z‑score** because it is:

* Simple to compute.  
* Scale‑invariant (works across equities, futures, and crypto).  
* Directly linked to statistical significance (|Z| > 2 ≈ 95% confidence of deviation).  

---  

## Data Requirements & Preparing Historical Data  

A robust backtest begins with clean, high‑quality data. Below we use daily adjusted close prices for the SPDR S&P 500 ETF (ticker **`SPY`**) from 2000‑01‑01 to 2023‑12‑31.

```python
import yfinance as yf
import pandas as pd

# Pull data
ticker = "SPY"
df = yf.download(ticker, start="2000-01-01", end="2023-12-31", progress=False)

# Keep only adjusted close and rename
prices = df["Adj Close"].rename("price").to_frame()
prices.head()
```

**Cleaning steps**  

1. **Drop missing days** – markets close on weekends/holidays; pandas `asfreq('B')` can align to business days.  
2. **Forward‑fill gaps** – rare data outages are filled with the last valid price.  
3. **Log‑returns** – optional for stationarity checks.  

```python
prices = prices.asfreq('B').ffill()
prices['log_ret'] = np.log(prices['price']).diff()
```

**Related**: [Untitled](/article-76)

Now we have a tidy series ready for the **mean reversion backtest**.  

---  

## Building a Simple Mean Reversion Backtest  

The following function encapsulates the entire workflow:  

```python
import numpy as np
import matplotlib.pyplot as plt

def mean_rev_backtest(df,
                     lookback=60,
                     entry_z=2.0,
                     exit_z=0.5,
                     tc=0.0005,          # 5 bps per round‑trip
                     capital=100_000):
    """
    Mean‑reversion backtest using Z‑score of price.
    Returns a DataFrame with equity curve and performance metrics.
    """
    # 1️⃣ Rolling statistics
    df['roll_mean'] = df['price'].rolling(lookback).mean()
    df['roll_std']  = df['price'].rolling(lookback).std()
    df.dropna(inplace=True)                # remove early NaNs

    # 2️⃣ Z‑score indicator
    df['zscore'] = (df['price'] - df['roll_mean']) / df['roll_std']

    # 3️⃣ Signal generation
    #   Long when z ≤ -entry_z, Short when z ≥ +entry_z
    df['signal'] = 0
    df.loc[df['zscore'] <= -entry_z, 'signal'] = 1      # long
    df.loc[df['zscore'] >=  entry_z, 'signal'] = -1     # short

    #   Exit when |z| ≤ exit_z
    df.loc[df['zscore'].abs() <= exit_z, 'signal'] = 0

    # 4️⃣ Position – we hold the signal until it changes
    df['position'] = df['signal'].replace(to_replace=0, method='ffill').fillna(0)

    # 5️⃣ Daily returns (assume daily rebalancing at close)
    df['ret'] = df['price'].pct_change()
    df['strategy_ret'] = df['position'].shift(1) * df['ret'] - tc * df['position'].diff().abs()

    # 6️⃣ Equity curve
    df['equity'] = (1 + df['strategy_ret']).cumprod() * capital

    return df
```

###  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## Running the backtest  

```python
result = mean_rev_backtest(prices.copy(),
                           lookback=60,
                           entry_z=2.0,
                           exit_z=0.5,
                           tc=0.0005,
                           capital=100_000)

# Plot equity curve
result['equity'].plot(figsize=(12,5), title='Mean‑Reversion Strategy Equity Curve (SPY)')
plt.ylabel('Portfolio Value ($)')
plt.show()
```

The chart typically shows periods of steady growth punctuated by drawdowns when the market trends strongly away from its mean (e.g., 

**Related**: [Untitled](/article-26)

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-66)
- [Untitled](/article-26)
- [Untitled](/article-76)
- [Untitled](/article-71)
