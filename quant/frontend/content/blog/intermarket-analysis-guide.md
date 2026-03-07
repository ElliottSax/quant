---
title: "Intermarket Analysis: Bonds, Commodities, Currencies, Stocks"
description: "Master intermarket analysis to understand cross-market relationships. Learn bond-stock rotation, commodity-currency links, and macro-driven trading signals."
date: "2026-04-05"
author: "Dr. James Chen"
category: "Technical Analysis"
tags: ["intermarket analysis", "cross-market", "bonds", "commodities", "currencies", "macro trading"]
keywords: ["intermarket analysis", "cross-asset analysis", "intermarket relationships trading"]
---

# Intermarket Analysis: Bonds, Commodities, Currencies, Stocks

Intermarket analysis examines the relationships between four major asset classes, bonds, commodities, currencies, and equities, to gain a broader perspective on market direction and identify trading opportunities that single-market analysis cannot reveal. Developed and popularized by John Murphy in the early 1990s, intermarket analysis recognizes that financial markets are interconnected, and price movements in one market often lead or confirm movements in others.

Understanding these cross-market relationships provides a macroeconomic context for individual trades, helps identify sector rotation opportunities, and provides early warning signals for major market turning points.

## The Four-Market Framework

### The Traditional Intermarket Relationships (Pre-2008)

John Murphy's original framework described the following sequence:

1. **Dollar weakness** leads to **commodity strength** (commodities are priced in dollars; weaker dollar = higher commodity prices)
2. **Commodity strength** leads to **bond weakness** (rising commodity prices signal inflation, which is negative for bonds)
3. **Bond weakness** (rising yields) eventually leads to **stock weakness** (higher borrowing costs reduce corporate earnings)
4. **Stock weakness** leads to **dollar strength** (flight to safety during equity selloffs)

This cycle repeats, creating a predictable rotation pattern.

### The Modern Intermarket Relationships (Post-2008)

The relationships have evolved, particularly since the 2008 financial crisis and the era of unprecedented monetary policy:

**Bond-Stock Correlation:** From 1965-2000, bonds and stocks were positively correlated (both driven by inflation expectations). Since 2000, they have been predominantly negatively correlated (bonds serve as a risk-off hedge). The 2022-2023 period challenged this again as rising inflation caused both stocks and bonds to decline.

**Dollar-Equity Relationship:** The dollar's relationship with equities has become regime-dependent. During risk-off events, the dollar strengthens (safe haven) while stocks decline. During US economic outperformance, both the dollar and US stocks can rally simultaneously.

**Commodity-Inflation Link:** While still present, the relationship has become more nuanced. Energy transition, supply chain restructuring, and geopolitical factors have added complexity beyond the simple dollar-commodity inverse relationship.

## Key Intermarket Relationships

### Bonds and Stocks

The bond-stock relationship is the most important intermarket dynamic for equity traders:

**The Yield Signal:** When 10-year Treasury yields rise from low levels (e.g., below 3%), it often reflects economic optimism and is positive for stocks. When yields rise from already elevated levels (e.g., above 4.5%), it reflects tightening financial conditions and becomes negative for stocks.

**The Yield Curve:** The spread between 10-year and 2-year Treasury yields has historically been one of the most reliable recession indicators:
- **Inverted curve (10Y - 2Y < 0):** Preceded every US recession since 1960
- **Steepening after inversion:** Often the strongest warning signal (recession typically starts 6-18 months after inversion)

**Trading Application:**
```python
def yield_curve_signal(ten_year_yield, two_year_yield):
    """Generate equity market signal from yield curve."""
    spread = ten_year_yield - two_year_yield

    if spread < -0.5:
        return 'DEFENSIVE'  # Deep inversion, recession risk high
    elif spread < 0:
        return 'CAUTIOUS'   # Mild inversion, reduce equity exposure
    elif spread > 1.0:
        return 'RISK_ON'    # Steep curve, economy expanding
    else:
        return 'NEUTRAL'    # Normal, no strong signal
```

