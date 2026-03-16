---
title: "Hierarchical Risk Parity: Machine Learning Portfolio Construction"
description: "Learn Hierarchical Risk Parity (HRP) portfolio allocation using clustering and graph theory for robust, diversified portfolio construction."
date: "2026-04-08"
author: "Dr. James Chen"
category: "Portfolio Management"
tags: ["HRP", "risk parity", "machine learning", "portfolio construction", "clustering"]
keywords: ["hierarchical risk parity", "HRP portfolio", "machine learning portfolio construction", "clustering portfolio allocation", "Lopez de Prado"]
---
# Hierarchical Risk Parity: Machine Learning Portfolio Construction

Hierarchical Risk Parity (HRP), introduced by Marcos Lopez de Prado in 2016, represents a fundamental departure from traditional [portfolio optimization](/blog/portfolio-optimization-guide). Rather than inverting a covariance matrix (which amplifies estimation errors), HRP uses [machine learning](/blog/machine-learning-trading) techniques -- hierarchical clustering and graph theory -- to build portfolios from the correlation structure of asset returns. The result is a portfolio construction method that is more stable, better diversified, and more robust to estimation error than both mean-variance optimization and standard risk parity.

## Why Traditional Methods Fail

Mean-variance optimization requires inverting the covariance matrix, an operation that is numerically unstable when assets are highly correlated or when the number of assets approaches the number of observations. Small estimation errors in the covariance matrix are amplified exponentially during inversion, producing portfolios that are concentrated, unstable, and heavily dependent on the most uncertain inputs.

Standard (inverse-volatility) risk parity avoids the covariance inversion problem but ignores correlations entirely, treating assets as independent. This produces suboptimal allocations when assets are highly correlated -- a portfolio with 10 equity ETFs and 2 bond ETFs under inverse-volatility risk parity will allocate approximately 83% to equities, failing to achieve meaningful diversification.

HRP occupies the middle ground: it uses correlation information without inverting the covariance matrix, producing portfolios that reflect the actual dependency structure of asset returns.

## The HRP Algorithm

HRP operates in three steps: tree clustering, quasi-diagonalization, and recursive bisection.

### Step 1: Tree Clustering

Convert the correlation matrix into a distance matrix:

**d(i,j) = sqrt((1 - rho(i,j)) / 2)**

Where rho(i,j) is the Pearson correlation between assets i and j. This distance metric has the property that perfectly correlated assets have distance 0, uncorrelated assets have distance approximately 0.707, and perfectly anti-correlated assets have distance 1.

