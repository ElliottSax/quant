---
title: Untitled
date: 2026-03-06
author: Stack Guide
category: strategies
tags: []
lastmod: 2026-03-06
description: Comprehensive guide to untitled---
# Mean Reversion Strategy: Backtest & Implementation
*Target audience: retail traders & quant enthusiasts*
---

## Table of Contents  

1. [What Is Mean Reversion?](#what-is-mean-reversion)  
2. [Why It Still Works in Modern Markets](#why-it-still-works-in-modern-markets)  
3. [Choosing a Reversion Indicator](#choosing-a-reversion-indicator)  
4. [Data & Universe Selection](#data--universe-selection)  
5. [Backtesting Framework (Python Example)](#backtesting-framework-python-example)  
6. [Backtest Results on Historical Data](#backtest-results-on-historical-data)  
7. [Risk Management & Position Sizing](#risk-management--position-sizing)  
8. [From Backtest to Live Trading](#from-backtest-to-live-trading)  
9. [Common Pitfalls & How to Avoid Them](#common-pitfalls--how-to-avoid-them)  
10. [Key Take‑aways](#key-take‑aways)  

Learn more: [backtesting strategies](/guides/backtesting)

---  

## What Is Mean Reversion?  

A **mean reversion trading strategy** assumes that price (or any statistical series) tends to drift back toward its historical average after deviating significantly. In mathematical terms, the series follows an Ornstein‑Uhlenbeck process:

Learn more: [trading algorithms](/strategies)

\[
dX_t = \theta (\mu - X_t) dt + \sigma dW_t
\]

where  

* \( \mu \) – long‑run mean,  
* \( \theta \) – speed of reversion,  
* \( \sigma \) – volatility,  
* \( W_t \) – Wiener process.  

Learn more: [risk management](/guides/risk)

If the current price is far above \( \mu \), the expected drift is negative (a **sell** signal). If it’s far below, the expected drift is positive (a **buy** signal).  

Mean reversion is not limited to single‑stock price; it can be applied to:  

* **Pairs** (e.g., Coca‑Cola vs. Pepsi),  
* **Spread** of a basket (e.g., sector ETFs),  
* **Volatility** or **volume** indicators,  
* **Technical metrics** such as Bollinger Bands, Z‑score of moving averages, or the **Relative Strength Index (RSI)**.  

---

## Why It Still Works in Modern Markets  

| Reason | Explanation |
|--------|-------------|
| **Liquidity & Market Microstructure** | High‑frequency order flow creates short‑lived imbalances that correct quickly. |
| **Behavioral Biases** | Over‑reaction to news, herd behavior, and anchoring lead to temporary price excursions. |
| **Regulatory Constraints** | Short‑selling restrictions and margin limits can delay correction, creating exploitable windows. |
| **Statistical Arbitrage** | Systematic strategies have grown, but many still rely on statistical regularities that persist. |

Even after decades of algorithmic trading, **mean reversion backtest** results remain robust when the model respects transaction costs and realistic execution slippage.

---

## Choosing a Reversion Indicator  

Below are three widely used **reversion indicators**. Pick one that matches your data frequency and trading horizon.

| Indicator | Calculation | Typical Look‑back | Signal Logic |
|-----------|-------------|-------------------|--------------|
| **Bollinger Bands (BB)** | Upper = SMA\(_{n}\) + k·σ, Lower = SMA\(_{n}\) – k·σ | n = 20 days, k = 2 | Price > Upper ⇒ Short; Price < Lower ⇒ Long |
| **Z‑Score of a Moving Average** | \(Z_t = \frac{P_t - \mu_{n}}{\sigma_{n}}\) | n = 30 days | Z > 1.5 ⇒ Short; Z < -1.5 ⇒ Long |
| **Pairs‑Spread Z‑Score** | \(\text{Spread}_t = P^A_t - \beta P^B_t\) → Z‑score of spread | n = 60 days | Same thresholds as above but applied to spread |

For this article we’ll focus on **Bollinger Bands** because they are intuitive, easy to code, and work well on equity ETFs such as **SPY** (the S&P 500 ETF).

**Related**: [Untitled](/article-61)

---

## Data & Universe Selection  

| Asset | Ticker | Frequency | Period | Source |
|-------|--------|-----------|--------|--------|
| S&P 500 ETF | SPY | Daily | 2005‑01‑01 → 2020‑12‑31 | Yahoo! Finance (adjusted close) |
| Risk‑free rate | 3‑Month T‑Bill | Daily | Same | FRED (via `pandas_datareader`) |

*Why SPY?*  
- High liquidity (average daily volume > 80 M shares).  
- Representative of the broad US equity market.  
- Minimal corporate actions (splits/dividends are already reflected in adjusted close).  

All data were cleaned for missing days (weekends/holidays) and forward‑filled for the risk‑free series.

**Related**: [Untitled](/article-11)

---

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## Backtesting Framework (Python Example)  

Below is a **self‑contained** backtest that can be run in a Jupyter notebook or a script. It uses only `pandas`, `numpy`, and `matplotlib`.  

```python
# --------------------------------------------------------------
# Mean Reversion Backtest – Bollinger Bands on SPY (2005‑2020)
# --------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from pandas_datareader import data as pdr

# ------------------------------------------------------------------
# 1. Load data
# ------------------------------------------------------------------
yf.pdr_override()  # use yfinance backend
spy = pdr.get_data_yahoo('SPY', start='2005-01-01', end='2020-12-31')
spy = spy['Adj Close'].to_frame(name='price')
spy['return'] = spy['price'].pct_change()

# Risk‑free rate (annualized 3‑M T‑Bill) – convert to daily
ffr = pdr.DataReader('DTB3', 'fred',
                     start='2005-01-01', end='2020-12-31')
ffr = ffr['DTB3'] / 100  # percent → decimal
ffr = ffr.resample('D').ffill().fillna(method='bfill')
ffr_daily = (1 + ffr) ** (1/252) - 1
spy['rf'] = ffr_daily.reindex(spy.index, method='ffill')

# ------------------------------------------------------------------
# 2. Bollinger Band parameters
# ------------------------------------------------------------------
N = 20               # SMA window
K = 2.0              # Std‑dev multiplier
spy['sma'] = spy['price'].rolling(N).mean()
spy['std'] = spy['price'].rolling(N).std()
spy['upper'] = spy['sma'] + K * spy['std']
spy['lower'] = spy['sma'] - K * spy['std']

# ------------------------------------------------------------------
# 3. Generate signals
# ------------------------------------------------------------------
# Long when price < lower; Short when price > upper
spy['position'] = 0
spy.loc[spy['price'] < spy['lower'], 'position'] = 1   # long
spy.loc[spy['price'] > spy['upper'], 'position'] = -1 # short

# Forward‑fill positions (hold until opposite signal)
spy['position'] = spy['position'].replace(to_replace=0, method='ffill')
spy['position'].fillna(0, inplace=True)

# ------------------------------------------------------------------
# 4. Compute strategy returns (gross)
# ------------------------------------------------------------------
spy['strategy_gross'] = spy['position'].shift(1) * spy['return']

# ------------------------------------------------------------------
# 5. Transaction cost model
# ------------------------------------------------------------------
TC = 0.0005          # 5 bps per round‑trip trade
spy['trade'] = spy['position'].diff().abs()
spy['tc'] = TC * spy['trade']
spy['strategy_net'] = spy['strategy_gross'] - spy['tc']

# ------------------------------------------------------------------
# 6. Performance metrics
# ------------------------------------------------------------------
def annualized_ret(series):
    return (1 + series).prod() ** (252/len(series)) - 1

def annualized_vol(series):
    return series.std() * np.sqrt(252)

def sharpe(series, rf_series):
    excess = series - rf_series
    return annualized_ret(excess) / annualized_vol(excess)

def max_dd(series):
    cum = (1 + series).cumprod()
    high = cum.c

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

**Related**: [Untitled](/article-31)

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-11)
- [Untitled](/article-31)
- [Untitled](/article-61)
- [Untitled](/article-6)
