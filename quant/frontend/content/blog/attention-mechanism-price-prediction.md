---
title: 'Attention Mechanisms for Price Prediction: Focusing on Relevant Market Signals'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: attention-mechanism-price-prediction
published_date: '2026-03-17'
last_updated: '2026-03-17'
---

# Attention Mechanisms for Price Prediction: Focusing on Relevant Market Signals

Attention mechanisms enable neural networks to selectively focus on the most important parts of input sequences. In trading, attention helps identify which price movements, indicators, or time periods are most predictive.

## Understanding Attention for Trading

Attention allows:
- Dynamic importance weighting of features
- Interpretable focus on key market signals
- Better long-range dependency capture
- Adaptive response to market regimes

## Complete Attention-Based Trading System

```python
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, LSTM, Layer, Dropout, MultiHeadAttention, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
import matplotlib.pyplot as plt

# Custom Attention Layer
class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def call(self, inputs):
        # inputs: (batch_size, sequence_length, features)
        query, key, value = inputs, inputs, inputs

        # Compute attention scores
        scores = tf.matmul(query, key, transpose_b=True)  # (batch, seq, seq)
        scores = scores / tf.math.sqrt(tf.cast(tf.shape(key)[-1], tf.float32))

        # Apply softmax to get attention weights
        attention_weights = tf.nn.softmax(scores, axis=-1)

        # Apply attention to values
        context = tf.matmul(attention_weights, value)

        return context, attention_weights

# Fetch and prepare data
ticker = "AAPL"
data = yf.download(ticker, start='2018-01-01', end='2024-01-01', progress=False)

# Create features
df = data.copy()
df['Returns'] = df['Close'].pct_change()
df['Volatility_20'] = df['Returns'].rolling(20).std()
df['RSI'] = calculate_rsi(df['Close'], 14)
df['MACD'] = calculate_macd(df['Close'])
df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

# Select features
feature_cols = ['Returns', 'Volatility_20', 'RSI', 'MACD', 'Volume_Ratio']
X = df[feature_cols].dropna().values
prices = df['Close'].values[len(df) - len(X):]

# Normalize
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Create sequences
lookback = 60
X_seq, y_seq = [], []

for i in range(len(X_scaled) - lookback):
    X_seq.append(X_scaled[i:i+lookback])
    y_seq.append((prices[i+lookback] > prices[i+lookback-1]).astype(int))

X_seq = np.array(X_seq)
y_seq = np.array(y_seq)

print(f"Input shape: {X_seq.shape}")

# Build Attention-Based Model
def build_attention_model(lookback=60, num_features=5):
    """Build LSTM with multi-head attention"""

    inputs = Input(shape=(lookback, num_features))

    # LSTM encoder
    lstm_out = LSTM(128, return_sequences=True, activation='relu')(inputs)
    lstm_out = Dropout(0.2)(lstm_out)

    # Multi-head attention
    attention_out = MultiHeadAttention(num_heads=4, key_dim=32)(lstm_out, lstm_out)
    attention_out = Dropout(0.2)(attention_out)

    # Second LSTM
    lstm_out2 = LSTM(64, return_sequences=False, activation='relu')(attention_out)
    lstm_out2 = Dropout(0.2)(lstm_out2)

    # Dense layers
    x = Dense(32, activation='relu')(lstm_out2)
    x = Dropout(0.2)(x)
    outputs = Dense(1, activation='sigmoid')(x)

    model = Model(inputs, outputs)
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

    return model

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
    return macd

# Split data
split_idx = int(0.8 * len(X_seq))
X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]

# Build and train model
model = build_attention_model(lookback=lookback, num_features=num_features)

print("\nTraining attention-based model...")
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    verbose=0
)

# Evaluate
train_acc = model.evaluate(X_train, y_train, verbose=0)[1]
test_acc = model.evaluate(X_test, y_test, verbose=0)[1]

print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

# Visualize training history
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(history.history['loss'], label='Train Loss')
axes[0].plot(history.history['val_loss'], label='Val Loss')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].set_title('Training History - Loss')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(history.history['accuracy'], label='Train Accuracy')
axes[1].plot(history.history['val_accuracy'], label='Val Accuracy')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].set_title('Training History - Accuracy')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## Attention Visualization

```python
# Build model with attention visualization
class AttentionVisualizationModel(Model):
    def __init__(self, lookback=60, num_features=5):
        super().__init__()
        self.lstm1 = LSTM(128, return_sequences=True, activation='relu')
        self.attention = MultiHeadAttention(num_heads=4, key_dim=32)
        self.lstm2 = LSTM(64, return_sequences=False, activation='relu')
        self.dense1 = Dense(32, activation='relu')
        self.output_layer = Dense(1, activation='sigmoid')

    def call(self, inputs, return_attention=False):
        x = self.lstm1(inputs)
        x, attention_weights = self.attention(x, x, return_attention_scores=True)
        x = self.lstm2(x)
        x = self.dense1(x)
        output = self.output_layer(x)

        if return_attention:
            return output, attention_weights
        return output

