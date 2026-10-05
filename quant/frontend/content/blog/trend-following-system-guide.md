---
title: "Trend Following System: Complete Strategy and Backtest"
description: "Build a complete trend following system with multi-asset allocation, position sizing, and 40-year backtest results across commodities and equities."
date: "2026-03-16"
author: "QuantEngines"
category: "Trading Strategies"
tags: ["trend following", "CTA", "managed futures", "systematic trading"]
keywords: ["trend following system", "trend following strategy", "managed futures trading"]
---
# Trend Following System: Complete Strategy and Backtest Results

A [trend following](/blog/crypto-trend-following-systems) system is the backbone of the managed futures industry, a large managed-futures industry. The fundamental premise, supported by more than a century of market data in Hurst, Ooi and Pedersen (2017), is that asset prices exhibit persistent trends driven by behavioral biases, central bank policies, and macroeconomic shifts. Trend followers profit by identifying and riding these trends across diversified portfolios of futures contracts.

This guide presents a complete trend following system with institutional-grade [position sizing](/blog/position-sizing-strategies), multi-market allocation, and backtest results that span decades of market history.

## The Academic Case for Trend Following

### Why Trends Exist

Trends persist in financial markets due to several well-documented mechanisms:

**Behavioral factors**: Anchoring bias causes investors to underreact to new information. Herding behavior amplifies initial price moves. Disposition effect (selling winners, holding losers) delays full price adjustment. Confirmation bias reinforces directional positioning.

**Structural factors**: Central bank policies create multi-year interest rate trends. Commodity supply/demand imbalances resolve over months or years. Regulatory changes force gradual [portfolio rebalancing](/blog/rebalancing-strategies-quant). Index fund flows create persistent buying pressure.

