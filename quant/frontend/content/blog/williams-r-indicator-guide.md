---
title: "Williams %R Indicator: Complete Trading Strategy Guide"
description: "Master Williams %R for momentum trading. Learn calculation, overbought/oversold signals, failure swings, and divergence strategies with examples."
date: "2026-03-15"
author: "Dr. James Chen"
category: "Technical Analysis"
tags: ["williams %R", "momentum indicator", "oscillator", "overbought oversold", "technical analysis"]
keywords: ["williams %R indicator", "williams percent range", "williams %R trading strategy"]
---

# Williams %R Indicator: Complete Trading Strategy Guide

Williams %R, developed by legendary trader Larry Williams in 1973, is a momentum oscillator that measures the current closing price relative to the highest high over a lookback period. Despite being one of the simplest indicators to calculate and interpret, Williams %R provides highly effective signals for identifying overbought and oversold conditions, momentum shifts, and potential trend reversals. Its inverse relationship with the Stochastic Oscillator makes it a natural complement to any momentum-based trading framework.

This guide covers the indicator's mechanics, signal interpretation, and three proven trading strategies with specific entry, exit, and risk management rules.

## Williams %R Calculation

The formula for Williams %R is:

**%R = ((Highest High - Close) / (Highest High - Lowest Low)) x -100**

Where:
- **Highest High** = Highest high over the lookback period (typically 14 periods)
- **Lowest Low** = Lowest low over the lookback period
- **Close** = Current closing price

The result ranges from -100 to 0:
- **-100** = The close equals the lowest low of the lookback period (maximum oversold)
- **0** = The close equals the highest high of the lookback period (maximum overbought)

### Relationship to the Stochastic Oscillator

Williams %R is mathematically the inverse of the Fast Stochastic %K, multiplied by -100:

- Stochastic %K measures how close the price is to the period high (0 to 100, higher = closer to high)
- Williams %R measures how far the price is from the period high (-100 to 0, closer to 0 = closer to high)

This inversion means that Williams %R readings above -20 correspond to Stochastic readings above 80, and Williams %R readings below -80 correspond to Stochastic readings below 20. The signals are effectively mirror images.

## Interpreting Williams %R Levels

**Overbought Zone: -20 to 0**
When %R is above -20, the current close is in the top 20% of the lookback period's range. This indicates strong recent buying pressure but also a potential area where the upside may be limited.

**Oversold Zone: -100 to -80**
When %R is below -80, the current close is in the bottom 20% of the lookback period's range. This indicates strong recent selling pressure and a potential area where the downside may be limited.

**Neutral Zone: -80 to -20**
Readings in the middle of the range indicate that price is neither at an extreme high nor low within the recent range. Neutral readings are generally not actionable for overbought/oversold strategies.

### The Trend Context Rule

As with all oscillators, overbought does not mean "sell" and oversold does not mean "buy." In strong uptrends, Williams %R can remain above -20 for extended periods as the close consistently prints near the period's high. During these persistent overbought conditions, selling based on the %R reading alone produces consistent losses.

**The rule:** In an uptrend (price above the 200-day SMA, or ADX > 25 with +DI > -DI), treat oversold readings as buying opportunities and ignore overbought readings. In a downtrend, treat overbought readings as selling opportunities and ignore oversold readings.

## Trading Strategy 1: Failure Swing

The failure swing is Larry Williams's preferred signal and one of the most reliable patterns the indicator produces.

### Bullish Failure Swing

1. Williams %R drops below -80 (enters oversold territory)
2. %R rises back above -80
3. %R pulls back but stays above -80 (fails to re-enter oversold territory)
4. %R then moves higher, confirming the failure swing

**Entry:** When %R rises above the level reached in step 2
**Stop-Loss:** Below the low made during the oversold reading
**Target:** When %R reaches the overbought zone (-20 to 0), or trail using a 2x ATR stop

### Bearish Failure Swing

1. Williams %R rises above -20 (enters overbought territory)
2. %R drops below -20
3. %R rises again but stays below -20 (fails to re-enter overbought territory)
4. %R drops further, confirming the failure swing

The failure swing indicates that the momentum that created the overbought/oversold condition has exhausted itself and a reversal is developing. The "failure" to return to the extreme zone confirms the momentum shift.

## Trading Strategy 2: Divergence Trading

Divergence between Williams %R and price provides some of the highest-probability reversal signals.

### Bullish Divergence

Price makes a new low, but Williams %R makes a higher low (does not confirm the price low). This indicates that despite lower prices, the closing price is higher relative to the period's range, meaning selling momentum is diminishing.

### Bearish Divergence

Price makes a new high, but Williams %R makes a lower high. Despite higher prices, the close is lower relative to the period's range, indicating weakening buying momentum.

**Trading Rules:**
- Identify the divergence on the daily chart
- Wait for Williams %R to cross out of the overbought/oversold zone in the direction of the divergence
- Enter on the cross with a stop beyond the recent price extreme
- Target: The 50-period SMA as the initial target, then trail

