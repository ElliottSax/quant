---
title: "Pivot Point Trading Strategy: Daily, Weekly, Monthly Levels"
description: "Master pivot point trading with Standard, Fibonacci, and Camarilla calculations. Learn intraday and swing strategies with pivot levels."
date: "2026-03-12"
author: "Dr. James Chen"
category: "Technical Analysis"
tags: ["pivot points", "intraday trading", "support resistance", "day trading", "technical analysis"]
keywords: ["pivot point trading strategy", "pivot point calculator", "pivot point levels"]
---
# Pivot Point Trading Strategy: Daily, Weekly, Monthly Levels

Pivot point trading is a time-tested methodology used extensively by floor traders and institutional desks to identify intraday support and resistance levels. Unlike discretionary support/resistance analysis, pivot points are calculated mathematically from the prior period's high, low, and close, producing objective levels that thousands of traders watch simultaneously. This shared attention creates self-reinforcing price reactions at pivot levels, making them among the most reliable intraday reference points available.

This guide covers the three main pivot point calculation methods, practical [trading strategies](/blog/backtesting-trading-strategies) for each, and the framework for integrating pivot levels into a complete trading system.

## Standard Pivot Point Calculation

The classic (floor trader) pivot point formula produces a central pivot and three levels of support and resistance:

**Central Pivot Point (PP):**
PP = (High + Low + Close) / 3

**Resistance Levels:**
- R1 = (2 x PP) - Low
- R2 = PP + (High - Low)
- R3 = High + 2 x (PP - Low)

**Support Levels:**
- S1 = (2 x PP) - High
- S2 = PP - (High - Low)
- S3 = Low - 2 x (High - PP)

For a stock that traded with a high of $152, low of $148, and close of $150:
- PP = ($152 + $148 + $150) / 3 = $150.00
- R1 = (2 x $150) - $148 = $152.00
- S1 = (2 x $150) - $152 = $148.00
- R2 = $150 + ($152 - $148) = $154.00
- S2 = $150 - ($152 - $148) = $146.00

These levels are plotted on the chart before the market opens, providing a roadmap for the trading session.

## Fibonacci Pivot Points

Fibonacci pivot points use the same central pivot but apply Fibonacci ratios to the prior range for support and resistance levels:

**PP** = (High + Low + Close) / 3
**R1** = PP + 0.382 x (High - Low)
**R2** = PP + 0.618 x (High - Low)
**R3** = PP + 1.000 x (High - Low)
**S1** = PP - 0.382 x (High - Low)
**S2** = PP - 0.618 x (High - Low)
**S3** = PP - 1.000 x (High - Low)

Fibonacci pivots tend to produce tighter support/resistance clusters than standard pivots, which many traders prefer for trading liquid markets like ES futures, major forex pairs, and large-cap stocks.

## Camarilla Pivot Points

Camarilla pivots, developed by Nick Scott in 1989, use a multiplier system that produces levels closer to the current price, making them particularly useful for mean-reversion intraday strategies:

**H4** = Close + 1.1 x (High - Low) / 2
**H3** = Close + 1.1 x (High - Low) / 4
**H2** = Close + 1.1 x (High - Low) / 6
**H1** = Close + 1.1 x (High - Low) / 12
**L1** = Close - 1.1 x (High - Low) / 12
**L2** = Close - 1.1 x (High - Low) / 6
**L3** = Close - 1.1 x (High - Low) / 4
**L4** = Close - 1.1 x (High - Low) / 2

The key Camarilla levels are H3, H4, L3, and L4. H3 and L3 are reversal levels ([mean reversion](/blog/mean-reversion-strategies-guide)), while H4 and L4 are breakout levels (trend continuation).

## Trading Strategy 1: Pivot Bounce (Mean Reversion)

The pivot bounce strategy trades reversals at pivot support and resistance levels.

**Setup Requirements:**
- Price approaches a pivot level (PP, S1, R1, S2, R2)
- A reversal candlestick pattern forms at the level (hammer, engulfing, doji)
- Volume supports the reversal (ideally above average)

**For Long Entries (at support):**
- Entry: Above the high of the confirmation candle at S1 or S2
- Stop-Loss: Below S1 by the average range of the last 5 candles, or below S2 if entering at S1
- Target: The central pivot point (PP) or R1

**For Short Entries (at resistance):**
- Entry: Below the low of the confirmation candle at R1 or R2
- Stop-Loss: Above R1 by the average range of the last 5 candles, or above R2 if entering at R1
- Target: PP or S1

**Win Rate Expectation:** Backtesting across major index futures shows pivot bounce strategies at S1 and R1 produce win rates between 55-62% with risk/reward ratios of approximately 1:1.2 to 1:1.5.

## Trading Strategy 2: Pivot Breakout

When price breaks through a pivot level with conviction, it often continues to the next level.

**Setup Requirements:**
- Price breaks above R1 (for longs) or below S1 (for shorts)
- The breakout candle closes beyond the level
- Volume increases on the breakout

