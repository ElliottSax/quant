"""
Portfolio Backtesting API Endpoints

Multi-asset portfolio backtesting with optimization and rebalancing
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
import yfinance as yf

from app.services.portfolio_backtesting import (
    PortfolioBacktestEngine,
    PortfolioBacktestResult,
    RebalanceFrequency,
    OptimizationMethod
)


router = APIRouter(prefix="/backtesting/portfolio", tags=["portfolio-backtesting"])


class PortfolioBacktestRequest(BaseModel):
    """Request model for portfolio backtest"""
    symbols: List[str] = Field(..., min_items=2, max_items=20, description="List of ticker symbols (2-20)")
    start_date: datetime
    end_date: datetime
    weights: Optional[Dict[str, float]] = None  # Custom weights (default: equal or optimized)
    optimization_method: OptimizationMethod = OptimizationMethod.EQUAL_WEIGHT
    initial_capital: float = Field(100000, gt=1000, description="Initial capital ($1000-$10M)")
    commission: float = Field(0.001, ge=0, le=0.05, description="Commission rate (0-5%)")
    slippage: float = Field(0.0005, ge=0, le=0.01, description="Slippage rate (0-1%)")
    rebalance_frequency: RebalanceFrequency = RebalanceFrequency.MONTHLY
    rebalance_threshold: float = Field(0.05, ge=0, le=0.5, description="Drift threshold (0-50%)")
    benchmark_symbol: str = "SPY"


class EfficientFrontierRequest(BaseModel):
    """Request for efficient frontier calculation"""
    symbols: List[str] = Field(..., min_items=2, max_items=20)
    start_date: datetime
    end_date: datetime
    num_portfolios: int = Field(100, ge=10, le=1000, description="Number of portfolios to generate")


@router.post("/demo/run", response_model=PortfolioBacktestResult)
async def run_portfolio_backtest_demo(request: PortfolioBacktestRequest):
    """
    Run portfolio backtest - DEMO MODE (no auth required)

    Features:
    - Multiple asset support (2-20 symbols)
    - Portfolio optimization (equal weight, min variance, max Sharpe, risk parity)
    - Automatic rebalancing
    - Correlation analysis
    - Efficient frontier

    Demo Limitations:
    - Maximum 1 year backtest
    - Limited to major US stocks
    - Rate limited
    """
    # Demo restrictions
    duration = (request.end_date - request.start_date).days
    if duration > 365:
        raise HTTPException(
            status_code=400,
            detail="Demo mode limited to 1 year. Upgrade for longer backtests."
        )

    # Validate symbols count
    if len(request.symbols) < 2:
        raise HTTPException(
            status_code=400,
            detail="Portfolio requires at least 2 symbols"
        )

    if len(request.symbols) > 20:
        raise HTTPException(
            status_code=400,
            detail="Demo mode limited to 20 symbols. Upgrade for larger portfolios."
        )

    # Validate dates
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    # Validate custom weights if provided
    if request.weights:
        if set(request.weights.keys()) != set(request.symbols):
            raise HTTPException(
                status_code=400,
                detail="Weights must be provided for all symbols"
            )

        weight_sum = sum(request.weights.values())
        if not (0.99 <= weight_sum <= 1.01):
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 1.0 (current: {weight_sum:.2f})"
            )

    # Fetch historical data for all symbols
    price_data = {}
    failed_symbols = []

    for symbol in request.symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=request.start_date,
                end=request.end_date,
                interval='1d'
            )

            if df.empty:
                failed_symbols.append(symbol)
            else:
                price_data[symbol] = df
        except Exception as e:
            failed_symbols.append(symbol)

    if failed_symbols:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbols: {', '.join(failed_symbols)}"
        )

    if not price_data:
        raise HTTPException(
            status_code=404,
            detail="No historical data found for any symbols"
        )

    # Create portfolio backtest engine
    engine = PortfolioBacktestEngine(
        initial_capital=request.initial_capital,
        commission=request.commission,
        slippage=request.slippage,
        rebalance_frequency=request.rebalance_frequency,
        rebalance_threshold=request.rebalance_threshold
    )

    # Run portfolio backtest
    try:
        result = await engine.run_portfolio_backtest(
            symbols=request.symbols,
            price_data=price_data,
            weights=request.weights,
            optimization_method=request.optimization_method,
            benchmark_symbol=request.benchmark_symbol
        )

        # Add efficient frontier if optimization was used
        if request.optimization_method != OptimizationMethod.CUSTOM:
            try:
                frontier = await engine.calculate_efficient_frontier(
                    price_data=price_data,
                    symbols=request.symbols,
                    num_portfolios=50
                )
                result.efficient_frontier = frontier
            except Exception:
                # Skip efficient frontier if calculation fails
                pass

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio backtest failed: {str(e)}"
        )


@router.post("/demo/efficient-frontier")
async def calculate_efficient_frontier_demo(request: EfficientFrontierRequest):
    """
    Calculate efficient frontier - DEMO MODE

    Returns set of optimal portfolios with varying risk/return profiles.
    Useful for portfolio optimization visualization.
    """
    # Demo restrictions
    duration = (request.end_date - request.start_date).days
    if duration > 365:
        raise HTTPException(
            status_code=400,
            detail="Demo mode limited to 1 year"
        )

    if len(request.symbols) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 symbols for efficient frontier"
        )

    # Fetch price data
    price_data = {}
    for symbol in request.symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=request.start_date,
                end=request.end_date,
                interval='1d'
            )
            if not df.empty:
                price_data[symbol] = df
        except Exception:
            pass

    if len(price_data) < 2:
        raise HTTPException(
            status_code=404,
            detail="Need data for at least 2 symbols"
        )

    # Calculate efficient frontier
    engine = PortfolioBacktestEngine()

    try:
        frontier = await engine.calculate_efficient_frontier(
            price_data=price_data,
            symbols=list(price_data.keys()),
            num_portfolios=request.num_portfolios
        )

        return {
            "symbols": list(price_data.keys()),
            "num_portfolios": len(frontier),
            "frontier": frontier,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Efficient frontier calculation failed: {str(e)}"
        )


@router.get("/demo/optimization-methods")
async def list_optimization_methods():
    """
    List available portfolio optimization methods

    Returns description of each optimization method.
    """
    return {
        "methods": [
            {
                "name": OptimizationMethod.EQUAL_WEIGHT,
                "title": "Equal Weight",
                "description": "Allocates equal weight to each asset (1/N)",
                "pros": "Simple, diversified, low turnover",
                "cons": "Ignores risk and return differences",
                "best_for": "Beginners, passive portfolios"
            },
            {
                "name": OptimizationMethod.MIN_VARIANCE,
                "title": "Minimum Variance",
                "description": "Minimizes portfolio volatility",
                "pros": "Lowest risk, stable returns",
                "cons": "May underperform in bull markets",
                "best_for": "Risk-averse investors, volatile markets"
            },
            {
                "name": OptimizationMethod.MAX_SHARPE,
                "title": "Maximum Sharpe Ratio",
                "description": "Maximizes risk-adjusted returns",
                "pros": "Optimal risk/return tradeoff",
                "cons": "Sensitive to estimation errors",
                "best_for": "Balanced portfolios, long-term investing"
            },
            {
                "name": OptimizationMethod.RISK_PARITY,
                "title": "Risk Parity",
                "description": "Equal risk contribution from each asset",
                "pros": "Balanced risk, robust",
                "cons": "May require leverage",
                "best_for": "Institutional portfolios, diversification"
            },
            {
                "name": OptimizationMethod.CUSTOM,
                "title": "Custom Weights",
                "description": "User-defined portfolio weights",
                "pros": "Full control, tactical allocation",
                "cons": "Requires expertise",
                "best_for": "Experienced investors, specific strategies"
            }
        ]
    }


@router.get("/demo/rebalance-frequencies")
async def list_rebalance_frequencies():
    """
    List available rebalancing frequencies

    Returns description of each rebalancing option.
    """
    return {
        "frequencies": [
            {
                "name": RebalanceFrequency.DAILY,
                "description": "Rebalance every trading day",
                "turnover": "Very High",
                "costs": "High transaction costs",
                "best_for": "Algorithmic strategies, high-frequency trading"
            },
            {
                "name": RebalanceFrequency.WEEKLY,
                "description": "Rebalance weekly (every 7 days)",
                "turnover": "High",
                "costs": "Moderate transaction costs",
                "best_for": "Active management, tactical allocation"
            },
            {
                "name": RebalanceFrequency.MONTHLY,
                "description": "Rebalance monthly (every 30 days)",
                "turnover": "Moderate",
                "costs": "Low transaction costs",
                "best_for": "Most portfolios, balanced approach (recommended)"
            },
            {
                "name": RebalanceFrequency.QUARTERLY,
                "description": "Rebalance quarterly (every 90 days)",
                "turnover": "Low",
                "costs": "Very low transaction costs",
                "best_for": "Long-term investors, passive strategies"
            },
            {
                "name": RebalanceFrequency.NEVER,
                "description": "Buy and hold (no rebalancing)",
                "turnover": "Zero",
                "costs": "Minimal transaction costs",
                "best_for": "True passive investing, long-term holders"
            }
        ]
    }
