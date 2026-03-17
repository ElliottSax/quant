---
title: 'Autoencoders for Anomaly Detection in Trading: Unsupervised Deep Learning'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: autoencoders-for-anomaly-detection-trading
published_date: '2026-03-17'
last_updated: '2026-03-17'
---

# Autoencoders for Anomaly Detection in Trading: Unsupervised Deep Learning

Autoencoders are unsupervised neural networks that compress data into a lower-dimensional representation, then reconstruct the original. In trading, they detect market anomalies and unusual price movements that may signal trading opportunities or risks.

## Understanding Autoencoders

Autoencoders consist of:
1. **Encoder**: Compresses input to lower-dimensional representation (bottleneck)
2. **Bottleneck**: Captures essential information
3. **Decoder**: Reconstructs original input from compressed representation

When trained on normal market data, the autoencoder reconstructs similar data well but struggles with anomalies, creating a high reconstruction error that signals anomalies.

## Complete Autoencoder Trading System

```python
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

# Data preparation
def prepare_autoencoder_data(ticker, start_date, end_date):
    """Prepare data for autoencoder training"""

    data = yf.download(ticker, start=start_date, end=end_date)
    df = data.copy()

    # Create comprehensive features
    df['Returns'] = df['Close'].pct_change()
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Volatility_10'] = df['Returns'].rolling(10).std()
    df['Volatility_20'] = df['Returns'].rolling(20).std()

    # Moving averages
    for period in [5, 10, 20, 50]:
        df[f'SMA_{period}'] = df['Close'].rolling(period).mean()
        df[f'EMA_{period}'] = df['Close'].ewm(span=period).mean()
        df[f'Distance_SMA_{period}'] = (df['Close'] - df[f'SMA_{period}']) / df[f'SMA_{period}']

    # Momentum indicators
    df['RSI_14'] = calculate_rsi(df['Close'], 14)
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df['Close'])
    df['Momentum_10'] = df['Close'] - df['Close'].shift(10)

    # Bollinger Bands
    sma = df['Close'].rolling(20).mean()
    std = df['Close'].rolling(20).std()
    df['BB_Position'] = (df['Close'] - (sma - 2*std)) / (4*std)
    df['BB_Width'] = 4*std / sma

    # ATR
    df['ATR_14'] = calculate_atr(df, 14)
    df['ATR_Ratio'] = df['ATR_14'] / df['Close']

    # Volume features
    if 'Volume' in df.columns:
        df['Volume_SMA'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        df['Price_Volume'] = df['Returns'] * df['Volume_Ratio']

    # High-Low features
    df['High_Low_Range'] = (df['High'] - df['Low']) / df['Close']
    df['Close_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])

    # Lagged returns
    for lag in [1, 2, 3, 5]:
        df[f'Return_Lag_{lag}'] = df['Returns'].shift(lag)

    return df.dropna()

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()
    return atr

# Prepare data
ticker = "AAPL"
df = prepare_autoencoder_data(ticker, "2018-01-01", "2024-01-01")

# Feature selection
feature_cols = [col for col in df.columns
                if col not in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume',
                               'Returns', 'Log_Returns']]

X = df[feature_cols].copy()
X = X.fillna(X.mean())

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data for training
X_train, X_test = train_test_split(X_scaled, test_size=0.2, shuffle=False)

print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")

# Build Autoencoder
input_dim = X_train.shape[1]
encoding_dim = max(input_dim // 3, 5)  # Bottleneck dimension

# Encoder
inputs = Input(shape=(input_dim,))
encoded = Dense(input_dim, activation='relu')(inputs)
encoded = Dropout(0.2)(encoded)
encoded = Dense(int(encoding_dim * 2), activation='relu')(encoded)
encoded = Dropout(0.2)(encoded)
encoded = Dense(encoding_dim, activation='relu', name='bottleneck')(encoded)

# Decoder
decoded = Dense(int(encoding_dim * 2), activation='relu')(encoded)
decoded = Dropout(0.2)(decoded)
decoded = Dense(input_dim, activation='relu')(decoded)
decoded = Dense(input_dim, activation='linear')(decoded)

# Autoencoder model
autoencoder = Model(inputs, decoded)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

print("\nAutoencoder Architecture:")
autoencoder.summary()

# Train autoencoder
history = autoencoder.fit(
    X_train, X_train,
    epochs=100,
    batch_size=32,
    validation_data=(X_test, X_test),
    shuffle=True,
    verbose=1
)

# Plot training history
plt.figure(figsize=(12, 5))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Autoencoder Training History')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Calculate reconstruction error
train_predictions = autoencoder.predict(X_train)
train_error = np.mean(np.square(X_train - train_predictions), axis=1)

test_predictions = autoencoder.predict(X_test)
test_error = np.mean(np.square(X_test - test_predictions), axis=1)

# Determine anomaly threshold (95th percentile of training error)
threshold = np.percentile(train_error, 95)

print(f"\nAnomaly Detection Results:")
print(f"Training error - Mean: {train_error.mean():.6f}, Std: {train_error.std():.6f}")
print(f"Test error - Mean: {test_error.mean():.6f}, Std: {test_error.std():.6f}")
print(f"Anomaly threshold (95th percentile): {threshold:.6f}")

# Identify anomalies
test_anomalies = (test_error > threshold).astype(int)
print(f"Anomalies detected in test set: {test_anomalies.sum()} / {len(test_anomalies)} ({test_anomalies.mean():.2%})")

# Visualize reconstruction errors
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# Train errors
axes[0].plot(train_error, label='Reconstruction Error', alpha=0.7)
axes[0].axhline(y=threshold, color='r', linestyle='--', label='Anomaly Threshold')
axes[0].set_ylabel('Reconstruction Error')
axes[0].set_title('Training Set Reconstruction Error')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Test errors
axes[1].plot(test_error, label='Reconstruction Error', alpha=0.7)
axes[1].axhline(y=threshold, color='r', linestyle='--', label='Anomaly Threshold')
anomaly_indices = np.where(test_anomalies)[0]
axes[1].scatter(anomaly_indices, test_error[anomaly_indices], color='r', s=50, label='Anomalies')
axes[1].set_xlabel('Sample')
axes[1].set_ylabel('Reconstruction Error')
axes[1].set_title('Test Set Reconstruction Error')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Variational Autoencoder (VAE) for Probabilistic Modeling

```python
# Variational Autoencoder for better anomaly detection
from tensorflow.keras.layers import Lambda
from tensorflow.keras import backend as K