**Long Entry:**
- Enter above R1 when the candle closes above it
- Stop-Loss: Below R1 (the broken level should now act as support)
- Target: R2 (first target), R3 (extended target)

**Short Entry:**
- Enter below S1 when the candle closes below it
- Stop-Loss: Above S1
- Target: S2 (first target), S3 (extended target)

**Filter:** Track whether the market opened above or below the central pivot. Markets that open above PP tend to trend higher (favoring long breakouts at R1), while markets that open below PP tend to trend lower (favoring short breakouts at S1).

## Trading Strategy 3: Central Pivot Range

The Central Pivot Range (CPR) uses three lines that bracket the area around the central pivot:

- **Top Central Pivot (TC)** = (PP - BC) + PP
- **Pivot Point (PP)** = (High + Low + Close) / 3
- **Bottom Central Pivot (BC)** = (High + Low) / 2

The width of the CPR provides a directional bias:
- **Narrow CPR** (TC and BC are close together): Expect a trending day with a breakout from the range
- **Wide CPR**: Expect a rangebound day with [mean reversion](/blog/mean-reversion-trading-strategy) from the edges

On narrow CPR days, focus on breakout strategies. On wide CPR days, focus on bounce strategies at CPR edges.

## Multi-Timeframe Pivot Analysis

Daily pivots are most common, but weekly and monthly pivots provide higher-timeframe context that strengthens daily pivot signals:

**Weekly Pivots:** Calculated using the prior week's high, low, and close. These levels are significant for swing traders and often align with key daily levels during the week.

**Monthly Pivots:** Calculated from the prior month's data. These represent the strongest pivot levels and are watched by institutional traders for position management.

**Confluence Trading:** When a daily pivot level falls within 0.25% of a weekly or monthly pivot level, the confluence creates a high-probability reaction zone. These aligned levels produce the strongest bounce and breakout signals.

## Python Implementation

```python
import pandas as pd

def calculate_pivots(high, low, close, method='standard'):
    pp = (high + low + close) / 3

    if method == 'standard':
        r1 = (2 * pp) - low
        r2 = pp + (high - low)
        r3 = high + 2 * (pp - low)
        s1 = (2 * pp) - high
        s2 = pp - (high - low)
        s3 = low - 2 * (high - pp)
    elif method == 'fibonacci':
        diff = high - low
        r1 = pp + 0.382 * diff
        r2 = pp + 0.618 * diff
        r3 = pp + 1.000 * diff
        s1 = pp - 0.382 * diff
        s2 = pp - 0.618 * diff
        s3 = pp - 1.000 * diff

    return {'PP': pp, 'R1': r1, 'R2': r2, 'R3': r3,
            'S1': s1, 'S2': s2, 'S3': s3}
```

## Key Takeaways

- Pivot points provide objective, mathematically calculated support and resistance levels that thousands of traders watch simultaneously.
- Three main methods exist: Standard (floor trader), Fibonacci, and Camarilla, each suited to different trading styles and market conditions.
- The central pivot (PP) serves as the session's directional bias: price above PP is bullish, below PP is bearish.
- Narrow CPR days favor breakout strategies, while wide CPR days favor mean-reversion approaches.
- Multi-timeframe pivot analysis (daily + weekly + monthly) identifies the highest-probability trading zones through confluence.
- Always use confirmation signals ([candlestick patterns](/blog/candlestick-patterns-complete-guide), volume) rather than blindly trading at pivot levels.

## Frequently Asked Questions

### Which pivot point method is best for day trading?

Standard pivot points are the most widely used and therefore produce the strongest self-reinforcing reactions for major markets like S&P 500 futures, EUR/USD, and large-cap stocks. Camarilla pivots work well for scalping strategies in highly liquid markets due to their tighter levels. Fibonacci pivots are preferred by traders who already use Fibonacci analysis as part of their broader technical framework. Test each method on your specific market and timeframe before committing.

### Should pivot points be calculated using regular trading hours or extended hours data?

For equities, use regular trading hours (RTH) data for pivot calculations. Extended hours volume is typically thin and can produce extreme high/low values that distort pivot levels. For 24-hour markets like forex or crypto, use the prior day's candlestick from your broker's server time (commonly New York close at 5:00 PM ET for forex). Consistency is more important than which specific cutoff you choose.

### How often do prices react to pivot levels?

Analysis of S&P 500 E-mini futures across multiple years shows that price touches or comes within 0.1% of at least one pivot level (PP, S1, R1, S2, R2) approximately 85% of trading days. Meaningful reactions (reversal of at least 0.25%) occur at these levels roughly 60-70% of the time. The central pivot point (PP) is touched on approximately 70% of trading days.

### Can pivot points be used for swing trading?

Yes, weekly and monthly pivot points are effective for swing trading. Weekly pivots provide support and resistance levels for multi-day holding periods, and monthly pivots serve as significant reference levels for position management. Many swing traders use weekly pivots for entries and exits while using monthly pivots for overall directional bias and risk management.
