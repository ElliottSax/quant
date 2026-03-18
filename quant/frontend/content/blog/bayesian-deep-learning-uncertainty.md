---
title: 'Bayesian Deep Learning for Uncertainty: Probabilistic Neural Networks for
  Trading'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: bayesian-deep-learning-uncertainty
published_date: '2026-03-18'
last_updated: '2026-03-18'
---

# Bayesian Deep Learning for Uncertainty: Probabilistic Neural Networks for Trading

Bayesian deep learning quantifies uncertainty in predictions through probability distributions. This approach is crucial for risk-aware trading decisions.

## Understanding Bayesian Deep Learning

Bayesian methods:
- Quantify prediction uncertainty
- Avoid overconfident predictions
- Adapt naturally to new data
- Enable principled decision-making

## Complete Bayesian Deep Learning System

```python
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_probability as tfp
from tensorflow.keras.layers import Input, Dense, Layer
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import matplotlib.pyplot as plt

# Bayesian Dense Layer with weight uncertainty
class BayesianDense(Layer):
    def __init__(self, units, prior_stddev=1.0, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        self.prior_stddev = prior_stddev

    def build(self, input_shape):
        # Mean weights
        self.w_mean = self.add_weight(
            name='w_mean',
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True
        )
        # Weight variance
        self.w_log_std = self.add_weight(
            name='w_log_std',
            shape=(input_shape[-1], self.units),
            initializer='glorot_uniform',
            trainable=True
        )
        # Bias mean
        self.b_mean = self.add_weight(
            name='b_mean',
            shape=(self.units,),
            initializer='zeros',
            trainable=True
        )
        # Bias variance
        self.b_log_std = self.add_weight(
            name='b_log_std',
            shape=(self.units,),
            initializer='glorot_uniform',
            trainable=True
        )

    def call(self, inputs, training=None):
        if training:
            # Sample weights and biases
            w = self.w_mean + tf.exp(self.w_log_std) * tf.random.normal(tf.shape(self.w_mean))
            b = self.b_mean + tf.exp(self.b_log_std) * tf.random.normal(tf.shape(self.b_mean))
        else:
            w = self.w_mean
            b = self.b_mean

        return tf.matmul(inputs, w) + b

# Build Bayesian Neural Network
def build_bayesian_model(input_dim):
    inputs = Input(shape=(input_dim,))

    x = BayesianDense(64)(inputs)
    x = tf.keras.layers.Activation('relu')(x)

    x = BayesianDense(32)(x)
    x = tf.keras.layers.Activation('relu')(x)

    # Output distribution (mean and log std)
    mean = BayesianDense(1)(x)
    log_std = BayesianDense(1)(x)

    model = Model(inputs, [mean, log_std])
    return model

# Fetch data
def prepare_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    df = data.copy()
    df['Returns'] = df['Close'].pct_change()
    df['Volatility_20'] = df['Returns'].rolling(20).std()
    df['RSI'] = calculate_rsi(df['Close'], 14)
    df['MACD'] = calculate_macd(df['Close'])

    features = ['Returns', 'Volatility_20', 'RSI', 'MACD']
    X = df[features].dropna().values
    y = df['Close'].dropna().values[-len(X):]

    return X, y

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

# Prepare data
X, y = prepare_data("AAPL", "2020-01-01", "2024-01-01")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

split = int(0.8 * len(X_scaled))
X_train, X_test = X_scaled[:split], X_scaled[split:]
y_train, y_test = y[:split], y[split:]

y_train = y_train.reshape(-1, 1)
y_test = y_test.reshape(-1, 1)

# Bayesian loss function (negative log likelihood)
def bayesian_loss(y_true, outputs):
    y_pred_mean, y_pred_log_std = outputs
    y_pred_std = tf.exp(y_pred_log_std)

    # Negative log likelihood
    nll = 0.5 * tf.math.log(2 * np.pi * y_pred_std ** 2) + \
          0.5 * ((y_true - y_pred_mean) ** 2) / (y_pred_std ** 2 + 1e-6)

    return tf.reduce_mean(nll)

# Build and train
print("Building and training Bayesian model...")
model = build_bayesian_model(X_train.shape[1])

# Custom training loop
optimizer = Adam(learning_rate=0.001)
train_losses = []

for epoch in range(50):
    with tf.GradientTape() as tape:
        mean, log_std = model(X_train, training=True)
        loss = bayesian_loss(y_train, (mean, log_std))

    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    train_losses.append(loss.numpy())

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/50, Loss: {loss.numpy():.4f}")

# Make predictions with uncertainty
print("\nMaking predictions with uncertainty...")

# Multiple samples for uncertainty
n_samples = 100
predictions_samples = []

for _ in range(n_samples):
    mean, log_std = model(X_test, training=True)
    predictions_samples.append(mean.numpy().flatten())

predictions_samples = np.array(predictions_samples)
pred_mean = predictions_samples.mean(axis=0)
pred_std = predictions_samples.std(axis=0)

# Calculate metrics
rmse = np.sqrt(np.mean((y_test.flatten() - pred_mean) ** 2))
mae = np.mean(np.abs(y_test.flatten() - pred_mean))

# Coverage: % of actuals within 95% confidence interval
ci_lower = pred_mean - 1.96 * pred_std
ci_upper = pred_mean + 1.96 * pred_std
coverage = np.mean((y_test.flatten() >= ci_lower) & (y_test.flatten() <= ci_upper))

print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"95% CI Coverage: {coverage:.2%}")

# Visualize
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Predictions with uncertainty
n_show = 100
indices = np.arange(len(y_test) - n_show, len(y_test))

axes[0, 0].plot(indices, y_test[-n_show:].flatten(), 'b-', linewidth=2, label='Actual')
axes[0, 0].plot(indices, pred_mean[-n_show:], 'r-', linewidth=2, label='Mean')
axes[0, 0].fill_between(
    indices,
    (pred_mean - 1.96 * pred_std)[-n_show:],
    (pred_mean + 1.96 * pred_std)[-n_show:],
    alpha=0.3,
    label='95% CI'
)
axes[0, 0].set_xlabel('Sample')
axes[0, 0].set_ylabel('Price ($)')
axes[0, 0].set_title('Bayesian Predictions with Uncertainty')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Uncertainty over time
axes[0, 1].plot(pred_std[-n_show:], linewidth=2)
axes[0, 1].fill_between(range(n_show), 0, pred_std[-n_show:], alpha=0.3)
axes[0, 1].set_xlabel('Sample')
axes[0, 1].set_ylabel('Prediction Std Dev')
axes[0, 1].set_title('Prediction Uncertainty Over Time')
axes[0, 1].grid(True, alpha=0.3)

# Error distribution
errors = np.abs(y_test.flatten() - pred_mean)
axes[1, 0].hist(errors, bins=30, alpha=0.7)
axes[1, 0].set_xlabel('Prediction Error ($)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].set_title('Error Distribution')
axes[1, 0].grid(True, alpha=0.3)

# Training loss
axes[1, 1].plot(train_losses, linewidth=2)
axes[1, 1].set_xlabel('Epoch')
axes[1, 1].set_ylabel('Loss')
axes[1, 1].set_title('Training Loss')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Posterior sampling for Monte Carlo
print("\nMonte Carlo Sampling from Posterior")

posterior_samples = np.array([
    model(X_test[0:1], training=True)[0].numpy().flatten()[0]
    for _ in range(1000)
])

print(f"Posterior Mean: {posterior_samples.mean():.2f}")
print(f"Posterior Std: {posterior_samples.std():.2f}")
print(f"95% Credible Interval: [{np.percentile(posterior_samples, 2.5):.2f}, {np.percentile(posterior_samples, 97.5):.2f}]")
```

## Trading with Uncertainty-Aware Decisions

```python
# Make trading decisions based on uncertainty
def create_uncertainty_aware_signals(pred_mean, pred_std, current_price, risk_tolerance=1.0):
    """Generate trading signals considering uncertainty"""

    signals = []
    expected_values = []

    for i in range(len(pred_mean)):
        # Expected return
        expected_return = (pred_mean[i] - current_price[i]) / current_price[i]

        # Downside risk (Value at Risk)
        var_95 = pred_mean[i] - 1.96 * pred_std[i]
        downside_risk = (var_95 - current_price[i]) / current_price[i]

        # Risk-adjusted signal
        if expected_return > abs(downside_risk) * risk_tolerance and pred_std[i] < np.percentile(pred_std, 75):
            signals.append('BUY')
        elif expected_return < downside_risk / 2:
            signals.append('SELL')
        else:
            signals.append('HOLD')

        expected_values.append({'return': expected_return, 'risk': abs(downside_risk)})

    return signals, expected_values
```

## Conclusion

Bayesian deep learning provides principled uncertainty quantification for trading. By understanding prediction confidence, traders can make more informed decisions and manage risk effectively.
