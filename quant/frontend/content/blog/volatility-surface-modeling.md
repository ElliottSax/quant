---
title: "Volatility Surface Modeling: Skew, Term Structure, and Smile"
description: "Model the implied volatility surface for options pricing. Skew dynamics, term structure, SVI parameterization, and local volatility with Python."
date: "2026-04-10"
author: "Dr. James Chen"
category: "Derivatives"
tags: ["volatility surface", "implied volatility", "skew", "SVI", "options pricing"]
keywords: ["volatility surface modeling", "implied volatility skew", "SVI parameterization"]
---

# Volatility Surface Modeling: Skew, Term Structure, and Smile

The implied volatility surface is the market's complete statement about the distribution of future asset returns. It captures two phenomena that Black-Scholes ignores: the volatility smile (OTM options trade at higher implied volatilities than ATM options) and the term structure (implied volatility varies with expiration). Understanding and modeling this surface is essential for options pricing, risk management, and volatility trading.

This guide covers the construction, parameterization, and analysis of implied volatility surfaces, from raw market quotes through fitted models suitable for pricing and hedging.

## Key Takeaways

- **The volatility surface has two dimensions**: strike (moneyness) and expiration (term structure).
- **Equity markets exhibit negative skew**: OTM puts have higher IV than OTM calls, reflecting demand for downside protection.
- **SVI parameterization** provides a flexible, arbitrage-free representation of the volatility smile.
- **The surface changes over time**: tracking surface dynamics provides trading signals for volatility strategies.

## Building the Volatility Surface from Market Data

```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize, curve_fit
from scipy.interpolate import RectBivariateSpline, griddata

class VolatilitySurface:
    """
    Build and interpolate an implied volatility surface
    from market option quotes.
    """

    def __init__(self, spot: float, rate: float = 0.05, dividend: float = 0.0):
        self.spot = spot
        self.rate = rate
        self.dividend = dividend
        self.raw_data = None
        self.interpolator = None

    def from_market_quotes(
        self,
        strikes: np.ndarray,
        expiries: np.ndarray,
        ivs: np.ndarray,
    ) -> "VolatilitySurface":
        """
        Build surface from raw market implied volatilities.

        Args:
            strikes: 1D array of strike prices
            expiries: 1D array of time-to-expiry (years)
            ivs: 1D array of implied volatilities (same length as strikes/expiries)
        """
        self.raw_data = pd.DataFrame({
            "strike": strikes,
            "expiry": expiries,
            "iv": ivs,
            "moneyness": np.log(strikes / self.spot),
            "log_moneyness": np.log(strikes / (
                self.spot * np.exp((self.rate - self.dividend) * expiries)
            )),
        })

        # Build 2D interpolator
        unique_expiries = np.sort(np.unique(expiries))
        unique_moneyness = np.sort(np.unique(self.raw_data["moneyness"].round(4)))

        if len(unique_expiries) >= 2 and len(unique_moneyness) >= 2:
            # Grid interpolation
            grid_iv = griddata(
                (self.raw_data["moneyness"], self.raw_data["expiry"]),
                self.raw_data["iv"],
                (unique_moneyness[:, None], unique_expiries[None, :]),
                method="cubic",
            )

            # Handle NaN from extrapolation
            mask = ~np.isnan(grid_iv)
            if mask.sum() > 4:
                self.interpolator = RectBivariateSpline(
                    unique_moneyness,
                    unique_expiries,
                    np.nan_to_num(grid_iv, nan=np.nanmean(grid_iv)),
                    kx=min(3, len(unique_moneyness) - 1),
                    ky=min(3, len(unique_expiries) - 1),
                )

        return self

    def get_iv(
        self, strike: float, expiry: float
    ) -> float:
        """Get interpolated implied volatility."""
        moneyness = np.log(strike / self.spot)

        if self.interpolator is not None:
            iv = float(self.interpolator(moneyness, expiry)[0, 0])
            return max(0.01, min(iv, 2.0))  # Bound to reasonable range

        # Fallback: nearest neighbor
        distances = np.sqrt(
            (self.raw_data["moneyness"] - moneyness)**2
            + (self.raw_data["expiry"] - expiry)**2 * 10
        )
        return self.raw_data.loc[distances.idxmin(), "iv"]

    def get_smile(self, expiry: float) -> pd.DataFrame:
        """Extract the volatility smile for a given expiry."""
        if self.raw_data is None:
            return pd.DataFrame()

        # Filter to nearest expiry
        available = self.raw_data["expiry"].unique()
        nearest = available[np.argmin(np.abs(available - expiry))]

        smile = self.raw_data[
            self.raw_data["expiry"] == nearest
        ].sort_values("strike").copy()

        return smile

    def get_term_structure(self, strike: float = None) -> pd.DataFrame:
        """Extract ATM or fixed-strike term structure."""
        if strike is None:
            strike = self.spot

        if self.interpolator is None:
            return pd.DataFrame()

        moneyness = np.log(strike / self.spot)
        expiries = np.sort(self.raw_data["expiry"].unique())

        ivs = [float(self.interpolator(moneyness, t)[0, 0]) for t in expiries]

        return pd.DataFrame({
            "expiry": expiries,
            "iv": ivs,
            "dte": (expiries * 365).astype(int),
        })
```

