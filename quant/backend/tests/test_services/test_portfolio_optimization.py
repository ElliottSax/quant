"""Tests for Portfolio Optimization service."""

import pytest
import pandas as pd
import numpy as np
from typing import Dict

from app.services.portfolio_optimization import (
    OptimizationObjective,
    PortfolioConstraints,
    OptimizedPortfolio,
    EfficientFrontier,
    PortfolioOptimizer,
    get_portfolio_optimizer,
)


class TestOptimizationObjective:
    """Test OptimizationObjective enum."""

    def test_optimization_objectives_exist(self):
        """Test that all optimization objectives are defined."""
        assert OptimizationObjective.MAX_SHARPE == "max_sharpe"
        assert OptimizationObjective.MIN_VOLATILITY == "min_volatility"
        assert OptimizationObjective.MAX_RETURN == "max_return"
        assert OptimizationObjective.EFFICIENT_FRONTIER == "efficient_frontier"
        assert OptimizationObjective.RISK_PARITY == "risk_parity"
        assert OptimizationObjective.MAX_DIVERSIFICATION == "max_diversification"

    def test_optimization_objective_count(self):
        """Test that we have all 6 objectives."""
        assert len(list(OptimizationObjective)) == 6


class TestPortfolioConstraints:
    """Test PortfolioConstraints model."""

    def test_default_constraints(self):
        """Test default constraint values."""
        constraints = PortfolioConstraints()

        assert constraints.min_weight == 0.0
        assert constraints.max_weight == 1.0
        assert constraints.target_return is None
        assert constraints.risk_free_rate == 0.02
        assert constraints.allow_short is False

    def test_custom_constraints(self):
        """Test custom constraint values."""
        constraints = PortfolioConstraints(
            min_weight=0.05,
            max_weight=0.40,
            target_return=0.15,
            risk_free_rate=0.03,
            allow_short=True
        )

        assert constraints.min_weight == 0.05
        assert constraints.max_weight == 0.40
        assert constraints.target_return == 0.15
        assert constraints.risk_free_rate == 0.03
        assert constraints.allow_short is True

    def test_no_short_selling_constraint(self):
        """Test that short selling can be disabled."""
        constraints = PortfolioConstraints(allow_short=False)
        assert constraints.allow_short is False