**Reliability Enhancement:** Divergence signals at key support/resistance levels or Fibonacci retracement levels are significantly more reliable than divergence in random chart locations. Always check for confluence before entering divergence trades.

## Trading Strategy 3: Multi-Timeframe Momentum

This strategy uses Williams %R across two timeframes to capture entries within the prevailing trend.

### Setup

1. **Weekly Williams %R:** Determines the trend bias
   - Weekly %R above -50: Bullish bias (only take long entries)
   - Weekly %R below -50: Bearish bias (only take short entries)

2. **Daily Williams %R:** Provides the entry signal
   - In a bullish weekly bias: Enter long when daily %R crosses above -80 (exits oversold)
   - In a bearish weekly bias: Enter short when daily %R crosses below -20 (exits overbought)

### Exit Rules

- **Profit target:** When daily %R reaches the opposite extreme (-20 for longs, -80 for shorts)
- **Stop-loss:** 2x ATR below entry (longs) or above entry (shorts)
- **Trailing stop:** Move stop to breakeven when daily %R reaches -50, then trail using the Chandelier Exit

This multi-timeframe approach ensures that entries align with the broader momentum direction while timing entries during short-term pullbacks within that trend.

## Williams %R Settings Optimization

The standard 14-period setting works well for daily charts across most markets. Alternative settings for different applications:

| Application | Period | Rationale |
|-------------|--------|-----------|
| Scalping (1-5 min) | 7-10 | Faster response for short timeframes |
| Day trading (15-60 min) | 14 | Standard setting |
| Swing trading (daily) | 14-21 | Balanced sensitivity |
| Position trading (weekly) | 14 | Standard on weekly bars |
| Trend confirmation | 28 | Smoother, fewer false signals |

Avoid over-optimizing the period setting. The standard 14-period setting is the most widely used, meaning more traders are watching the same levels, which creates self-reinforcing behavior at those readings.

## Python Implementation

```python
import pandas as pd
import numpy as np

def williams_r(df, period=14):
    highest_high = df['High'].rolling(period).max()
    lowest_low = df['Low'].rolling(period).min()
    wr = ((highest_high - df['Close']) / (highest_high - lowest_low)) * -100
    return wr

def williams_r_signals(df, period=14, ob=-20, os=-80):
    df['WR'] = williams_r(df, period)
    df['WR_prev'] = df['WR'].shift(1)

    # Oversold exit (bullish signal)
    df['Buy_Signal'] = (df['WR_prev'] < os) & (df['WR'] >= os)

    # Overbought exit (bearish signal)
    df['Sell_Signal'] = (df['WR_prev'] > ob) & (df['WR'] <= ob)

    return df
```

## Key Takeaways

- Williams %R measures the current close relative to the highest high over the lookback period, ranging from -100 (oversold) to 0 (overbought).
- The indicator is the mathematical inverse of the Fast Stochastic %K and provides equivalent information with an inverted scale.
- Overbought/oversold readings are conditions, not automatic signals. Always filter by the prevailing trend direction before acting.
- The failure swing pattern (inability to return to the extreme zone after exiting it) is one of the most reliable Williams %R signals.
- Divergence between price and Williams %R at key support/resistance levels provides high-probability reversal setups.
- Multi-timeframe analysis (weekly trend direction + daily entry signal) significantly improves win rates by ensuring entries align with broader momentum.

## Frequently Asked Questions

### How is Williams %R different from the Stochastic Oscillator?

Williams %R is the mathematical inverse of the Fast Stochastic %K. While the stochastic measures how close the price is to the period's high (0-100 scale), Williams %R measures how far the price is from the period's high (-100 to 0 scale). The stochastic adds a signal line (%D) and smoothing, which Williams %R does not include by default. In practice, many traders find Williams %R simpler to interpret because it uses a single line without signal line crossovers.

### What is the best Williams %R setting for forex?

The standard 14-period setting works well for forex trading on all timeframes. For scalping on 1-minute to 5-minute charts, reducing the period to 7 or 10 can provide faster signals. For longer-term forex analysis on daily and weekly charts, the 14-period setting remains optimal. The most important factor is not the period setting but the trend filter, as taking only trend-aligned signals dramatically improves performance in directional forex markets.

### Can Williams %R be used as a standalone indicator?

While Williams %R provides valuable information on its own, it performs best when combined with trend-identification tools. At minimum, pair Williams %R with a moving average (50 or 200 SMA) to determine trend direction, and only take %R signals in the direction of the trend. Using Williams %R in isolation, particularly in mean-reversion mode during strong trends, is one of the most common causes of losses with this indicator.

### How do you handle Williams %R signals in choppy markets?

In rangebound or choppy markets, Williams %R tends to oscillate between overbought and oversold zones frequently, producing many signals with lower reliability. To filter these, add a volatility filter such as the ADX. When ADX is below 20 (non-trending), either avoid Williams %R signals entirely or require them to occur at clearly defined horizontal support and resistance levels. When ADX is above 25 (trending), Williams %R signals in the trend direction become much more reliable.
