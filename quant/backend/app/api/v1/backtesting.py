"""
Backtesting API Endpoints

Test trading strategies on historical data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import pandas as pd

from app.services.backtesting import (
    BacktestEngine,
    BacktestResult
)
from app.services.strategies import STRATEGY_REGISTRY, get_strategy, get_strategies_by_tier
from app.services.market_data import MarketDataProvider, DataProvider, Interval
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/backtesting", tags=["backtesting"])


class BacktestRequest(BaseModel):
    """Request model for backtest"""
    symbol: str
    start_date: datetime
    end_date: datetime
    strategy: str  # Strategy name
    strategy_params: Dict = {}
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005


class PriceBar(BaseModel):
    """Price bar data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class StrategyInfo(BaseModel):
    """Strategy information"""
    name: str
    description: str
    parameters: Dict
    category: str


@router.post("/run", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run backtest with specified strategy

    Simulates trading strategy on historical data and returns
    comprehensive performance metrics including:
    - Returns (total, annual, risk-adjusted)
    - Drawdown analysis
    - Trade statistics
    - Equity curve
    """
    # Validate dates
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    duration = (request.end_date - request.start_date).days
    if duration > 3650:  # 10 years
        raise HTTPException(
            status_code=400,
            detail="Maximum backtest duration is 10 years"
        )

    # Create backtest engine
    engine = BacktestEngine(
        initial_capital=request.initial_capital,
        commission=request.commission,
        slippage=request.slippage
    )

    # Get strategy function from registry
    strategy_info = get_strategy(request.strategy)
    if not strategy_info:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown strategy: {request.strategy}"
        )

    # Check user subscription tier (placeholder - implement real subscription check)
    user_tier = 'free'  # TODO: Get from current_user.subscription_tier
    strategy_tier = strategy_info['tier']

    # Verify access
    tier_hierarchy = {'free': 0, 'premium': 1, 'enterprise': 2}
    if tier_hierarchy.get(user_tier, 0) < tier_hierarchy.get(strategy_tier, 0):
        raise HTTPException(
            status_code=403,
            detail=f"Strategy '{request.strategy}' requires {strategy_tier} subscription"
        )

    strategy_func = strategy_info['function']

    # Fetch historical data (placeholder - integrate with data provider)
    price_data = await _fetch_historical_data(
        request.symbol,
        request.start_date,
        request.end_date
    )

    if price_data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data found for {request.symbol}"
        )

    # Run backtest
    try:
        result = await engine.run_backtest(
            symbol=request.symbol,
            price_data=price_data,
            strategy=strategy_func,
            **request.strategy_params
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest execution failed: {str(e)}"
        )


@router.get("/strategies", response_model=List[StrategyInfo])
async def list_strategies(
    tier: Optional[str] = Query(None, description="Filter by subscription tier"),
    current_user: User = Depends(get_current_user)
):
    """
    List available trading strategies

    Returns strategies based on user's subscription tier.
    Query parameter 'tier' can override for preview purposes.
    """
    # Get user's tier (placeholder)
    user_tier = tier or 'free'  # TODO: Get from current_user.subscription_tier

    # Get strategies for this tier
    available_strategies = get_strategies_by_tier(user_tier)

    # Convert to response format
    strategies = []
    for name, info in available_strategies.items():
        # Get strategy parameters from function signature
        # Simplified version - could introspect function for exact params
        parameters = _get_strategy_parameters(name)

        strategies.append(StrategyInfo(
            name=name,
            description=f"{info['description']} [{info['tier'].upper()}]",
            parameters=parameters,
            category=info['category']
        ))

    return strategies


@router.post("/optimize")
async def optimize_strategy(
    symbol: str,
    strategy: str,
    start_date: datetime,
    end_date: datetime,
    parameters_range: Dict,
    optimization_metric: str = "sharpe_ratio",
    current_user: User = Depends(get_current_user)
):
    """
    Optimize strategy parameters

    Runs multiple backtests with different parameter combinations
    to find optimal settings based on specified metric

    Example parameters_range:
    {
        "fast_period": [10, 15, 20, 25, 30],
        "slow_period": [40, 50, 60, 70]
    }
    """
    # This would run parameter grid search
    # Placeholder for now
    return {
        "symbol": symbol,
        "strategy": strategy,
        "optimization_metric": optimization_metric,
        "best_parameters": {},
        "best_score": 0.0,
        "total_combinations": 0,
        "message": "Strategy optimization coming soon"
    }


@router.post("/walk-forward")
async def walk_forward_analysis(
    symbol: str,
    strategy: str,
    start_date: datetime,
    end_date: datetime,
    in_sample_ratio: float = 0.7,
    num_splits: int = 5,
    current_user: User = Depends(get_current_user)
):
    """
    Walk-forward analysis

    Performs rolling window backtesting:
    1. Optimize on in-sample period
    2. Test on out-of-sample period
    3. Roll forward and repeat

    Helps validate strategy robustness and prevent overfitting
    """
    return {
        "symbol": symbol,
        "strategy": strategy,
        "num_splits": num_splits,
        "results": [],
        "message": "Walk-forward analysis coming soon"
    }


@router.get("/compare")
async def compare_strategies(
    symbol: str,
    strategies: List[str] = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user)
):
    """
    Compare multiple strategies

    Runs backtests for multiple strategies on the same data
    and returns comparative metrics
    """
    return {
        "symbol": symbol,
        "strategies": strategies,
        "comparison": [],
        "message": "Strategy comparison coming soon"
    }


@router.post("/monte-carlo")
async def monte_carlo_simulation(
    backtest_result: BacktestResult,
    num_simulations: int = 1000,
    confidence_level: float = 0.95,
    current_user: User = Depends(get_current_user)
):
    """
    Monte Carlo simulation on backtest results

    Generates multiple random scenarios based on backtest returns
    to estimate probability distributions of outcomes
    """
    return {
        "num_simulations": num_simulations,
        "confidence_level": confidence_level,
        "expected_return": 0.0,
        "value_at_risk": 0.0,
        "probability_of_loss": 0.0,
        "message": "Monte Carlo simulation coming soon"
    }


# Helper functions

def _get_strategy_parameters(strategy_name: str) -> Dict:
    """Get default parameters for a strategy"""
    # Parameter definitions for each strategy
    params_map = {
        'ma_crossover': {
            "fast_period": {"type": "int", "default": 20, "description": "Fast MA period"},
            "slow_period": {"type": "int", "default": 50, "description": "Slow MA period"}
        },
        'rsi': {
            "rsi_period": {"type": "int", "default": 14, "description": "RSI period"},
            "oversold": {"type": "float", "default": 30, "description": "Oversold threshold"},
            "overbought": {"type": "float", "default": 70, "description": "Overbought threshold"}
        },
        'bollinger_breakout': {
            "period": {"type": "int", "default": 20, "description": "BB period"},
            "std_dev": {"type": "float", "default": 2.0, "description": "Standard deviations"}
        },
        'macd': {
            "fast_period": {"type": "int", "default": 12, "description": "Fast EMA"},
            "slow_period": {"type": "int", "default": 26, "description": "Slow EMA"},
            "signal_period": {"type": "int", "default": 9, "description": "Signal line"}
        },
        'mean_reversion_zscore': {
            "lookback": {"type": "int", "default": 20, "description": "Lookback period"},
            "entry_threshold": {"type": "float", "default": 2.0, "description": "Entry Z-score"},
            "exit_threshold": {"type": "float", "default": 0.5, "description": "Exit Z-score"}
        },
        'momentum': {
            "lookback": {"type": "int", "default": 20, "description": "Momentum period"},
            "momentum_threshold": {"type": "float", "default": 0.05, "description": "Min momentum %"}
        },
        'triple_ema': {
            "short_period": {"type": "int", "default": 8, "description": "Short EMA"},
            "medium_period": {"type": "int", "default": 21, "description": "Medium EMA"},
            "long_period": {"type": "int", "default": 55, "description": "Long EMA"}
        },
        'ichimoku_cloud': {
            "conversion_period": {"type": "int", "default": 9, "description": "Conversion line"},
            "base_period": {"type": "int", "default": 26, "description": "Base line"},
            "span_b_period": {"type": "int", "default": 52, "description": "Span B"},
            "displacement": {"type": "int", "default": 26, "description": "Displacement"}
        },
        'multi_timeframe': {
            "short_ma": {"type": "int", "default": 20, "description": "Short MA"},
            "long_ma": {"type": "int", "default": 50, "description": "Long MA"},
            "higher_tf_ma": {"type": "int", "default": 200, "description": "Higher TF MA"}
        },
        'volatility_breakout_atr': {
            "atr_period": {"type": "int", "default": 14, "description": "ATR period"},
            "breakout_multiplier": {"type": "float", "default": 2.0, "description": "Breakout ATR multiplier"}
        },
    }
    return params_map.get(strategy_name, {})


async def _fetch_historical_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """
    Fetch historical price data from Yahoo Finance with fallback to mock data

    Uses MarketDataProvider with Yahoo Finance as primary source.
    Falls back to mock data if Yahoo Finance is unavailable.
    """
    # Initialize market data provider (Yahoo Finance free tier)
    provider = MarketDataProvider(provider=DataProvider.YAHOO_FINANCE)

    try:
        # Fetch real historical data
        bars = await provider.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=Interval.DAY_1
        )

        if not bars:
            raise ValueError(f"No data returned for {symbol}")

        # Convert to DataFrame
        data = {
            'timestamp': [bar.timestamp for bar in bars],
            'open': [bar.open for bar in bars],
            'high': [bar.high for bar in bars],
            'low': [bar.low for bar in bars],
            'close': [bar.close for bar in bars],
            'volume': [bar.volume for bar in bars],
        }

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    except Exception as e:
        # Log error and use mock data for testing
        import logging
        logging.warning(f"Failed to fetch real data for {symbol}: {e}. Using mock data for testing.")

        # Generate synthetic data for testing
        import numpy as np
        num_days = (end_date - start_date).days
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        np.random.seed(hash(symbol) % (2**32))  # Deterministic but symbol-specific
        price_base = 100
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = price_base * np.exp(np.cumsum(returns))

        data = {
            'timestamp': dates,
            'open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
            'high': prices * (1 + np.random.uniform(0.0, 0.02, len(dates))),
            'low': prices * (1 + np.random.uniform(-0.02, 0.0, len(dates))),
            'close': prices,
            'volume': np.random.uniform(1e6, 5e6, len(dates))
        }

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    finally:
        await provider.close()
