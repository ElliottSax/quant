---
title: "ATR (Average True Range): Volatility-Based Position Sizing"
description: "Master ATR for volatility measurement, position sizing, and stop-loss placement. Learn the Keltner Channel and ATR trailing stop strategies."
date: "2026-03-13"
author: "Dr. James Chen"
category: "Technical Analysis"
tags: ["ATR", "average true range", "volatility", "position sizing", "risk management"]
keywords: ["ATR average true range", "ATR position sizing", "ATR stop loss"]
---
# ATR (Average True Range): Volatility-Based Position Sizing

The Average True Range (ATR), developed by J. Welles Wilder Jr. in 1978, is the standard measure of market volatility in [technical analysis](/blog/python-technical-analysis-library). Unlike directional indicators that measure where price is going, ATR measures how much price moves regardless of direction. This makes it an essential tool for [position sizing](/blog/position-sizing-strategies), stop-loss placement, and volatility-adjusted risk management, functions that directly impact a trader's survival and long-term profitability.

This guide covers ATR calculation, practical applications for position sizing and stop placement, and advanced volatility-based strategies that adapt to changing market conditions.

## ATR Calculation

ATR is calculated in two steps.

### Step 1: True Range (TR)

True Range is the greatest of the following three values:

- Current High minus Current Low
- Absolute value of (Current High minus Previous Close)
- Absolute value of (Current Low minus Previous Close)

The second and third calculations account for gaps. If a stock closes at $100 and opens the next day at $103 with a high of $105 and low of $102, the simple range (High - Low) would be $3, but the True Range would be $5 ($105 - $100 previous close), capturing the full extent of the overnight move.

### Step 2: Average True Range

ATR is a smoothed average of the True Range over a specified number of periods, typically 14:

ATR = [(Prior ATR x 13) + Current TR] / 14

This is Wilder's smoothing method, which is equivalent to an exponential moving average with a smoothing factor of 1/14. The first ATR value is simply the arithmetic mean of the first 14 True Range values.

**Interpretation:** An ATR of $2.50 on a daily chart means the stock typically moves $2.50 per day (in either direction). An ATR of 45 pips on EUR/USD means the pair typically moves 45 pips daily.

## ATR for Position Sizing

Position sizing is arguably the most important application of ATR. By sizing positions based on current volatility, traders ensure that each trade carries a consistent level of risk in dollar terms, regardless of the underlying asset's price or volatility.

### The ATR Position Sizing Formula

**Position Size = (Account Risk per Trade) / (ATR Multiplier x ATR)**

Where:
- **Account Risk per Trade** = Account Balance x Risk Percentage (e.g., $100,000 x 1% = $1,000)
- **ATR Multiplier** = Stop distance expressed in ATR units (typically 1.5 to 3)
- **ATR** = Current 14-period ATR value

**Example:** A trader with a $100,000 account risking 1% per trade ($1,000) on a stock with an ATR of $3.00, using a 2x ATR stop:

Position Size = $1,000 / (2 x $3.00) = $1,000 / $6.00 = 166 shares

If the same stock enters a volatile period and ATR increases to $5.00:

Position Size = $1,000 / (2 x $5.00) = $1,000 / $10.00 = 100 shares

The dollar risk remains $1,000 in both cases, but the position size automatically adjusts to account for the higher volatility. This prevents the common mistake of maintaining the same position size in high-volatility environments, which dramatically increases dollar risk.

### Turtle Trading Position Sizing

The famous Turtle Trading system, developed by Richard Dennis and William Eckhardt in the 1980s, used ATR (which they called "N") as the sole determinant of position size:

**Unit Size = (1% of Account) / (ATR x Dollar per Point)**

Turtles would enter one unit initially and add up to three additional units at 0.5 ATR intervals as the trade moved in their favor, ensuring that each additional unit carried the same dollar risk as the initial entry.

## ATR for Stop-Loss Placement

ATR-based stops adapt to current volatility, solving the problem of stops that are either too tight (triggered by normal noise) or too wide (risking excessive capital).

### Fixed ATR Multiple Stop

The most common approach uses a fixed multiple of ATR for stop placement:

- **Tight stop (1x ATR):** Aggressive, suitable for mean-[reversion strategies](/blog/mean-reversion-strategies-guide)
- **Standard stop (1.5-2x ATR):** Balanced, suitable for most trend-following strategies
- **Wide stop (2.5-3x ATR):** Conservative, suitable for longer-term positions

**Example:** If a stock is trading at $50 with a 14-day ATR of $2, a 2x ATR stop would be placed $4 below the entry (at $46).

### Chandelier Exit

The Chandelier Exit, developed by Charles Le Beau, trails a stop at a fixed ATR distance from the highest high (for long positions) or lowest low (for short positions) since the trade was entered:

**Long Stop** = Highest High since Entry - (3 x ATR)
**Short Stop** = Lowest Low since Entry + (3 x ATR)