latent_dim = 8

# Sampling layer for VAE
def sampling(args):
    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon

# Build VAE
inputs = Input(shape=(input_dim,))
x = Dense(input_dim, activation='relu')(inputs)
x = Dropout(0.2)(x)
x = Dense(64, activation='relu')(x)

z_mean = Dense(latent_dim, name='z_mean')(x)
z_log_var = Dense(latent_dim, name='z_log_var')(x)

z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

# Decoder
decoder_inputs = Input(shape=(latent_dim,))
x = Dense(64, activation='relu')(decoder_inputs)
x = Dropout(0.2)(x)
outputs = Dense(input_dim, activation='linear')(x)

decoder_model = Model(decoder_inputs, outputs, name='decoder')

vae_outputs = decoder_model(z)
vae = Model(inputs, vae_outputs, name='vae')

# VAE loss
def vae_loss(x, x_decoded_mean):
    reconstruction_loss = tf.keras.losses.mse(x, x_decoded_mean)
    reconstruction_loss *= input_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    return K.mean(reconstruction_loss + kl_loss)

vae.compile(optimizer=Adam(learning_rate=0.001), loss=vae_loss)

# Train VAE
vae_history = vae.fit(
    X_train, X_train,
    epochs=100,
    batch_size=32,
    validation_data=(X_test, X_test),
    verbose=0
)

# Calculate VAE reconstruction error
vae_train_pred = vae.predict(X_train)
vae_train_error = np.mean(np.square(X_train - vae_train_pred), axis=1)