## SVI Parameterization

The Stochastic Volatility Inspired (SVI) model by Jim Gatheral provides a flexible parameterization of the volatility smile that is widely used in practice.

```python
class SVIModel:
    """
    SVI (Stochastic Volatility Inspired) parameterization.

    Total implied variance w(k) = a + b * (rho*(k-m) + sqrt((k-m)^2 + sigma^2))

    Where:
        k = log(K/F) = log-moneyness
        a = overall level of variance
        b = slope (controls wings)
        rho = rotation (skew direction)
        m = translation (shifts smile horizontally)
        sigma = smoothness at the vertex

    Constraints for no-arbitrage:
        a + b * sigma * sqrt(1 - rho^2) >= 0
        b >= 0
        |rho| < 1
        sigma > 0
    """

    def __init__(self):
        self.params = None

    @staticmethod
    def svi_total_variance(
        k: np.ndarray, a: float, b: float, rho: float, m: float, sigma: float
    ) -> np.ndarray:
        """SVI total implied variance function."""
        return a + b * (rho * (k - m) + np.sqrt((k - m)**2 + sigma**2))

    @staticmethod
    def svi_implied_vol(
        k: np.ndarray, T: float, a: float, b: float, rho: float, m: float, sigma: float
    ) -> np.ndarray:
        """Convert SVI total variance to implied volatility."""
        total_var = SVIModel.svi_total_variance(k, a, b, rho, m, sigma)
        # Clamp to avoid sqrt of negative
        total_var = np.maximum(total_var, 1e-8)
        return np.sqrt(total_var / T)

    def fit(
        self,
        moneyness: np.ndarray,
        total_variance: np.ndarray,
        initial_guess: dict = None,
    ) -> dict:
        """
        Fit SVI parameters to market implied total variance.

        Args:
            moneyness: log(K/F) values
            total_variance: IV^2 * T values
        """
        if initial_guess is None:
            initial_guess = {
                "a": np.mean(total_variance),
                "b": 0.1,
                "rho": -0.3,
                "m": 0.0,
                "sigma": 0.1,
            }

        def objective(params):
            a, b, rho, m, sigma = params
            model_var = self.svi_total_variance(moneyness, a, b, rho, m, sigma)
            return np.sum((model_var - total_variance)**2)

        # Constraints
        bounds = [
            (-0.5, 1.0),     # a
            (0.001, 1.0),    # b
            (-0.999, 0.999), # rho
            (-0.5, 0.5),     # m
            (0.001, 1.0),    # sigma
        ]

        result = minimize(
            objective,
            x0=list(initial_guess.values()),
            bounds=bounds,
            method="L-BFGS-B",
        )

        params = {
            "a": result.x[0],
            "b": result.x[1],
            "rho": result.x[2],
            "m": result.x[3],
            "sigma": result.x[4],
        }

        # Verify no-arbitrage condition
        no_arb = params["a"] + params["b"] * params["sigma"] * np.sqrt(1 - params["rho"]**2) >= 0

        self.params = params
        self.params["no_arbitrage"] = no_arb
        self.params["fit_rmse"] = np.sqrt(result.fun / len(moneyness))

        return params

    def predict(
        self, moneyness: np.ndarray, T: float
    ) -> np.ndarray:
        """Predict implied volatility from fitted SVI model."""
        if self.params is None:
            raise RuntimeError("Model not fitted. Call fit() first.")
        return self.svi_implied_vol(
            moneyness, T,
            self.params["a"], self.params["b"],
            self.params["rho"], self.params["m"],
            self.params["sigma"],
        )
```

## Skew Analysis and Trading Signals

The volatility skew contains information about market expectations and risk appetite.

