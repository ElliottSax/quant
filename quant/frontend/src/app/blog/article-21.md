---
title: Untitled
date: 2026-03-06
author: Stack Guide
category: strategies
tags: []
lastmod: 2026-03-06
description: Comprehensive guide to untitled---
# Mean Reversion Strategy: Backtest & Implementation
*Keywords: **mean reversion trading strategy**, mean reversion backtest, reversion indicator*
---

## Introduction  

Mean reversion is one of the most intuitive concepts in quantitative finance: prices that stray far from their historical norm tend to drift back toward that mean over time. While the idea sounds simple, turning it into a robust **mean reversion trading strategy** requires careful selection of assets, a reliable **reversion indicator**, disciplined risk management, and thorough **backtesting**.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we walk through a complete end‑to‑end workflow that retail traders and aspiring quants can follow today:

Learn more: [trading algorithms](/strategies)

1. **Data selection** – picking a liquid instrument and the right look‑back window.  
2. **Indicator design** – constructing a statistical signal (Z‑score, Bollinger Bands, etc.).  
3. **Strategy rules** – entry, exit, and position sizing.  
4. **Mean reversion backtest** – evaluating performance on historical data.  
5. **Risk management** – controlling drawdowns and preserving capital.  
6. **Live implementation** – a short Python snippet that can be dropped into a backtesting framework such as **Backtrader** or **Zipline**.  

Learn more: [risk management](/guides/risk)

All calculations are demonstrated on the S&P 500 ETF (ticker **SPY**) from **1 Jan 2010** to **31 Dec 2020** – a period that includes the 2011 “Flash Crash”, the 2015‑16 oil‑price shock, and the 2020 COVID‑19 market collapse. By the end you’ll have a reproducible **mean reversion backtest** and a clear set of guidelines for turning the idea into a live **mean reversion trading strategy**.

---

## 1. Why Mean Reversion?  

### 1.1 Theoretical Foundations  

Mean reversion stems from two related statistical concepts:

| Concept | Description |
|---------|-------------|
| **Stationarity** | A stationary price series has a constant mean and variance over time. If a series reverts to a constant level, it is “mean‑reverting”. |
| **Ornstein‑Uhlenbeck (OU) Process** | The continuous‑time analogue of a mean‑reverting random walk:  d\(X_t\) = \(\theta(\mu - X_t)dt + \sigma dW_t\). The parameter \(\theta\) controls the speed of reversion. |

Empirically, many asset classes display “local” mean‑reversion over short horizons (days to weeks) even if the long‑term trend is upward. For equity indices, the daily price often oscillates around a moving average, providing a fertile ground for a **reversion indicator**.

### 1.2 Practical Appeal  

* **High win‑rate** – Because the entry condition is triggered only after a sizable deviation, the probability of a successful reversal is often > 60 % in backtests.  
* **Market‑neutral potential** – By pairing long and short legs (e.g., pairs trading) the strategy can generate returns independent of market direction.  
* **Simplicity** – A basic version needs only price data and a few statistical calculations, making it accessible for retail traders.

---

## 2. Data Selection & Pre‑processing  

| Step | Description |
|------|-------------|
| **Instrument** | SPY (ETF tracking the S&P 500). Daily adjusted close price ensures dividend‑adjusted continuity. |
| **Period** | 01‑Jan‑2010 → 31‑Dec‑2020 (2,767 trading days). |
| **Cleaning** | Remove missing values, align timestamps, compute log‑returns for volatility estimates. |
| **Look‑back window** | 20‑day rolling window (≈ 1 trading month). This balances responsiveness and noise reduction. |

```python
import pandas as pd
import yfinance as yf

# Pull data
spy = yf.download('SPY', start='2010-01-01', end='2021-01-01')
spy = spy['Adj Close'].rename('price').to_frame()
# Rolling stats
window = 20
spy['ma']   = spy['price'].rolling(window).mean()
spy['std']  = spy['price'].rolling(window).std()
```

---

## 3. Building a Reversion Indicator  

A **reversion indicator** quantifies how far the current price deviates from its recent mean. Three popular choices are:

### 3.1 Z‑Score (Standardized Distance)  

\[
Z_t = \frac{P_t - \mu_{t}}{\sigma_{t}}
\]

* **Interpretation** – Z‑score > 2 indicates the price is > 2 σ above the mean; Z‑score < −2 signals a deep discount.  
* **Pros** – Scale‑free, works across assets.  
* **Cons** – Assumes normality; extreme market moves can produce “fat‑tail” outliers.

### 3.2 Bollinger Bands  

Upper = MA + k·σ, Lower = MA − k·σ (k = 2 is standard).  
* **Signal** – Price touching the upper band → short; touching the lower band → long.  
* **Pros** – Visually intuitive; widely used by traders.  
* **Cons** – Band width expands during volatility spikes, potentially delaying entries.

**Related**: [Untitled](/article-76)

### 3.3 OU‑Based Half‑Life  

Estimate the half‑life of mean reversion via an OLS regression of \(\Delta P_t\) on \(P_{t-1} - \mu\). If half‑life < 10 days, the series is deemed suitable for a short‑term mean‑reversion strategy.  

For this tutorial we adopt the **Z‑score** because it directly yields the **mean reversion backtest** thresholds we will use.

**Related**: [Untitled](/article-46)

```python
spy['zscore'] = (spy['price'] - spy['ma']) / spy['std']
```

---

## 4. Strategy Rules  

| Condition | Action |
|-----------|--------|
| **Entry Long** | `zscore <= -2` → buy 1 % of equity (adjusted for risk). |
| **Entry Short** | `zscore >= +2` → sell short 1 % of equity. |
| **Exit** | When `|zscore| < 0.5` (price back within half a standard deviation) *or* after 10 trading days, whichever occurs first. |
| **Stop‑Loss** | 2 % adverse move from entry price (triggers immediate exit). |
| **Position Sizing** | Fixed fractional (1 % of capital) with volatility scaling: `size = (0.01 * equity) / (price * std)`. |

The entry thresholds (`±2`) reflect the classic “2‑sigma rule”, yielding roughly 5 % of days with a signal. The exit rule (`|zscore| < 0.5`) ensures the trade stays in the “reversion zone” and reduces exposure to trend continuation.

---

## 5. Mean Reversion Backtest  

###  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 5.1 Backtesting Engine  

We use **Backtrader** because it handles commissions, slippage, and portfolio accounting out of the box. The core logic is encapsulated in a `MeanReversion` strategy class.

```python
import backtrader as bt

class MeanReversion(bt.Strategy):
    params = dict(
        z_entry = 2.0,
        z_exit  = 0.5,
        stop_pct = 0.02,
        max_holding = 10
    )
    def __init__(self):
        self.z = (self.data.close - bt.indicators.SMA(self.data.close, period=20)) / \
                 bt.indicators.StdDev(self.data.close, period=20)
        self.entry_price = {}
        self.days_held = {}
    def next(self):
        # Check existing positions for exit or stop
        for trade in list(self.position):
            if not trade: continue
        # Long entry
        if not self.position and self.z[0] <= -self.p.z_entry:
            size = self.broker.getcash() * 0.01 / (self

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.

**Related**: [Untitled](/article-36)



---

## You May Also Like

- [Untitled](/article-76)
- [Untitled](/article-36)
- [Untitled](/article-46)
- [Untitled](/article-11)
