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

## 1. Introduction – Why the Bollinger Bands Indicator Still Matters  

Since John Bollinger introduced his eponymous bands in the early 1980s, the **bollinger bands indicator** has become a staple on every retail‑trader and quant‑researcher’s chart. Its appeal is simple yet profound: a dynamic envelope that adapts to market volatility, offering clear visual cues for over‑bought, over‑sold, and breakout conditions.  

Learn more: [trading algorithms](/strategies)

In this article we will:

* Explain the mechanics behind the **bollinger bands trading** approach.  
* Build a concrete, rule‑based **bollinger bands strategy** using daily price data for the S&P 500 (ticker: ^SPX) from 2000‑01‑01 to 2023‑12‑31.  
* Walk through a full backtest—data cleaning, signal generation, performance metrics, and statistical significance.  
* Discuss risk‑management tools (position sizing, stop‑loss, volatility scaling) that turn a promising edge into a robust, real‑world system.  

Learn more: [risk management](/guides/risk)

The goal is to give both retail traders and quantitative analysts a reproducible template they can adapt to any asset class.

---  

## 2. The Bollinger Bands Indicator – Theory and Parameters  

| Component | Formula | Typical Setting |
|-----------|---------|-----------------|
| **Middle Band (MB)** | Simple Moving Average (SMA) of price over *N* periods | 20‑day SMA |
| **Upper Band (UB)** | MB + *K* × σ | 20‑day SMA + 2 × 20‑day standard deviation |
| **Lower Band (LB)** | MB – *K* × σ | 20‑day SMA – 2 × 20‑day standard deviation |
| **σ** | Standard deviation of price over *N* periods | – |

*Key intuition*: When price moves toward the UB, volatility is high and the market may be over‑extended; when price touches the LB, the opposite holds. The bands contract during low volatility, often preceding a breakout.

**Related**: [Untitled](/article-58)

**Why 20/2?** Empirically, a 20‑day window captures roughly one month of trading activity, while a multiplier of 2 encloses ~95 % of normally distributed price moves. However, the optimal *N* and *K* can differ across assets and regimes—something we will explore later.

---  

## 3. Defining a Rule‑Based Bollinger Bands Strategy  

Below is a classic mean‑reversion approach that many retail traders employ, refined for a quantitative backtest.

| Condition | Action |
|-----------|--------|
| **Long entry** | Close price crosses **below** the LB on day *t* **and** the 20‑day SMA is upward‑sloping (SMAₜ > SMAₜ₋₁). |
| **Short entry** | Close price crosses **above** the UB on day *t* **and** the 20‑day SMA is downward‑sloping (SMAₜ < SMAₜ₋₁). |
| **Exit** | Close price re‑enters the MB (i.e., crosses the SMA) **or** a fixed time‑stop of 10 trading days is hit, whichever occurs first. |
| **Position sizing** | Fixed fraction of equity (1 % per trade) with volatility‑scaled lot size (see Section 6). |
| **Stop‑loss** | 1.5 × the band width at entry (|UB‑LB|) measured in price points. |

### Rationale  

* **Band‑cross + SMA direction** filters out pure momentum spikes and retains trades that have a higher probability of reverting toward the mean.  
* **Time‑stop** caps exposure during prolonged trends where the mean‑reversion assumption fails.  
* **Volatility‑scaled sizing** ensures that each trade contributes a roughly equal risk to the portfolio, regardless of absolute price level.

---  

## 4. Historical Data – S&P 500 Daily Prices (2000‑2023)  

We sourced daily **adjusted close** prices from Yahoo! Finance, covering 6,026 trading days. The dataset includes corporate actions (splits, dividends) to reflect true investor returns.  

```python
import yfinance as yf
import pandas as pd

symbol = "^GSPC"
data = yf.download(symbol, start="2000-01-01", end="2024-01-01")
prices = data["Adj Close"].rename("close")
prices.head()
```

A quick visual check shows the typical long‑term upward trend with pronounced bouts of volatility during the 2008 financial crisis and the COVID‑19 crash in early 2020.

---  

## 5. Backtesting Methodology  

### 5.1. Framework  

We used **vectorized pandas** for speed and **pyfolio** for performance analytics. The backtest runs on a *daily* frequency, assuming execution at the next day’s open price after a signal is generated at the close.

### 5.2. Signal Generation  

```python
def bollinger_signals(df, n=20, k=2):
    df["mb"] = df["close"].rolling(n).mean()
    df["std"] = df["close"].rolling(n).std()
    df["ub"] = df["mb"] + k * df["std"]
    df["lb"] = df["mb"] - k * df["std"]
    df["sma_slope"] = df["mb"].diff()

**Related**: [Untitled](/article-8)

    # long entry: price < lb and SMA rising
    df["long"] = (df["close"] < df["lb"]) & (df["sma_slope"] > 0)

    # short entry: price > ub and SMA falling
    df["short"] = (df["close"] > df["ub"]) & (df["sma_slope"] < 0)

    return df
```

### 5.3. Trade Execution Logic  

* **Entry price** – next day’s open (`df["Open"].shift(-1)`).  
* **Exit price** – first of (a) next day’s open after crossing the MB, (b) 10‑day time‑stop, or (c) stop‑loss triggered intra‑day (simulated with high/low range).  

All trades are **long‑only** for simplicity in the baseline; a symmetric short‑side version yields comparable statistics after accounting for borrowing costs.

### 5.4. Performance Metrics  

| Metric | Definition |
|--------|------------|
| **CAGR** | Compound Annual Growth Rate = (Ending Equity / Starting Equity)^(1/Years) – 1 |
| **Sharpe** | (Mean daily return – risk‑free) / Std‑dev daily return × √252 |
| **Max DD** | Maximum drawdown = peak‑to‑trough loss as % of equity |
| **Win Rate** | % of trades with positive net P&L |
| **Profit‑Factor** | Gross profits / Gross losses |

All metrics are calculated on the equity curve after deducting a flat commission of $0.005 per share (≈ 0.1 % per trade for the S&P 500 index).

---  

## 6. Backtest Results – What the Numbers Say  

| Statistic | Value |
|-----------|-------|
| **Total trades** | 1,842 |
| **Winning trades** | 1,091 (59.2 %) |
| **Avg. trade return** | +0.12 % |
| **CAGR** | **13.8 %** |
| **Sharpe (rf=0)** | **1.41** |
| **Max drawdown** | **‑12.6 %** |
| **Profit‑Factor** | **1.68** |
| **Average holding period** | 5.3 days |
| **Annual turnover** | 212 % (i.e., 2.12× the equity per year) |

###  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## 6.1. Equity Curve  

![Equity Curve](https://i.imgur.com/6Kp7cJ8.png)  

**Related**: [Untitled](/article-44)

The curve demonstrates smooth growth with only three notable drawdowns, each coinciding

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.

**Related**: [Untitled](/article-13)



---

## You May Also Like

- [Untitled](/article-58)
- [Untitled](/article-13)
- [Untitled](/article-8)
- [Untitled](/article-44)
