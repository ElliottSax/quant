---
title: "ADX Indicator: Measuring Trend Strength for Better Entries"
description: "Master the ADX indicator to measure trend strength and filter trading signals. Learn +DI/-DI crossovers, ADX thresholds, and trend-following strategies."
date: "2026-03-16"
author: "Dr. James Chen"
category: "Technical Analysis"
tags: ["ADX", "trend strength", "directional movement", "DMI", "technical analysis"]
keywords: ["ADX indicator", "average directional index", "ADX trend strength"]
---

# ADX Indicator: Measuring Trend Strength for Better Entries

The Average Directional Index (ADX), developed by J. Welles Wilder Jr. in 1978, answers a fundamental question that most indicators ignore: how strong is the current trend? While momentum oscillators like RSI and the stochastic measure price direction and overbought/oversold conditions, the ADX exclusively measures trend strength regardless of direction. An ADX reading of 30 indicates a strong trend whether the market is going up or down. This unique property makes the ADX an essential filter for any trading strategy, as the strength of a trend directly determines whether trend-following or mean-reversion approaches are more appropriate.

This guide covers the complete ADX system, including the Directional Movement Index (+DI/-DI) crossovers, ADX thresholds, and practical strategies for integrating ADX into your trading.

## The Directional Movement System

The ADX is part of a broader system called the Directional Movement System, which includes three components:

### +DI (Positive Directional Indicator)

Measures the strength of upward price movement. Calculated from the Positive Directional Movement (+DM), which is the current high minus the prior high (when it exceeds the prior low minus the current low and is positive).

### -DI (Negative Directional Indicator)

Measures the strength of downward price movement. Calculated from the Negative Directional Movement (-DM), which is the prior low minus the current low (when it exceeds the current high minus the prior high and is positive).

### ADX (Average Directional Index)

The smoothed average of the Directional Index (DX), where DX = |+DI - -DI| / (+DI + -DI) x 100. The standard smoothing period is 14.

## Complete ADX Calculation

The calculation proceeds through several steps:

**Step 1: Calculate +DM and -DM for each period**
- +DM = Current High - Prior High (if positive and > |Prior Low - Current Low|, else 0)
- -DM = Prior Low - Current Low (if positive and > |Current High - Prior High|, else 0)

**Step 2: Calculate True Range (TR)**
- TR = max(Current High - Current Low, |Current High - Prior Close|, |Current Low - Prior Close|)

