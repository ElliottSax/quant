---
title: 'Conformal Prediction for Trading Uncertainty: Distribution-Free Confidence
  Sets'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: conformal-prediction-trading-uncertainty
published_date: '2026-03-22'
last_updated: '2026-03-22'
---

# Conformal Prediction for Trading Uncertainty: Distribution-Free Confidence Sets

Conformal prediction provides distribution-free confidence sets for trading predictions without assuming underlying data distributions. This approach is ideal for financial applications where assumptions may not hold.

## Understanding Conformal Prediction

Conformal prediction:
- Provides valid confidence intervals without distribution assumptions
- Adapts to changing market conditions
- Maintains coverage guarantees
- Improves decision-making with uncertainty quantification

## Complete Conformal Prediction Trading System

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Conformal Predictor Implementation
class ConformalPredictor:
    def __init__(self, model, alpha=0.1):
        self.model = model
        self.alpha = alpha  # Significance level
        self.calibration_scores = None
        self.quantile_value = None

    def fit(self, X_train, y_train, X_cal, y_cal):
        """Train model and calibrate on hold-out data"""
        self.model.fit(X_train, y_train)

        # Get predictions on calibration set
        y_pred_cal = self.model.predict(X_cal)

        # Calculate residuals (non-conformity scores)
        self.calibration_scores = np.abs(y_cal - y_pred_cal)

        # Find quantile for confidence interval
        n = len(self.calibration_scores)
        quantile_idx = int(np.ceil((n + 1) * (1 - self.alpha) / n))
        self.quantile_value = np.sort(self.calibration_scores)[min(quantile_idx - 1, n - 1)]

    def predict(self, X_test):
        """Get point predictions and confidence intervals"""
        y_pred = self.model.predict(X_test)

        # Confidence interval width
        lower = y_pred - self.quantile_value
        upper = y_pred + self.quantile_value

        return y_pred, lower, upper

# Fetch data
def fetch_market_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    df = data.copy()
    df['Returns'] = df['Close'].pct_change()
    df['Volatility_20'] = df['Returns'].rolling(20).std()
    df['RSI'] = calculate_rsi(df['Close'], 14)
    df['MACD'] = calculate_macd(df['Close'])

    features = ['Returns', 'Volatility_20', 'RSI', 'MACD']
    X = df[features].dropna().values
    y = df['Close'].dropna().values[-len(X):]

    return X, y, df

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    return ema_fast - ema_slow

# Download data
ticker = "AAPL"
X, y, df = fetch_market_data(ticker, "2018-01-01", "2024-01-01")

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data: train / calibration / test
train_size = int(0.6 * len(X_scaled))
cal_size = int(0.2 * len(X_scaled))

X_train = X_scaled[:train_size]
y_train = y[:train_size]

X_cal = X_scaled[train_size:train_size+cal_size]
y_cal = y[train_size:train_size+cal_size]

X_test = X_scaled[train_size+cal_size:]
y_test = y[train_size+cal_size:]

print(f"Train: {len(X_train)}, Cal: {len(X_cal)}, Test: {len(X_test)}")

# Train model
base_model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)

# Create conformal predictor
cp = ConformalPredictor(base_model, alpha=0.1)
cp.fit(X_train, y_train, X_cal, y_cal)

print(f"Quantile value: {cp.quantile_value:.4f}")

# Get predictions with confidence intervals
y_pred, y_lower, y_upper = cp.predict(X_test)

# Calculate coverage
coverage = np.mean((y_test >= y_lower) & (y_test <= y_upper))
avg_width = np.mean(y_upper - y_lower)

print(f"\nConformal Prediction Results:")
print(f"Coverage (should be ~90%): {coverage:.2%}")
print(f"Average interval width: ${avg_width:.2f}")

# Visualize predictions with confidence intervals
fig, ax = plt.subplots(figsize=(14, 7))

# Plot last 100 predictions
n_show = 100
indices = np.arange(len(y_test) - n_show, len(y_test))

ax.plot(indices, y_test[-n_show:], 'b-', linewidth=2, label='Actual')
ax.plot(indices, y_pred[-n_show:], 'r-', linewidth=2, label='Prediction')
ax.fill_between(indices, y_lower[-n_show:], y_upper[-n_show:], alpha=0.3, label='90% Confidence Interval')

ax.set_xlabel('Sample')
ax.set_ylabel('Price ($)')
ax.set_title('Conformal Prediction with Confidence Intervals')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Analyze interval widths over time
interval_widths = y_upper - y_lower

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Interval widths over time
axes[0].plot(interval_widths, alpha=0.7, linewidth=1)
axes[0].set_xlabel('Sample')
axes[0].set_ylabel('Interval Width ($)')
axes[0].set_title('Prediction Interval Width Over Time')
axes[0].grid(True, alpha=0.3)

