---
title: "Feature Engineering for Trading Models: Creating Alpha Signals"
description: "Master feature engineering for quantitative trading. Technical, fundamental, alternative data features with proper normalization and selection techniques."
date: "2026-03-22"
author: "Dr. James Chen"
category: "Data Science"
tags: ["feature engineering", "alpha signals", "machine learning", "quantitative trading", "data science"]
keywords: ["feature engineering trading", "alpha signal generation", "trading features machine learning"]
---

# Feature Engineering for Trading Models: Creating Alpha Signals

Feature engineering is the process that separates profitable quantitative models from academic exercises. Raw market data -- prices, volumes, timestamps -- contains latent information that models cannot extract without human-guided transformation. The features you construct encode your hypotheses about what drives returns, and the quality of these hypotheses determines the ceiling of model performance far more than the choice of algorithm.

This guide systematically covers feature categories, construction techniques, normalization methods, and selection procedures that quant researchers use to build robust trading signals.

## Key Takeaways

- **Features encode hypotheses.** Every feature embodies a belief about what information predicts returns. Build features from domain knowledge, not random transformations.
- **Cross-sectional normalization** (ranking or z-scoring across the universe at each time step) is critical for features that vary in scale across assets and time.
- **Information leakage is the primary risk.** Any feature that uses future data, survivorship-biased data, or point-in-time violations will produce false alpha.
- **Feature interaction and combination** often generate stronger signals than individual features.

## Price-Based Features

Price features capture momentum, mean-reversion, and volatility patterns.

```python
import numpy as np
import pandas as pd

class PriceFeatures:
    """Generate features from OHLCV price data."""

    @staticmethod
    def momentum_features(
        close: pd.Series, windows: list[int] = None
    ) -> pd.DataFrame:
        """
        Multi-horizon momentum signals.
        Captures the tendency for past winners to continue winning.
        """
        windows = windows or [5, 10, 21, 63, 126, 252]
        features = pd.DataFrame(index=close.index)

        for w in windows:
            # Simple return momentum
            features[f"mom_{w}d"] = close.pct_change(w)

            # Volatility-adjusted momentum
            vol = close.pct_change().rolling(w).std()
            features[f"mom_vol_adj_{w}d"] = features[f"mom_{w}d"] / vol

            # Rank momentum (percentile of current return vs history)
            features[f"mom_rank_{w}d"] = (
                features[f"mom_{w}d"]
                .rolling(252)
                .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
            )

        return features

    @staticmethod
    def mean_reversion_features(
        close: pd.Series,
        high: pd.Series,
        low: pd.Series,
    ) -> pd.DataFrame:
        """
        Features that capture overextension from moving averages.
        """
        features = pd.DataFrame(index=close.index)

        for w in [10, 20, 50, 200]:
            sma = close.rolling(w).mean()
            features[f"dist_sma_{w}"] = (close - sma) / sma

        # Bollinger Band position (-1 to +1 range)
        for w in [20, 50]:
            sma = close.rolling(w).mean()
            std = close.rolling(w).std()
            features[f"bb_pct_{w}"] = (close - sma) / (2 * std)

        # High-low range position (Williams %R concept)
        for w in [14, 21]:
            hh = high.rolling(w).max()
            ll = low.rolling(w).min()
            features[f"range_pct_{w}"] = (close - ll) / (hh - ll)

        return features

    @staticmethod
    def volatility_features(
        close: pd.Series,
        high: pd.Series,
        low: pd.Series,
    ) -> pd.DataFrame:
        """
        Volatility and risk features.
        """
        features = pd.DataFrame(index=close.index)
        returns = close.pct_change()

        # Realized volatility at multiple horizons
        for w in [5, 10, 21, 63]:
            features[f"realized_vol_{w}d"] = returns.rolling(w).std() * np.sqrt(252)

        # Volatility of volatility
        vol_21 = returns.rolling(21).std()
        features["vol_of_vol"] = vol_21.rolling(21).std()

        # Parkinson volatility (uses High-Low)
        log_hl = np.log(high / low)
        for w in [10, 21]:
            features[f"parkinson_vol_{w}d"] = (
                np.sqrt(log_hl.pow(2).rolling(w).mean() / (4 * np.log(2)))
                * np.sqrt(252)
            )

        # Volatility ratio (short-term vs long-term)
        features["vol_ratio_5_21"] = (
            returns.rolling(5).std() / returns.rolling(21).std()
        )
        features["vol_ratio_21_63"] = (
            returns.rolling(21).std() / returns.rolling(63).std()
        )

        # Skewness and kurtosis
        for w in [21, 63]:
            features[f"skew_{w}d"] = returns.rolling(w).skew()
            features[f"kurt_{w}d"] = returns.rolling(w).kurt()

        return features
```

## Volume Features