# Get attention weights
viz_model = AttentionVisualizationModel()
viz_model.set_weights(model.get_weights())

# Sample prediction
sample_input = X_test[0:1]
predictions, attention_weights = viz_model(sample_input, return_attention=True)

# Visualize attention
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# First head
attention_first = attention_weights[0, 0, :, :].numpy()
im = axes[0].imshow(attention_first, cmap='hot', aspect='auto')
axes[0].set_title('Attention Weights - Head 1')
axes[0].set_xlabel('Keys (Time Steps)')
axes[0].set_ylabel('Queries (Time Steps)')
plt.colorbar(im, ax=axes[0])

# Average attention
attention_avg = np.mean(attention_weights[0].numpy(), axis=0)
axes[1].imshow(attention_avg, cmap='hot', aspect='auto')
axes[1].set_title('Average Attention Across Heads')
axes[1].set_xlabel('Keys (Time Steps)')
axes[1].set_ylabel('Queries (Time Steps)')
plt.colorbar(im, ax=axes[1])

plt.tight_layout()
plt.show()

# Find most attended timesteps
attention_importance = attention_avg.sum(axis=0)
top_timesteps = np.argsort(attention_importance)[-5:]

print(f"Most attended time steps: {top_timesteps}")
```

## Self-Attention for Feature Importance

```python
# Analyze which features get most attention
class FeatureAttentionModel(Model):
    def __init__(self, lookback=60, num_features=5):
        super().__init__()
        self.feature_attention = Dense(num_features, activation='softmax')
        self.lstm = LSTM(64, activation='relu')
        self.dense = Dense(32, activation='relu')
        self.output_layer = Dense(1, activation='sigmoid')

    def call(self, inputs, return_feature_weights=False):
        # inputs: (batch_size, lookback, num_features)

        # Feature-level attention
        feature_weights = self.feature_attention(inputs)  # (batch, lookback, num_features)

        # Apply attention weights
        weighted_inputs = inputs * feature_weights
        x = self.lstm(weighted_inputs)
        x = self.dense(x)
        output = self.output_layer(x)

        if return_feature_weights:
            return output, feature_weights
        return output

# Train feature attention model
feature_model = FeatureAttentionModel()
feature_model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy')
feature_model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=0)

# Analyze feature importance
_, feature_weights = feature_model(X_test[0:1], return_feature_weights=True)
feature_importance = feature_weights[0].numpy().mean(axis=0)

print("\nFeature Importance from Attention:")
for i, col in enumerate(feature_cols):
    print(f"{col}: {feature_importance[i]:.4f}")

# Visualize
plt.figure(figsize=(10, 6))
plt.bar(feature_cols, feature_importance, color='steelblue', alpha=0.7)
plt.ylabel('Attention Weight')
plt.title('Feature Importance from Attention Mechanism')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## Trading Signals from Attention

```python
# Generate trading signals based on attention patterns
def generate_attention_signals(model, X, threshold=0.6):
    """Generate trading signals from attention model"""

    predictions = model.predict(X, verbose=0)
    signals = []

    for pred in predictions:
        if pred[0] > threshold:
            signals.append('BUY')
        elif pred[0] < (1 - threshold):
            signals.append('SELL')
        else:
            signals.append('HOLD')

    return signals, predictions

signals, predictions = generate_attention_signals(model, X_test)

# Simple backtest
portfolio_value = 10000
cash = portfolio_value
position = 0
portfolio_values = []

for i in range(len(signals)):
    current_price = prices[split_idx + i + lookback]

    if signals[i] == 'BUY' and cash > 0:
        position = cash / current_price
        cash = 0

    elif signals[i] == 'SELL' and position > 0:
        cash = position * current_price
        position = 0

    portfolio_value = cash + position * current_price
    portfolio_values.append(portfolio_value)

# Performance
total_return = (portfolio_values[-1] - 10000) / 10000
print(f"\nStrategy Performance:")
print(f"Total Return: {total_return:.2%}")

# Visualize
plt.figure(figsize=(14, 6))
plt.plot(portfolio_values, label='Attention Model Strategy')
plt.axhline(y=10000, color='r', linestyle='--', label='Initial Capital')
plt.xlabel('Days')
plt.ylabel('Portfolio Value')
plt.title('Trading Strategy Based on Attention Mechanism')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## Conclusion

Attention mechanisms provide interpretable, focused neural networks for trading. By visualizing what the model attends to, traders gain insight into which market signals drive predictions, enabling better understanding and refinement of trading strategies.