**Step 3: Smooth over 14 periods (Wilder's smoothing)**
- Smoothed +DM14 = Prior +DM14 - (Prior +DM14 / 14) + Current +DM
- Same for -DM14 and TR14

**Step 4: Calculate +DI and -DI**
- +DI14 = (Smoothed +DM14 / Smoothed TR14) x 100
- -DI14 = (Smoothed -DM14 / Smoothed TR14) x 100

**Step 5: Calculate DX**
- DX = (|+DI14 - -DI14| / (+DI14 + -DI14)) x 100

**Step 6: Calculate ADX**
- ADX = 14-period smoothed average of DX (Wilder's smoothing method)

## Interpreting ADX Values

ADX readings provide a clear framework for assessing trend strength:

| ADX Value | Trend Strength | Trading Implication |
|-----------|---------------|---------------------|
| 0-15 | Absent/Weak | No trend; avoid trend-following strategies |
| 15-25 | Developing | Trend may be emerging; prepare but wait for confirmation |
| 25-50 | Strong | Trend is established; trend-following strategies appropriate |
| 50-75 | Very Strong | Powerful trend; trail stops tightly, expect potential exhaustion |
| 75-100 | Extremely Strong | Rare; often seen in crisis/euphoria; unsustainable |

### ADX Direction Matters

The value of ADX tells you strength, but the direction of ADX tells you whether the trend is strengthening or weakening:

- **Rising ADX:** The trend (up or down) is gaining momentum. Trend-following entries are favorable.
- **Falling ADX:** The trend is losing momentum. Existing positions should tighten stops; new trend-following entries are risky.
- **Flat ADX below 20:** The market is rangebound. Mean-reversion strategies are appropriate.

## Trading Strategy 1: +DI/-DI Crossover with ADX Filter

The Directional Movement crossover system generates trend-following signals filtered by ADX strength.

**Bullish Signal:**
- +DI crosses above -DI (directional shift to bullish)
- ADX is above 20 (confirming sufficient trend strength exists)
- ADX is rising (confirming the trend is strengthening)

**Bearish Signal:**
- -DI crosses above +DI
- ADX is above 20 and rising

**Entry:** On the crossover candle's close
**Stop-Loss:** Below the swing low that preceded the crossover (longs) or above the swing high (shorts)
**Exit:** When ADX turns down from above 40 (trend weakening), or when a reverse crossover occurs

**Performance Note:** The +DI/-DI crossover without ADX filtering produces excessive false signals in rangebound markets. Adding the ADX > 20 filter eliminates approximately 40-50% of losing trades in non-trending conditions, significantly improving net profitability.

## Trading Strategy 2: ADX Breakout System

This strategy uses ADX to identify the transition from range to trend, entering positions at the start of new trends.

**Setup:**
1. ADX has been below 20 for at least 10 periods (confirming a range-bound condition)
2. ADX crosses above 20 (indicating a new trend is developing)
3. +DI and -DI have separated (indicating direction)

**Entry:**
- If +DI is above -DI when ADX crosses 20: Enter long
- If -DI is above +DI when ADX crosses 20: Enter short

**Stop-Loss:** The midpoint of the range that preceded the breakout
**Target:** Trail with a 2x ATR trailing stop, as new trends can extend significantly

**Rationale:** Periods of low ADX (below 20) correspond to volatility compression and consolidation. When the ADX finally rises above 20, a new trend is emerging from the consolidation, and these breakouts often produce sustained directional moves.

## Trading Strategy 3: ADX Trend Exhaustion Filter

High ADX readings can signal trend exhaustion, providing contrarian setups.

**Setup:**
- ADX rises above 45-50 (indicating a very strong, potentially overextended trend)
- ADX begins to turn downward from above 45
- A divergence appears on RSI or stochastic (price makes new extreme but momentum does not)

**Entry:** Counter to the prevailing trend when ADX turns down and a confirmation signal appears (reversal candlestick, momentum divergence)
**Stop-Loss:** Beyond the extreme made during the high ADX reading
**Target:** The 20-period SMA (mean reversion) or the prior consolidation zone

This is an advanced strategy that should be used with caution. Strong trends can remain strong longer than expected, and premature counter-trend entries can be costly. The ADX turndown from above 45 is a necessary condition, but a momentum divergence provides the confirming evidence needed to act.

## Using ADX as a Strategy Filter

Perhaps the most valuable application of ADX is as a filter for other trading strategies:

### For Trend-Following Strategies (Moving Average Crossovers, Breakouts)
- **Enable:** When ADX > 25 and rising
- **Disable:** When ADX < 20

### For Mean-Reversion Strategies (RSI, Stochastic, Bollinger Bands)
- **Enable:** When ADX < 20
- **Disable:** When ADX > 30

### For Breakout Strategies
- **Enable:** When ADX has been below 20 for 10+ periods and begins rising
- **Disable:** When ADX is above 40 (breakout has already occurred)

This filtering mechanism alone can improve the profitability of most trading systems by ensuring that trend-following signals are only taken when a trend exists and mean-reversion signals are only taken when the market is ranging.

## Python Implementation

```python
import pandas as pd
import numpy as np

def adx(df, period=14):
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff().multiply(-1)

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    # When +DM > -DM, keep +DM, else 0 (and vice versa)
    plus_dm[plus_dm < minus_dm] = 0
    minus_dm[minus_dm < plus_dm] = 0

    tr = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )

    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx_val = dx.ewm(alpha=1/period, adjust=False).mean()

    return adx_val, plus_di, minus_di
```

## Key Takeaways

- ADX measures trend strength on a 0-100 scale without indicating direction. Readings above 25 indicate a tradeable trend; below 20 indicates a ranging market.
- Rising ADX signals strengthening momentum; falling ADX signals weakening momentum, regardless of whether the trend is up or down.
- The +DI/-DI crossover system provides directional signals, but these should always be filtered by ADX level to avoid false signals in rangebound markets.
- ADX below 20 for extended periods followed by a rise above 20 often signals the beginning of a new trend, providing early breakout entries.
- The most practical use of ADX is as a filter for other strategies: enable trend-following when ADX > 25, enable mean-reversion when ADX < 20.
- Very high ADX readings (above 45-50) that begin declining can signal trend exhaustion, but counter-trend trades require additional confirmation (divergences, reversal patterns).

## Frequently Asked Questions

### What is a good ADX reading for trend trading?

An ADX reading above 25 generally indicates sufficient trend strength for trend-following strategies to be profitable. Readings between 25 and 50 represent the most tradeable conditions, as the trend is strong enough to produce directional moves but not so extreme that exhaustion is imminent. Readings above 50 indicate very powerful trends that warrant tighter trailing stops and awareness of potential reversal.

### Why does ADX sometimes lag?

ADX uses Wilder's smoothing method, which is equivalent to an exponential moving average. The 14-period default setting means the ADX takes time to reflect changes in trend strength. The DX (unsmoothed) responds faster but is noisier. Some traders use a shorter period (7-10) for the ADX smoothing to increase responsiveness, though this comes at the cost of more false signals.

### How do you trade when ADX is falling?

A falling ADX indicates that the current trend is losing momentum. This does not necessarily mean a reversal is occurring; it may simply mean the market is transitioning from trending to ranging. When ADX is falling, reduce position sizes, tighten trailing stops on existing trend-following positions, and begin looking for mean-reversion setups. Avoid entering new trend-following positions until ADX stabilizes and begins rising again.

### Can ADX be used for cryptocurrency trading?

Yes, ADX works well for cryptocurrency markets. Due to crypto's tendency toward strong directional moves, ADX readings above 25 are common during trending periods. The 14-period default setting on daily charts remains appropriate. For crypto-specific adjustments, some traders use a slightly longer period (20) to smooth out the higher baseline volatility, but this is a minor refinement rather than a necessity.