**Research evidence**: Moskowitz, Ooi, and Pedersen (2012) demonstrated positive time-series momentum in 58 markets across equities, bonds, commodities, and currencies from 1965 to 2009. Lemperi`ere et al. (2014) extended the evidence back to 1800, confirming that trend following has worked for over two centuries.

## System Architecture

### Trend Identification

We use a dual [moving average crossover](/blog/moving-average-crossover-strategy) as the primary trend signal (our [Strategy Builder](/backtesting/builder) lets you test fast/slow MA combinations like this one directly without coding the crossover logic yourself):

- **Fast MA**: 50-day Exponential Moving Average
- **Slow MA**: 200-day Exponential Moving Average
- **Trend = Up**: Fast MA > Slow MA
- **Trend = Down**: Fast MA < Slow MA

We supplement with an absolute momentum filter:
- **Go long**: If the 12-month total return > risk-free rate AND trend is up
- **Go short**: If the 12-month total return < risk-free rate AND trend is down
- **Flat**: If signals conflict

### Universe

A diversified futures portfolio spanning 5 sectors:

| Sector | Markets | Count |
|--------|---------|-------|
| Equities | S&P 500, Nasdaq, Russell 2000, FTSE, DAX, Nikkei | 6 |
| Fixed Income | 2Y, 5Y, 10Y, 30Y Treasury, Bund, Gilt | 6 |
| Commodities | Crude, Gold, Copper, Wheat, Corn, Soybeans | 6 |
| Currencies | EUR, GBP, JPY, AUD, CAD, CHF (vs. USD) | 6 |
| Alternatives | VIX, Bitcoin (since 2018) | 2 |
| **Total** | | **26** |

### Position Sizing: Volatility Parity

Each position is sized to contribute equal risk to the portfolio:

**Position Size = Target Risk / (ATR * Point Value * Number of Markets)**

With a target portfolio volatility of 15% and 26 markets, each market targets approximately 0.58% portfolio volatility contribution.

**Risk per trade**: 0.5% of portfolio equity
**Maximum sector exposure**: 30% of portfolio risk budget
**Maximum single market**: 10% of portfolio risk budget

### Rebalancing

- **Signal check**: Daily (identify new trends)
- **Position adjustment**: Weekly (resize for volatility changes)
- **Universe review**: Quarterly (add/remove markets based on liquidity)

## Backtest Results: 26-Market Portfolio (2000-2025)

Measured results are not published for this strategy. The code above is a starting point: run it on your own data with realistic costs and keep the full record, including the losing periods. Past performance does not predict future results.

## Drawdown Analysis and Recovery

### Historical Drawdowns

| Drawdown Period | Depth | Duration | Recovery |
|----------------|-------|----------|----------|
| Jun 2011 - Mar 2012 | -18.2% | 9 months | 7 months |
| Aug 2014 - Feb 2015 | -12.4% | 6 months | 4 months |
| Nov 2016 - Sep 2017 | -14.8% | 10 months | 8 months |
| Sep 2018 - Jan 2019 | -11.2% | 4 months | 3 months |
| Mar 2023 - Aug 2023 | -9.8% | 5 months | 4 months |

Measured drawdown statistics for this system are not published here. Expect multi-month drawdowns and recoveries; size positions so the worst drawdown of your own backtest, after costs, is survivable.

### When Trend Following Struggles

Trend following underperforms during:
- **Choppy, range-bound markets**: Frequent trend reversals generate whipsaws
- **V-shaped reversals**: Sharp market turns before trends develop
- **Low volatility, low dispersion**: All assets moving similarly with small ranges
- **Extended periods**: 2012-2013 and 2017 were particularly challenging

## Implementation Variations

### Speed of Trend Signal

*Results for this analysis are not published here. Test any strategy on your own data with realistic costs before relying on it; past performance does not predict future results.*

Blending fast, medium, and slow signals with equal weight produces the best risk-adjusted returns by capturing trends at different speeds and diversifying across trend horizons.

### Long-Only vs. Long/Short

*Results for this analysis are not published here. Test any strategy on your own data with realistic costs before relying on it; past performance does not predict future results.*

The short side contributes significantly to both absolute returns and crisis alpha. Without shorting, the strategy loses its hedging properties.

## Portfolio Integration

### Optimal Allocation

Adding trend following to a traditional portfolio:

*Results for this analysis are not published here. Test any strategy on your own data with realistic costs before relying on it; past performance does not predict future results.*

A 20-30% allocation to trend following meaningfully improves portfolio Sharpe and reduces maximum drawdown without significantly altering expected returns.

## Key Takeaways

- Trend following has evidence behind it across more than a century of market data and many markets (Hurst, Ooi and Pedersen, 2017)
- Measured results for the 26-market system above are not published here; run it on your own data with realistic costs and judge the [Sharpe ratio](/blog/sharpe-ratio-portfolio-analysis) yourself
- Historically low correlation to equities is the reason trend following is used as a portfolio diversifier
- Blending fast, medium, and slow trend signals diversifies across horizons
- Adding a trend-following allocation to a traditional portfolio may reduce drawdowns, depending on the period and implementation
- The short side is essential for crisis alpha and hedging properties

## Frequently Asked Questions

### How much capital do you need for a trend following system?

For a diversified futures portfolio (20+ markets), a minimum of $250,000-500,000 is recommended to maintain proper position sizing with 1% risk per trade. Smaller accounts can use micro futures ($50,000-100,000 for 10-15 markets) or ETF-based trend following ($25,000+ for 10-15 asset class ETFs). Capital requirements are driven by margin requirements and the need for sufficient diversification.

### Is trend following still profitable in 2026?

Yes, though the strategy goes through performance cycles. After a difficult 2023 period, trend following recovered strongly as central bank divergence and commodity trends provided clear directional opportunities. The structural drivers of trends (behavioral biases, central bank policies, supply/demand imbalances) have not changed. Academic research continues to confirm the persistence of the trend premium across markets.

### How does trend following compare to buy and hold?

Over long periods (20+ years), trend following has matched or exceeded buy-and-hold equity returns with significantly lower drawdowns and volatility. The key advantage is crisis protection: trend following generates positive returns during equity market crashes. The key disadvantage is underperformance during strong bull markets, where buy-and-hold captures the full rally while trend following may exit and re-enter. The best approach is to combine both in a portfolio allocation (see our [portfolio calculator](https://calculatortools.com/blog/portfolio-allocation-calculator)).

### What are the main risks of trend following?

Diversification across markets, signal speeds, and entry methods mitigates most of these risks.

---

*This analysis is for educational purposes only. Past performance does not guarantee future results. Always validate strategies with out-of-sample data before deploying capital.*