class TestOptimizedPortfolio:
    """Test OptimizedPortfolio model."""

    def test_create_optimized_portfolio(self):
        """Test creating an optimized portfolio."""
        portfolio = OptimizedPortfolio(
            weights={"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3},
            expected_return=0.12,
            volatility=0.15,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            max_drawdown=0.10,
            var_95=0.05,
            cvar_95=0.07,
            diversification_ratio=1.2,
            objective_value=1.5
        )

        assert portfolio.weights == {"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3}
        assert portfolio.expected_return == 0.12
        assert portfolio.volatility == 0.15
        assert portfolio.sharpe_ratio == 1.5
        assert portfolio.max_drawdown == 0.10

    def test_portfolio_weights_sum_to_one(self):
        """Test that portfolio weights sum to approximately 1."""
        portfolio = OptimizedPortfolio(
            weights={"AAPL": 0.4, "GOOGL": 0.35, "MSFT": 0.25},
            expected_return=0.10,
            volatility=0.12,
            sharpe_ratio=1.0,
            sortino_ratio=1.2,
            max_drawdown=0.08,
            var_95=0.04,
            cvar_95=0.06,
            diversification_ratio=1.1,
            objective_value=1.0
        )

        total_weight = sum(portfolio.weights.values())
        assert abs(total_weight - 1.0) < 0.01


class TestEfficientFrontier:
    """Test EfficientFrontier model."""

    def test_create_efficient_frontier(self):
        """Test creating efficient frontier data."""
        frontier = EfficientFrontier(
            returns=[0.08, 0.10, 0.12],
            volatilities=[0.10, 0.12, 0.15],
            sharpe_ratios=[0.6, 0.67, 0.67],
            portfolios=[
                {"AAPL": 0.5, "GOOGL": 0.5},
                {"AAPL": 0.4, "GOOGL": 0.6},
                {"AAPL": 0.3, "GOOGL": 0.7}
            ]
        )

        assert len(frontier.returns) == 3
        assert len(frontier.volatilities) == 3
        assert len(frontier.sharpe_ratios) == 3
        assert len(frontier.portfolios) == 3


class TestPortfolioOptimizer:
    """Test PortfolioOptimizer class."""

    @pytest.fixture
    def optimizer(self):
        """Create a portfolio optimizer instance."""
        return PortfolioOptimizer(risk_free_rate=0.02)

    @pytest.fixture
    def sample_returns_data(self):
        """Create sample returns data for 3 assets."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')

        # Generate correlated returns
        returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 252),
            'GOOGL': np.random.normal(0.0008, 0.018, 252),
            'MSFT': np.random.normal(0.0009, 0.019, 252)
        }, index=dates)

        return returns

    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer.risk_free_rate == 0.02

    async def test_optimize_max_sharpe(self, optimizer, sample_returns_data):
        """Test optimizing for maximum Sharpe ratio."""
        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_SHARPE
        )

        assert isinstance(result, OptimizedPortfolio)
        assert len(result.weights) == 3
        assert abs(sum(result.weights.values()) - 1.0) < 0.01
        assert result.sharpe_ratio > 0

    async def test_optimize_min_volatility(self, optimizer, sample_returns_data):
        """Test optimizing for minimum volatility."""
        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MIN_VOLATILITY
        )

        assert isinstance(result, OptimizedPortfolio)
        assert result.volatility > 0
        assert result.volatility < 1.0  # Reasonable volatility

    async def test_optimize_max_return(self, optimizer, sample_returns_data):
        """Test optimizing for maximum return."""
        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_RETURN
        )

        assert isinstance(result, OptimizedPortfolio)
        assert result.expected_return > 0

    async def test_optimize_risk_parity(self, optimizer, sample_returns_data):
        """Test risk parity optimization."""
        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.RISK_PARITY
        )

        assert isinstance(result, OptimizedPortfolio)
        assert abs(sum(result.weights.values()) - 1.0) < 0.01

    async def test_optimize_with_constraints(self, optimizer, sample_returns_data):
        """Test optimization with custom constraints."""
        constraints = PortfolioConstraints(
            min_weight=0.1,
            max_weight=0.5
        )

        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_SHARPE,
            constraints=constraints
        )

        # Check that weights respect constraints
        for weight in result.weights.values():
            assert weight >= 0.1 - 0.01  # Small tolerance
            assert weight <= 0.5 + 0.01

    async def test_optimize_with_short_selling(self, optimizer, sample_returns_data):
        """Test optimization allowing short positions."""
        constraints = PortfolioConstraints(allow_short=True)

        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_SHARPE,
            constraints=constraints
        )

        # Weights should sum to 1 but can be negative
        assert abs(sum(result.weights.values()) - 1.0) < 0.01

    async def test_portfolio_metrics_calculated(self, optimizer, sample_returns_data):
        """Test that all portfolio metrics are calculated."""
        result = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_SHARPE
        )

        assert result.expected_return is not None
        assert result.volatility is not None
        assert result.sharpe_ratio is not None
        assert result.sortino_ratio is not None
        assert result.max_drawdown is not None
        assert result.var_95 is not None
        assert result.cvar_95 is not None
        assert result.diversification_ratio is not None

    async def test_generate_efficient_frontier(self, optimizer, sample_returns_data):
        """Test generating efficient frontier."""
        frontier = await optimizer.generate_efficient_frontier(
            returns_data=sample_returns_data,
            num_portfolios=10
        )

        assert isinstance(frontier, EfficientFrontier)
        assert len(frontier.returns) > 0
        assert len(frontier.volatilities) > 0
        assert len(frontier.sharpe_ratios) > 0
        assert len(frontier.portfolios) > 0

    async def test_efficient_frontier_properties(self, optimizer, sample_returns_data):
        """Test that efficient frontier has expected properties."""
        frontier = await optimizer.generate_efficient_frontier(
            returns_data=sample_returns_data,
            num_portfolios=20
        )

        # Returns should generally increase along frontier
        # (though not strictly monotonic due to optimization constraints)
        assert max(frontier.returns) > min(frontier.returns)

        # All volatilities should be positive
        assert all(vol > 0 for vol in frontier.volatilities)

    def test_calculate_sortino_ratio(self, optimizer):
        """Test Sortino ratio calculation."""
        # Create returns with some negative values
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, -0.005, 0.02])

        sortino = optimizer._calculate_sortino_ratio(returns, risk_free_rate=0.02)

        assert isinstance(sortino, float)
        # Sortino should handle downside deviation

    def test_calculate_sortino_ratio_no_downside(self, optimizer):
        """Test Sortino ratio when no downside deviation."""
        # All positive returns
        returns = pd.Series([0.01, 0.02, 0.015, 0.02, 0.025])

        sortino = optimizer._calculate_sortino_ratio(returns, risk_free_rate=0.02)

        # Should return 0 when no downside
        assert sortino == 0.0

    def test_calculate_max_drawdown(self, optimizer):
        """Test maximum drawdown calculation."""
        # Create returns that lead to a drawdown
        returns = pd.Series([0.05, 0.03, -0.10, -0.05, 0.02, 0.03])

        max_dd = optimizer._calculate_max_drawdown(returns)

        assert isinstance(max_dd, float)
        assert max_dd >= 0  # Max drawdown is positive

    def test_calculate_max_drawdown_positive_returns(self, optimizer):
        """Test max drawdown with only positive returns."""
        returns = pd.Series([0.01, 0.02, 0.015, 0.02])

        max_dd = optimizer._calculate_max_drawdown(returns)

        # Should be very small or zero
        assert max_dd >= 0
        assert max_dd < 0.01

    def test_calculate_var_cvar(self, optimizer):
        """Test VaR and CVaR calculation."""
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))

        var_95, cvar_95 = optimizer._calculate_var_cvar(returns, confidence=0.95)

        assert isinstance(var_95, float)
        assert isinstance(cvar_95, float)
        assert var_95 >= 0
        assert cvar_95 >= 0
        assert cvar_95 >= var_95  # CVaR should be >= VaR

    def test_calculate_var_cvar_different_confidence(self, optimizer):
        """Test VaR/CVaR with different confidence levels."""
        returns = pd.Series(np.random.normal(0.001, 0.02, 252))

        var_90, cvar_90 = optimizer._calculate_var_cvar(returns, confidence=0.90)
        var_99, cvar_99 = optimizer._calculate_var_cvar(returns, confidence=0.99)

        # Higher confidence should give higher VaR
        assert var_99 >= var_90

    def test_calculate_diversification_ratio(self, optimizer):
        """Test diversification ratio calculation."""
        # Create sample data
        expected_returns = pd.Series({'AAPL': 0.10, 'GOOGL': 0.12, 'MSFT': 0.11})
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01, 0.015],
             [0.01, 0.05, 0.02],
             [0.015, 0.02, 0.045]],
            index=['AAPL', 'GOOGL', 'MSFT'],
            columns=['AAPL', 'GOOGL', 'MSFT']
        )
        weights = np.array([0.33, 0.33, 0.34])

        div_ratio = optimizer._calculate_diversification_ratio(
            weights, expected_returns, cov_matrix
        )

        assert isinstance(div_ratio, float)
        assert div_ratio >= 1.0  # Should be >= 1 for diversified portfolio

    def test_calculate_diversification_ratio_single_asset(self, optimizer):
        """Test diversification ratio for single asset portfolio."""
        expected_returns = pd.Series({'AAPL': 0.10, 'GOOGL': 0.12, 'MSFT': 0.11})
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01, 0.015],
             [0.01, 0.05, 0.02],
             [0.015, 0.02, 0.045]],
            index=['AAPL', 'GOOGL', 'MSFT'],
            columns=['AAPL', 'GOOGL', 'MSFT']
        )
        weights = np.array([1.0, 0.0, 0.0])  # All in one asset

        div_ratio = optimizer._calculate_diversification_ratio(
            weights, expected_returns, cov_matrix
        )

        # Single asset should have div ratio close to 1
        assert abs(div_ratio - 1.0) < 0.01

    async def test_monte_carlo_simulation(self, optimizer, sample_returns_data):
        """Test Monte Carlo simulation."""
        portfolio = {"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3}

        results = await optimizer.monte_carlo_simulation(
            current_portfolio=portfolio,
            returns_data=sample_returns_data,
            num_simulations=1000,
            time_horizon_days=252
        )

        assert results["num_simulations"] == 1000
        assert results["time_horizon_days"] == 252
        assert "expected_return" in results
        assert "median_return" in results
        assert "percentiles" in results
        assert "probability_positive" in results
        assert "probability_loss" in results

    async def test_monte_carlo_percentiles(self, optimizer, sample_returns_data):
        """Test that Monte Carlo percentiles are ordered."""
        portfolio = {"AAPL": 0.5, "GOOGL": 0.5, "MSFT": 0.0}

        results = await optimizer.monte_carlo_simulation(
            current_portfolio=portfolio,
            returns_data=sample_returns_data,
            num_simulations=1000
        )

        percentiles = results["percentiles"]
        assert percentiles["5th"] <= percentiles["25th"]
        assert percentiles["25th"] <= percentiles["50th"]
        assert percentiles["50th"] <= percentiles["75th"]
        assert percentiles["75th"] <= percentiles["95th"]

    async def test_monte_carlo_probabilities_sum(self, optimizer, sample_returns_data):
        """Test that Monte Carlo probabilities sum to ~1."""
        portfolio = {"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.34}

        results = await optimizer.monte_carlo_simulation(
            current_portfolio=portfolio,
            returns_data=sample_returns_data,
            num_simulations=1000
        )

        prob_positive = results["probability_positive"]
        prob_loss = results["probability_loss"]

        # Probabilities should sum to approximately 1
        assert abs(prob_positive + prob_loss - 1.0) < 0.01

    async def test_optimize_two_assets(self, optimizer):
        """Test optimization with just two assets."""
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
        returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 252),
            'GOOGL': np.random.normal(0.0008, 0.018, 252)
        }, index=dates)

        result = await optimizer.optimize(
            returns_data=returns,
            objective=OptimizationObjective.MAX_SHARPE
        )

        assert len(result.weights) == 2
        assert abs(sum(result.weights.values()) - 1.0) < 0.01

    async def test_optimize_five_assets(self, optimizer):
        """Test optimization with five assets."""
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
        returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, 252),
            'GOOGL': np.random.normal(0.0008, 0.018, 252),
            'MSFT': np.random.normal(0.0009, 0.019, 252),
            'AMZN': np.random.normal(0.0012, 0.025, 252),
            'TSLA': np.random.normal(0.0015, 0.03, 252)
        }, index=dates)

        result = await optimizer.optimize(
            returns_data=returns,
            objective=OptimizationObjective.MIN_VOLATILITY
        )

        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 0.01

    async def test_max_sharpe_vs_min_vol(self, optimizer, sample_returns_data):
        """Test that max Sharpe and min vol give different results."""
        max_sharpe = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MAX_SHARPE
        )

        min_vol = await optimizer.optimize(
            returns_data=sample_returns_data,
            objective=OptimizationObjective.MIN_VOLATILITY
        )

        # These should generally give different portfolios
        # Min vol should have lower volatility
        assert min_vol.volatility <= max_sharpe.volatility + 0.01

    def test_maximize_sharpe_objective(self, optimizer):
        """Test internal Sharpe maximization function."""
        expected_returns = pd.Series([0.10, 0.12, 0.11])
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01, 0.015],
             [0.01, 0.05, 0.02],
             [0.015, 0.02, 0.045]]
        )
        initial_weights = np.array([0.33, 0.33, 0.34])
        bounds = tuple((0, 1) for _ in range(3))
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        result = optimizer._maximize_sharpe(
            initial_weights, expected_returns, cov_matrix, bounds, cons
        )

        assert result.success
        assert len(result.x) == 3
        assert abs(np.sum(result.x) - 1.0) < 0.01

    def test_minimize_volatility_objective(self, optimizer):
        """Test internal volatility minimization function."""
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01, 0.015],
             [0.01, 0.05, 0.02],
             [0.015, 0.02, 0.045]]
        )
        initial_weights = np.array([0.33, 0.33, 0.34])
        bounds = tuple((0, 1) for _ in range(3))
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        result = optimizer._minimize_volatility(
            initial_weights, cov_matrix, bounds, cons
        )

        assert result.success
        assert len(result.x) == 3

    def test_maximize_return_objective(self, optimizer):
        """Test internal return maximization function."""
        expected_returns = pd.Series([0.10, 0.12, 0.11])
        initial_weights = np.array([0.33, 0.33, 0.34])
        bounds = tuple((0, 1) for _ in range(3))
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        result = optimizer._maximize_return(
            initial_weights, expected_returns, bounds, cons
        )

        assert result.success
        # Should allocate to highest return asset
        max_return_idx = expected_returns.argmax()
        assert result.x[max_return_idx] > 0.8  # Most weight to best asset

    def test_risk_parity_objective(self, optimizer):
        """Test internal risk parity function."""
        cov_matrix = pd.DataFrame(
            [[0.04, 0.01, 0.015],
             [0.01, 0.05, 0.02],
             [0.015, 0.02, 0.045]]
        )
        initial_weights = np.array([0.33, 0.33, 0.34])
        bounds = tuple((0, 1) for _ in range(3))
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

        result = optimizer._risk_parity(
            initial_weights, cov_matrix, bounds, cons
        )

        assert result.success
        assert abs(np.sum(result.x) - 1.0) < 0.01


class TestGetPortfolioOptimizer:
    """Test the get_portfolio_optimizer singleton function."""

    def test_get_optimizer_creates_instance(self):
        """Test that get_portfolio_optimizer creates an instance."""
        from app.services import portfolio_optimization
        portfolio_optimization._portfolio_optimizer = None  # Reset

        optimizer = get_portfolio_optimizer()
        assert isinstance(optimizer, PortfolioOptimizer)

    def test_get_optimizer_singleton(self):
        """Test that get_portfolio_optimizer returns same instance."""
        opt1 = get_portfolio_optimizer()
        opt2 = get_portfolio_optimizer()

        assert opt1 is opt2  # Same instance

    def test_get_optimizer_custom_risk_free_rate(self):
        """Test creating optimizer with custom risk-free rate."""
        from app.services import portfolio_optimization
        portfolio_optimization._portfolio_optimizer = None  # Reset

        optimizer = get_portfolio_optimizer(risk_free_rate=0.03)
        assert optimizer.risk_free_rate == 0.03