Volume patterns reveal institutional activity and conviction behind price moves.

```python
class VolumeFeatures:
    """Generate features from volume data."""

    @staticmethod
    def compute(
        close: pd.Series,
        volume: pd.Series,
    ) -> pd.DataFrame:
        """Volume-based features."""
        features = pd.DataFrame(index=close.index)
        returns = close.pct_change()

        # Relative volume (current vs average)
        for w in [5, 10, 20]:
            features[f"rel_volume_{w}d"] = volume / volume.rolling(w).mean()

        # Volume trend
        features["volume_trend_10d"] = (
            volume.rolling(5).mean() / volume.rolling(20).mean()
        )

        # On-Balance Volume (OBV) momentum
        obv = (np.sign(returns) * volume).cumsum()
        features["obv_momentum_10d"] = obv.pct_change(10)
        features["obv_momentum_21d"] = obv.pct_change(21)

        # Volume-price divergence
        # High volume on down days = bearish
        # High volume on up days = bullish
        features["vp_correlation_10d"] = (
            returns.rolling(10).corr(volume.pct_change())
        )

        # Money Flow Index components
        typical_price = close  # Simplified (should use (H+L+C)/3)
        money_flow = typical_price * volume
        pos_flow = money_flow.where(returns > 0, 0).rolling(14).sum()
        neg_flow = money_flow.where(returns <= 0, 0).rolling(14).sum()
        features["mfi_14"] = 100 - (100 / (1 + pos_flow / neg_flow.replace(0, 1)))

        # VWAP deviation
        vwap = (close * volume).rolling(20).sum() / volume.rolling(20).sum()
        features["vwap_deviation"] = (close - vwap) / vwap

        return features
```

## Cross-Sectional Features

Cross-sectional features rank each asset relative to its peers at each point in time.

```python
class CrossSectionalFeatures:
    """
    Features computed across a universe of stocks at each time step.
    Critical for factor models and long-short strategies.
    """

    @staticmethod
    def cross_sectional_rank(
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Rank each asset vs peers at each time step.
        Output is percentile [0, 1] where 1 = highest.
        """
        return data.rank(axis=1, pct=True)

    @staticmethod
    def cross_sectional_zscore(
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Z-score each asset vs peers at each time step.
        Handles outliers by winsorizing at 3 std.
        """
        mean = data.mean(axis=1)
        std = data.std(axis=1)

        zscore = data.subtract(mean, axis=0).divide(std, axis=0)

        # Winsorize
        return zscore.clip(-3, 3)

    @staticmethod
    def sector_relative_features(
        returns: pd.DataFrame,
        sector_map: dict[str, str],
        windows: list[int] = None,
    ) -> pd.DataFrame:
        """
        Compute sector-relative momentum and other features.
        Isolates stock-specific signal from sector effects.
        """
        windows = windows or [21, 63]
        features = pd.DataFrame(index=returns.index)

        # Group by sector
        sectors = pd.Series(sector_map)

        for window in windows:
            cum_returns = returns.rolling(window).sum()

            for ticker in returns.columns:
                sector = sectors.get(ticker, "Unknown")
                sector_peers = [
                    t for t, s in sectors.items()
                    if s == sector and t != ticker and t in returns.columns
                ]

                if len(sector_peers) > 0:
                    sector_avg = cum_returns[sector_peers].mean(axis=1)
                    features[f"{ticker}_sector_rel_{window}d"] = (
                        cum_returns[ticker] - sector_avg
                    )

        return features
```

## Feature Normalization

Proper normalization ensures features are comparable across assets and time.

```python
class FeatureNormalizer:
    """
    Normalize features for ML models with financial-specific methods.
    """

    @staticmethod
    def rolling_zscore(
        series: pd.Series, window: int = 252
    ) -> pd.Series:
        """Z-score using rolling mean and std."""
        mean = series.rolling(window).mean()
        std = series.rolling(window).std()
        return (series - mean) / std.replace(0, 1)

    @staticmethod
    def rolling_percentile(
        series: pd.Series, window: int = 252
    ) -> pd.Series:
        """Rolling percentile rank [0, 1]."""
        return series.rolling(window).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        )

    @staticmethod
    def winsorize(
        series: pd.Series, limits: tuple = (0.01, 0.99)
    ) -> pd.Series:
        """Clip extreme values at specified percentiles."""
        lower = series.quantile(limits[0])
        upper = series.quantile(limits[1])
        return series.clip(lower, upper)

    @staticmethod
    def power_transform(
        series: pd.Series, method: str = "yeo-johnson"
    ) -> pd.Series:
        """Apply power transform for Gaussian-like distribution."""
        from sklearn.preprocessing import PowerTransformer
        pt = PowerTransformer(method=method)
        values = series.dropna().values.reshape(-1, 1)
        transformed = pt.fit_transform(values)
        result = series.copy()
        result.loc[series.notna()] = transformed.flatten()
        return result
```

