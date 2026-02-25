"""
Portfolio Optimization API Endpoints

Optimize portfolio allocation using Modern Portfolio Theory.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.services.portfolio_optimization import (
    PortfolioOptimizer,
    OptimizationObjective,
    PortfolioConstraints,
    OptimizedPortfolio,
    EfficientFrontier,
    get_portfolio_optimizer
)
from app.services.market_data import get_market_data_provider, Interval
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class OptimizeRequest(BaseModel):
    """Request model for portfolio optimization"""
    symbols: List[str]
    objective: OptimizationObjective = OptimizationObjective.MAX_SHARPE
    lookback_days: int = 252  # 1 year
    constraints: Optional[PortfolioConstraints] = None


class EfficientFrontierRequest(BaseModel):
    """Request model for efficient frontier"""
    symbols: List[str]
    num_portfolios: int = 50
    lookback_days: int = 252
    constraints: Optional[PortfolioConstraints] = None


class MonteCarloRequest(BaseModel):
    """Request model for Monte Carlo simulation"""
    portfolio: Dict[str, float]  # Symbol -> weight
    num_simulations: int = 10000
    time_horizon_days: int = 252
    lookback_days: int = 252


@router.post("/optimize", response_model=OptimizedPortfolio)
async def optimize_portfolio(
    request: OptimizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize portfolio allocation

    Uses Modern Portfolio Theory to find optimal weights based on:
    - Maximum Sharpe Ratio
    - Minimum Volatility
    - Maximum Return
    - Risk Parity

    Returns optimized weights and comprehensive risk metrics
    """
    if len(request.symbols) < 2:
        raise HTTPException(
            status_code=400,
            detail="Minimum 2 symbols required for optimization"
        )

    if len(request.symbols) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 symbols allowed"
        )

    # Fetch historical data
    data_provider = get_market_data_provider()
    optimizer = get_portfolio_optimizer()

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=request.lookback_days)

    try:
        # Get historical data for all symbols
        import pandas as pd
        returns_dict = {}

        for symbol in request.symbols:
            bars = await data_provider.get_historical_data(
                symbol.upper(),
                start_date,
                end_date,
                Interval.DAY_1
            )

            if not bars:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for symbol: {symbol}"
                )

            # Calculate returns
            prices = [bar.close for bar in bars]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            returns_dict[symbol.upper()] = returns

        # Create DataFrame
        returns_df = pd.DataFrame(returns_dict)

        # Optimize
        result = await optimizer.optimize(
            returns_df,
            objective=request.objective,
            constraints=request.constraints
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/efficient-frontier", response_model=EfficientFrontier)
async def generate_efficient_frontier(
    request: EfficientFrontierRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate efficient frontier

    Returns a series of optimal portfolios along the efficient frontier,
    showing the trade-off between risk and return
    """
    if len(request.symbols) < 2:
        raise HTTPException(
            status_code=400,
            detail="Minimum 2 symbols required"
        )

    # Fetch historical data
    data_provider = get_market_data_provider()
    optimizer = get_portfolio_optimizer()

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=request.lookback_days)

    try:
        import pandas as pd
        returns_dict = {}

        for symbol in request.symbols:
            bars = await data_provider.get_historical_data(
                symbol.upper(),
                start_date,
                end_date,
                Interval.DAY_1
            )

            prices = [bar.close for bar in bars]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            returns_dict[symbol.upper()] = returns

        returns_df = pd.DataFrame(returns_dict)

        # Generate frontier
        frontier = await optimizer.generate_efficient_frontier(
            returns_df,
            num_portfolios=request.num_portfolios,
            constraints=request.constraints
        )

        return frontier

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate efficient frontier: {str(e)}"
        )


@router.post("/monte-carlo")
async def run_monte_carlo(
    request: MonteCarloRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run Monte Carlo simulation

    Simulates portfolio performance over time using historical returns
    to estimate probability distributions of outcomes
    """
    if not request.portfolio:
        raise HTTPException(
            status_code=400,
            detail="Portfolio weights required"
        )

    # Validate weights sum to 1
    total_weight = sum(request.portfolio.values())
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Portfolio weights must sum to 1.0 (current: {total_weight})"
        )

    # Fetch historical data
    data_provider = get_market_data_provider()
    optimizer = get_portfolio_optimizer()

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=request.lookback_days)

    try:
        import pandas as pd
        returns_dict = {}

        for symbol in request.portfolio.keys():
            bars = await data_provider.get_historical_data(
                symbol.upper(),
                start_date,
                end_date,
                Interval.DAY_1
            )

            prices = [bar.close for bar in bars]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            returns_dict[symbol.upper()] = returns

        returns_df = pd.DataFrame(returns_dict)

        # Run simulation
        results = await optimizer.monte_carlo_simulation(
            current_portfolio=request.portfolio,
            returns_data=returns_df,
            num_simulations=request.num_simulations,
            time_horizon_days=request.time_horizon_days
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Monte Carlo simulation failed: {str(e)}"
        )


