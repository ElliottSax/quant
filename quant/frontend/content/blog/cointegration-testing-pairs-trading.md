---
title: 'Cointegration Testing for Pairs Trading: Statistical Arbitrage Foundations'
slug: cointegration-testing-pairs-trading
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-03-22'
last_updated: '2026-03-22'
---

# Cointegration Testing for Pairs Trading: Statistical Arbitrage Foundations

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

Cointegration reveals long-term equilibrium relationships between assets. Two assets can move independently in the short term but revert to a stable relationship over time. This principle forms the basis of profitable pairs trading. This guide explores cointegration testing and application.

## Cointegration vs Correlation

```python
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Download two related stocks
data = yf.download(['EWA', 'EWC'], start='2020-01-01', end='2025-12-31', progress=False)['Close']

# Check correlation
returns = data.pct_change()
correlation = returns['EWA'].corr(returns['EWC'])

print(f"Correlation: {correlation:.3f}")

# Check price ratio (spread)
price_ratio = data['EWA'] / data['EWC']
price_ratio.name = 'EWA/EWC Price Ratio'

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Prices
ax = axes[0]
ax.plot(data.index, data['EWA'], label='EWA', linewidth=2)
ax.plot(data.index, data['EWC'], label='EWC', linewidth=2)
ax.set_ylabel('Price')
ax.set_title('EWA vs EWC Prices')
ax.legend()
ax.grid(True, alpha=0.3)

# Spread (price ratio)
ax = axes[1]
ax.plot(price_ratio.index, price_ratio.values, linewidth=2, color='purple')
ax.axhline(y=price_ratio.mean(), color='red', linestyle='--', label='Mean')
ax.fill_between(price_ratio.index, price_ratio.mean() - price_ratio.std(),
               price_ratio.mean() + price_ratio.std(), alpha=0.2, color='purple', label='±1σ')
ax.set_ylabel('Price Ratio')
ax.set_title('Price Ratio (Spread)')
ax.legend()
ax.grid(True, alpha=0.3)

# Returns
ax = axes[2]
ax.scatter(returns['EWC'] * 100, returns['EWA'] * 100, alpha=0.3, s=10)
ax.set_xlabel('EWC Return (%)')
ax.set_ylabel('EWA Return (%)')
ax.set_title('Returns Scatter')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Johansen Cointegration Test

```python
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.vector_ar.vecm import coint_johansen

# Download data
data = yf.download(['PEP', 'KO'], start='2020-01-01', end='2025-12-31', progress=False)['Close']

# Johansen test
result = coint_johansen(data, det_order=0, k_ar_diff=1)

print("Johansen Cointegration Test Results:\n")
print("Trace Statistic:")
print(result.lr1)  # Critical values 90%, 95%, 99%
print("\nTrace Test Values:")
print(result.lr1_trace)

# If test statistic > critical value, cointegrated
if result.lr1_trace[0] > result.lr1[0, 1]:  # 95% level
    print("\n✓ Cointegration detected at 95% confidence!")
else:
    print("\n✗ No cointegration detected")

# Eigenvector gives cointegrating vector
print(f"\nCointegrating Vector: {result.evec[:, 0]}")
```

## Augmented Dickey-Fuller for Cointegration

```python
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.stattools import adfuller, coint

# Download data
data = yf.download(['BRK.B', 'BRK.A'], start='2023-01-01', end='2025-12-31', progress=False)['Close']

# Direct cointegration test
coint_stat, p_value, _ = coint(data['BRK.A'], data['BRK.B'])

print("Cointegration Test (Engle-Granger):\n")
print(f"Test Statistic: {coint_stat:.4f}")
print(f"P-Value: {p_value:.4f}")

if p_value < 0.05:
    print("✓ Cointegrated at 95% confidence level")
else:
    print("✗ Not cointegrated")

# Test for stationarity of spread
spread = data['BRK.A'] - data['BRK.B']
adf_result = adfuller(spread, autolag='AIC')

print(f"\nADF Test on Spread:\n")
print(f"ADF Statistic: {adf_result[0]:.4f}")
print(f"P-Value: {adf_result[1]:.4f}")

if adf_result[1] < 0.05:
    print("✓ Spread is stationary (cointegrated)")
else:
    print("✗ Spread is non-stationary")
```

## Pairs Trading Strategy

```python
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