# Distribution of interval widths
axes[1].hist(interval_widths, bins=50, alpha=0.7)
axes[1].axvline(np.mean(interval_widths), color='r', linestyle='--', label=f'Mean: ${np.mean(interval_widths):.2f}')
axes[1].set_xlabel('Interval Width ($)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Prediction Intervals')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Adaptive Conformal Prediction

```python
# Adaptive conformal prediction for non-stationary data
class AdaptiveConformalPredictor:
    def __init__(self, model, alpha=0.1, window_size=50):
        self.model = model
        self.alpha = alpha
        self.window_size = window_size
        self.quantile_history = []

    def update(self, x_new, y_new, y_pred_new):
        """Update with new data point"""
        # Calculate residual
        residual = abs(y_new - y_pred_new)

        # Update quantile estimate
        if len(self.quantile_history) < self.window_size:
            self.quantile_history.append(residual)
        else:
            self.quantile_history.pop(0)
            self.quantile_history.append(residual)

        # Recalculate quantile
        n = len(self.quantile_history)
        quantile_idx = int(np.ceil((n + 1) * (1 - self.alpha) / n))
        current_quantile = np.sort(self.quantile_history)[min(quantile_idx - 1, n - 1)]

        return current_quantile

# Testing adaptive conformal prediction
adaptive_cp = AdaptiveConformalPredictor(base_model, alpha=0.1, window_size=50)

# Simulate online predictions
quantile_history = []
online_predictions = []

for i in range(len(X_test)):
    # Make prediction
    y_pred_i = base_model.predict(X_test[i:i+1])[0]

    # Update adaptive predictor
    if i > 0:
        quantile = adaptive_cp.update(X_test[i], y_test[i], y_pred_i)
        quantile_history.append(quantile)

    online_predictions.append(y_pred_i)

# Visualize adaptive quantile
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(quantile_history, label='Adaptive Quantile', linewidth=2)
ax.axhline(cp.quantile_value, color='r', linestyle='--', label='Static Quantile')
ax.set_xlabel('Sample')
ax.set_ylabel('Quantile Value')
ax.set_title('Adaptive vs Static Conformal Quantile')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## Trading Strategy with Uncertainty

```python
# Trading strategy that uses confidence intervals
def create_robust_trading_signals(y_pred, y_lower, y_upper, current_price, risk_level='normal'):
    """Generate trading signals based on confidence intervals"""

    signals = []
    confidence_scores = []

    for i in range(len(y_pred)):
        pred_return = (y_pred[i] - current_price[i]) / current_price[i]
        lower_return = (y_lower[i] - current_price[i]) / current_price[i]
        upper_return = (y_upper[i] - current_price[i]) / current_price[i]

        # Confidence in prediction
        interval_width = upper_return - lower_return
        confidence = 1 / (1 + interval_width)  # Wider interval = less confidence

        if risk_level == 'conservative':
            threshold = 0.02
        elif risk_level == 'aggressive':
            threshold = 0.01
        else:
            threshold = 0.015

        if pred_return > threshold and confidence > 0.7:
            signals.append('BUY')
        elif pred_return < -threshold and confidence > 0.7:
            signals.append('SELL')
        else:
            signals.append('HOLD')

        confidence_scores.append(confidence)

    return signals, np.array(confidence_scores)

# Generate signals
current_prices = y_test
signals, confidences = create_robust_trading_signals(
    y_pred, y_lower, y_upper, current_prices
)

# Backtest with uncertainty
portfolio_value = 10000
cash = portfolio_value
position = 0
portfolio_values = []

for i, signal in enumerate(signals):
    if signal == 'BUY' and cash > 0 and confidences[i] > 0.7:
        position = cash / current_prices[i]
        cash = 0

    elif signal == 'SELL' and position > 0:
        cash = position * current_prices[i]
        position = 0

    portfolio_value = cash + position * current_prices[i]
    portfolio_values.append(portfolio_value)

total_return = (portfolio_values[-1] - 10000) / 10000
print(f"\nConformal Prediction Strategy:")
print(f"Total Return: {total_return:.2%}")

# Visualize strategy
plt.figure(figsize=(14, 6))
plt.plot(portfolio_values, label='Portfolio Value', linewidth=2)
plt.axhline(10000, color='r', linestyle='--', label='Initial Capital')
plt.xlabel('Days')
plt.ylabel('Portfolio Value')
plt.title('Trading Strategy Based on Conformal Prediction')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## Conclusion

Conformal prediction provides principled, distribution-free confidence intervals for trading predictions. This approach is particularly valuable in finance where distribution assumptions often fail, enabling more reliable uncertainty quantification for risk management and decision-making.