vae_test_pred = vae.predict(X_test)
vae_test_error = np.mean(np.square(X_test - vae_test_pred), axis=1)

vae_threshold = np.percentile(vae_train_error, 95)

print(f"VAE Anomaly threshold: {vae_threshold:.6f}")
vae_anomalies = (vae_test_error > vae_threshold).astype(int)
print(f"VAE Anomalies detected: {vae_anomalies.sum()}")
```

## Trading Strategy Using Anomalies

```python
def create_anomaly_trading_signals(anomalies, prices, window=5):
    """Generate trading signals from detected anomalies"""

    signals = []

    for i in range(len(anomalies)):
        if i < window:
            signals.append('HOLD')
            continue

        # Count anomalies in recent window
        recent_anomalies = anomalies[i-window:i].sum()

        if recent_anomalies >= 2:
            # Potential mean reversion opportunity
            signals.append('BUY')
        else:
            signals.append('HOLD')

    return signals

# Generate signals
anomaly_signals = create_anomaly_trading_signals(test_anomalies, df['Close'].iloc[-len(test_anomalies):])

# Backtest anomaly-based strategy
def backtest_anomaly_strategy(df, signals, initial_capital=10000):
    """Backtest anomaly detection strategy"""

    cash = initial_capital
    position = 0
    portfolio_values = []
    trades = []

    prices = df['Close'].values[-len(signals):]

    for i in range(len(signals)):
        if i >= len(prices):
            break

        price = prices[i]

        if signals[i] == 'BUY' and cash > 0 and i < len(prices) - 5:
            # Check if price recovered
            future_price = prices[min(i+5, len(prices)-1)]
            if future_price > price * 1.02:  # Profit opportunity
                position = (cash * 0.9) / price
                cash = cash * 0.1
                trades.append(('BUY', price))

        elif signals[i] == 'SELL' and position > 0:
            cash = position * price * 0.9
            position = 0
            trades.append(('SELL', price))

        portfolio_value = cash + position * price
        portfolio_values.append(portfolio_value)

    return np.array(portfolio_values), trades

portfolio_values, trades = backtest_anomaly_strategy(
    df.iloc[-len(test_anomalies):],
    anomaly_signals,
    initial_capital=10000
)

# Performance metrics
returns = np.diff(portfolio_values) / portfolio_values[:-1]
total_return = (portfolio_values[-1] - 10000) / 10000
sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)

print(f"\nAnomaly Detection Strategy Results:")
print(f"Total Return: {total_return:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
print(f"Total Trades: {len(trades)}")

# Visualize
plt.figure(figsize=(14, 6))
plt.plot(portfolio_values, linewidth=2, label='Portfolio Value')
plt.axhline(y=10000, color='r', linestyle='--', label='Initial Capital')
plt.xlabel('Days')
plt.ylabel('Portfolio Value ($)')
plt.title('Autoencoder Anomaly Detection Strategy')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## Ensemble Anomaly Detection

```python
# Combine multiple anomaly detection methods
def ensemble_anomaly_detection(ae_errors, vae_errors, threshold=0.95):
    """Combine multiple autoencoder results"""

    ae_threshold = np.percentile(ae_errors, threshold)
    vae_threshold = np.percentile(vae_errors, threshold)

    ae_anom = ae_errors > ae_threshold
    vae_anom = vae_errors > vae_threshold

    # Require both methods to agree
    ensemble_anom = ae_anom & vae_anom

    # Or vote-based (at least 2/3 methods agree)
    return ensemble_anom

ensemble_anomalies = ensemble_anomaly_detection(test_error, vae_test_error)
print(f"Ensemble anomalies: {ensemble_anomalies.sum()}")
```

## Conclusion

Autoencoders provide powerful unsupervised anomaly detection capabilities for trading. By learning normal market patterns and identifying deviations, they can signal trading opportunities or warn of potential risks. When combined with proper trading strategies and risk management, autoencoder-based systems offer a novel approach to quantitative trading.