```python
class SkewAnalyzer:
    """
    Analyze the volatility skew for trading signals.
    """

    @staticmethod
    def compute_skew_metrics(
        strikes: np.ndarray,
        ivs: np.ndarray,
        spot: float,
        expiry: float,
    ) -> dict:
        """
        Compute standardized skew metrics.
        """
        moneyness = strikes / spot
        atm_iv = np.interp(1.0, moneyness, ivs)

        # 25-delta skew (approximated by 95-105% moneyness)
        iv_95 = np.interp(0.95, moneyness, ivs)
        iv_105 = np.interp(1.05, moneyness, ivs)
        skew_25d = iv_95 - iv_105

        # Risk reversal (OTM put IV - OTM call IV)
        iv_90 = np.interp(0.90, moneyness, ivs)
        iv_110 = np.interp(1.10, moneyness, ivs)
        risk_reversal = iv_90 - iv_110

        # Butterfly (wings vs body)
        butterfly = 0.5 * (iv_90 + iv_110) - atm_iv

        # Skew slope (linear regression)
        from numpy.polynomial.polynomial import polyfit
        slope = np.polyfit(moneyness, ivs, 1)[0]

        return {
            "atm_iv": atm_iv,
            "skew_25d": skew_25d,
            "risk_reversal": risk_reversal,
            "butterfly": butterfly,
            "skew_slope": slope,
            "put_skew": iv_95 - atm_iv,
            "call_skew": iv_105 - atm_iv,
        }

    @staticmethod
    def skew_zscore(
        current_skew: float,
        historical_skew: pd.Series,
        window: int = 252,
    ) -> float:
        """
        Z-score of current skew vs its history.
        High z-score = skew is steep relative to history (bearish sentiment).
        Low z-score = skew is flat (complacent).
        """
        recent = historical_skew.iloc[-window:]
        return (current_skew - recent.mean()) / recent.std()

    @staticmethod
    def term_structure_slope(
        atm_ivs: pd.Series,  # Indexed by expiry
    ) -> dict:
        """
        Analyze the IV term structure.
        Normal: upward sloping (longer expiry = higher IV)
        Inverted: downward sloping (near-term stress)
        """
        if len(atm_ivs) < 2:
            return {"slope": 0, "shape": "insufficient_data"}

        expiries = atm_ivs.index.values.astype(float)
        ivs = atm_ivs.values

        slope = np.polyfit(expiries, ivs, 1)[0]

        # Contango vs backwardation
        if ivs[0] < ivs[-1]:
            shape = "contango"
        elif ivs[0] > ivs[-1] * 1.05:
            shape = "backwardation"
        else:
            shape = "flat"

        return {
            "slope": slope,
            "shape": shape,
            "front_iv": ivs[0],
            "back_iv": ivs[-1],
            "spread": ivs[0] - ivs[-1],
        }
```

## Local Volatility Model

The Dupire local volatility model provides a volatility that is consistent with all observed option prices simultaneously.

```python
class LocalVolatility:
    """
    Dupire's local volatility model.
    Computes the unique diffusion coefficient consistent with
    all observed European option prices.

    sigma_local^2(K,T) = (dC/dT + (r-q)*K*dC/dK + q*C) /
                          (0.5 * K^2 * d2C/dK2)
    """

    def __init__(self, surface: VolatilitySurface):
        self.surface = surface

    def compute(
        self,
        strike: float,
        expiry: float,
        dK: float = None,
        dT: float = None,
    ) -> float:
        """
        Compute local volatility at (strike, expiry) using
        finite differences on the implied volatility surface.
        """
        S = self.surface.spot
        r = self.surface.rate
        q = self.surface.dividend

        if dK is None:
            dK = strike * 0.01
        if dT is None:
            dT = max(expiry * 0.01, 1/365)

        # Get surrounding IVs for finite differences
        iv_center = self.surface.get_iv(strike, expiry)

        # dC/dT via finite difference
        iv_T_up = self.surface.get_iv(strike, expiry + dT)
        iv_T_down = self.surface.get_iv(strike, max(expiry - dT, dT))

        # dC/dK and d2C/dK2
        iv_K_up = self.surface.get_iv(strike + dK, expiry)
        iv_K_down = self.surface.get_iv(strike - dK, expiry)

        # Convert IVs to prices for Dupire formula
        from scipy.stats import norm as normal_dist

        def bs_call(s, k, t, vol):
            d1 = (np.log(s/k) + (r - q + 0.5*vol**2)*t) / (vol*np.sqrt(t))
            d2 = d1 - vol*np.sqrt(t)
            return s*np.exp(-q*t)*normal_dist.cdf(d1) - k*np.exp(-r*t)*normal_dist.cdf(d2)

        # Prices
        C = bs_call(S, strike, expiry, iv_center)
        C_Tup = bs_call(S, strike, expiry + dT, iv_T_up)
        C_Tdn = bs_call(S, strike, max(expiry - dT, dT), iv_T_down)
        C_Kup = bs_call(S, strike + dK, expiry, iv_K_up)
        C_Kdn = bs_call(S, strike - dK, expiry, iv_K_down)

        # Finite differences
        dC_dT = (C_Tup - C_Tdn) / (2 * dT)
        dC_dK = (C_Kup - C_Kdn) / (2 * dK)
        d2C_dK2 = (C_Kup - 2*C + C_Kdn) / (dK**2)

        # Dupire formula
        numerator = dC_dT + (r - q) * strike * dC_dK + q * C
        denominator = 0.5 * strike**2 * d2C_dK2

        if denominator <= 0 or numerator < 0:
            return iv_center  # Fallback to implied vol

        local_var = numerator / denominator
        return np.sqrt(max(local_var, 1e-8))
```