Apply hierarchical clustering (single-linkage, complete-linkage, or Ward's method) to the distance matrix to build a dendrogram. Ward's method, which minimizes within-cluster variance, typically produces the most balanced trees for financial data.

The dendrogram organizes assets into a tree structure where closely correlated assets are grouped together. This structure captures the hierarchical nature of financial markets: individual stocks cluster into sectors, sectors cluster into markets, and markets cluster into asset classes.

### Step 2: Quasi-Diagonalization

Reorder the covariance matrix rows and columns according to the dendrogram's leaf order. This rearrangement places correlated assets adjacent to each other, creating a quasi-diagonal structure where large covariances are concentrated near the diagonal.

This quasi-diagonalization ensures that when the algorithm recursively divides the portfolio, each division separates relatively uncorrelated groups of assets, producing more effective diversification.

### Step 3: Recursive Bisection

Starting with the full set of assets, recursively split the portfolio into two sub-portfolios and allocate risk between them based on their inverse variance:

1. Split the ordered asset list into two halves at the dendrogram's top-level division
2. Calculate the variance of each half (using the clustered covariance sub-matrix)
3. Allocate inversely proportional to variance: w_left = var_right / (var_left + var_right)
4. Recursively apply steps 1-3 to each half until reaching individual assets

The variance of each cluster can be calculated as the variance of the inverse-variance-weighted portfolio within that cluster:

**var_cluster = 1 / (1^T * diag(Sigma_cluster)^(-1) * 1)**

This recursive process produces a complete weight vector without ever inverting the full covariance matrix. The only matrix operations involve small sub-matrices at each level of the hierarchy.

## HRP vs. Competing Methods: Empirical Comparison

Lopez de Prado's original paper and subsequent studies demonstrate HRP's advantages through Monte Carlo simulation:

### Out-of-Sample Performance (10,000 simulations, 40 assets)

| Method | Sharpe Ratio | Max Drawdown | Turnover | Stability |
|--------|-------------|--------------|----------|-----------|
| Mean-Variance (MVO) | 0.48 | -28.3% | 0.85 | Low |
| Inverse-Volatility RP | 0.52 | -22.1% | 0.15 | High |
| Equal Risk Contribution | 0.55 | -20.8% | 0.22 | Medium |
| HRP | 0.57 | -19.5% | 0.18 | High |

Key observations:
- HRP achieves the highest Sharpe ratio, benefiting from correlation-aware diversification without covariance inversion
- Maximum drawdown is lowest for HRP, reflecting better tail risk properties from hierarchical diversification
- Turnover is low (comparable to inverse-volatility RP), indicating stable weight estimates
- Stability (measured by weight variation across simulations) is high, confirming robustness to estimation error

### Sensitivity to Estimation Error

When the true covariance matrix is perturbed with noise (simulating estimation error), HRP's performance degrades gracefully while MVO's performance collapses. At noise levels where the correlation matrix is contaminated with 30% random noise:
- MVO Sharpe ratio drops by 45%
- HRP Sharpe ratio drops by only 12%

This robustness is the primary practical advantage of HRP for real-world portfolio construction.

## Implementation Details

### Linkage Method Selection

The choice of linkage method in Step 1 affects portfolio characteristics:

**Single linkage**: Produces elongated clusters (chaining effect). Assets are added to the nearest cluster one at a time. This can produce unbalanced trees and suboptimal diversification.

**Complete linkage**: Produces compact, balanced clusters. Each merge minimizes the maximum distance between cluster members. Better for financial data where tight clusters correspond to sectors or asset classes.

**Ward's method**: Minimizes the total within-cluster variance at each merge step. Produces the most balanced dendrogram and is the default choice for HRP implementations.

### Distance Metric Variations

The standard correlation-based distance metric can be modified:

**Tail correlation distance**: Replace Pearson correlation with lower-tail dependence (Clayton copula) or conditional correlation during drawdowns. This produces portfolios optimized for crisis diversification rather than average-case diversification.

**Information-theoretic distance**: Use mutual information instead of correlation, capturing non-linear dependencies. Mutual information equals zero only for truly independent variables, while correlation can be zero for dependent-but-non-linear relationships.

**Rolling distance**: Use expanding or rolling windows for correlation estimation. Shorter windows make the clustering more responsive to regime changes but less stable.

### Handling New Assets

When a new asset is added to the universe, the dendrogram must be updated. Rather than reconstructing from scratch (which could change the entire portfolio), the new asset can be inserted into the existing tree at its most natural position based on its correlation profile. This produces minimal portfolio disruption, an important practical consideration for funds with frequent universe changes.

## Extensions and Variants

### Hierarchical Equal Risk Contribution (HERC)

HERC, introduced by Raffinot (2017), modifies the recursive bisection step to equalize risk contributions rather than allocating inversely to variance. This produces portfolios where each cluster contributes equally to total portfolio risk, analogous to [equal risk contribution](/blog/risk-parity-portfolio) (ERC) but respecting the hierarchical structure.

HERC generally produces more equally weighted portfolios than HRP, which can be advantageous when the investor has no information about relative asset attractiveness.

### Nested Clustered Optimization (NCO)

NCO, introduced by Lopez de Prado (2019), applies mean-variance optimization within clusters and risk parity between clusters. This exploits the insight that intra-cluster correlations are high (making inversion of small sub-matrices stable) while inter-cluster correlations are lower (making risk parity between clusters appropriate).

NCO can incorporate expected return estimates within clusters, providing a bridge between HRP's robustness and MVO's ability to express views.

### Dynamic HRP

Extend HRP to multiple time periods by:
1. Computing the dendrogram at each rebalancing date using a rolling window
2. Applying a smoothing function to portfolio weights to reduce turnover from dendrogram changes
3. Optionally incorporating regime detection to select different clustering parameters for different market states

## Practical Considerations

### Rebalancing Frequency

HRP portfolios are more stable than MVO portfolios, so less frequent rebalancing is acceptable. Monthly rebalancing is typical, with quarterly rebalancing producing only marginally higher tracking error. [Transaction cost](/blog/transaction-cost-analysis) savings from reduced rebalancing often exceed the marginal benefit of more frequent optimization.

### Universe Size

HRP performs well across universe sizes from 10 to 500+ assets. For very small universes (fewer than 10), the hierarchical structure offers limited benefit over simple inverse-volatility weighting. For large universes (100+), HRP's advantage over MVO becomes more pronounced as the covariance matrix becomes increasingly difficult to estimate and invert reliably.

### Integration with Factor Models

HRP's clustering can be seeded with fundamental information (sector classifications, factor exposures) rather than relying entirely on statistical correlations. This produces more interpretable clusters and more stable portfolios, particularly when return history is limited.

## Key Takeaways

- Hierarchical Risk Parity uses machine learning clustering to build portfolios from the correlation structure without inverting the covariance matrix, avoiding the estimation error amplification that plagues mean-variance optimization
- The three-step algorithm (clustering, quasi-diagonalization, recursive bisection) produces portfolios that are more diversified, more stable, and more robust to estimation error than both MVO and simple risk parity
- HRP outperforms competing methods in out-of-sample tests, with higher Sharpe ratios, lower drawdowns, and substantially lower sensitivity to input estimation error
- Ward's linkage method and correlation-based distance metrics are the standard choices, though tail-dependence and information-theoretic variants offer improved crisis diversification
- Extensions including HERC, NCO, and dynamic HRP address specific limitations and allow integration of return views, [factor models](/blog/quantitative-factor-models), and time-varying dynamics

## Frequently Asked Questions

### Does HRP require expected return estimates?

No. HRP allocates based solely on the covariance (or correlation) matrix, making it a risk-based allocation method. This is both its strength (avoiding the noisy expected return estimation problem) and its limitation (it cannot express views on relative asset attractiveness). The NCO extension allows incorporating return estimates within clusters while maintaining HRP's robustness between clusters.

### How does HRP handle assets with short return histories?

Assets with limited history can be incorporated by using fundamental characteristics to assign them to clusters. For example, a newly listed technology stock can be placed in the technology cluster based on sector classification, and its within-cluster weight can be determined from its available (short) return history. Factor-model-based covariance estimation can supplement limited historical data.

### Is HRP suitable for high-frequency portfolio construction?

HRP's computational cost (dominated by the clustering step) is O(N^2 * log(N)), which is fast enough for daily rebalancing of portfolios with hundreds of assets. For intra-day rebalancing with thousands of assets, the clustering step can be computed once and reused, with only the recursive bisection weights updated using intra-day covariance estimates.

### What software libraries implement HRP?

Python's `riskfolio-lib` and `PyPortfolioOpt` both include HRP implementations. Lopez de Prado's original code is available in his book "Advances in Financial Machine Learning" (2018). The `scipy.cluster.hierarchy` module provides the underlying clustering algorithms. For production implementations, the clustering step can be parallelized across multiple cores.

### How does HRP perform during market crises?

HRP tends to outperform MVO during crises because its diversification is more robust. When correlations spike (as they do during crises), MVO portfolios that were diversified based on normal-period correlations experience higher-than-expected losses. HRP's hierarchical structure provides structural diversification that is less sensitive to correlation shifts, though no risk-based allocation method can fully protect against the correlation convergence that characterizes severe crises.
