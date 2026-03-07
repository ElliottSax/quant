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

Mean reversion is one of the oldest and most intuitive concepts in quantitative finance. The core idea is simple: **prices tend to drift back toward an equilibrium level** after periods of deviation. While the notion sounds obvious, turning it into a robust **mean reversion trading strategy** requires careful selection of a **reversion indicator**, rigorous **backtesting**, and disciplined **risk management**.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we walk through a complete end‑to‑end workflow that a retail trader or budding quant can replicate:

Learn more: [trading algorithms](/strategies)

1. **Select a market and data set** – we use daily SPY (S&P 500 ETF) data from 2010‑01‑01 to 2020‑12‑31.  
2. **Define a reversion indicator** – a 20‑day Bollinger‑Band Z‑score.  
3. **Build entry/exit rules** – long when the price is sufficiently below the band, short when it is above.  
4. **Run a mean reversion backtest** – using Python/Backtrader, we present performance metrics and visualisations.  
5. **Apply risk‑management techniques** – position sizing, volatility scaling, and stop‑losses.  
6. **Validate out‑of‑sample** – a walk‑forward test on 2021‑2023 data.  

Learn more: [risk management](/guides/risk)

By the end you’ll have a ready‑to‑trade **mean reversion trading strategy** you can adapt to other assets, time frames, or indicators.

---

## 1. Why Mean Reversion Works (and When It Fails)  

### 1.1 The Statistical Basis  

Mean reversion stems from the Ornstein‑Uhlenbeck (OU) process, a continuous‑time stochastic model where the drift term pulls the series toward a long‑run mean μ:

\[
dX_t = \theta(\mu - X_t)dt + \sigma dW_t
\]

- **θ** controls the speed of reversion.  
- **σ** is the volatility of the random shock.  

If a price series behaves like an OU process, deviations are temporary and provide trading opportunities.

### 1.2 Empirical Evidence  

Research on equity indices shows a statistically significant negative autocorrelation at lags of 5‑20 days, especially during *range‑bound* market regimes. For example, a study of the S&P 500 (1990‑2019) found an average **half‑life** of 12 trading days for price deviations from a 30‑day moving average.

### 1.3 When Mean Reversion Breaks Down  

- **Trending regimes** (e.g., 2008‑2009 crisis, 2020 COVID‑19 rally) can produce prolonged moves away from the mean.  
- **Structural breaks** (policy shifts, regime changes) alter the underlying equilibrium level.  

Thus, a robust strategy must detect regime changes and adjust exposure accordingly.

---

## 2. Choosing a Reversion Indicator  

A **reversion indicator** quantifies how far the current price is from its “fair” value. Below are three popular choices, with a focus on the one we’ll use for the backtest.

| Indicator | Formula | Typical Look‑back | Pros | Cons |
|-----------|---------|-------------------|------|------|
| **Bollinger‑Band Z‑score** | \( Z_t = \frac{P_t - \mu_{t}}{\sigma_{t}} \) | 20 days (μ = SMA, σ = STD) | Intuitive, captures volatility | Sensitive to outliers |
| **Half‑Life of OU** | \( \lambda = -\frac{\ln(\rho)}{\Delta t} \) (ρ = lag‑1 autocorr.) | 30‑60 days | Directly measures reversion speed | Requires regression each step |
| **RSI (Relative Strength Index)** | \( 100 - \frac{100}{1+RS} \) | 14 days | Widely available, non‑parametric | Bounded 0‑100, less granular |

**Why we pick the Bollinger‑Band Z‑score:**  

- It provides a standardized metric (units of σ) that is comparable across assets.  
- The 20‑day window balances responsiveness with noise reduction.  
- It integrates both price level (μ) and volatility (σ) – essential for risk‑adjusted sizing.

**Related**: [Untitled](/article-46)

---

## 3. Data Preparation  

We use daily adjusted close prices for **SPY** (the S&P 500 ETF) sourced via `yfinance`. The sample period (2010‑01‑01 → 2020‑12‑31) captures both bull and bear markets, offering a balanced test environment.

```python
import yfinance as yf
import pandas as pd

# Load data
spy = yf.download('SPY', start='2010-01-01', end='2020-12-31')
spy = spy['Adj Close'].to_frame(name='price')
spy.dropna(inplace=True)

# Compute 20‑day SMA and STD
spy['sma20'] = spy['price'].rolling(window=20).mean()
spy['std20'] = spy['price'].rolling(window=20).std()

# Z‑score (reversion indicator)
spy['zscore'] = (spy['price'] - spy['sma20']) / spy['std20']
spy.dropna(inplace=True)
spy.head()
```

The resulting `zscore` column is our **reversion indicator**. Positive values indicate the price is above the mean (potential short), negative values indicate it is below (potential long).

---

## 4. Defining the Mean Reversion Trading Strategy  

### 4.1 Entry Rules  

| Signal | Condition | Action |
|--------|-----------|--------|
| **Long** | `zscore <= -1.5` | Enter a long position (buy) |
| **Short** | `zscore >= +1.5` | Enter a short position (sell) |

The ±1.5 σ threshold captures roughly the outer 13 % of a normal distribution, providing a decent risk‑reward balance.

### 4.2 Exit Rules  

| Signal | Condition | Action |
|--------|-----------|--------|
| **Flat** | `-0.5 < zscore < 0.5` | Close any open position |
| **Time‑stop** | Position held > 15 days | Close position (limits drift) |

### 4.3 Position Sizing  

We allocate **1 % of equity per trade**, scaled by the inverse of the 20‑day realized volatility (`std20`). This **volatility‑adjusted sizing** keeps the dollar risk roughly constant across high‑ and low‑volatility periods.

**Related**: [Untitled](/article-6)

```python
initial_capital = 100_000
risk_per_trade = 0.01  # 1%

# Volatility scaling factor
spy['vol_target'] = spy['std20'] / spy['std20'].mean()
```

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 5. The Mean Reversion Backtest  

We implement the strategy in **Backtrader**, a Python backtesting engine that handles slippage, commissions, and portfolio bookkeeping.

```python
import backtrader as bt

class MeanReversion(bt.Strategy):
    params = dict(
        entry_z=1.5,
        exit_z=0.5,
        max_holding=15,
        risk=0.01,
    )
    
    def __init__(self):
        self.z = self.datas[0].zscore
        self.sma = self.datas[0].sma20
        self.std = self.datas[0].std20
        self.entry_price = None
        self.bar_executed = 0

    def next(self):
        # Exit condition
        if self.position

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

**Related**: [Untitled](/article-36)

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-6)
- [Untitled](/article-46)
- [Untitled](/article-36)
- [Untitled](/article-16)
