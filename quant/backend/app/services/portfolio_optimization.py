"""
Portfolio Optimization Service

Implement Modern Portfolio Theory and other optimization algorithms.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import numpy as np
import pandas as pd
from scipy.optimize import minimize


class OptimizationObjective(str, Enum):
    """Optimization objectives"""
    MAX_SHARPE = "max_sharpe"  # Maximum Sharpe Ratio
    MIN_VOLATILITY = "min_volatility"  # Minimum Volatility
    MAX_RETURN = "max_return"  # Maximum Return
    EFFICIENT_FRONTIER = "efficient_frontier"  # Generate efficient frontier
    RISK_PARITY = "risk_parity"  # Equal risk contribution
    MAX_DIVERSIFICATION = "max_diversification"  # Maximum diversification


class PortfolioConstraints(BaseModel):
    """Portfolio optimization constraints"""
    min_weight: float = 0.0  # Minimum weight per asset
    max_weight: float = 1.0  # Maximum weight per asset
    target_return: Optional[float] = None  # Target return for efficient frontier
    risk_free_rate: float = 0.02  # Annual risk-free rate (2%)
    allow_short: bool = False  # Allow short positions


class OptimizedPortfolio(BaseModel):
    """Optimized portfolio result"""
    weights: Dict[str, float]  # Symbol -> weight
    expected_return: float  # Annual expected return
    volatility: float  # Annual volatility (std dev)
    sharpe_ratio: float  # Sharpe ratio
    sortino_ratio: float  # Sortino ratio
    max_drawdown: float  # Maximum historical drawdown
    var_95: float  # Value at Risk (95% confidence)
    cvar_95: float  # Conditional VaR
    diversification_ratio: float  # Diversification metric
    objective_value: float  # Value of optimization objective


class EfficientFrontier(BaseModel):
    """Efficient frontier data"""
    returns: List[float]
    volatilities: List[float]
    sharpe_ratios: List[float]
    portfolios: List[Dict[str, float]]  # List of weight dictionaries


class PortfolioOptimizer:
    """
    Portfolio optimization using Modern Portfolio Theory

    Implements various optimization strategies:
    - Maximum Sharpe Ratio
    - Minimum Volatility
    - Maximum Return
    - Risk Parity
    - Efficient Frontier generation
    """

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    async def optimize(
        self,
        returns_data: pd.DataFrame,
        objective: OptimizationObjective = OptimizationObjective.MAX_SHARPE,
        constraints: Optional[PortfolioConstraints] = None
    ) -> OptimizedPortfolio:
        """
        Optimize portfolio allocation

        Args:
            returns_data: DataFrame with returns for each asset (columns = symbols)
            objective: Optimization objective
            constraints: Portfolio constraints

        Returns:
            Optimized portfolio with weights and metrics
        """
        if constraints is None:
            constraints = PortfolioConstraints()

        # Calculate expected returns and covariance
        expected_returns = returns_data.mean() * 252  # Annualize
        cov_matrix = returns_data.cov() * 252  # Annualize

        # Number of assets
        num_assets = len(returns_data.columns)

        # Initial guess (equal weight)
        initial_weights = np.array([1.0 / num_assets] * num_assets)

        # Bounds for weights
        if constraints.allow_short:
            bounds = tuple((-1, 1) for _ in range(num_assets))
        else:
            bounds = tuple((constraints.min_weight, constraints.max_weight) for _ in range(num_assets))

        # Constraints
        cons = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1

        # Optimize based on objective
        if objective == OptimizationObjective.MAX_SHARPE:
            result = self._maximize_sharpe(
                initial_weights, expected_returns, cov_matrix, bounds, cons
            )
        elif objective == OptimizationObjective.MIN_VOLATILITY:
            result = self._minimize_volatility(
                initial_weights, cov_matrix, bounds, cons
            )
        elif objective == OptimizationObjective.MAX_RETURN:
            result = self._maximize_return(
                initial_weights, expected_returns, bounds, cons
            )
        elif objective == OptimizationObjective.RISK_PARITY:
            result = self._risk_parity(
                initial_weights, cov_matrix, bounds, cons
            )
        else:
            raise ValueError(f"Unsupported objective: {objective}")

        # Calculate portfolio metrics
        weights = result.x
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol

        # Calculate additional metrics
        portfolio_returns = (returns_data * weights).sum(axis=1)
        sortino_ratio = self._calculate_sortino_ratio(portfolio_returns, self.risk_free_rate)
        max_drawdown = self._calculate_max_drawdown(portfolio_returns)
        var_95, cvar_95 = self._calculate_var_cvar(portfolio_returns, 0.95)
        div_ratio = self._calculate_diversification_ratio(weights, expected_returns, cov_matrix)

        # Create weight dictionary
        weight_dict = {
            symbol: float(weight)
            for symbol, weight in zip(returns_data.columns, weights)
        }

        return OptimizedPortfolio(
            weights=weight_dict,
            expected_return=float(portfolio_return),
            volatility=float(portfolio_vol),
            sharpe_ratio=float(sharpe_ratio),
            sortino_ratio=float(sortino_ratio),
            max_drawdown=float(max_drawdown),
            var_95=float(var_95),
            cvar_95=float(cvar_95),
            diversification_ratio=float(div_ratio),
            objective_value=float(result.fun)
        )

    def _maximize_sharpe(self, initial_weights, expected_returns, cov_matrix, bounds, cons):
        """Maximize Sharpe Ratio"""
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe  # Minimize negative Sharpe

        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        return result

    def _minimize_volatility(self, initial_weights, cov_matrix, bounds, cons):
        """Minimize portfolio volatility"""
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        return result

    def _maximize_return(self, initial_weights, expected_returns, bounds, cons):
        """Maximize portfolio return"""
        def negative_return(weights):
            return -np.dot(weights, expected_returns)

        result = minimize(
            negative_return,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        return result

    def _risk_parity(self, initial_weights, cov_matrix, bounds, cons):
        """Risk parity allocation - equal risk contribution"""
        def risk_parity_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights)
            risk_contrib = weights * marginal_contrib / portfolio_vol
            # Minimize variance of risk contributions
            return np.sum((risk_contrib - risk_contrib.mean()) ** 2)

        result = minimize(
            risk_parity_objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        return result

    async def generate_efficient_frontier(
        self,
        returns_data: pd.DataFrame,
        num_portfolios: int = 50,
        constraints: Optional[PortfolioConstraints] = None
    ) -> EfficientFrontier:
        """
        Generate efficient frontier

        Args:
            returns_data: DataFrame with returns
            num_portfolios: Number of portfolios to generate
            constraints: Portfolio constraints

        Returns:
            Efficient frontier data
        """
        if constraints is None:
            constraints = PortfolioConstraints()

        expected_returns = returns_data.mean() * 252
        cov_matrix = returns_data.cov() * 252

        num_assets = len(returns_data.columns)
        initial_weights = np.array([1.0 / num_assets] * num_assets)

        # Bounds
        if constraints.allow_short:
            bounds = tuple((-1, 1) for _ in range(num_assets))
        else:
            bounds = tuple((constraints.min_weight, constraints.max_weight) for _ in range(num_assets))

        # Find min and max return portfolios
        min_return = expected_returns.min()
        max_return = expected_returns.max()

        # Generate target returns
        target_returns = np.linspace(min_return, max_return, num_portfolios)

        returns_list = []
        vols_list = []
        sharpe_list = []
        portfolios_list = []

        for target_return in target_returns:
            # Constraint: target return
            cons = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return}
            ]

            # Minimize volatility for target return
            def portfolio_volatility(weights):
                return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

            try:
                result = minimize(
                    portfolio_volatility,
                    initial_weights,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=cons,
                    options={'maxiter': 1000}
                )

                if result.success:
                    weights = result.x
                    port_return = np.dot(weights, expected_returns)
                    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                    sharpe = (port_return - self.risk_free_rate) / port_vol

                    returns_list.append(float(port_return))
                    vols_list.append(float(port_vol))
                    sharpe_list.append(float(sharpe))

                    weight_dict = {
                        symbol: float(weight)
                        for symbol, weight in zip(returns_data.columns, weights)
                    }
                    portfolios_list.append(weight_dict)

            except Exception as e:
                print(f"Error optimizing for return {target_return}: {e}")
                continue

        return EfficientFrontier(
            returns=returns_list,
            volatilities=vols_list,
            sharpe_ratios=sharpe_list,
            portfolios=portfolios_list
        )

    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float) -> float:
        """Calculate Sortino Ratio"""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = downside_returns.std()

        if downside_std == 0:
            return 0.0

        sortino = (excess_returns.mean() / downside_std) * np.sqrt(252)
        return float(sortino)

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        return float(abs(max_dd))

    def _calculate_var_cvar(self, returns: pd.Series, confidence: float) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional VaR"""
        sorted_returns = returns.sort_values()
        index = int((1 - confidence) * len(sorted_returns))

        var = abs(sorted_returns.iloc[index])
        cvar = abs(sorted_returns.iloc[:index].mean())

        return float(var), float(cvar)

    def _calculate_diversification_ratio(
        self,
        weights: np.ndarray,
        expected_returns: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> float:
        """Calculate diversification ratio"""
        # Weighted average volatility
        individual_vols = np.sqrt(np.diag(cov_matrix))
        weighted_vol_sum = np.dot(weights, individual_vols)

        # Portfolio volatility
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        if portfolio_vol == 0:
            return 1.0

        div_ratio = weighted_vol_sum / portfolio_vol
        return float(div_ratio)

    async def monte_carlo_simulation(
        self,
        current_portfolio: Dict[str, float],
        returns_data: pd.DataFrame,
        num_simulations: int = 10000,
        time_horizon_days: int = 252
    ) -> Dict:
        """
        Monte Carlo simulation for portfolio performance

        Args:
            current_portfolio: Current portfolio weights
            returns_data: Historical returns data
            num_simulations: Number of simulations
            time_horizon_days: Time horizon in days

        Returns:
            Simulation results with confidence intervals
        """
        # Calculate portfolio returns
        weights = np.array([current_portfolio.get(symbol, 0) for symbol in returns_data.columns])
        portfolio_returns = (returns_data * weights).sum(axis=1)

        # Mean and std of portfolio returns
        mean_return = portfolio_returns.mean()
        std_return = portfolio_returns.std()

        # Run simulations
        simulations = np.random.normal(
            mean_return,
            std_return,
            (num_simulations, time_horizon_days)
        )

        # Calculate cumulative returns
        cumulative_returns = (1 + simulations).cumprod(axis=1)
        final_values = cumulative_returns[:, -1]

        # Calculate statistics
        percentiles = np.percentile(final_values, [5, 25, 50, 75, 95])

        return {
            "num_simulations": num_simulations,
            "time_horizon_days": time_horizon_days,
            "expected_return": float(np.mean(final_values) - 1),
            "median_return": float(percentiles[2] - 1),
            "std_deviation": float(np.std(final_values)),
            "percentiles": {
                "5th": float(percentiles[0] - 1),
                "25th": float(percentiles[1] - 1),
                "50th": float(percentiles[2] - 1),
                "75th": float(percentiles[3] - 1),
                "95th": float(percentiles[4] - 1)
            },
            "probability_positive": float(np.sum(final_values > 1) / num_simulations),
            "probability_loss": float(np.sum(final_values < 1) / num_simulations)
        }


# Global instance
_portfolio_optimizer: Optional[PortfolioOptimizer] = None


def get_portfolio_optimizer(risk_free_rate: float = 0.02) -> PortfolioOptimizer:
    """Get or create portfolio optimizer instance"""
    global _portfolio_optimizer
    if _portfolio_optimizer is None:
        _portfolio_optimizer = PortfolioOptimizer(risk_free_rate)
    return _portfolio_optimizer
