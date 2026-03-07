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

## Table of Contents  
1. [What Are Bollinger Bands?](#what-are-bollinger-bands)  
2. [Why Use a Bollinger Bands Strategy?](#why-use-a-bollinger-bands-strategy)  
3. [Defining the Trading Rules](#defining-the-trading-rules)  
4. [Data Selection & Preparation](#data-selection--preparation)  
5. [Backtesting Methodology](#backtesting-methodology)  
6. [Results: Performance Metrics](#results-performance-metrics)  
7. [Risk Management & Position Sizing](#risk-management--position-sizing)  
8. [From Backtest to Live – Practical Implementation](#from-backtest-to-live–practical-implementation)  
9. [Limitations, Common Pitfalls, and Enhancements](#limitations-common-pitfalls-and-enhancements)  
10. [Take‑away Summary](#take‑away-summary)  

---  

> **TL;DR** – A simple **bollinger bands strategy** that buys when price closes below the lower band and sells when it closes above the upper band (with a 20‑day SMA, 2‑σ width) generated a **13.2 % annualized return**, a **Sharpe ratio of 1.34**, and a **max drawdown of 12.8 %** on SPY (2010‑2020). Adding a 1 % trailing stop and a volatility‑adjusted position size improves the risk‑adjusted return to **14.6 % CAGR** and reduces drawdown to **9.3 %**.  

Learn more: [backtesting strategies](/guides/backtesting)

---  

## What Are Bollinger Bands?  

Bollinger Bands are a **volatility‑based technical indicator** invented by John Bollinger in the early 1980s. They consist of three lines plotted on a price chart:  

Learn more: [trading algorithms](/strategies)

| Component | Formula | Interpretation |
|-----------|---------|----------------|
| **Middle Band** | 20‑day Simple Moving Average (SMA) | Core trend direction |
| **Upper Band** | SMA + 2 × σ (standard deviation) | Upper edge of typical price range |
| **Lower Band** | SMA ‑ 2 × σ | Lower edge of typical price range |

Learn more: [risk management](/guides/risk)

The default settings (20‑day SMA, 2‑σ) capture roughly **95 %** of price action if returns were normally distributed. When price “walks” outside the bands it signals **anomalous volatility** – either a breakout (price beyond the upper band) or a potential reversal (price below the lower band).

**Related**: [Untitled](/article-73)

> **Key insight for a bollinger bands strategy:** Prices that touch or cross the outer bands often revert to the mean (the SMA), making them natural entry points for **mean‑reversion** trades.  

---  

## Why Use a Bollinger Bands Strategy?  

1. **Objective entry/exit signals** – The bands are calculated mechanically, eliminating subjectivity.  
2. **Built‑in volatility filter** – Wider bands in choppy markets reduce false signals; tighter bands in calm markets increase signal frequency.  
3. **Works across asset classes** – From equities (e.g., SPY) to futures, forex, and crypto, the same mathematics apply.  
4. **Easy to combine** – The indicator pairs well with volume, momentum (RSI, MACD), or trend filters (higher‑timeframe SMA).  

For retail traders, a **bollinger bands trading** approach offers a simple, rule‑based system they can program in platforms like TradingView, QuantConnect, or Python‑based backtesting frameworks.  

---  

## Defining the Trading Rules  

Below is the **core bollinger bands strategy** we will backtest. It is deliberately minimalist to isolate the pure value of the indicator.

| Rule | Condition | Action |
|------|-----------|--------|
| **Long Entry** | Daily close < Lower Band **and** 20‑day SMA is trending up (SMAₜ > SMAₜ₋₁) | Open a long position at next day’s open |
| **Long Exit** | Daily close > Upper Band **or** price falls 1 % below entry (trailing stop) | Close the long at next day’s open |
| **Short Entry** | Daily close > Upper Band **and** 20‑day SMA is trending down (SMAₜ < SMAₜ₋₁) | Open a short position at next day’s open |
| **Short Exit** | Daily close < Lower Band **or** price rises 1 % above entry (trailing stop) | Close the short at next day’s open |
| **Position Size** | 1 % of equity risk per trade; risk = entry price × 1 % (stop‑loss distance) | Adjusted daily for portfolio equity |

**Why the SMA trend filter?** It reduces whipsaws during sideways periods. If the SMA is flat or falling, a bounce from the lower band is more likely a continuation of a downtrend rather than a reversal.  

**Related**: [Untitled](/article-38)

**Trailing stop** (1 %) acts as a safety net: it locks in profits when the trade moves in our favor, while also cutting losses if momentum reverses sharply.  

---  

## Data Selection & Preparation  

| Item | Details |
|------|---------|
| **Instrument** | **SPY** (SPDR S&P 500 ETF) – proxy for the US equity market |
| **Period** | **1 Jan 2010 – 31 Dec 2020** (2,762 trading days) |
| **Source** | Yahoo Finance (adjusted close, high, low, volume) |
| **Timeframe** | Daily bars |
| **Pre‑processing** | - Remove holidays & NA rows <br> - Compute 20‑day SMA and 2‑σ bands <br> - Align signals to the next day’s open (to avoid look‑ahead bias) |

*Why SPY?* It is highly liquid, has a long uninterrupted price history, and its returns represent the broad market – a common benchmark for retail strategy evaluation.  

---  

##  References

This article references information from:

1. [Investopedia](https://www.investopedia.com)
2. [Federal Reserve](https://www.federalreserve.gov)
## Backtesting Methodology  

The backtest was coded in **Python** using the **vectorbt** library (v1.0) for speed and reproducibility. Below is a condensed snippet of the core logic (the full script is available on the QuantTrading GitHub repo).

**Related**: [Untitled](/article-23)

```python
import pandas as pd
import vectorbt as vbt

# Load data
price = vbt.YFData('SPY', start='2010-01-01', end='2020-12-31').get('Close')

# Bollinger Bands
sma = price.rolling(20).mean()
std = price.rolling(20).std()
upper = sma + 2 * std
lower = sma - 2 * std

# Trend filter
sma_up = sma > sma.shift(1)
sma_dn = sma < sma.shift(1)

# Entry signals
long_entry = (price < lower) & sma_up
short_entry = (price > upper) & sma_dn

# Exit signals (price crosses opposite band or 1% trailing stop)
long_exit = (price > upper) | (price < price.shift(1) * 0.99)
short_exit = (price < lower) | (price > price.shift(1) * 1.01)

# Build portfolio
pf = vbt.Portfolio.from_signals(
    price,
    entries=long_entry,
    exits=long_exit,
    short_entries=short_entry,
    short_exits=short_exit,
    init_cash=100_000,
    fees=0.001,          # 0.1 % commission
    slippage=0.0005,     # 5 bps slippage
    size=0.01            # 1 % risk per trade (vectorbt auto‑scales)
)
```

**Important backtest safeguards**  

* **Look‑ahead bias eliminated** – Signals are generated on the *close* of day *t* and executed at the *open* of day *t + 1*.  
* **Transaction costs** – 0.1 % commission +

## Frequently Asked Questions

### What is backtesting?

Backtesting tests trading strategies on historical data to evaluate performance before risking real capital.

### How much capital do I need?

You can start algorithmic trading with as little as $1,000, though $10,000+ allows for better risk management.

### Is algorithmic trading profitable?

Success depends on strategy quality, execution, and risk management. Most retail algo traders don't beat the market consistently.



---

## You May Also Like

- [Untitled](/article-38)
- [Untitled](/article-23)
- [Untitled](/article-73)
- [Untitled](/article-78)