@router.get("/analyze")
async def analyze_portfolio(
    symbols: List[str] = Query(...),
    weights: List[float] = Query(...),
    lookback_days: int = Query(default=252),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze existing portfolio

    Returns comprehensive metrics for a given portfolio allocation
    """
    if len(symbols) != len(weights):
        raise HTTPException(
            status_code=400,
            detail="Number of symbols must match number of weights"
        )

    total_weight = sum(weights)
    if abs(total_weight - 1.0) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to 1.0 (current: {total_weight})"
        )

    # Create portfolio dict
    portfolio = {sym.upper(): weight for sym, weight in zip(symbols, weights)}

    # Fetch historical data
    data_provider = get_market_data_provider()
    optimizer = get_portfolio_optimizer()

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=lookback_days)

    try:
        import pandas as pd
        import numpy as np
        returns_dict = {}

        for symbol in symbols:
            bars = await data_provider.get_historical_data(
                symbol.upper(),
                start_date,
                end_date,
                Interval.DAY_1
            )

            prices = [bar.close for bar in bars]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            returns_dict[symbol.upper()] = returns

        returns_df = pd.DataFrame(returns_dict)

        # Calculate metrics
        expected_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252

        weights_array = np.array(weights)
        portfolio_return = np.dot(weights_array, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights_array.T, np.dot(cov_matrix, weights_array)))
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_vol

        # Portfolio returns series
        portfolio_returns = (returns_df * weights_array).sum(axis=1)

        # Calculate Sortino
        excess_returns = portfolio_returns - 0.02 / 252
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = downside_returns.std()
        sortino = (excess_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Max drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = abs(drawdown.min())

        return {
            "portfolio": portfolio,
            "metrics": {
                "expected_return": float(portfolio_return),
                "volatility": float(portfolio_vol),
                "sharpe_ratio": float(sharpe_ratio),
                "sortino_ratio": float(sortino),
                "max_drawdown": float(max_dd)
            },
            "lookback_days": lookback_days
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analysis failed: {str(e)}"
        )


@router.get("/rebalance")
async def suggest_rebalancing(
    current_symbols: List[str] = Query(...),
    current_weights: List[float] = Query(...),
    target_objective: OptimizationObjective = Query(default=OptimizationObjective.MAX_SHARPE),
    current_user: User = Depends(get_current_user)
):
    """
    Suggest portfolio rebalancing

    Compares current allocation to optimal and suggests rebalancing trades
    """
    if len(current_symbols) != len(current_weights):
        raise HTTPException(
            status_code=400,
            detail="Symbols and weights must have same length"
        )

    # Get optimal portfolio
    optimize_req = OptimizeRequest(
        symbols=current_symbols,
        objective=target_objective
    )

    optimal = await optimize_portfolio(optimize_req, current_user)

    # Calculate differences
    rebalancing = []
    for symbol, current_weight in zip(current_symbols, current_weights):
        optimal_weight = optimal.weights.get(symbol.upper(), 0)
        difference = optimal_weight - current_weight

        if abs(difference) > 0.01:  # 1% threshold
            rebalancing.append({
                "symbol": symbol.upper(),
                "current_weight": current_weight,
                "target_weight": optimal_weight,
                "difference": difference,
                "action": "increase" if difference > 0 else "decrease"
            })

    return {
        "current_portfolio": {sym: w for sym, w in zip(current_symbols, current_weights)},
        "optimal_portfolio": optimal.weights,
        "rebalancing_needed": len(rebalancing) > 0,
        "trades": rebalancing,
        "expected_improvement": {
            "sharpe_ratio": optimal.sharpe_ratio
        }
    }
