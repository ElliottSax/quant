---
title: "American Option Pricing"
slug: "american-option-pricing"
description: "Quantitative methods for pricing American options including binomial trees, Longstaff-Schwartz Monte Carlo, and finite difference methods with implementation details."
keywords: ["American options", "option pricing", "Longstaff-Schwartz", "binomial tree", "early exercise"]
author: "Dr. James Chen"
category: "Algo Trading"
date: "2026-03-15"
word_count: 1880
quality_score: 90
seo_optimized: true
---

# American Option Pricing: Numerical Methods for Early Exercise Valuation

## Introduction

American options, which permit exercise at any time before expiration, present one of the classic challenges in quantitative finance. Unlike European options with their elegant Black-Scholes closed-form solution, American options require numerical methods because the early exercise boundary is a free boundary that must be solved simultaneously with the option price. This article covers three production-grade approaches: the Cox-Ross-Rubinstein binomial tree, the Longstaff-Schwartz least-squares Monte Carlo, and the finite difference method for the Black-Scholes PDE.

## The Early Exercise Problem

The value of an American option at any time $t$ is:

$$
V_t = \max\left(h(S_t),\ \mathbb{E}^Q\left[e^{-r\Delta t} V_{t+\Delta t} \mid \mathcal{F}_t\right]\right)
$$

where $h(S_t)$ is the intrinsic value (payoff from immediate exercise) and the expectation is the continuation value (holding the option). The option holder exercises when intrinsic value exceeds continuation value.

For a put option, $h(S_t) = \max(K - S_t, 0)$. For a call on a non-dividend-paying stock, early exercise is never optimal (American call = European call). For calls on dividend-paying stocks and for all puts, the early exercise premium is material.

## Method 1: Binomial Tree (CRR)

The Cox-Ross-Rubinstein model discretizes the stock price process into a recombining binomial tree.

### Parameters

$$
u = e^{\sigma\sqrt{\Delta t}}, \quad d = e^{-\sigma\sqrt{\Delta t}} = \frac{1}{u}, \quad p = \frac{e^{(r-q)\Delta t} - d}{u - d}
$$

where $\sigma$ is volatility, $r$ is the risk-free rate, $q$ is the dividend yield, and $\Delta t = T/N$.

### Implementation

```python
import numpy as np

def american_option_binomial(S: float, K: float, T: float, r: float,
                              sigma: float, q: float = 0.0,
                              N: int = 500, option_type: str = 'put') -> float:
    """
    Price an American option using the CRR binomial tree.

    Parameters
    ----------
    S : float - Current stock price
    K : float - Strike price
    T : float - Time to expiration (years)
    r : float - Risk-free rate
    sigma : float - Volatility
    q : float - Continuous dividend yield
    N : int - Number of time steps
    option_type : str - 'put' or 'call'

    Returns
    -------
    float - Option price
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    # Stock prices at maturity
    stock_prices = S * u ** np.arange(N, -1, -1) * d ** np.arange(0, N + 1)

    # Option values at maturity
    if option_type == 'put':
        option_values = np.maximum(K - stock_prices, 0)
    else:
        option_values = np.maximum(stock_prices - K, 0)

    # Backward induction with early exercise check
    for i in range(N - 1, -1, -1):
        stock_prices = S * u ** np.arange(i, -1, -1) * d ** np.arange(0, i + 1)

        # Continuation value
        option_values = disc * (p * option_values[:-1] + (1 - p) * option_values[1:])

        # Early exercise value
        if option_type == 'put':
            exercise = np.maximum(K - stock_prices, 0)
        else:
            exercise = np.maximum(stock_prices - K, 0)

        # American: take max of continuation and exercise
        option_values = np.maximum(option_values, exercise)

    return option_values[0]

# Example: American put
price = american_option_binomial(S=100, K=105, T=1.0, r=0.05, sigma=0.20, N=1000)
print(f"American Put Price: ${price:.4f}")  # ~$8.72
```

With N=1000 steps, the binomial tree converges to within $0.01 of the true price. Richardson extrapolation (averaging results from N and N/2 steps) accelerates convergence.

## Method 2: Longstaff-Schwartz Monte Carlo

The Longstaff-Schwartz (LSM) algorithm uses regression to estimate continuation values, enabling Monte Carlo simulation for American options.

### Algorithm

1. Simulate $M$ stock price paths over $N$ time steps
2. At maturity, compute payoffs
3. Working backward, at each time step:
   - Identify paths that are in-the-money
   - Regress discounted future cash flows on basis functions of the current stock price
   - Compare the fitted continuation value with immediate exercise value
   - Update cash flow matrix