class PairsTrading:
    """Implement pairs trading strategy"""

    def __init__(self, ticker1, ticker2, lookback=252):
        self.ticker1 = ticker1
        self.ticker2 = ticker2
        self.lookback = lookback
        self.data = None
        self.spread = None

    def download_data(self, start_date, end_date):
        """Download price data"""
        self.data = yf.download([self.ticker1, self.ticker2], start=start_date, end=end_date, progress=False)['Close']

    def calculate_spread(self):
        """Calculate normalized spread"""
        # Normalize prices to 0-1 range for comparable units
        norm_ticker1 = (self.data[self.ticker1] - self.data[self.ticker1].min()) / \
                      (self.data[self.ticker1].max() - self.data[self.ticker1].min())
        norm_ticker2 = (self.data[self.ticker2] - self.data[self.ticker2].min()) / \
                      (self.data[self.ticker2].max() - self.data[self.ticker2].min())

        self.spread = norm_ticker1 - norm_ticker2

    def generate_signals(self, threshold=1.5):
        """Generate trading signals based on spread"""
        spread_mean = self.spread.rolling(self.lookback).mean()
        spread_std = self.spread.rolling(self.lookback).std()

        z_score = (self.spread - spread_mean) / spread_std

        signals = pd.Series(0, index=z_score.index)
        signals[z_score > threshold] = -1  # Short spread (long ticker2, short ticker1)
        signals[z_score < -threshold] = 1  # Long spread (long ticker1, short ticker2)

        return signals, z_score

    def backtest(self, threshold=1.5):
        """Backtest pairs trading strategy"""
        self.calculate_spread()
        signals, z_score = self.generate_signals(threshold)

        # Calculate returns
        returns1 = self.data[self.ticker1].pct_change()
        returns2 = self.data[self.ticker2].pct_change()

        # Strategy returns (simplified)
        strategy_returns = signals.shift(1) * (returns1 - returns2)

        cumulative = (1 + strategy_returns).cumprod()

        return {
            'cumulative_returns': cumulative,
            'strategy_returns': strategy_returns,
            'z_score': z_score,
            'spread': self.spread,
            'signals': signals
        }

# Test strategy
strategy = PairsTrading('PEP', 'KO')
strategy.download_data('2023-01-01', '2025-12-31')
results = strategy.backtest(threshold=1.5)

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Cumulative returns
ax = axes[0]
ax.plot((results['cumulative_returns'] - 1) * 100, linewidth=2, color='steelblue')
ax.set_ylabel('Return (%)')
ax.set_title('Pairs Trading Strategy - Cumulative Returns')
ax.grid(True, alpha=0.3)

# Z-score with thresholds
ax = axes[1]
ax.plot(results['z_score'], linewidth=1, color='purple')
ax.axhline(y=1.5, color='red', linestyle='--', alpha=0.5)
ax.axhline(y=-1.5, color='red', linestyle='--', alpha=0.5)
ax.fill_between(results['z_score'].index, -1.5, 1.5, alpha=0.1, color='green')
ax.set_ylabel('Z-Score')
ax.set_title('Spread Z-Score')
ax.grid(True, alpha=0.3)

# Trading signals
ax = axes[2]
ax.scatter(results['signals'][results['signals'] == 1].index,
          results['z_score'][results['signals'] == 1], color='green', marker='^', s=100, label='Long')
ax.scatter(results['signals'][results['signals'] == -1].index,
          results['z_score'][results['signals'] == -1], color='red', marker='v', s=100, label='Short')
ax.plot(results['z_score'], alpha=0.3, color='gray')
ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax.set_ylabel('Z-Score')
ax.set_xlabel('Date')
ax.set_title('Trading Signals')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Performance metrics
returns = results['strategy_returns'].dropna()
sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

print(f"\nStrategy Performance:")
print(f"  Annual Return: {returns.mean() * 252:.2%}")
print(f"  Sharpe Ratio: {sharpe:.2f}")
print(f"  Win Rate: {(returns > 0).sum() / len(returns):.1%}")
```

## Conclusion

Cointegration provides a statistical foundation for pairs trading. Key points:

1. Cointegration ≠ Correlation; tests long-term equilibrium
2. Use Johansen or Engle-Granger tests to identify cointegrated pairs
3. Monitor spread mean reversion for trading signals
4. Always validate statistical relationships before trading
5. Account for transaction costs which significantly reduce profits

Pairs trading can be profitable but requires rigorous statistical validation.