## Feature Selection

Not all features add value. Remove redundant, noisy, and leaky features systematically.

```python
class FeatureSelector:
    """
    Select informative features and remove noise.
    """

    @staticmethod
    def information_coefficient(
        features: pd.DataFrame,
        target: pd.Series,
        method: str = "rank",
    ) -> pd.Series:
        """
        Compute IC (rank correlation) between each feature and target.
        IC > 0.02 is typically considered meaningful for daily data.
        """
        ic_values = {}

        for col in features.columns:
            valid = features[col].notna() & target.notna()
            if valid.sum() < 100:
                continue

            if method == "rank":
                corr = features.loc[valid, col].rank().corr(target[valid].rank())
            else:
                corr = features.loc[valid, col].corr(target[valid])

            ic_values[col] = corr

        ic = pd.Series(ic_values).sort_values(ascending=False)
        return ic

    @staticmethod
    def remove_multicollinear(
        features: pd.DataFrame,
        threshold: float = 0.85,
    ) -> list[str]:
        """
        Remove features with correlation above threshold.
        Keeps the feature with higher average absolute IC.
        """
        corr = features.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

        to_drop = set()
        for col in upper.columns:
            high_corr = upper.index[upper[col] > threshold].tolist()
            if high_corr:
                to_drop.update(high_corr)

        keep = [c for c in features.columns if c not in to_drop]
        print(f"Removed {len(to_drop)} multicollinear features, keeping {len(keep)}")
        return keep

    @staticmethod
    def rolling_ic_stability(
        feature: pd.Series,
        target: pd.Series,
        window: int = 252,
    ) -> pd.Series:
        """
        Rolling IC to assess feature stability over time.
        Stable features have consistent IC; unstable ones are unreliable.
        """
        rolling_ic = feature.rolling(window).corr(target)
        return rolling_ic
```

## Putting It All Together

```python
def build_feature_matrix(
    ohlcv: pd.DataFrame,
    target_horizon: int = 5,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Complete feature engineering pipeline.
    Returns (features, target) aligned and cleaned.
    """
    close = ohlcv["Close"]
    high = ohlcv["High"]
    low = ohlcv["Low"]
    volume = ohlcv["Volume"]

    # Generate all feature groups
    price_feat = PriceFeatures()
    vol_feat = VolumeFeatures()
    normalizer = FeatureNormalizer()

    momentum = price_feat.momentum_features(close)
    mean_rev = price_feat.mean_reversion_features(close, high, low)
    volatility = price_feat.volatility_features(close, high, low)
    vol_features = vol_feat.compute(close, volume)

    # Combine
    features = pd.concat([momentum, mean_rev, volatility, vol_features], axis=1)

    # Normalize all features with rolling z-score
    for col in features.columns:
        features[col] = normalizer.rolling_zscore(features[col], window=252)

    # Winsorize extremes
    for col in features.columns:
        features[col] = normalizer.winsorize(features[col], limits=(0.01, 0.99))

    # Create target
    target = close.pct_change(target_horizon).shift(-target_horizon)

    # Align and clean
    combined = pd.concat([features, target.rename("target")], axis=1).dropna()
    X = combined.drop(columns=["target"])
    y = combined["target"]

    print(f"Feature matrix: {X.shape[0]} samples x {X.shape[1]} features")

    return X, y
```

## FAQ

### How many features should a trading model have?

The optimal number depends on your sample size. A common rule of thumb is to have at least 50-100 observations per feature to avoid overfitting. For daily models with 5 years of data (1,250 samples), limit yourself to 15-25 well-chosen features. For intraday models with millions of observations, you can use hundreds. Always prefer fewer, higher-quality features over many weak ones.

### Should features be normalized before or after train/test split?

Normalize after splitting, using only training data statistics. If you normalize on the full dataset first, information from the test period leaks into the training features, inflating backtest performance. In production, use an expanding window to compute normalization statistics: at each prediction time, normalize using all data available up to that point.

### What is the difference between alpha features and risk features?

Alpha features predict expected returns (e.g., momentum, sentiment). Risk features predict volatility, correlation, or tail risk (e.g., realized volatility, implied volatility skew). Both are valuable: alpha features generate trading signals, while risk features determine position sizing and portfolio construction. Some features serve both purposes. A complete trading system needs both.

### How do I detect look-ahead bias in features?

Look-ahead bias occurs when a feature uses information not available at the time of prediction. Common sources: (1) using point-in-time data that was revised later (GDP, earnings), (2) computing statistics using the full sample (e.g., z-scoring with the global mean), (3) features that implicitly depend on future prices through rebalancing dates or index membership. Test by adding random future-only features; if the model uses them, your pipeline has leakage.
