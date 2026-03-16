---
title: "Time Series Analysis for Stock Markets: ARIMA and Beyond"
description: "Master time series analysis for stocks with ARIMA, GARCH, and state-space models. Stationarity testing, forecasting, and volatility modeling with Python code."
date: "2026-03-15"
author: "Dr. James Chen"
category: "Data Science"
tags: ["time series", "ARIMA", "GARCH", "forecasting", "volatility modeling"]
keywords: ["time series analysis stocks", "ARIMA stock prediction", "GARCH volatility model"]
---
# Time Series Analysis for Stock Markets: ARIMA and Beyond

Time series analysis provides the statistical foundation for understanding and forecasting financial markets. Before the [machine learning](/blog/machine-learning-trading) era, methods like ARIMA and GARCH were the primary tools for price and volatility forecasting. Today they remain essential: ARIMA models serve as benchmarks against which more complex models must prove their worth, and GARCH remains the industry standard for volatility estimation in risk management and options pricing (see our [options calculator](https://calculatortools.com/blog/options-profit-calculator)).

This guide covers the full time series modeling pipeline for stocks, from stationarity testing through ARIMA and GARCH estimation to out-of-sample evaluation.

## Key Takeaways

- **Stationarity is a prerequisite** for classical time series models. Raw stock prices are non-stationary; returns are approximately stationary.
- **ARIMA models** capture linear autoregressive and moving average patterns in return series.
- **GARCH models** capture the volatility clustering that ARIMA ignores, which is critical for risk management and options pricing.
- **Information criteria** (AIC, BIC) guide model selection, but out-of-sample performance is the definitive test.

## Stationarity Testing

Stationarity means the statistical properties of a time series do not change over time. The Augmented Dickey-Fuller (ADF) and KPSS tests provide complementary perspectives.

```python
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings("ignore")

def test_stationarity(series: pd.Series, name: str = "Series") -> dict:
    """
    Run ADF and KPSS tests for stationarity.
    ADF H0: unit root exists (non-stationary)
    KPSS H0: series is stationary

    Interpretation:
    - ADF reject + KPSS fail to reject -> Stationary
    - ADF fail to reject + KPSS reject -> Non-stationary
    - Both reject -> Trend-stationary (difference needed)
    - Neither reject -> Inconclusive
    """
    # ADF test
    adf_result = adfuller(series.dropna(), autolag="AIC")
    adf_statistic = adf_result[0]
    adf_pvalue = adf_result[1]

    # KPSS test
    kpss_result = kpss(series.dropna(), regression="c", nlags="auto")
    kpss_statistic = kpss_result[0]
    kpss_pvalue = kpss_result[1]

    results = {
        "name": name,
        "adf_statistic": adf_statistic,
        "adf_pvalue": adf_pvalue,
        "adf_stationary": adf_pvalue < 0.05,
        "kpss_statistic": kpss_statistic,
        "kpss_pvalue": kpss_pvalue,
        "kpss_stationary": kpss_pvalue > 0.05,
    }

    conclusion = "Stationary" if results["adf_stationary"] and results["kpss_stationary"] else "Non-stationary"
    print(f"\n{name}:")
    print(f"  ADF: stat={adf_statistic:.4f}, p={adf_pvalue:.4f} -> {'Stationary' if results['adf_stationary'] else 'Non-stationary'}")
    print(f"  KPSS: stat={kpss_statistic:.4f}, p={kpss_pvalue:.4f} -> {'Stationary' if results['kpss_stationary'] else 'Non-stationary'}")
    print(f"  Conclusion: {conclusion}")

    return results

# Example: Test prices vs returns
# prices = pd.Series(...)
# test_stationarity(prices, "Price Level")
# test_stationarity(prices.pct_change().dropna(), "Returns")
```

## ACF and PACF Analysis

The autocorrelation function (ACF) and partial autocorrelation function (PACF) reveal the order of AR and MA components.

```python
def analyze_autocorrelation(
    series: pd.Series, lags: int = 40, title: str = ""
):
    """
    Plot ACF and PACF with significance bands.
    PACF cutoff -> AR order (p)
    ACF cutoff -> MA order (q)
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
    plot_acf(series.dropna(), lags=lags, ax=ax1, title=f"ACF - {title}")
    plot_pacf(series.dropna(), lags=lags, ax=ax2, title=f"PACF - {title}")
    plt.tight_layout()
    return fig


def identify_arima_order(
    series: pd.Series, max_p: int = 5, max_d: int = 2, max_q: int = 5
) -> tuple[int, int, int]:
    """
    Automatic ARIMA order selection using AIC.
    Tests all combinations up to (max_p, max_d, max_q).
    """
    best_aic = np.inf
    best_order = (0, 0, 0)

    # Determine differencing order
    d = 0
    temp = series.copy()
    for d_test in range(max_d + 1):
        result = adfuller(temp.dropna())
        if result[1] < 0.05:
            d = d_test
            break
        temp = temp.diff().dropna()
    else:
        d = max_d

    # Grid search over p, q
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            if p == 0 and q == 0:
                continue
            try:
                model = ARIMA(series, order=(p, d, q))
                result = model.fit()
                if result.aic < best_aic:
                    best_aic = result.aic
                    best_order = (p, d, q)
            except Exception:
                continue

    print(f"Best ARIMA order: {best_order} (AIC: {best_aic:.2f})")
    return best_order
```

## ARIMA Modeling

Fit an ARIMA model and generate forecasts with confidence intervals.

```python
def fit_arima(
    series: pd.Series,
    order: tuple[int, int, int] = (1, 1, 1),
    forecast_steps: int = 21,
) -> dict:
    """
    Fit ARIMA model and produce forecasts with diagnostics.
    """
    model = ARIMA(series, order=order)
    result = model.fit()

    # Model diagnostics
    print(result.summary().tables[1])
    print(f"\nAIC: {result.aic:.2f}")
    print(f"BIC: {result.bic:.2f}")

    # Residual diagnostics
    residuals = result.resid
    lb_stat, lb_pvalue = result.test_serial_correlation("ljungbox", lags=[10])[0]

    print(f"Ljung-Box p-value (lag 10): {lb_pvalue[0]:.4f}")
    print("Residuals are white noise" if lb_pvalue[0] > 0.05 else "Residual autocorrelation detected")

    # Forecast
    forecast = result.get_forecast(steps=forecast_steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int(alpha=0.05)

    return {
        "model": result,
        "residuals": residuals,
        "forecast_mean": forecast_mean,
        "forecast_lower": conf_int.iloc[:, 0],
        "forecast_upper": conf_int.iloc[:, 1],
        "aic": result.aic,
        "bic": result.bic,
    }
```

## GARCH Volatility Modeling

GARCH models capture the fact that large price moves cluster together. This is essential for risk management, options pricing, and position sizing.

```python
from arch import arch_model

def fit_garch(
    returns: pd.Series,
    p: int = 1,
    q: int = 1,
    dist: str = "t",
    forecast_horizon: int = 21,
) -> dict:
    """
    Fit GARCH(p,q) model for volatility estimation.

    Args:
        returns: return series (not prices)
        p: GARCH lag order
        q: ARCH lag order
        dist: error distribution ('normal', 't', 'skewt')
        forecast_horizon: number of periods to forecast
    """
    # Scale returns to percentage for numerical stability
    scaled_returns = returns * 100

    model = arch_model(
        scaled_returns,
        vol="Garch",
        p=p,
        q=q,
        dist=dist,
        mean="AR",
        lags=1,
    )
    result = model.fit(disp="off")

    print(result.summary().tables[1])

    # Conditional volatility (annualized, back to decimal)
    conditional_vol = result.conditional_volatility / 100 * np.sqrt(252)

    # Forecast
    forecast = result.forecast(horizon=forecast_horizon)
    forecast_vol = np.sqrt(forecast.variance.dropna().values[-1]) / 100 * np.sqrt(252)

    # Standardized residuals for model diagnostics
    std_resid = result.std_resid

    return {
        "model": result,
        "conditional_vol": conditional_vol,
        "forecast_vol": forecast_vol,
        "std_residuals": std_resid,
        "alpha": result.params.get("alpha[1]", None),
        "beta": result.params.get("beta[1]", None),
        "persistence": result.params.get("alpha[1]", 0) + result.params.get("beta[1]", 0),
    }

# Example usage
# returns = prices.pct_change().dropna()
# garch_result = fit_garch(returns, p=1, q=1, dist="t")
# print(f"Volatility persistence: {garch_result['persistence']:.4f}")
```

## EGARCH for Asymmetric Volatility

Stocks exhibit the leverage effect: negative returns increase volatility more than positive returns of the same magnitude. EGARCH captures this asymmetry.

```python
def fit_egarch(
    returns: pd.Series,
    p: int = 1,
    q: int = 1,
) -> dict:
    """
    EGARCH model for asymmetric volatility response.
    Captures leverage effect (negative returns -> higher vol).
    """
    scaled_returns = returns * 100

    model = arch_model(
        scaled_returns,
        vol="EGARCH",
        p=p,
        q=q,
        dist="skewt",
        mean="Zero",
    )
    result = model.fit(disp="off")

    # Check for leverage effect
    gamma = result.params.get("gamma[1]", 0)
    leverage = "Yes" if gamma < 0 else "No"

    print(f"Leverage effect: {leverage} (gamma = {gamma:.4f})")
    print(f"Negative shocks increase vol by {abs(gamma):.1%} more than positive")

    return {
        "model": result,
        "gamma": gamma,
        "leverage_effect": leverage,
        "conditional_vol": result.conditional_volatility / 100 * np.sqrt(252),
    }
```

## Rolling Forecast Evaluation

The correct way to evaluate time series forecasts is with a rolling or expanding window.

```python
def rolling_forecast_evaluation(
    series: pd.Series,
    order: tuple = (1, 0, 1),
    window_size: int = 252,
    forecast_horizon: int = 1,
) -> pd.DataFrame:
    """
    Rolling window ARIMA forecast evaluation.
    Refit model at each step to simulate real-time forecasting.
    """
    forecasts = []
    actuals = []

    for i in range(window_size, len(series) - forecast_horizon):
        train = series.iloc[i - window_size:i]
        actual = series.iloc[i + forecast_horizon - 1]

        try:
            model = ARIMA(train, order=order)
            result = model.fit()
            forecast = result.forecast(steps=forecast_horizon)
            forecasts.append(forecast.iloc[-1])
        except Exception:
            forecasts.append(np.nan)

        actuals.append(actual)

    results = pd.DataFrame({
        "actual": actuals,
        "forecast": forecasts,
    }, index=series.index[window_size:len(series) - forecast_horizon])

    results["error"] = results["actual"] - results["forecast"]
    results["abs_error"] = results["error"].abs()

    # Evaluation metrics
    mae = results["abs_error"].mean()
    rmse = np.sqrt((results["error"] ** 2).mean())

    # Direction accuracy
    actual_dir = (results["actual"] > 0).astype(int)
    forecast_dir = (results["forecast"] > 0).astype(int)
    direction_accuracy = (actual_dir == forecast_dir).mean()

    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Direction Accuracy: {direction_accuracy:.1%}")

    return results
```

## Combining ARIMA and GARCH

The standard approach uses ARIMA for the conditional mean and GARCH for the conditional variance.

```python
def arima_garch_model(
    returns: pd.Series,
    arima_order: tuple = (1, 0, 1),
    garch_order: tuple = (1, 1),
) -> dict:
    """
    Two-stage ARIMA-GARCH model.
    Stage 1: ARIMA for conditional mean
    Stage 2: GARCH on ARIMA residuals for conditional variance
    """
    # Stage 1: ARIMA
    arima_model = ARIMA(returns, order=arima_order)
    arima_result = arima_model.fit()
    arima_residuals = arima_result.resid

    # Stage 2: GARCH on residuals
    garch = arch_model(
        arima_residuals * 100,
        vol="Garch",
        p=garch_order[0],
        q=garch_order[1],
        dist="t",
        mean="Zero",
    )
    garch_result = garch.fit(disp="off")

    cond_vol = garch_result.conditional_volatility / 100 * np.sqrt(252)

    print(f"ARIMA AIC: {arima_result.aic:.2f}")
    print(f"GARCH persistence: {garch_result.params.get('alpha[1]', 0) + garch_result.params.get('beta[1]', 0):.4f}")

    return {
        "arima_model": arima_result,
        "garch_model": garch_result,
        "conditional_mean": arima_result.fittedvalues,
        "conditional_vol": cond_vol,
        "standardized_residuals": garch_result.std_resid,
    }
```

## FAQ

### Is ARIMA useful for predicting stock prices?

ARIMA is generally not useful for predicting stock price levels with profitable accuracy, because prices are close to a random walk and ARIMA forecast intervals widen rapidly. However, ARIMA is valuable for (1) benchmarking more complex models, (2) modeling stationary transformed series like returns or spreads, and (3) short-horizon mean-reversion signals in high-frequency contexts. The primary value of ARIMA in quant finance is as a building block rather than a standalone predictor.

### When should I use GARCH instead of historical volatility?

Use GARCH whenever you need forward-looking volatility estimates that react to recent market conditions. Historical volatility (rolling standard deviation) assigns equal weight to all observations in the window, while GARCH weights recent observations more heavily and captures volatility clustering. GARCH is essential for options pricing, risk-[based position sizing](/blog/atr-average-true-range-guide), and any system where volatility regime changes affect decisions.

### How do I choose between GARCH, EGARCH, and GJR-GARCH?

Standard GARCH(1,1) is the default choice and works well in most situations. Use EGARCH when you need to model the leverage effect (asymmetric response to positive vs negative returns), which is common in equity markets. GJR-GARCH is an alternative asymmetric specification. In practice, fit all three and compare via BIC. For most equity applications, EGARCH or GJR-GARCH will outperform standard GARCH due to the leverage effect.

### How do I test if my ARIMA residuals are white noise?

Apply the Ljung-Box test to the residuals at multiple lag lengths (10, 20, 30). If the p-values are all above 0.05, the residuals show no significant autocorrelation, confirming the model has captured the linear dependence structure. Also check residual ACF/PACF plots visually for any remaining patterns.
