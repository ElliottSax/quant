---
title: "Scikit-Learn for Stock Prediction: Machine Learning Models"
description: "Build stock prediction models with scikit-learn. Random forests, gradient boosting, and SVMs for price direction forecasting with proper validation techniques."
date: "2026-03-13"
author: "Dr. James Chen"
category: "Machine Learning"
tags: ["scikit-learn", "machine learning", "stock prediction", "random forest", "gradient boosting"]
keywords: ["scikit-learn stock prediction", "machine learning stock market", "random forest trading"]
---

# Scikit-Learn for Stock Prediction: Machine Learning Models

Machine learning models offer the ability to capture nonlinear relationships in financial data that linear models miss. However, applying scikit-learn to stock prediction is fraught with pitfalls. Naive train/test splits introduce look-ahead bias, feature engineering without domain knowledge produces noise, and overfitting masquerades as alpha.

This guide walks through the correct approach: time-series-aware splitting, financially meaningful features, proper model selection, and honest evaluation. The goal is not to predict exact prices but to forecast the probability of directional moves with enough edge to be tradable after costs.

## Key Takeaways

- **Never use random train/test splits** for time series data. Always use temporal splits or expanding/rolling windows.
- **Feature engineering is 80% of the work.** Raw OHLCV data alone rarely produces useful signals.
- **Gradient boosting (XGBoost, LightGBM)** consistently outperforms other models on tabular financial data.
- **Evaluate with financial metrics** (Sharpe, profit factor), not just accuracy or AUC.

## Problem Formulation

We frame stock prediction as a binary classification problem: will the price go up or down over the next N trading days?

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    classification_report,
)

def create_target(
    prices: pd.Series, horizon: int = 5, threshold: float = 0.0
) -> pd.Series:
    """
    Binary target: 1 if price increases by more than threshold
    over the next `horizon` trading days, else 0.
    """
    future_return = prices.pct_change(horizon).shift(-horizon)
    target = (future_return > threshold).astype(int)
    return target

# Example
# target = create_target(close_prices, horizon=5, threshold=0.005)
```

## Feature Engineering

The features you provide determine the ceiling of model performance. Use financially meaningful indicators rather than arbitrary transformations.

```python
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create ML features from OHLCV data.
    All features use only past data (no look-ahead).
    """
    features = pd.DataFrame(index=df.index)
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Price momentum features
    for window in [5, 10, 21, 63]:
        features[f"return_{window}d"] = close.pct_change(window)
        features[f"vol_{window}d"] = close.pct_change().rolling(window).std()

    # Moving average ratios (mean-reversion signals)
    for window in [10, 20, 50, 200]:
        sma = close.rolling(window).mean()
        features[f"price_to_sma_{window}"] = close / sma - 1

    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    features["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    features["macd"] = ema_12 - ema_26
    features["macd_signal"] = features["macd"].ewm(span=9).mean()
    features["macd_hist"] = features["macd"] - features["macd_signal"]

    # Bollinger Band position
    bb_sma = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    features["bb_position"] = (close - bb_sma) / (2 * bb_std)

    # Volume features
    features["volume_sma_ratio"] = volume / volume.rolling(20).mean()
    features["volume_change"] = volume.pct_change(5)

    # Volatility features
    features["high_low_range"] = (high - low) / close
    features["atr_14"] = (
        pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1).rolling(14).mean() / close
    )

    # Day of week (cyclical encoding)
    features["day_sin"] = np.sin(2 * np.pi * df.index.dayofweek / 5)
    features["day_cos"] = np.cos(2 * np.pi * df.index.dayofweek / 5)

    # Month (cyclical encoding)
    features["month_sin"] = np.sin(2 * np.pi * df.index.month / 12)
    features["month_cos"] = np.cos(2 * np.pi * df.index.month / 12)

    return features
```

## Time-Series Train/Test Split

Standard k-fold cross-validation is invalid for time series because it randomly mixes future and past data. Use temporal splits exclusively.

```python
from sklearn.model_selection import TimeSeriesSplit

def temporal_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    gap: int = 5,
) -> tuple:
    """
    Split data temporally with a gap to prevent leakage.

    Args:
        gap: number of rows between train and test to prevent
             target leakage from overlapping horizons
    """
    split_idx = int(len(X) * (1 - test_size))

    X_train = X.iloc[:split_idx - gap]
    y_train = y.iloc[:split_idx - gap]
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]

    return X_train, X_test, y_train, y_test


def walk_forward_validation(
    X: pd.DataFrame,
    y: pd.Series,
    model,
    n_splits: int = 5,
    gap: int = 5,
) -> list[dict]:
    """
    Walk-forward (expanding window) cross-validation.
    More realistic than standard TimeSeriesSplit.
    """
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=gap)
    results = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        # Scale features (fit on train only)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, "predict_proba") else None

        fold_result = {
            "fold": fold,
            "train_size": len(train_idx),
            "test_size": len(test_idx),
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
        }
        results.append(fold_result)
        print(f"Fold {fold}: Acc={fold_result['accuracy']:.3f}, "
              f"Prec={fold_result['precision']:.3f}")

    return results
```

## Model Training and Comparison

Compare multiple model families and select based on out-of-sample performance.

```python
def train_and_evaluate(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> dict:
    """Train multiple models and compare performance."""

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=500,
            max_depth=6,
            min_samples_leaf=20,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_leaf=20,
            random_state=42,
        ),
        "SVM": SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=42,
        ),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "report": classification_report(y_test, y_pred),
        }

        print(f"\n--- {name} ---")
        print(results[name]["report"])

    return results
```

## Feature Importance Analysis

Understanding which features drive predictions is critical for model validation and strategy insight.

```python
def analyze_feature_importance(
    model, feature_names: list[str], top_n: int = 15
) -> pd.DataFrame:
    """
    Extract and rank feature importances from tree-based models.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        raise ValueError("Model does not have feature_importances_ attribute")

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=False)

    print(f"\nTop {top_n} Features:")
    for _, row in importance_df.head(top_n).iterrows():
        bar = "=" * int(row["importance"] * 200)
        print(f"  {row['feature']:25s} {row['importance']:.4f} {bar}")

    return importance_df
