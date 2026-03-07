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

Mean reversion is one of the most intuitive concepts in quantitative finance: **prices tend to drift back toward an average value over time**. When a security deviates far enough from its historical norm, a *mean reversion trading strategy* bets that the price will swing back toward that norm, generating a profit.  

Learn more: [backtesting strategies](/guides/backtesting)

In this article we will:

1. Explain the statistical foundations of mean reversion.  
2. Walk through a **complete mean reversion backtest** on real‑world data (SPY 2000‑2020).  
3. Show how to translate the backtest into a live‑trading implementation.  
4. Discuss risk‑management techniques that protect capital while preserving upside.  

Learn more: [trading algorithms](/strategies)

All code snippets are written in Python and rely on open‑source libraries (pandas, NumPy, matplotlib, and Backtrader). You can copy‑paste them into a Jupyter notebook and run them end‑to‑end.  

Learn more: [risk management](/guides/risk)

> **Keywords** – *mean reversion trading strategy*, *mean reversion backtest*, *reversion indicator*  

---  

## 1. Why Mean Reversion Works (and When It Fails)  

### 1.1 Statistical Basis  

Mean‑reverting processes are often modeled with an **Ornstein‑Uhlenbeck (OU) diffusion**:

\[
dX_t = \theta(\mu - X_t)dt + \sigma dW_t
\]

* \( \mu \) – long‑run equilibrium level (the “mean”).  
* \( \theta \) – speed of reversion: larger values pull the process back faster.  
* \( \sigma \) – volatility of the random shock.  

If a price series follows an OU process, the distance from the mean (the **z‑score**) is normally distributed, making it a natural **reversion indicator**.

### 1.2 Market Regimes  

Mean reversion thrives in:

| Regime | Typical Characteristics |
|--------|--------------------------|
| **Range‑bound** | Prices oscillate within a tight band; volatility is moderate. |
| **Mean‑reverting pairs** | Two correlated assets diverge temporarily (e.g., Coca‑Cola vs Pepsi). |
| **Post‑news over‑reaction** | Sharp spikes that settle back after the initial shock. |

Mean reversion **breaks down** during strong trends, structural breaks (e.g., a company’s business model changes), or when transaction costs dominate the expected profit. Recognizing the regime is part of risk management (see Section 5).

---  

## 2. Data & Tools  

### 2.1 Data Source  

For the backtest we’ll use **daily adjusted close prices of the SPDR S&P 500 ETF (SPY)** from 01‑Jan‑2000 to 31‑Dec‑2020. The data is freely available via Yahoo Finance:

```python
import yfinance as yf
import pandas as pd

spy = yf.download('SPY', start='2000-01-01', end='2020-12-31')
spy = spy['Adj Close'].rename('SPY')
```

**Related**: [Untitled](/article-6)

### 2.2 Required Packages  

```bash
pip install pandas numpy matplotlib backtrader yfinance
```

* `pandas` – data manipulation.  
* `numpy` – numerical operations.  
* `matplotlib` – visualisation.  
* `backtrader` – backtesting engine (handles slippage, commission, and order management).  

---  

## 3. Building the Mean Reversion Indicator  

Two popular **reversion indicators** are:

| Indicator | Formula | Typical Look‑back |
|-----------|---------|-------------------|
| **Z‑Score of a rolling mean** | \( z_t = \frac{P_t - \mu_{t}}{\sigma_{t}} \) | 20‑60 days |
| **Bollinger Bands** | Upper = \( \mu_{t} + k\sigma_{t} \); Lower = \( \mu_{t} - k\sigma_{t} \) | 20 days, \(k=2\) |

We’ll implement the Z‑Score because it directly measures deviation from the mean and is easy to threshold.

```python
import numpy as np

def add_zscore(df, window=30):
    """Append rolling mean, std, and z‑score to a price series."""
    df['Mean'] = df['SPY'].rolling(window).mean()
    df['Std']  = df['SPY'].rolling(window).std()
    df['Z']    = (df['SPY'] - df['Mean']) / df['Std']
    return df.dropna()
    
spy_df = add_zscore(spy.to_frame(), window=30)
```

**Signal rule**  

* **Long entry** when \( Z_t < -1.5 \) → price is far below its mean.  
* **Short entry** when \( Z_t > +1.5 \) → price is far above its mean.  
* **Exit** when the Z‑score crosses zero (i.e., price re‑enters the mean).  

These thresholds are a common starting point; you can optimise them later.

---  

## 4. The Mean Reversion Backtest  

### 4.1 Backtrader Strategy Skeleton  

```python
import backtrader as bt

class MeanReversion(bt.Strategy):
    params = dict(
        z_entry = 1.5,      # absolute Z‑score needed to trigger a trade
        z_exit  = 0.0,      # exit when Z‑score crosses zero
        size    = 1000,     # number of shares per trade (fixed size)
        stoploss = 0.02,    # 2% stop‑loss on each position
    )

**Related**: [Untitled](/article-46)

    def __init__(self):
        # Pull the pre‑calculated Z‑score from the data feed
        self.z = self.datas[0].Z

    def next(self):
        # No open position?
        if not self.position:
            if self.z[0] < -self.p.z_entry:
                self.buy(size=self.p.size)
            elif self.z[0] >  self.p.z_entry:
                self.sell(size=self.p.size)

        # Position exists – check exit or stop‑loss
        else:
            # Exit when Z‑score crosses zero
            if (self.position.size > 0 and self.z[0] > self.p.z_exit) or \
               (self.position.size < 0 and self.z[0] < -self.p.z_exit):
                self.close()

            # Simple 2% trailing stop‑loss
            cur_price = self.datas[0].close[0]
            entry_price = self.position.price
            if self.position.size > 0:
                if cur_price <= entry_price * (1 - self.p.stoploss):
                    self.close()
            else:
                if cur_price >= entry_price * (1 + self.p.stoploss):
                    self.close()
```

### 4.2 Feeding the Data  

Backtrader expects a `PandasData` subclass that includes the custom column `Z`.

```python
class ZScoreData(bt.feeds.PandasData):
    cols = (
        ('Z', -1),   # column index -1 tells Backtrader to look up by name
    )
    # Inherit all default columns (Open, High, Low, Close, Volume, OpenInterest)
    
data = ZScoreData(dataname=spy_df)
```

###  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 4.3 Running the Engine  

**Related**: [Untitled](/article-56)

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(MeanReversion)
cerebro.adddata(data)
cerebro.broker.setcash(100_000)          # initial capital
cerebro.broker.setcommission(commission=0.0005)  # 

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-46)
- [Untitled](/article-6)
- [Untitled](/article-56)
- [Untitled](/article-21)