### Commodities and Currencies

Structural commodity-currency links provide some of the most tradable intermarket signals:

**Commodity Currencies:**
- **AUD/USD** correlates with iron ore and copper prices (r = 0.5-0.7 over rolling 1-year windows)
- **CAD** (inverse USD/CAD) correlates with crude oil (r = 0.4-0.7)
- **NOK** correlates with Brent crude oil
- **NZD** correlates with dairy commodity prices
- **ZAR** correlates with gold and platinum

**Gold and the Dollar:**
Gold and the US Dollar Index (DXY) maintain a persistent negative correlation (-0.3 to -0.6 over most periods). Gold serves as both an inflation hedge and a dollar alternative, meaning dollar weakness drives gold demand.

**Trading Application:** When gold and the dollar both strengthen simultaneously, it signals extreme risk aversion (both safe havens being bid). This condition typically precedes or accompanies significant equity selloffs.

### Equity Sectors and Commodities

Sector-commodity relationships provide actionable signals for equity sector rotation:

| Commodity | Equity Sector | Relationship |
|-----------|--------------|--------------|
| Crude Oil | Energy (XLE) | Positive (r ~ 0.7-0.8) |
| Copper | Materials (XLB), Industrials (XLI) | Positive (r ~ 0.5-0.6) |
| Gold | Gold Miners (GDX) | Positive (r ~ 0.8-0.9) |
| Lumber | Homebuilders (XHB) | Positive (r ~ 0.4-0.6) |
| Agricultural | Consumer Staples (XLP) | Negative (higher input costs reduce margins) |

## Intermarket Analysis in Practice

### The Risk-On / Risk-Off Framework

Modern intermarket analysis frequently reduces to a single dimension: risk appetite.

**Risk-On Characteristics:**
- Stocks rising, especially growth and small-cap sectors
- Bond yields rising moderately (money flowing out of safety)
- Dollar weakening (capital flowing to riskier currencies)
- Commodity currencies (AUD, CAD, NZD) strengthening
- Credit spreads tightening (investment grade and high yield)
- VIX declining

**Risk-Off Characteristics:**
- Stocks declining, especially cyclical sectors
- Bond yields falling sharply (flight to safety)
- Dollar strengthening (safe haven demand)
- Yen strengthening (carry trade unwind)
- Gold rising
- VIX rising
- Credit spreads widening

### Building a Risk Appetite Dashboard

```python
import pandas as pd
import numpy as np

class RiskAppetiteDashboard:
    """Aggregate intermarket signals into a risk appetite score."""

    def __init__(self):
        self.signals = {}

    def update(self, spy_return, tlt_return, dxy_return, vix_level,
               gold_return, high_yield_spread):
        """Update dashboard with latest market data."""

        # Equity signal (positive return = risk on)
        self.signals['equity'] = 1 if spy_return > 0 else -1

        # Bond signal (negative return = risk on, money leaving safety)
        self.signals['bonds'] = -1 if tlt_return > 0 else 1

        # Dollar signal (weakness = risk on)
        self.signals['dollar'] = -1 if dxy_return > 0 else 1

        # VIX signal (below 20 = risk on)
        self.signals['vix'] = 1 if vix_level < 20 else (-1 if vix_level > 30 else 0)

        # Gold signal (weakness = risk on)
        self.signals['gold'] = -1 if gold_return > 0 else 1

        # Credit signal (tight spreads = risk on)
        self.signals['credit'] = 1 if high_yield_spread < 4.0 else -1

    def risk_score(self):
        """Calculate aggregate risk appetite score (-6 to +6)."""
        return sum(self.signals.values())

    def interpretation(self):
        score = self.risk_score()
        if score >= 4:
            return 'Strong Risk-On'
        elif score >= 2:
            return 'Moderate Risk-On'
        elif score >= -1:
            return 'Neutral'
        elif score >= -3:
            return 'Moderate Risk-Off'
        else:
            return 'Strong Risk-Off'
```

