#!/usr/bin/env python3
"""Quick test of portfolio optimization service without pytest infrastructure."""

import os
import sys
import asyncio
import pandas as pd
import numpy as np

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.portfolio_optimization import (
    OptimizationObjective,
    PortfolioConstraints,
    OptimizedPortfolio,
    PortfolioOptimizer,
)


def test_optimization_objectives():
    """Test that all optimization objectives exist."""
    assert OptimizationObjective.MAX_SHARPE == "max_sharpe"
    assert OptimizationObjective.MIN_VOLATILITY == "min_volatility"
    assert OptimizationObjective.MAX_RETURN == "max_return"
    assert OptimizationObjective.RISK_PARITY == "risk_parity"
    print("✓ Optimization objectives test passed")


def test_portfolio_constraints():
    """Test portfolio constraints."""
    constraints = PortfolioConstraints(
        min_weight=0.1,
        max_weight=0.5,
        risk_free_rate=0.02
    )

    assert constraints.min_weight == 0.1
    assert constraints.max_weight == 0.5
    assert constraints.risk_free_rate == 0.02
    print("✓ Portfolio constraints test passed")


def test_optimizer_creation():
    """Test creating an optimizer."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    assert optimizer.risk_free_rate == 0.02
    print("✓ Optimizer creation test passed")


async def test_optimize_max_sharpe():
    """Test optimizing for maximum Sharpe ratio."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    # Create sample returns data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'GOOGL': np.random.normal(0.0008, 0.018, 252),
        'MSFT': np.random.normal(0.0009, 0.019, 252)
    }, index=dates)

    result = await optimizer.optimize(
        returns_data=returns,
        objective=OptimizationObjective.MAX_SHARPE
    )

    assert isinstance(result, OptimizedPortfolio)
    assert len(result.weights) == 3
    assert abs(sum(result.weights.values()) - 1.0) < 0.01
    assert result.sharpe_ratio > 0
    print("✓ Optimize max Sharpe test passed")


async def test_optimize_min_volatility():
    """Test optimizing for minimum volatility."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'GOOGL': np.random.normal(0.0008, 0.018, 252),
        'MSFT': np.random.normal(0.0009, 0.019, 252)
    }, index=dates)

    result = await optimizer.optimize(
        returns_data=returns,
        objective=OptimizationObjective.MIN_VOLATILITY
    )

    assert isinstance(result, OptimizedPortfolio)
    assert result.volatility > 0
    assert result.volatility < 1.0
    print("✓ Optimize min volatility test passed")


async def test_efficient_frontier():
    """Test generating efficient frontier."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'GOOGL': np.random.normal(0.0008, 0.018, 252)
    }, index=dates)

    frontier = await optimizer.generate_efficient_frontier(
        returns_data=returns,
        num_portfolios=5
    )

    assert len(frontier.returns) > 0
    assert len(frontier.volatilities) > 0
    assert len(frontier.portfolios) > 0
    print("✓ Efficient frontier test passed")


async def test_monte_carlo_simulation():
    """Test Monte Carlo simulation."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'GOOGL': np.random.normal(0.0008, 0.018, 252)
    }, index=dates)

    portfolio = {"AAPL": 0.6, "GOOGL": 0.4}

    results = await optimizer.monte_carlo_simulation(
        current_portfolio=portfolio,
        returns_data=returns,
        num_simulations=100,
        time_horizon_days=252
    )

    assert results["num_simulations"] == 100
    assert "expected_return" in results
    assert "percentiles" in results
    print("✓ Monte Carlo simulation test passed")


def test_calculate_metrics():
    """Test metric calculation methods."""
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)

    # Test max drawdown
    returns = pd.Series([0.05, 0.03, -0.10, -0.05, 0.02])
    max_dd = optimizer._calculate_max_drawdown(returns)
    assert max_dd >= 0

    # Test VaR/CVaR
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))
    var_95, cvar_95 = optimizer._calculate_var_cvar(returns, 0.95)
    assert var_95 >= 0
    assert cvar_95 >= var_95

    print("✓ Metric calculation test passed")


if __name__ == "__main__":
    print("Running quick portfolio optimization tests...")
    print()

    # Run sync tests
    test_optimization_objectives()
    test_portfolio_constraints()
    test_optimizer_creation()
    test_calculate_metrics()

    # Run async tests
    asyncio.run(test_optimize_max_sharpe())
    asyncio.run(test_optimize_min_volatility())
    asyncio.run(test_efficient_frontier())
    asyncio.run(test_monte_carlo_simulation())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