```

## Financial Evaluation

Accuracy is a misleading metric for trading. A model with 52% accuracy can be highly profitable if its correct predictions have larger magnitude than its errors.

```python
def financial_evaluation(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    returns: np.ndarray,
) -> dict:
    """
    Evaluate model predictions using financial metrics.

    Args:
        y_true: actual labels (1=up, 0=down)
        y_pred: predicted labels
        returns: actual forward returns
    """
    # Strategy returns: go long when predicting up, flat otherwise
    strategy_returns = np.where(y_pred == 1, returns, 0)

    # Long/short: go long when predicting up, short when down
    ls_returns = np.where(y_pred == 1, returns, -returns)

    # Metrics
    total_trades = (y_pred == 1).sum()
    winning_trades = ((y_pred == 1) & (returns > 0)).sum()

    strategy_cumulative = (1 + strategy_returns).prod() - 1
    sharpe = (
        np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252)
        if np.std(strategy_returns) > 0 else 0
    )

    gains = strategy_returns[strategy_returns > 0]
    losses = strategy_returns[strategy_returns < 0]
    profit_factor = (
        gains.sum() / abs(losses.sum()) if len(losses) > 0 and losses.sum() != 0 else np.inf
    )

    return {
        "total_return": strategy_cumulative,
        "sharpe_ratio": sharpe,
        "total_trades": total_trades,
        "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
        "profit_factor": profit_factor,
        "avg_win": gains.mean() if len(gains) > 0 else 0,
        "avg_loss": losses.mean() if len(losses) > 0 else 0,
        "max_drawdown": (
            (pd.Series((1 + strategy_returns).cumprod()).cummax()
             - pd.Series((1 + strategy_returns).cumprod()))
            / pd.Series((1 + strategy_returns).cumprod()).cummax()
        ).max(),
    }
```

## Complete Pipeline

Putting it all together into a reproducible pipeline.

```python
def run_prediction_pipeline(
    ticker: str = "SPY",
    start: str = "2018-01-01",
    end: str = "2025-12-31",
    horizon: int = 5,
):
    """End-to-end ML prediction pipeline with proper methodology."""

    # 1. Fetch data
    import yfinance as yf
    df = yf.download(ticker, start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 2. Engineer features and create target
    features = engineer_features(df)
    target = create_target(df["Close"], horizon=horizon, threshold=0.002)

    # 3. Align and drop NaN
    combined = pd.concat([features, target.rename("target")], axis=1).dropna()
    X = combined.drop(columns=["target"])
    y = combined["target"]

    print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
    print(f"Target distribution: {y.value_counts().to_dict()}")

    # 4. Temporal split
    X_train, X_test, y_train, y_test = temporal_train_test_split(
        X, y, test_size=0.2, gap=horizon
    )

    # 5. Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 6. Train and evaluate
    results = train_and_evaluate(
        X_train_scaled, X_test_scaled, y_train.values, y_test.values
    )

    # 7. Financial evaluation of best model
    best_name = max(results, key=lambda k: results[k]["accuracy"])
    best_model = results[best_name]["model"]
    y_pred = best_model.predict(X_test_scaled)

    test_returns = df["Close"].pct_change(horizon).shift(-horizon)
    test_returns_aligned = test_returns.loc[X_test.index].values

    fin_metrics = financial_evaluation(y_test.values, y_pred, test_returns_aligned)

    print(f"\n=== Financial Evaluation ({best_name}) ===")
    for k, v in fin_metrics.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    return results, fin_metrics

# Run the pipeline
# results, metrics = run_prediction_pipeline("SPY")
```

## FAQ

### Can machine learning reliably predict stock prices?

Machine learning cannot predict exact stock prices with useful accuracy. However, ML models can identify probabilistic edges in price direction, especially when combined with strong feature engineering and proper risk management. Even a 52-55% directional accuracy, combined with good risk/reward ratios, produces profitable strategies after costs.

### Which scikit-learn model works best for stock prediction?

Gradient boosting models (GradientBoostingClassifier, or external libraries like XGBoost and LightGBM) consistently perform best on tabular financial data. They handle nonlinear relationships, feature interactions, and noisy labels better than random forests or SVMs. Always start with gradient boosting as your baseline.

### How do I prevent overfitting in financial ML models?

Use three defenses: (1) time-series cross-validation with a gap between train and test periods, (2) regularization via depth limits, minimum leaf sizes, and learning rate shrinkage, (3) feature selection to remove noisy or redundant inputs. Additionally, evaluate on financial metrics (Sharpe, profit factor) rather than just accuracy, as accuracy does not account for the magnitude of gains vs losses.

### How much data do I need to train a stock prediction model?

For daily prediction models with 20-30 features, a minimum of 5 years (approximately 1,250 trading days) is needed for meaningful training and out-of-sample evaluation. More data is better, but be aware that market regimes change. Consider using expanding or rolling windows to adapt to structural shifts, and weight recent data more heavily if appropriate.