## Surface Dynamics and Trading

```python
def surface_change_signal(
    current_surface: VolatilitySurface,
    previous_surface: VolatilitySurface,
    expiry: float = 30/365,
) -> dict:
    """
    Compare two volatility surfaces to generate trading signals.

    Changes in surface shape (steepening/flattening of skew,
    shifts in term structure) are predictive of future returns.
    """
    skew_analyzer = SkewAnalyzer()
    strikes = np.linspace(
        current_surface.spot * 0.85,
        current_surface.spot * 1.15,
        30,
    )

    current_ivs = np.array([current_surface.get_iv(k, expiry) for k in strikes])
    previous_ivs = np.array([previous_surface.get_iv(k, expiry) for k in strikes])

    current_metrics = skew_analyzer.compute_skew_metrics(
        strikes, current_ivs, current_surface.spot, expiry
    )
    previous_metrics = skew_analyzer.compute_skew_metrics(
        strikes, previous_ivs, previous_surface.spot, expiry
    )

    return {
        "atm_iv_change": current_metrics["atm_iv"] - previous_metrics["atm_iv"],
        "skew_change": current_metrics["skew_25d"] - previous_metrics["skew_25d"],
        "rr_change": current_metrics["risk_reversal"] - previous_metrics["risk_reversal"],
        "butterfly_change": current_metrics["butterfly"] - previous_metrics["butterfly"],
        "skew_steepening": current_metrics["skew_25d"] > previous_metrics["skew_25d"],
        "current_metrics": current_metrics,
        "previous_metrics": previous_metrics,
    }
```

## FAQ

### Why does the volatility smile exist?

The volatility smile exists because real-world return distributions have fatter tails and negative skewness compared to the log-normal distribution assumed by Black-Scholes. OTM puts are priced higher (higher IV) because tail risk is underestimated by log-normal models, and institutional demand for downside protection (portfolio insurance) further elevates put IVs. The smile became more pronounced after the 1987 crash, when the market recognized the need to price tail risk explicitly.

### What is the difference between implied, local, and stochastic volatility?

Implied volatility is the Black-Scholes input that matches market prices, producing one number per option. Local volatility (Dupire) is a deterministic volatility function sigma(S,t) that reproduces all market prices simultaneously. Stochastic volatility models (Heston, SABR) treat volatility itself as a random process with its own dynamics. Local vol produces no smile dynamics (future smiles are flat), while stochastic vol captures realistic smile evolution. Production systems often use SABR or Heston for exotic pricing.

### How do I trade the volatility skew?

Common skew trades include: (1) risk reversals (buy OTM put, sell OTM call) to express a view on skew steepening, (2) put spreads or call spreads that benefit from skew normalization, (3) ratio spreads that are vega-neutral but skew-exposed. The key insight is that skew tends to mean-revert: when it becomes unusually steep (expensive puts), selling the skew and hedging with delta often profits. Monitor skew z-scores relative to 6-12 month history.

### What is the SVI model and why is it popular?

The SVI (Stochastic Volatility Inspired) model parameterizes the total implied variance as a function of log-moneyness using five parameters. It is popular because: (1) it fits market smiles accurately with few parameters, (2) it has a natural connection to stochastic volatility theory, (3) simple conditions on parameters guarantee no static arbitrage, and (4) it interpolates and extrapolates smoothly. SVI is the industry standard for parameterizing individual smile slices before constructing the full surface.
