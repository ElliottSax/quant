---
title: "Quantitative Factor Models: Fama-French and Beyond"
description: "Build factor models for portfolio construction and risk analysis. Fama-French, Carhart, quality, and custom factors with Python implementation."
date: "2026-03-31"
author: "Dr. James Chen"
category: "Trading Strategies"
tags: ["factor models", "Fama-French", "risk factors", "portfolio construction", "alpha generation"]
keywords: ["quantitative factor models", "Fama-French model", "factor investing python"]
---

# Quantitative Factor Models: Fama-French and Beyond

Factor models decompose asset returns into systematic components (factors) and idiosyncratic residuals. They serve two essential purposes in quantitative finance: explaining cross-sectional return differences (why some stocks outperform others) and constructing portfolios with targeted risk exposures.

The Fama-French three-factor model transformed investing by demonstrating that small-cap and value stocks earn systematic premiums beyond what CAPM predicts. Since then, the factor zoo has expanded to hundreds of proposed factors, though only a handful have survived rigorous out-of-sample testing.

## Key Takeaways

- **Factor models explain 60-90% of portfolio return variation**, leaving only 10-40% attributable to stock selection skill.
- **Five factors have robust empirical support**: market, size, value, profitability, and investment (Fama-French five-factor model).
- **Factor timing is extremely difficult.** Most alpha comes from factor construction (selecting the right securities within each factor) rather than timing factor exposures.
- **Factor crowding** reduces expected returns. When too many investors target the same factor, valuations compress and the premium shrinks.

## Loading Factor Data

The Fama-French factor data is freely available from Kenneth French's data library.

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def load_ff_factors(
    model: str = "5",
    frequency: str = "daily",
) -> pd.DataFrame:
    """
    Load Fama-French factor returns from the data library.

    Args:
        model: '3' for three-factor, '5' for five-factor
        frequency: 'daily' or 'monthly'
    """
    import pandas_datareader.data as web

    if model == "3":
        dataset = "F-F_Research_Data_Factors"
    elif model == "5":
        dataset = "F-F_Research_Data_5_Factors_2x3"
    else:
        raise ValueError(f"Unknown model: {model}")

    if frequency == "daily":
        dataset += "_daily"

    ff = web.DataReader(dataset, "famafrench", start="2000-01-01")
    df = ff[0] / 100  # Convert from percentage to decimal

    # Rename columns for clarity
    column_map = {
        "Mkt-RF": "market",
        "SMB": "size",
        "HML": "value",
        "RMW": "profitability",
        "CMA": "investment",
        "RF": "risk_free",
    }
    df.rename(columns=column_map, inplace=True)

    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()

    return df


def load_momentum_factor(frequency: str = "daily") -> pd.Series:
    """Load the Carhart momentum factor (UMD)."""
    import pandas_datareader.data as web

    dataset = "F-F_Momentum_Factor"
    if frequency == "daily":
        dataset += "_daily"

    mom = web.DataReader(dataset, "famafrench", start="2000-01-01")
    series = mom[0].iloc[:, 0] / 100

    if isinstance(series.index, pd.PeriodIndex):
        series.index = series.index.to_timestamp()

    return series.rename("momentum")
