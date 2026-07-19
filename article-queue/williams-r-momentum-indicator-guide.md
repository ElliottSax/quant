---
title: Williams %R Momentum Indicator Guide
slug: williams-r-momentum-indicator-guide
description: Master Williams %R with overbought/oversold zones, momentum divergence,
author: Content Team
category: Technical Indicators
tags: []
keyword: Williams %R momentum indicator guide
date: '''2026-03-19'''
readTime: 12-15 min read
---

## Quick Answer

Williams %R measures overbought/oversold on -100 to 0 scale (inverse of Stochastic). %R below -80 = oversold (buy setup). %R above -20 = overbought (sell setup). %R divergence = strong reversal signal. Zero-line cross = momentum shift. Works well on 1H-4H charts with 55-65% win rate.

## Introduction

Williams %R is a momentum oscillator measuring price position relative to recent highs/lows. Created by Larry Williams, this indicator is essentially an inverted Stochastic with a slightly different calculation. This comprehensive guide covers everything from basic overbought/oversold trading to advanced divergence patterns and professional trading techniques.

## Understanding Williams %R

### Key Features

**Scale:** 0 to -100 (inverted)
**Overbought:** -20 to 0
**Oversold:** -80 to -100
**Neutral:** -20 to -80

**Calculation:** %R = (High - Close) / (High - Low) × -100

## Core Williams %R Strategies

### Strategy 1: Oversold Bounce

**Buy Setup:**
- %R drops below -80 (oversold)
- %R bounces back above -80
- Price at support level
- Entry: Close above -80
- Target: -50 or above
- Win rate: 55-60%

**Sell Setup:**
- %R rises above -20 (overbought)
- %R drops back below -20
- Price at resistance level
- Entry: Close below -20
- Target: -50 or below
- Win rate: 55-60%

### Strategy 2: Williams %R Divergence

**Bullish Divergence:**
- Price lower low, %R higher low
- Entry: Break above swing high
- Win rate: 65%

**Bearish Divergence:**
- Price higher high, %R lower high
- Entry: Break below swing low
- Win rate: 65%

### Strategy 3: Zero-Line Momentum

**Buy Signal:**
- %R crosses above -50
- Momentum turning positive
- Entry: Above cross
- Win rate: 55%

**Sell Signal:**
- %R crosses below -50
- Momentum turning negative
- Entry: Below cross
- Win rate: 55%

## Real-World Williams %R Examples

### Example 1: Hourly AAPL
- %R: -92 (oversold)
- %R crosses above -80
- Entry: $185.50
- Target: $187.00
- Result: +$1.50

### Example 2: 4H EURUSD
- Price: Higher high at 1.0950
- %R: Lower high (-15)
- Bearish divergence
- Entry: Short below 1.0900
- Target: 1.0850
- Result: +100 pips

### Example 3: Daily SPY
- %R: -88 (oversold)
- SPY at support $450
- Bounce signal
- Entry: $452
- Target: $460
- Result: +$8

## Williams %R Settings

### Standard Williams %R (14)
- Most common
- Works across timeframes
- Good balance
- Recommended starting point

### Faster %R (7-10)
- Quicker signals
- More false signals
- Day trading/scalping
- Requires confirmation

### Slower %R (21)
- Smoother signals
- Fewer trades
- Swing trading
- Higher reliability

## Timeframe Optimization

### 1H Charts
- %R (14) standard
- Overbought/oversold trades
- Frequent signals
- Win rate: 55%

### 4H Charts
- %R (14) standard
- Divergence most reliable
- Swing trading sweet spot
- Win rate: 60-65%

### Daily Charts
- %R (21) smoother
- Major reversals only
- Position trading
- Win rate: 65-70%

### Scalping (5-15 min)
- %R (7-10) faster
- Oversold entries best
- Tight stops required
- Win rate: 50-55%

## Common Williams %R Mistakes

1. Trading extremes directly (should wait for reversal)
2. Ignoring divergence context
3. Using same settings everywhere
4. No price action confirmation
5. Overleveraging signals
6. Trading in choppy markets

## Williams %R + Price Action

**High-Probability Setups:**
- %R oversold + support bounce = 65% win rate
- %R overbought + resistance rejection = 65% win rate
- %R divergence + trendline break = 70% win rate
- %R extreme + volume spike = 70% win rate

## Advanced Williams %R Techniques

### %R Trendlines

Draw trendlines on %R indicator:

**Uptrend Trendline:**
- Connect swing lows
- Break signals weakness
- Win rate: 60%

**Downtrend Trendline:**
- Connect swing highs
- Break signals strength
- Win rate: 60%

### %R Multi-Timeframe

Use %R across timeframes:

**Daily:** Overall trend
**4H:** Intermediate momentum
**1H:** Entry timing
**Win Rate:** 70%+ with alignment

## Platform Implementation

### TradingView
```
study("Williams %R Strategy", overlay=false)
wr = ta.williams_r(high, low, close, 14)
plot(wr, color=color.blue, title="Williams %R")
hline(-20, color=color.red)
hline(-80, color=color.green)
```

### MetaTrader 5
```
#include <Trade\Trade.mqh>
double wr = iWPR(Symbol(), PERIOD_H1, 14);
if(wr < -80) { /* oversold */ }
if(wr > -20) { /* overbought */ }
```

---

## FAQ Section

**Q: What's the difference between Williams %R and Stochastic?**
A: Williams %R is -100 to 0; Stochastic is 0 to 100. Otherwise very similar. Test both.

**Q: What period for Williams %R?**
A: Standard 14. Test 7-21 for your timeframe.

**Q: Can %R work on 1-minute charts?**
A: Yes, use 7-10 period. Noisier than 4H+ but workable with confirmation.

**Q: Is Williams %R better than RSI?**
A: Different calculations, similar results. %R inverted may feel backwards for some traders.

**Q: How do I identify %R divergence?**
A: Compare price swing lows/highs with %R values. Use lines to align.

---

## Conclusion

Williams %R is a powerful momentum oscillator measuring overbought/oversold conditions. Focus on -80/-20 reversals and divergence for best results.

Combine %R with price action and support/resistance for highest probability setups.

**Action Steps:**
1. Set Williams %R(14) on your platform
2. Study 30 charts identifying -80/-20 zones
3. Paper trade oversold bounces for 50 trades
4. Add divergence identification
5. Track win rate by strategy type

With Williams %R mastery, identify powerful momentum shifts and reversals across timeframes.