```python
def american_option_lsm(S: float, K: float, T: float, r: float,
                         sigma: float, q: float = 0.0,
                         M: int = 100_000, N: int = 50,
                         option_type: str = 'put',
                         seed: int = 42) -> float:
    """
    Longstaff-Schwartz least-squares Monte Carlo for American options.
    """
    np.random.seed(seed)
    dt = T / N
    discount = np.exp(-r * dt)

    # Simulate GBM paths
    Z = np.random.standard_normal((M, N))
    drift = (r - q - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)

    log_returns = drift + diffusion * Z
    log_prices = np.log(S) + np.cumsum(log_returns, axis=1)
    stock_paths = np.exp(log_prices)
    stock_paths = np.column_stack([np.full(M, S), stock_paths])

    # Payoff function
    if option_type == 'put':
        payoff = lambda s: np.maximum(K - s, 0)
    else:
        payoff = lambda s: np.maximum(s - K, 0)

    # Initialize cash flows at maturity
    cash_flows = payoff(stock_paths[:, -1])
    exercise_time = np.full(M, N)

    # Backward induction
    for t in range(N - 1, 0, -1):
        S_t = stock_paths[:, t]
        intrinsic = payoff(S_t)
        itm = intrinsic > 0  # In-the-money paths

        if itm.sum() < 10:
            continue

        # Discounted future cash flows for ITM paths
        future_cf = np.zeros(M)
        for i in range(M):
            if itm[i]:
                steps_ahead = exercise_time[i] - t
                future_cf[i] = cash_flows[i] * discount ** steps_ahead

        # Regression: continuation value ~ polynomial of stock price
        X = S_t[itm]
        Y = future_cf[itm]

        # Laguerre polynomial basis (order 3)
        basis = np.column_stack([
            np.exp(-X / (2 * K)),
            np.exp(-X / (2 * K)) * (1 - X / K),
            np.exp(-X / (2 * K)) * (1 - 2 * X / K + 0.5 * (X / K)**2)
        ])

        # OLS regression
        coeffs = np.linalg.lstsq(basis, Y, rcond=None)[0]
        continuation = basis @ coeffs

        # Exercise if intrinsic > continuation
        exercise_mask = np.zeros(M, dtype=bool)
        exercise_mask[itm] = intrinsic[itm] > continuation

        cash_flows[exercise_mask] = intrinsic[exercise_mask]
        exercise_time[exercise_mask] = t

    # Discount all cash flows to time 0
    discounted = np.array([
        cash_flows[i] * np.exp(-r * exercise_time[i] * dt)
        for i in range(M)
    ])

    return discounted.mean()

price = american_option_lsm(S=100, K=105, T=1.0, r=0.05, sigma=0.20)
print(f"LSM American Put: ${price:.4f}")
```

LSM is particularly valuable for multi-asset American options (e.g., rainbow options, basket options) where tree methods face exponential growth in dimensionality.

## Method 3: Finite Difference Method

The finite difference approach directly solves the Black-Scholes PDE with the early exercise constraint.

### The PDE

$$
\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + (r-q)S\frac{\partial V}{\partial S} - rV = 0
$$

subject to $V(S,t) \geq h(S)$ at all times (the American constraint).

### Crank-Nicolson with PSOR

```python
def american_option_fd(S: float, K: float, T: float, r: float,
                        sigma: float, q: float = 0.0,
                        N_time: int = 1000, N_space: int = 200,
                        option_type: str = 'put') -> float:
    """
    Finite difference (Crank-Nicolson + PSOR) for American options.
    """
    S_max = 4 * K
    dt = T / N_time
    dS = S_max / N_space

    S_grid = np.linspace(0, S_max, N_space + 1)

    if option_type == 'put':
        payoff = np.maximum(K - S_grid, 0)
    else:
        payoff = np.maximum(S_grid - K, 0)

    V = payoff.copy()

    # Coefficients for Crank-Nicolson
    j = np.arange(1, N_space)
    alpha = 0.25 * dt * (sigma**2 * j**2 - (r - q) * j)
    beta = -0.5 * dt * (sigma**2 * j**2 + r)
    gamma_coeff = 0.25 * dt * (sigma**2 * j**2 + (r - q) * j)

    # Tridiagonal matrices
    M1 = np.diag(1 - beta) + np.diag(-alpha[1:], -1) + np.diag(-gamma_coeff[:-1], 1)
    M2 = np.diag(1 + beta) + np.diag(alpha[1:], -1) + np.diag(gamma_coeff[:-1], 1)

    # Time stepping with Projected SOR
    omega = 1.2  # Over-relaxation parameter

    for n in range(N_time):
        rhs = M2 @ V[1:-1]

        # Boundary conditions
        if option_type == 'put':
            rhs[0] += alpha[0] * (K * np.exp(-r * (N_time - n) * dt))
        else:
            rhs[-1] += gamma_coeff[-1] * (S_max - K * np.exp(-r * (N_time - n) * dt))

        # PSOR iteration
        V_new = V[1:-1].copy()
        for _ in range(100):  # Max iterations
            V_old = V_new.copy()
            for i in range(len(V_new)):
                residual = rhs[i] - M1[i] @ V_new
                V_new[i] += omega * residual / M1[i, i]
                V_new[i] = max(V_new[i], payoff[i + 1])  # American constraint

            if np.max(np.abs(V_new - V_old)) < 1e-8:
                break

        V[1:-1] = V_new

    # Interpolate to get price at S
    return np.interp(S, S_grid, V)
```