```

## Factor Regression and Attribution

Decompose any portfolio's returns into factor exposures and alpha.

```python
class FactorModel:
    """
    Multi-factor model for return attribution and risk decomposition.
    """

    def __init__(self, factor_names: list[str] = None):
        self.factor_names = factor_names or [
            "market", "size", "value", "profitability", "investment"
        ]
        self.betas = None
        self.alpha = None
        self.r_squared = None
        self.residuals = None

    def fit(
        self,
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame,
        risk_free: pd.Series = None,
    ) -> "FactorModel":
        """
        Regress portfolio returns on factors.
        R_p - R_f = alpha + beta_1*F_1 + ... + beta_k*F_k + epsilon
        """
        # Align dates
        common = portfolio_returns.index.intersection(factor_returns.index)
        y = portfolio_returns.loc[common]
        X = factor_returns.loc[common, self.factor_names]

        if risk_free is not None:
            rf = risk_free.loc[common]
            y = y - rf

        # Drop NaN
        valid = ~(X.isna().any(axis=1) | y.isna())
        y = y[valid]
        X = X[valid]

        # OLS regression
        reg = LinearRegression()
        reg.fit(X.values, y.values)

        self.alpha = reg.intercept_
        self.betas = pd.Series(reg.coef_, index=self.factor_names)
        self.r_squared = reg.score(X.values, y.values)
        self.residuals = pd.Series(
            y.values - reg.predict(X.values), index=y.index
        )

        return self

    def attribution(
        self,
        factor_returns: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Decompose portfolio return into factor contributions.
        """
        common = factor_returns.index
        contributions = pd.DataFrame(index=common)

        contributions["alpha"] = self.alpha
        for factor in self.factor_names:
            if factor in factor_returns.columns:
                contributions[factor] = (
                    self.betas[factor] * factor_returns[factor]
                )

        contributions["total_factor"] = contributions[self.factor_names].sum(axis=1)
        contributions["idiosyncratic"] = (
            self.residuals.reindex(common).fillna(0)
        )

        return contributions

    def summary(self) -> None:
        """Print model summary."""
        print("Factor Model Summary")
        print("=" * 50)
        print(f"Alpha (annualized): {self.alpha * 252:.2%}")
        print(f"R-squared: {self.r_squared:.3f}")
        print(f"\nFactor Betas:")
        for factor, beta in self.betas.items():
            significance = "***" if abs(beta) > 0.2 else "**" if abs(beta) > 0.1 else ""
            print(f"  {factor:15s}: {beta:+.4f} {significance}")
        print(f"\nResidual Vol (annualized): {self.residuals.std() * np.sqrt(252):.2%}")
```

## Building Custom Factors

Beyond standard academic factors, custom factors tailored to specific investment universes often provide stronger signals.

```python
class FactorConstructor:
    """
    Construct tradable factor portfolios from stock-level signals.
    """

    @staticmethod
    def construct_long_short_factor(
        signals: pd.DataFrame,
        returns: pd.DataFrame,
        n_quantiles: int = 5,
        weighting: str = "equal",
    ) -> pd.DataFrame:
        """
        Build a long-short factor from cross-sectional signals.

        Args:
            signals: DataFrame (dates x stocks) of signal values
            returns: DataFrame (dates x stocks) of forward returns
            n_quantiles: number of groups (long top quantile, short bottom)
            weighting: 'equal' or 'signal' (signal-weighted)
        """
        factor_returns = []

        for date in signals.index:
            signal_row = signals.loc[date].dropna()
            return_row = returns.loc[date].reindex(signal_row.index).dropna()

            common = signal_row.index.intersection(return_row.index)
            if len(common) < n_quantiles * 5:
                continue

            s = signal_row.loc[common]
            r = return_row.loc[common]

            # Assign quantiles
            quantile_labels = pd.qcut(s, n_quantiles, labels=False, duplicates="drop")

            # Long portfolio (top quantile)
            long_mask = quantile_labels == quantile_labels.max()
            # Short portfolio (bottom quantile)
            short_mask = quantile_labels == quantile_labels.min()

            if weighting == "equal":
                long_ret = r[long_mask].mean()
                short_ret = r[short_mask].mean()
            elif weighting == "signal":
                long_weights = s[long_mask] / s[long_mask].sum()
                short_weights = s[short_mask].abs() / s[short_mask].abs().sum()
                long_ret = (r[long_mask] * long_weights).sum()
                short_ret = (r[short_mask] * short_weights).sum()

            factor_returns.append({
                "date": date,
                "long_return": long_ret,
                "short_return": short_ret,
                "factor_return": long_ret - short_ret,
                "long_count": long_mask.sum(),
                "short_count": short_mask.sum(),
                "spread": s[long_mask].mean() - s[short_mask].mean(),
            })

        return pd.DataFrame(factor_returns).set_index("date")

    @staticmethod
    def quality_factor(
        roe: pd.DataFrame,
        debt_equity: pd.DataFrame,
        earnings_stability: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Construct a quality factor from fundamental data.
        High quality = high ROE + low leverage + stable earnings.
        """
        # Rank each component cross-sectionally
        roe_rank = roe.rank(axis=1, pct=True)
        leverage_rank = 1 - debt_equity.rank(axis=1, pct=True)  # Lower is better
        stability_rank = earnings_stability.rank(axis=1, pct=True)

        # Composite quality score
        quality = (roe_rank + leverage_rank + stability_rank) / 3

        return quality

    @staticmethod
    def momentum_factor(
        prices: pd.DataFrame,
        lookback: int = 252,
        skip: int = 21,
    ) -> pd.DataFrame:
        """
        12-1 month momentum factor (skip most recent month).
        """
        total_return = prices.pct_change(lookback)
        recent_return = prices.pct_change(skip)

        # 12-1 momentum: exclude most recent month
        momentum = total_return - recent_return

        return momentum
```

## Factor Risk Model

Use factors for portfolio risk decomposition and management.

```python
class FactorRiskModel:
    """
    Factor-based risk model for portfolio analytics.
    """

    def __init__(
        self,
        factor_returns: pd.DataFrame,
        asset_betas: pd.DataFrame,
    ):
        """
        Args:
            factor_returns: (T x K) factor return history
            asset_betas: (N x K) factor loadings per asset
        """
        self.factor_returns = factor_returns
        self.asset_betas = asset_betas

        # Factor covariance matrix
        self.factor_cov = factor_returns.cov() * 252  # Annualized

    def portfolio_risk_decomposition(
        self,
        weights: pd.Series,
    ) -> dict:
        """
        Decompose portfolio risk into factor and specific components.
        """
        # Portfolio factor exposures
        common_assets = weights.index.intersection(self.asset_betas.index)
        w = weights.loc[common_assets]
        B = self.asset_betas.loc[common_assets]

        # Portfolio factor betas
        portfolio_betas = B.T @ w

        # Factor risk contribution
        factor_var = portfolio_betas @ self.factor_cov @ portfolio_betas
        factor_vol = np.sqrt(max(factor_var, 0))

        # Individual factor contributions
        factor_contributions = {}
        for factor in self.factor_cov.columns:
            beta = portfolio_betas[factor]
            marginal = beta * (self.factor_cov[factor] @ portfolio_betas)
            factor_contributions[factor] = marginal / max(factor_var, 1e-10)

        return {
            "total_factor_vol": factor_vol,
            "portfolio_betas": portfolio_betas,
            "factor_contributions": pd.Series(factor_contributions),
            "factor_cov": self.factor_cov,
        }

    def factor_neutral_portfolio(
        self,
        alpha_scores: pd.Series,
        target_betas: dict = None,
        max_weight: float = 0.05,
    ) -> pd.Series:
        """
        Construct a factor-neutral portfolio that maximizes alpha
        while constraining factor exposures.

        Uses simple iterative approach (for production, use CVXPY).
        """
        target_betas = target_betas or {
            f: 0.0 for f in self.factor_cov.columns
        }

        # Start with alpha-sorted weights
        common = alpha_scores.index.intersection(self.asset_betas.index)
        scores = alpha_scores.loc[common]
        betas = self.asset_betas.loc[common]

        # Rank-based initial weights
        weights = scores.rank(pct=True) - 0.5  # Center at zero
        weights = weights / weights.abs().sum()  # Normalize

        # Cap individual weights
        weights = weights.clip(-max_weight, max_weight)

        # Iterative neutralization (simplified)
        for _ in range(10):
            port_betas = betas.T @ weights
            for factor, target in target_betas.items():
                if factor in port_betas.index:
                    excess_beta = port_betas[factor] - target
                    factor_loads = betas[factor]
                    adjustment = -excess_beta * factor_loads / (factor_loads ** 2).sum()
                    weights += adjustment
                    weights = weights.clip(-max_weight, max_weight)

        # Re-normalize
        weights = weights / weights.abs().sum()

        return weights
```

## Factor Performance Analysis

```python
def factor_performance_report(
    factor_returns: pd.Series,
    factor_name: str,
) -> dict:
    """Comprehensive factor performance analysis."""
    annual_return = factor_returns.mean() * 252
    annual_vol = factor_returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0

    # Drawdown
    cumulative = (1 + factor_returns).cumprod()
    drawdown = (cumulative.cummax() - cumulative) / cumulative.cummax()

    # Regime analysis
    positive_months = factor_returns.resample("ME").sum()
    hit_rate = (positive_months > 0).mean()

    # Rolling Sharpe
    rolling_sharpe = (
        factor_returns.rolling(252).mean()
        / factor_returns.rolling(252).std()
        * np.sqrt(252)
    )

    report = {
        "factor": factor_name,
        "annual_return": annual_return,
        "annual_vol": annual_vol,
        "sharpe": sharpe,
        "max_drawdown": drawdown.max(),
        "monthly_hit_rate": hit_rate,
        "skewness": factor_returns.skew(),
        "kurtosis": factor_returns.kurtosis(),
        "min_rolling_sharpe": rolling_sharpe.min(),
        "max_rolling_sharpe": rolling_sharpe.max(),
        "t_statistic": annual_return / (annual_vol / np.sqrt(len(factor_returns) / 252)),
    }

    print(f"\n{factor_name} Factor Report:")
    print(f"  Annual Return: {annual_return:.2%}")
    print(f"  Annual Vol: {annual_vol:.2%}")
    print(f"  Sharpe: {sharpe:.2f}")
    print(f"  Max Drawdown: {report['max_drawdown']:.2%}")
    print(f"  Monthly Hit Rate: {hit_rate:.1%}")
    print(f"  t-statistic: {report['t_statistic']:.2f}")

    return report
```

## FAQ

### Which factors have the strongest empirical evidence?

The market factor (equity risk premium) has the strongest evidence across nearly all markets and time periods. After that, the value factor (HML), size factor (SMB), and momentum factor (UMD) have the longest track records and broadest international evidence. The profitability (RMW) and investment (CMA) factors from the Fama-French five-factor model have strong evidence since their introduction. Quality and low-volatility factors also have robust support.

### How do I build a factor-neutral portfolio?

Factor neutrality means your portfolio has zero (or near-zero) exposure to specified factors. The standard approach: (1) estimate each stock's factor betas via regression, (2) compute the portfolio's aggregate factor exposure as the weighted sum of individual betas, (3) use an optimizer to find weights that maximize alpha while constraining factor exposures to zero. In practice, use a quadratic optimizer (CVXPY) with explicit constraints on each factor beta.

### Why do factor premiums vary over time?

Factor premiums are not constant because they are compensation for bearing risk that varies with economic conditions. Value premiums are higher during economic recoveries (when distressed companies rebound), momentum premiums are higher in trending markets, and quality premiums are higher during recessions (flight to quality). This time variation makes factor timing tempting but difficult: most factor timing strategies fail to improve on static allocations after costs.

### What is factor crowding and how do I detect it?

Factor crowding occurs when too many investors hold similar factor-tilted portfolios, compressing the factor's valuation spread and reducing future returns. Detect crowding by monitoring: (1) the factor's valuation spread (e.g., the price-to-book gap between value and growth quintiles), (2) the factor's recent performance (strong past performance attracts capital), (3) short interest concentration (crowded shorts are vulnerable to squeezes). When a factor's valuation spread narrows significantly below historical norms, consider reducing exposure.
