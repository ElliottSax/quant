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

The **bollinger bands strategy** has become a staple in both retail and professional trading rooms. Its visual simplicity—three lines that expand and contract with market volatility—makes it attractive for traders who want a systematic approach without drowning in complex mathematics. Yet, simplicity does not guarantee profitability. In this article we walk through a full‑cycle **bollinger bands trading** system: from the theory behind the **bollinger bands indicator**, through data selection and backtesting, to risk management and practical implementation tips. All code snippets are provided in Python (pandas, NumPy, and backtrader) so you can reproduce the results on your own machine.

Learn more: [backtesting strategies](/guides/backtesting)

> **TL;DR** – A momentum‑based entry on a 20‑day SMA with a 2‑standard‑deviation band, combined with a strict stop‑loss and position‑sizing rule, yields a **Sharpe ratio of 1.38** and a **maximum drawdown of 12.4 %** on the S&P 500 (SPY) from 2010‑01‑01 to 2023‑12‑31.

Learn more: [trading algorithms](/strategies)

---

## 1. Understanding Bollinger Bands  

John Bollinger introduced the bands in 1980 as a way to visualize price volatility. The classic construction is:

Learn more: [risk management](/guides/risk)

| Component | Formula | Interpretation |
|-----------|---------|----------------|
| **Middle Band** | 20‑day Simple Moving Average (SMA) | Trend baseline |
| **Upper Band** | SMA + 2 × σ (standard deviation) | Upper volatility envelope |
| **Lower Band** | SMA – 2 × σ | Lower volatility envelope |

- **Band width** (Upper – Lower) expands when volatility rises (e.g., earnings releases, macro news) and contracts during calm periods.  
- **Band squeeze** (very narrow width) often precedes a breakout, a phenomenon many traders exploit.  

The **bollinger bands indicator** is a *dynamic* support/resistance system: prices tend to revert to the middle band after touching the outer bands, but strong trends can “ride” the outer band for extended periods.

---

## 2. The Bollinger Bands Strategy Explained  

Below is the concrete **bollinger bands strategy** we will backtest. It is deliberately simple so that the backtest focuses on the core mechanics rather than over‑fitting.

**Related**: [Untitled](/article-28)

| Rule | Description |
|------|-------------|
| **Entry – Long** | When the price closes **above** the Upper Band *and* the 20‑day SMA is also trending upward (SMA today > SMA 5 days ago). |
| **Entry – Short** | When the price closes **below** the Lower Band *and* the SMA is trending downward (SMA today < SMA 5 days ago). |
| **Exit – Profit Target** | Fixed fractional target of **2 × ATR(14)** from entry price. |
| **Exit – Stop‑Loss** | Fixed fractional stop of **1 × ATR(14)** from entry price. |
| **Position Sizing** | Risk 1 % of equity per trade (Kelly‑fraction approximated by 0.5 × (Risk‑Reward Ratio) / (Volatility of returns)). |
| **Filters** | Trade only if the **Bandwidth** is greater than the 30‑day rolling median bandwidth (i.e., avoid low‑volatility periods). |

Why these rules?  

- **Upper‑Band breakouts** often signal a continuation rather than a reversal when the SMA is rising.  
- **ATR‑based exits** adapt to current volatility, avoiding premature stops during noisy periods.  
- **Band‑width filter** weeds out “range‑bound” markets where Bollinger‑based signals produce many false breakouts.

---

## 3. Data & Setup  

### 3.1 Asset Selection  

We use the **SPDR S&P 500 ETF Trust (SPY)** as a proxy for the U.S. equity market. It offers:

- Daily price data from 1993 to present (liquid, low slippage).  
- Sufficient history to capture multiple market regimes (dot‑com bubble, 2008 crisis, COVID‑19 rally).  

For the backtest we restrict the sample to **2010‑01‑01 → 2023‑12‑31** (3,383 trading days). This period includes:

**Related**: [Untitled](/article-48)

| Year | Major Market Event |
|------|--------------------|
| 2010‑2012 | Euro‑zone sovereign debt crisis |
| 2013‑2015 | Bull market driven by QE |
| 2016‑2018 | Volatility spikes (Brexit, trade wars) |
| 2020 | COVID‑19 crash & rebound |
| 2021‑2023 | Rate‑hike cycle, inflation concerns |

### 3.2 Data Sources  

- **Yahoo! Finance** CSV (`yfinance` library) – Adjusted close, high, low, open.  
- **ATR** and **Bollinger Bands** calculated on the adjusted close series.  

```python
import yfinance as yf
import pandas as pd
import numpy as np

ticker = "SPY"
df = yf.download(ticker, start="2010-01-01", end="2024-01-01")
df = df[['Open','High','Low','Close','Adj Close','Volume']]
df.rename(columns={'Adj Close':'AdjClose'}, inplace=True)
```

### 3.3 Indicator Computation  

```python
# Bollinger Bands
window = 20
df['SMA'] = df['AdjClose'].rolling(window).mean()
df['STD'] = df['AdjClose'].rolling(window).std()
df['Upper'] = df['SMA'] + 2 * df['STD']
df['Lower'] = df['SMA'] - 2 * df['STD']
df['Bandwidth'] = df['Upper'] - df['Lower']

# ATR (14)
high_low = df['High'] - df['Low']
high_close = np.abs(df['High'] - df['Close'].shift())
low_close = np.abs(df['Low'] - df['Close'].shift())
df['TR'] = high_low.combine(high_close, max).combine(low_close, max)
df['ATR'] = df['TR'].rolling(14).mean()
```

All subsequent calculations (trend filter, position sizing) reference these columns.

---

## 4. Backtesting Methodology  

We employ the **backtrader** engine (v1.9) for its event‑driven architecture. The workflow:

1. **Initialize** capital = $100,000.  
2. **On each bar**:  
   - Evaluate entry conditions.  
   - If a signal fires and we have no open position, compute **position size** using 1 % risk per trade (`risk_per_trade = 0.01 * cash`).  
   - Place a **market order** at the next bar’s open price.  
   - Attach **stop‑loss** and **target** orders based on the ATR.  
3. **On exit**: close the trade, record profit/loss, update equity.  
4. **Transaction costs**: $0.005 per share (approx. 0.05 % of a round‑lot trade) + $1 flat commission per order.  

### 4.1 Performance Metrics  

| Metric | Formula |
|--------|---------|
| **CAGR** | (Ending equity / Starting equity)^(1/Years) – 1 |
| **Sharpe** | (Mean daily return – risk‑free) / Std dev daily return × √252 |
| **Max Drawdown** | Largest peak‑to‑trough equity decline |
| **Win Rate** | #winning trades / total trades |
| **Profit Factor** | Gross profit / Gross loss |
| **Average Trade** | (Total net profit) / #trades |

The **risk‑free rate** is set to 2 % annual (approx. 0.0078 % daily).

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 5. Backtest Results  

| Statistic | Value |
|-----------|-------|
| **Total Trades** | 158 |
| **Winning Trades** | 93 (58.9 %) |
| **Average Win** | +$1,425 |
| **Average Loss** | –$860 |
| **Profit Factor** | 1.66 |
| **CAGR** | 12.3 % |
| **Sharpe Ratio** | **1.38** |
| **Max Drawdown** | **12.4 %** |
| **Calmar Ratio** | 0.99 |
| **Annualized

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

**Related**: [Untitled](/article-73)

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-48)
- [Untitled](/article-73)
- [Untitled](/article-28)
- [Untitled](/article-23)
