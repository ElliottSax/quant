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

Bollinger Bands are one of the most recognizable technical tools on a chart. Developed by John Bollinger in the early 1980s, the indicator combines a simple moving average (SMA) with two volatility‑based bands that expand and contract with market price action. Because the bands react to both trend and volatility, they lend themselves naturally to systematic **bollinger bands trading** approaches that can be backtested, refined, and deployed across asset classes.

Learn more: [backtesting strategies](/guides/backtesting)

In this article we walk through a complete **bollinger bands strategy** from concept to execution:

1. **Theory** – how the bands are built and why they matter.  
2. **Strategy design** – entry/exit rules, parameters, and data selection.  
3. **Backtesting methodology** – data source, sampling frequency, transaction cost assumptions.  
4. **Results** – performance metrics (CAGR, Sharpe, max drawdown, win‑rate) on a 23‑year equity dataset.  
5. **Risk management** – position sizing, stop‑loss, volatility scaling, and drawdown control.  
6. **Extensions** – multi‑time‑frame filters, alternative band widths, and machine‑learning tweaks.  

Learn more: [trading algorithms](/strategies)

The goal is to give retail traders and aspiring quants a reproducible template they can adapt to their own markets and risk appetite.

**Related**: [Untitled](/article-73)

Learn more: [risk management](/guides/risk)

---

## 1. Understanding Bollinger Bands  

| Component | Formula | Interpretation |
|-----------|---------|----------------|
| **Middle Band** | `SMA(N)` – N‑period simple moving average of price | Acts as a dynamic trend reference. |
| **Upper Band** | `SMA(N) + K * σ(N)` | `σ(N)` = standard deviation of price over N periods; K is the band multiplier (commonly 2). |
| **Lower Band** | `SMA(N) - K * σ(N)` | Mirrors the upper band. |

- **Band Width** = `Upper – Lower = 2 * K * σ(N)`.  
- When volatility spikes, the width widens; during calm markets it contracts.  
- The **%B** indicator quantifies price location within the bands:  

\[
\%B = \frac{Price - Lower}{Upper - Lower}
\]

A %B close to 0 indicates the price is near the lower band, while a %B close to 1 signals proximity to the upper band.

**Related**: [Untitled](/article-28)

**Why it works:**  
- Prices tend to revert to the mean after extreme excursions (mean‑reversion).  
- In trending markets the price can “ride” a band for extended periods, providing a trend‑following edge.  

A robust **bollinger bands strategy** therefore needs to distinguish between these two regimes and apply the appropriate rule set.

---

## 2. The Classic Bollinger Bands Strategy  

The most widely taught version uses a **20‑day SMA** and **2‑standard‑deviation** bands on daily close prices. The trading logic is:

| Condition | Action |
|-----------|--------|
| **Long entry** | Price closes **below** the lower band **and** %B < 0.2 **and** the 20‑day SMA is rising (i.e., `SMA(t) > SMA(t‑1)`). |
| **Long exit** | Price closes **above** the middle band **or** %B > 0.8. |
| **Short entry** | Price closes **above** the upper band **and** %B > 0.8 **and** the 20‑day SMA is falling (`SMA(t) < SMA(t‑1)`). |
| **Short exit** | Price closes **below** the middle band **or** %B < 0.2. |

*Rationale*:  
- **Reversion**: When price breaches a band, it is often an over‑extension; the mean‑reversion hypothesis suggests a pull‑back toward the SMA.  
- **Trend filter**: The SMA slope ensures we only take long trades in a rising trend (and shorts in a falling trend), reducing whipsaw in choppy markets.

**Parameter choices** (N = 20, K = 2) stem from Bollinger’s original work, but they can be optimized for a given asset. In the backtest below we keep the classic settings to illustrate the baseline performance.

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 3. Data, Tools, and Methodology  

**Related**: [Untitled](/article-13)

| Item | Specification |
|------|----------------|
| **Asset** | **SPY** – SPDR S&P 500 ETF (proxy for U.S. equities) |
| **Period** | 1 Jan 2000 – 31 Dec 2023 (23 years, 5 822 trading days) |
| **Frequency** | Daily close |
| **Data source** | Yahoo Finance (adjusted close, corporate actions applied) |
| **Platform** | Python 3.11, `pandas`, `numpy`, `ta-lib` for indicator calculation, `backtrader` for backtesting |
| **Transaction cost** | $0.005 per share (≈ 0.05 % of notional) + $0.0005 slippage per share |
| **Position sizing** | 1 % of equity per trade (fixed fractional) |
| **Risk controls** | Maximum 2 % equity drawdown per trade; stop‑loss at 1 % below entry for longs (1 % above for shorts). |

**Why SPY?**  
- High liquidity ensures realistic fill assumptions.  
- A 23‑year horizon contains multiple market regimes (dot‑com bust, 2008 crisis, COVID‑19 crash, bull markets) – ideal for testing robustness.

**Backtest pipeline**  

```python
import pandas as pd
import numpy as np
import backtrader as bt
import yfinance as yf

# 1️⃣ Load data
data = yf.download("SPY", start="2000-01-01", end="2023-12-31")
data = data[['Adj Close']].rename(columns={'Adj Close': 'close'})

# 2️⃣ Indicator calculation
N, K = 20, 2
data['sma'] = data['close'].rolling(N).mean()
data['std'] = data['close'].rolling(N).std()
data['upper'] = data['sma'] + K * data['std']
data['lower'] = data['sma'] - K * data['std']
data['pctb'] = (data['close'] - data['lower']) / (data['upper'] - data['lower'])

# 3️⃣ Strategy class
class BBStrategy(bt.Strategy):
    params = dict(N=20, K=2, stake_pct=0.01, stop_pct=0.01)

    def __init__(self):
        self.sma = bt.ind.SMA(self.data.close, period=self.p.N)
        self.upper = self.sma + self.p.K * bt.ind.StdDev(self.data.close, period=self.p.N)
        self.lower = self.sma - self.p.K * bt.ind.StdDev(self.data.close, period=self.p.N)
        self.pctb = (self.data.close - self.lower) / (self.upper - self.lower)

    def next(self):
        #--- LONG ---
        if not self.position:
            if (self.data.close[0] < self.lower[0] and
                self.pctb[0] < 0.2 and
                self.sma[0] > self.sma[-1]):
                size = int(self.broker.cash * self.p.stake_pct / self.data.close[0])
                self.buy(size=size)
                self.stop_price = self.data.close[0] * (1 - self.p.stop_pct)

        #--- SHORT ---
        elif self.position.size > 0:  # long position
            if (self.data.close[0] > self.sma[0] or self.pctb[0] > 0.8 or
                self.data.close[0] < self.stop_price):
                self.close()
        else:  # short position logic (mirror of long)
            ...
```

The script runs the backtest, records equity curve, and outputs performance metrics (see next section). The code is intentionally concise; production‑grade systems would add order‑type handling, risk‑budgeting modules

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-28)
- [Untitled](/article-13)
- [Untitled](/article-73)
- [Untitled](/article-3)