## Sector Rotation Using Intermarket Signals

Intermarket analysis provides a framework for equity sector rotation based on the business cycle:

### Early Expansion (Bonds rally, then stocks begin to rally)
- **Overweight:** Financials, Consumer Discretionary, Technology
- **Underweight:** Utilities, Consumer Staples

### Mid Expansion (Stocks rally, commodities begin to rally)
- **Overweight:** Industrials, Materials, Energy
- **Underweight:** Utilities, Healthcare (defensive)

### Late Expansion (Commodities rally, bonds begin to decline)
- **Overweight:** Energy, Materials, Commodities
- **Underweight:** Technology, Consumer Discretionary

### Contraction (Stocks decline, bonds rally)
- **Overweight:** Utilities, Consumer Staples, Healthcare
- **Underweight:** Financials, Industrials, Materials

## Leading Indicator Relationships

Some intermarket relationships have consistent lead-lag structures:

1. **Copper leads equities:** Copper prices (often called "Dr. Copper" for its economic sensitivity) tend to lead equity moves by 1-3 months, as copper demand reflects industrial activity before it shows up in corporate earnings.

2. **Credit spreads lead equities:** High-yield bond spreads widening ahead of equity declines is one of the most reliable intermarket warning signals. The credit market is typically faster to price in deteriorating conditions.

3. **Yield curve leads the economy:** Yield curve inversion leads recessions by 6-18 months. This relationship has held for over 60 years with no false positives (though the lag varies).

4. **Dollar leads emerging markets:** Dollar strength typically precedes emerging market equity weakness by 1-3 months, as dollar-denominated debt becomes more expensive to service.

## Key Takeaways

- Intermarket analysis examines relationships between bonds, commodities, currencies, and equities to provide macro context for trading decisions.
- The risk-on/risk-off framework simplifies intermarket analysis into a single dimension that drives most cross-asset correlations.
- Bond yields, the yield curve, and credit spreads provide the most reliable leading signals for equity market direction.
- Commodity-currency links (AUD/iron ore, CAD/oil, gold/dollar) offer actionable trading signals based on structural economic relationships.
- Sector rotation based on the business cycle uses intermarket signals to overweight and underweight equity sectors at the appropriate times.
- Intermarket relationships are not static; they evolve with monetary policy regimes, structural economic changes, and geopolitical shifts. Regularly validate that assumed relationships still hold.

## Frequently Asked Questions

### How do I start using intermarket analysis in my trading?

Begin with the simplest and most reliable relationship: monitor the 10-year Treasury yield and its impact on equity sectors. When yields rise, financials tend to benefit while utilities and REITs tend to suffer. Next, add the Dollar Index (DXY) and its relationship with commodities and emerging markets. Build complexity gradually as you verify each relationship in real-time.

### Does intermarket analysis work for day trading?

On very short timeframes (minutes to hours), intermarket relationships are less reliable because noise dominates. However, starting each trading day with an intermarket assessment (where are bonds, commodities, the dollar, and the VIX relative to yesterday?) provides valuable context for directional bias. Many professional day traders use overnight bond futures and pre-market equity index futures as their primary directional guide.

### How has central bank policy changed intermarket relationships?

Central bank quantitative easing (QE) and tightening (QT) have significantly altered intermarket dynamics. During QE periods, the traditional bond-stock negative correlation strengthened as central bank bond buying suppressed yields, encouraging equity risk-taking. During QT periods, both bonds and stocks can decline together as liquidity is withdrawn. When analyzing intermarket relationships, consider the current monetary policy regime as a critical context variable.

### What data sources do I need for intermarket analysis?

At minimum, track: SPY (US equities), TLT or 10-year yield (bonds), DXY (dollar), GLD (gold), USO or CL (crude oil), and VIX (volatility). For more comprehensive analysis, add: HYG (high yield credit), EEM (emerging markets), copper futures, and sector ETFs (XLF, XLE, XLU). All of these are available through free data sources like Yahoo Finance or through broker platforms.