This trailing stop locks in profits as the trend progresses while maintaining enough distance to avoid being stopped by normal volatility. The 3x ATR multiplier is standard, but can be adjusted based on backtesting.

### ATR Trailing Stop Implementation

```python
import pandas as pd
import numpy as np

def atr_trailing_stop(df, atr_period=14, multiplier=3):
    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['ATR'] = df['TR'].rolling(atr_period).mean()

    # Chandelier Exit (long)
    df['Highest_High'] = df['High'].expanding().max()
    df['Chandelier_Stop'] = df['Highest_High'] - (multiplier * df['ATR'])

    return df
```

## ATR for Volatility Analysis

### Volatility Regimes

ATR can identify shifts in market volatility regimes that have significant implications for strategy selection:

- **Low ATR (below 20-period average):** Rangebound conditions, favor mean-reversion strategies, tight stops, larger position sizes
- **Rising ATR:** Emerging trend or shock event, transition to trend-following, widen stops, reduce position sizes
- **High ATR (above 20-period average):** Trending or volatile conditions, favor momentum/trend-following strategies, wider stops, smaller positions
- **Falling ATR:** Trend exhaustion, potential reversal zone, tighten trailing stops on existing positions

### ATR Ratio (Normalized Volatility)

To compare volatility across different assets or time periods, normalize ATR by dividing by the closing price:

**ATR% = (ATR / Close) x 100**

This produces a percentage-based volatility measure. A stock at $50 with an ATR of $2 has an ATR% of 4%, while a stock at $200 with an ATR of $6 has an ATR% of 3%. Despite the higher absolute ATR, the $200 stock is less volatile on a percentage basis.

## Keltner Channels: ATR-Based Bands

Keltner Channels use ATR to create volatility bands around a moving average:

- **Middle Line:** 20-period EMA
- **Upper Band:** 20-period EMA + (2 x ATR)
- **Lower Band:** 20-period EMA - (2 x ATR)

Unlike [Bollinger Bands](/blog/bollinger-bands-trading-strategy) (which use standard deviation), Keltner Channels expand and contract based on True Range volatility. [Trading strategies](/blog/backtesting-trading-strategies) include:

- **Mean reversion:** Enter long at the lower band, short at the upper band (rangebound markets)
- **Breakout:** Enter in the direction of a close outside the bands (trending markets)
- **Squeeze:** When Bollinger Bands move inside Keltner Channels, a volatility squeeze is forming, anticipating a significant breakout

## Key Takeaways

- ATR measures how much price moves, not which direction, making it the standard tool for volatility-based risk management.
- ATR-based position sizing ensures consistent dollar risk across trades regardless of asset volatility, automatically reducing size in volatile conditions and increasing size in calm conditions.
- The standard ATR stop-loss multiplier is 1.5-2x ATR for most strategies, with the Chandelier Exit providing an effective trailing stop method.
- Normalize ATR by price (ATR%) to compare volatility across different assets and price levels.
- Falling ATR indicates consolidation and potential breakout setups; rising ATR signals emerging trends or volatility events.
- Keltner Channels provide ATR-based dynamic support and resistance that adapts to changing market volatility.

## Frequently Asked Questions

### What is the best ATR period for day trading versus swing trading?

For day trading, shorter ATR periods (7-10) on intraday charts (5-minute, 15-minute) respond faster to volatility changes during the session. For swing trading, the standard 14-period ATR on daily charts works well. For position trading, a 20-period ATR provides smoother volatility estimates. The key principle is that shorter periods increase sensitivity (faster response to volatility changes) while longer periods provide more stable readings.

### How do you adjust ATR position sizing for correlated positions?

When holding multiple positions that are positively correlated (e.g., multiple tech stocks), the portfolio risk is higher than the sum of individual position risks suggests. Reduce position sizes by the correlation factor. If two positions have a correlation of 0.8, treat them as approximately 1.8 positions worth of risk rather than 2.0. Some traders apply a maximum total risk rule (e.g., total portfolio ATR exposure cannot exceed 5% of account equity).

### Can ATR predict market direction?

ATR does not indicate direction, only the magnitude of price movement. However, ATR trends can provide contextual clues. A sustained increase in ATR often accompanies new trends, while declining ATR during a trend suggests the trend is maturing and may be approaching exhaustion. Extremely low ATR readings (relative to historical norms) often precede significant breakout moves, as volatility compression tends to lead to volatility expansion.

### Why use ATR instead of standard deviation for volatility?

ATR accounts for gaps between sessions (through the True Range calculation), while standard deviation of returns may understate volatility when significant gaps occur. ATR also directly measures price movement in the same units as the asset, making it intuitive for setting stop-loss levels and position sizes. Standard deviation is more appropriate for statistical analysis and options pricing (see our [options calculator](https://calculatortools.com/blog/options-profit-calculator)), while ATR is more practical for active trading risk management.
