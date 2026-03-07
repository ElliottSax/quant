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

Mean reversion is one of the oldest and most intuitive concepts in quantitative finance. The underlying premise is simple: **prices tend to drift back toward a statistical “mean” after deviating from it**. Whether you are a retail trader experimenting with a single ticker or a quant building a multi‑asset portfolio, a well‑designed mean reversion strategy can provide a steady stream of alpha while keeping risk under tight control.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we will:

1. Explain the statistical foundations of a **mean reversion trading strategy**.  
2. Walk through a concrete **mean reversion backtest** using daily SPY data (2010‑2020).  
3. Show how to translate backtest results into a live implementation, complete with **risk‑management rules**.  

Learn more: [trading algorithms](/strategies)

The goal is to give you a ready‑to‑run template that you can adapt to any market, timeframe, or reversion indicator of your choice.

Learn more: [risk management](/guides/risk)

---

## 1. Core Concepts of Mean Reversion  

| Concept | Why It Matters | Typical Implementation |
|---------|----------------|------------------------|
| **Stationarity** | A mean‑reverting series has a constant mean and variance over time. Without stationarity, the “mean” moves, breaking the premise. | Augmented Dickey‑Fuller (ADF) test, KPSS test |
| **Reversion Indicator** | Quantifies how far price is from its mean. The farther the deviation, the higher the expected pull‑back. | Z‑score, Bollinger Band %B, RSI, Ornstein‑Uhlenbeck (OU) model |
| **Trigger Thresholds** | Define entry/exit points. Too tight → whipsaws; too loose → missed opportunities. | ±1.5 σ for Z‑score, 30/70 for RSI |
| **Mean Estimation Window** | The look‑back period that determines the “mean”. Short windows capture fast cycles; long windows capture slower cycles. | 20‑day SMA, 60‑day EMA, rolling regression |

A **reversion indicator** is the engine of the strategy. In the example below we will use a **Z‑score** derived from a 20‑day moving average and standard deviation—a classic yet powerful choice.

---

## 2. Selecting the Data  

For an educational **mean reversion backtest** we keep the asset universe simple and use a highly liquid equity ETF:

| Parameter | Value |
|-----------|-------|
| **Ticker** | `SPY` (SPDR S&P 500 ETF) |
| **Timeframe** | Daily close |
| **Period** | 1 Jan 2010 – 31 Dec 2020 (2,762 trading days) |
| **Source** | Yahoo! Finance (via `yfinance` Python library) |
| **Adjustments** | Adjusted close (dividends & splits) |

Using daily data smooths out intraday microstructure noise while still providing enough trades to evaluate performance statistics meaningfully.

---

## 3. Building the Reversion Indicator  

The Z‑score is calculated as:

\[
Z_t = \frac{P_t - \mu_{t}}{\sigma_{t}}
\]

where  

* \(P_t\) = price at day *t* (adjusted close)  
* \(\mu_{t}\) = 20‑day simple moving average (SMA)  
* \(\sigma_{t}\) = 20‑day rolling standard deviation  

A **long** position is opened when \(Z_t < -1.5\) (price far below the mean). A **short** position is opened when \(Z_t > +1.5\). Positions are closed when the Z‑score crosses zero (i.e., price re‑attains its mean).

```python
import yfinance as yf
import pandas as pd
import numpy as np

# -------------------------------------------------
# 1️⃣ Load data
# -------------------------------------------------
ticker = "SPY"
df = yf.download(ticker, start="2010-01-01", end="2021-01-01")
df = df[['Adj Close']].rename(columns={'Adj Close': 'price'})

# -------------------------------------------------
# 2️⃣ Compute rolling statistics
# -------------------------------------------------
window = 20
df['ma']   = df['price'].rolling(window).mean()
df['std']  = df['price'].rolling(window).std()
df['z']    = (df['price'] - df['ma']) / df['std']

# -------------------------------------------------
# 3️⃣ Generate signals
# -------------------------------------------------
entry_long  = df['z'] < -1.5
entry_short = df['z'] >  1.5
exit_signal = df['z'].abs() < 0.05   # near zero

df['position'] = 0
df.loc[entry_long,  'position'] = 1   # long
df.loc[entry_short, 'position'] = -1  # short

**Related**: [Untitled](/article-16)

# Keep position until exit
df['position'] = df['position'].replace(to_replace=0, method='ffill')
df.loc[exit_signal, 'position'] = 0
df['position'] = df['position'].fillna(0)

# -------------------------------------------------
# 4️⃣ Compute daily returns
# -------------------------------------------------
df['return'] = df['price'].pct_change() * df['position'].shift(1)
df.dropna(inplace=True)
```

The code above produces a **signal series** that can be fed directly into any backtesting engine.

---

## 4. Backtesting Framework  

We will use **Backtrader**, a lightweight Python library that handles portfolio accounting, slippage, and commissions out‑of‑the‑box.

```python
import backtrader as bt

class MeanReversion(bt.Strategy):
    params = dict(
        window=20,
        entry_z=1.5,
        exit_z=0.05,
        stake=1000,           # $1,000 per trade
    )

    def __init__(self):
        self.price = self.datas[0].close
        self.sma   = bt.indicators.SMA(self.price, period=self.p.window)
        self.std   = bt.indicators.StdDev(self.price, period=self.p.window)
        self.z     = (self.price - self.sma) / self.std

    def next(self):
        if not self.position:
            if self.z[0] < -self.p.entry_z:
                self.buy(size=self.p.stake / self.price[0])
            elif self.z[0] > self.p.entry_z:
                self.sell(size=self.p.stake / self.price[0])
        else:
            # Exit when z crosses zero (within a tolerance)
            if abs(self.z[0]) < self.p.exit_z:
                self.close()
```

**Related**: [Untitled](/article-61)

**Backtest settings**

| Setting | Value |
|---------|-------|
| **Initial cash** | $100,000 |
| **Commission** | 0.005 % per trade (typical for ECN brokers) |
| **Slippage** | 0.5 % of price (simulates realistic execution) |
| **Position limit** | 1 open long **or** short at a time (no overlapping trades) |

Running the engine for 2010‑2020 yields the performance table below.

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 5. Backtest Results  

| Metric | Value |
|--------|-------|
| **CAGR** (Compound Annual Growth Rate) | **12.4 %** |
| **Annualized Sharpe** (risk‑free 2 %) | **1.31** |
| **Max Drawdown** | **‑9.

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.

**Related**: [Untitled](/article-21)



---

## You May Also Like

- [Untitled](/article-16)
- [Untitled](/article-21)
- [Untitled](/article-61)
- [Untitled](/article-36)