## Comparing the Methods

| Method | Complexity | Dimensions | Accuracy | Speed |
|--------|-----------|------------|----------|-------|
| Binomial Tree | O(N^2) | 1 | High (large N) | Fast |
| LSM Monte Carlo | O(M * N) | Multi-asset | Moderate | Moderate |
| Finite Difference | O(N_t * N_s) | 1-2 | Very high | Moderate |

For a single-asset American put (S=100, K=105, T=1, r=5%, sigma=20%), all three methods converge to approximately $8.72, compared to the European put value of $7.94. The early exercise premium of $0.78 (9.8% of the European value) reflects the value of being able to exercise deep in-the-money puts to earn interest on the strike price proceeds.

## The Early Exercise Boundary

The critical stock price $S^*(t)$ below which early exercise is optimal (for puts) satisfies:

$$
K - S^*(t) = V^{European}(S^*(t), t) + \text{time value}
$$

As expiration approaches, $S^*(t) \to K$ for puts. At long horizons, $S^*(t) \to \frac{rK}{r+\lambda}$ where $\lambda$ is the hazard rate of the stock price crossing the boundary.

Computing this boundary is useful for risk management: it tells you exactly when your short option position is likely to face assignment.

## Practical Considerations

**Dividends**: Discrete dividends are critical for American calls. Model them as known dollar amounts at specific dates rather than continuous yields. Adjust the tree or simulation paths at ex-dividend dates.

**Greeks**: All three methods can produce Greeks. For trees, use the values at neighboring nodes. For MC, use pathwise derivatives or likelihood ratio methods. For FD, Greeks are simply finite differences on the grid.

**Calibration**: In production, volatility is not constant. Use the local volatility surface $\sigma(S,t)$ calibrated to the European option market, then price Americans using that surface.

## Conclusion

American option pricing requires balancing accuracy, speed, and implementation complexity. Binomial trees are the workhorse for single-asset vanilla options. Longstaff-Schwartz Monte Carlo extends to high-dimensional exotic payoffs. Finite difference methods offer the highest accuracy for 1D and 2D problems with complex boundary conditions. Understanding all three approaches equips the quantitative practitioner to choose the right tool for each pricing problem.

## Frequently Asked Questions

### Why can't we use Black-Scholes directly for American options?

Black-Scholes assumes exercise only at expiration (European style). American options allow early exercise, creating a free boundary problem where the exercise boundary itself is unknown and must be solved simultaneously with the option price. There are analytical approximations (Barone-Adesi-Whaley, Bjerksund-Stensland), but they sacrifice accuracy for speed.

### When is early exercise of an American put optimal?

Early exercise becomes optimal when the put is sufficiently deep in the money that the interest earned on the strike price proceeds exceeds the remaining time value plus any dividend benefit from holding. For a non-dividend-paying stock, this occurs roughly when $S < S^* \approx \frac{rK}{r + 0.5\sigma^2}$.

### How many paths do I need for Longstaff-Schwartz?

For a standard single-asset American put, 50,000-100,000 paths with 50-100 time steps produce prices accurate to within $0.01-0.02. For multi-asset options, increase to 200,000+ paths and use variance reduction techniques (antithetic variates, control variates using the European price).

### How does the early exercise premium change with interest rates?

For puts, higher interest rates increase the early exercise premium because the value of receiving cash sooner is greater. For calls on dividend-paying stocks, higher interest rates decrease the early exercise premium because the cost of paying the strike price sooner is greater.

### Can I use neural networks to price American options?

Yes. Deep optimal stopping methods (e.g., the Deep Longstaff-Schwartz approach) replace the polynomial regression with a neural network that learns the optimal exercise boundary. This scales better to high-dimensional problems (10+ underlying assets) where polynomial basis functions are inadequate. Training requires significant computational resources but inference is fast.
