---
title: Untitled
date: 2026-03-06
author: Stack Guide
category: strategies
tags: []
lastmod: 2026-03-06
description: Comprehensive guide to untitled---
# Bollinger Bands Strategy: Complete Backtest
*Keywords: **bollinger bands strategy**, bollinger bands trading, bollinger bands indicator*
---

## Introduction  

The **bollinger bands strategy** has become a staple in the toolbox of both retail traders and professional quants. Its visual simplicity—three lines that expand and contract with market volatility—makes it attractive for quick decision‑making, while its statistical foundation (a moving average plus/minus a multiple of standard deviation) offers a rigorous way to capture mean‑reversion or breakout dynamics.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we walk through a **complete backtest** of a popular Bollinger Bands trading system, using real historical data, a transparent Python backtesting framework, and a thorough risk‑management overlay. By the end you will have:

Learn more: [trading algorithms](/strategies)

* A clear description of the Bollinger Bands indicator and the exact entry/exit rules of our **bollinger bands trading** model.  
* Step‑by‑step code snippets that you can paste into a QuantTrading.vercel.app notebook.  
* A full set of performance metrics (CAGR, Sharpe, max drawdown, win‑rate, etc.) and a sensitivity analysis of the key parameters.  
* Practical guidance on position sizing, stop‑loss placement, and the pitfalls that often trip up naïve implementations.  

Learn more: [risk management](/guides/risk)

The goal is not to sell a “magic bullet” but to demonstrate a **data‑driven**, reproducible approach that you can adapt to your own asset universe and risk appetite.  

---

## Understanding Bollinger Bands  

Bollinger Bands were introduced by John Bollinger in the 1980s. The classic construction is:

| Component | Formula | Typical Parameter |
|-----------|---------|-------------------|
| Middle Band | Simple Moving Average (SMA) of *N* periods | *N* = 20 |
| Upper Band | SMA + *K* × σ (standard deviation) | *K* = 2 |
| Lower Band | SMA – *K* × σ | *K* = 2 |

*Why it works*: When volatility spikes, the bands widen; when markets are calm, they contract. Prices that touch or breach the outer bands are statistically rare (≈5% of the time for *K* = 2) and often precede a reversal, while a **squeeze**—a period of very narrow bands—can foreshadow a strong upcoming move.

For a **bollinger bands indicator**‑based strategy we can exploit two distinct phenomena:

1. **Mean‑reversion**: Price reverts toward the middle band after hitting an outer band.  
2. **Breakout**: A sustained move beyond the outer band signals a new trend.  

Our backtest focuses on the first phenomenon (mean‑reversion) because it yields a higher win‑rate and is easier to model with realistic transaction costs.

---

## Designing the Bollinger Bands Strategy  

### Core Rules  

| Condition | Action |
|-----------|--------|
| **Long entry** | Price closes **below** the lower band *and* the SMA is trending up (SMA\_today > SMA\_yesterday). |
| **Short entry** | Price closes **above** the upper band *and* the SMA is trending down (SMA\_today < SMA\_yesterday). |
| **Exit** | Close the position when price touches the middle band **or** after a maximum holding period of 10 days, whichever comes first. |
| **Stop‑loss** | 1.5 × (Upper‑Band – Lower‑Band) away from entry price (dynamic based on current volatility). |
| **Position size** | Fixed fraction of equity (2% per trade) scaled by the inverse of the band width (volatility‑adjusted). |

### Rationale  

* The SMA trend filter reduces false signals during sideways markets.  
* Using the middle band as an exit point aligns with the mean‑reversion premise: once price re‑approaches the average, the expected drift diminishes.  
* A dynamic stop‑loss tied to band width respects the underlying volatility — tighter bands mean tighter stops, preventing premature exits in low‑vol environments.

### Parameter Choices  

* **N = 20** (20‑day SMA) – standard for daily data.  
* **K = 2** – gives a 95% confidence envelope.  
* **Holding limit = 10 days** – caps exposure while allowing enough time for a reversion.  

**Related**: [Untitled](/article-13)

We will later test the sensitivity of *N* and *K* to see how robust the performance is.

---

## Data Selection and Preparation  

| Symbol | Exchange | Period | Frequency |
|--------|----------|--------|-----------|
| **SPY** (S&P 500 ETF) | NYSE | 2000‑01‑03 → 2023‑12‑29 | Daily |
| **AAPL** | NASDAQ | 2000‑01‑03 → 2023‑12‑29 | Daily |
| **EURUSD** (FX) | Oanda | 2000‑01‑03 → 2023‑12‑29 | Daily |

We selected a diversified set (equity, ETF, FX) to illustrate that the **bollinger bands strategy** works across asset classes. Data were sourced from **Yahoo Finance** (for equities) and **Oanda** (for FX) and cleaned as follows:

1. Remove rows with missing `Adj Close`.  
2. Align dates across symbols to a common calendar (business days).  
3. Compute the SMA and standard deviation using a rolling window of *N* = 20.  
4. Store the three band columns (`upper`, `middle`, `lower`) for later reference.  

A quick sanity check on SPY’s 2020‑2021 period shows the classic “COVID‑19 squeeze”: band width shrank dramatically in February 2020 and exploded in March 2020, providing a textbook illustration of volatility‑driven signal generation.

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## Backtesting Framework  

We employed **Backtrader**, a Python library that integrates seamlessly with QuantTrading.vercel.app notebooks. The skeleton code is reproduced below (≈30 lines) to help you reproduce the results instantly.

**Related**: [Untitled](/article-28)

```python
import backtrader as bt
import pandas as pd
import yfinance as yf

# -------------------------------------------------
# 1. Load data
# -------------------------------------------------
ticker = "SPY"
df = yf.download(ticker, start="2000-01-01", end="2023-12-31")
df = df[['Adj Close']].rename(columns={'Adj Close': 'close'})

# -------------------------------------------------
# 2. Compute Bollinger Bands
# -------------------------------------------------
N = 20
K = 2.0
df['sma'] = df['close'].rolling(N).mean()
df['std'] = df['close'].rolling(N).std()
df['upper'] = df['sma'] + K * df['std']
df['lower'] = df['sma'] - K * df['std']
df.dropna(inplace=True)

# -------------------------------------------------
# 3. Define Strategy
# -------------------------------------------------
class BBMeanReversion(bt.Strategy):
    params = dict(N=N, K=K, risk_per_trade=0.02, max_holding=10)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma = self.datas[0].sma
        self.upper = self.datas[0].upper
        self.lower = self.datas[0].lower
        self.middle = self.datas[0].sma

    def next(self):
        # Check for existing position
        if not self.position:
            # LONG entry
            if (self.dataclose[0] < self.lower[0]) and (self.sma[0] > self.sma[-1]):
                size = self.broker.getcash() * self.p.risk_per_trade / (self.upper[0] - self.lower[0])
                self.buy(size=size)
               

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.

**Related**: [Untitled](/article-48)



---

## You May Also Like

- [Untitled](/article-13)
- [Untitled](/article-48)
- [Untitled](/article-28)
- [Untitled](/article-23)
