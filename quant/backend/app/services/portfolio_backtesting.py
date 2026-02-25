"""
Portfolio-Level Backtesting Engine

Supports multi-asset backtesting with:
- Multiple symbols with custom weights
- Portfolio optimization (efficient frontier)
- Correlation analysis
- Rebalancing strategies
- Portfolio-level metrics
"""

from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from pydantic import BaseModel


class RebalanceFrequency(str, Enum):
    """Portfolio rebalancing frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    NEVER = "never"


class OptimizationMethod(str, Enum):
    """Portfolio optimization method"""
    EQUAL_WEIGHT = "equal_weight"
    MARKET_CAP = "market_cap"
    MIN_VARIANCE = "min_variance"
    MAX_SHARPE = "max_sharpe"
    RISK_PARITY = "risk_parity"
    CUSTOM = "custom"


@dataclass
class PortfolioAllocation:
    """Portfolio allocation at a point in time"""
    timestamp: datetime
    weights: Dict[str, float]  # symbol -> weight
    values: Dict[str, float]   # symbol -> dollar value
    total_value: float


@dataclass
class PortfolioTrade:
    """Portfolio rebalancing trade"""
    timestamp: datetime
    symbol: str
    action: str  # "BUY" or "SELL"
    shares: float
    price: float
    value: float
    commission: float
    reason: str  # "initial" | "rebalance" | "signal"


class PortfolioMetrics(BaseModel):
    """Portfolio performance metrics"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float

    # Portfolio-specific metrics
    avg_correlation: float
    diversification_ratio: float
    turnover: float  # Annual portfolio turnover
    num_rebalances: int

    # Component analysis
    best_asset: str
    worst_asset: str
    asset_contributions: Dict[str, float]  # symbol -> return contribution


class PortfolioBacktestResult(BaseModel):
    """Portfolio backtest result"""
    symbol_list: List[str]
    start_date: datetime
    end_date: datetime
    duration_days: int
    initial_capital: float
    final_value: float

    # Performance
    metrics: PortfolioMetrics

    # Time series data
    equity_curve: List[Dict]  # [{timestamp, portfolio_value, benchmark_value, drawdown}]
    allocations: List[Dict]   # [{timestamp, weights: {symbol: weight}}]
    trades: List[PortfolioTrade]

    # Correlation & diversification
    correlation_matrix: Dict[str, Dict[str, float]]

    # Individual asset performance
    individual_returns: Dict[str, float]  # symbol -> total return

    # Optimization data (if applicable)
    efficient_frontier: Optional[List[Dict]] = None  # [{risk, return, weights}]

    class Config:
        arbitrary_types_allowed = True


class PortfolioBacktestEngine:
    """
    Multi-asset portfolio backtesting engine

    Features:
    - Multiple asset support with custom weights
    - Automatic rebalancing (periodic or threshold-based)
    - Portfolio optimization
    - Correlation analysis
    - Transaction costs and slippage
    """

    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 0.1% per trade
        slippage: float = 0.0005,   # 0.05% slippage
        rebalance_frequency: RebalanceFrequency = RebalanceFrequency.MONTHLY,
        rebalance_threshold: float = 0.05,  # 5% drift triggers rebalance
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.rebalance_frequency = rebalance_frequency
        self.rebalance_threshold = rebalance_threshold

    async def run_portfolio_backtest(
        self,
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],  # symbol -> price DataFrame
        weights: Optional[Dict[str, float]] = None,  # symbol -> weight (default: equal)
        optimization_method: OptimizationMethod = OptimizationMethod.EQUAL_WEIGHT,
        benchmark_symbol: str = "SPY",
    ) -> PortfolioBacktestResult:
        """
        Run portfolio backtest with multiple assets

        Args:
            symbols: List of ticker symbols
            price_data: Dictionary mapping symbols to price DataFrames
            weights: Optional custom weights (default: equal weight)
            optimization_method: Portfolio optimization method
            benchmark_symbol: Benchmark for comparison (default: SPY)
        """
        # Validate inputs
        if not symbols:
            raise ValueError("Must provide at least one symbol")

        for symbol in symbols:
            if symbol not in price_data:
                raise ValueError(f"Price data missing for {symbol}")

        # Align all price data to common date range
        aligned_data = self._align_price_data(price_data, symbols)

        if aligned_data.empty:
            raise ValueError("No overlapping price data found")

        # Calculate initial weights
        if weights is None:
            if optimization_method == OptimizationMethod.EQUAL_WEIGHT:
                weights = {symbol: 1.0 / len(symbols) for symbol in symbols}
            else:
                weights = await self._optimize_weights(
                    aligned_data, symbols, optimization_method
                )

        # Validate weights sum to 1.0
        weight_sum = sum(weights.values())
        if not np.isclose(weight_sum, 1.0, atol=0.01):
            # Normalize weights
            weights = {k: v / weight_sum for k, v in weights.items()}

        # Run backtest simulation
        result = await self._simulate_portfolio(
            symbols=symbols,
            price_data=aligned_data,
            initial_weights=weights,
            benchmark_symbol=benchmark_symbol,
        )

        return result

    def _align_price_data(
        self,
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str]
    ) -> pd.DataFrame:
        """Align all price data to common date range and merge"""
        # Ensure all DataFrames have 'close' column
        dfs = []
        for symbol in symbols:
            df = price_data[symbol].copy()
            if 'close' not in df.columns:
                if 'Close' in df.columns:
                    df['close'] = df['Close']
                else:
                    raise ValueError(f"No close price found for {symbol}")

            # Select only close price and rename
            df = df[['close']].copy()
            df.columns = [symbol]
            dfs.append(df)

        # Merge all DataFrames on date index
        aligned = pd.concat(dfs, axis=1, join='inner')
        aligned = aligned.dropna()  # Remove any rows with missing data

        return aligned

    async def _optimize_weights(
        self,
        price_data: pd.DataFrame,
        symbols: List[str],
        method: OptimizationMethod,
    ) -> Dict[str, float]:
        """Calculate optimal portfolio weights"""

        if method == OptimizationMethod.EQUAL_WEIGHT:
            return {symbol: 1.0 / len(symbols) for symbol in symbols}

        # Calculate returns
        returns = price_data.pct_change().dropna()

        if method == OptimizationMethod.MIN_VARIANCE:
            return self._min_variance_weights(returns, symbols)

        elif method == OptimizationMethod.MAX_SHARPE:
            return self._max_sharpe_weights(returns, symbols)

        elif method == OptimizationMethod.RISK_PARITY:
            return self._risk_parity_weights(returns, symbols)

        else:
            # Default to equal weight
            return {symbol: 1.0 / len(symbols) for symbol in symbols}

    def _min_variance_weights(
        self,
        returns: pd.DataFrame,
        symbols: List[str]
    ) -> Dict[str, float]:
        """Calculate minimum variance portfolio weights"""
        # Covariance matrix
        cov_matrix = returns.cov()

        # Inverse of covariance matrix
        try:
            inv_cov = np.linalg.inv(cov_matrix)
        except np.linalg.LinAlgError:
            # Singular matrix, use equal weights
            return {symbol: 1.0 / len(symbols) for symbol in symbols}

        # Minimum variance weights: w = (Σ^-1 * 1) / (1^T * Σ^-1 * 1)
        ones = np.ones(len(symbols))
        weights = inv_cov @ ones
        weights = weights / weights.sum()

        # Ensure non-negative and normalize
        weights = np.maximum(weights, 0)
        weights = weights / weights.sum()

        return {symbol: float(w) for symbol, w in zip(symbols, weights)}

    def _max_sharpe_weights(
        self,
        returns: pd.DataFrame,
        symbols: List[str],
        risk_free_rate: float = 0.02
    ) -> Dict[str, float]:
        """Calculate maximum Sharpe ratio portfolio weights"""
        mean_returns = returns.mean() * 252  # Annualize
        cov_matrix = returns.cov() * 252

        # Simple optimization: try many random portfolios
        num_portfolios = 10000
        best_sharpe = -np.inf
        best_weights = None

        for _ in range(num_portfolios):
            # Random weights
            w = np.random.random(len(symbols))
            w = w / w.sum()

            # Portfolio return and risk
            port_return = np.dot(w, mean_returns)
            port_std = np.sqrt(np.dot(w, np.dot(cov_matrix, w)))

            # Sharpe ratio
            sharpe = (port_return - risk_free_rate) / port_std if port_std > 0 else 0

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = w

        if best_weights is None:
            return {symbol: 1.0 / len(symbols) for symbol in symbols}

        return {symbol: float(w) for symbol, w in zip(symbols, best_weights)}

    def _risk_parity_weights(
        self,
        returns: pd.DataFrame,
        symbols: List[str]
    ) -> Dict[str, float]:
        """Calculate risk parity portfolio weights"""
        # Risk parity: each asset contributes equally to portfolio risk
        volatilities = returns.std() * np.sqrt(252)  # Annualized

        # Inverse volatility weighting
        inv_vol = 1.0 / volatilities
        weights = inv_vol / inv_vol.sum()

        return {symbol: float(w) for symbol, w in zip(symbols, weights)}

    async def _simulate_portfolio(
        self,
        symbols: List[str],
        price_data: pd.DataFrame,
        initial_weights: Dict[str, float],
        benchmark_symbol: str,
    ) -> PortfolioBacktestResult:
        """Simulate portfolio performance over time"""

        # Initialize portfolio
        current_weights = initial_weights.copy()
        portfolio_value = self.initial_capital
        cash = 0.0
        holdings = {}  # symbol -> shares

        # Track metrics
        equity_curve = []
        allocations = []
        trades = []

        # Get dates
        dates = price_data.index
        start_date = dates[0]
        end_date = dates[-1]

        # Initial allocation
        for symbol in symbols:
            target_value = portfolio_value * current_weights[symbol]
            price = price_data.loc[start_date, symbol]
            shares = target_value / price
            holdings[symbol] = shares

            # Record trade
            commission_cost = target_value * self.commission
            trades.append(PortfolioTrade(
                timestamp=start_date,
                symbol=symbol,
                action="BUY",
                shares=shares,
                price=price,
                value=target_value,
                commission=commission_cost,
                reason="initial"
            ))

        # Simulation loop
        last_rebalance = start_date
        peak_value = portfolio_value

        for date in dates:
            # Calculate current portfolio value
            portfolio_value = sum(
                holdings.get(symbol, 0) * price_data.loc[date, symbol]
                for symbol in symbols
            )

            # Track equity curve
            drawdown = ((portfolio_value - peak_value) / peak_value) * 100 if peak_value > 0 else 0
            peak_value = max(peak_value, portfolio_value)

            equity_curve.append({
                "timestamp": date.isoformat(),
                "portfolio_value": round(portfolio_value, 2),
                "drawdown": round(drawdown, 2)
            })

            # Track allocations
            current_allocation = {}
            for symbol in symbols:
                asset_value = holdings.get(symbol, 0) * price_data.loc[date, symbol]
                current_allocation[symbol] = asset_value / portfolio_value if portfolio_value > 0 else 0

            allocations.append({
                "timestamp": date.isoformat(),
                "weights": {k: round(v, 4) for k, v in current_allocation.items()}
            })

            # Check if rebalancing needed
            should_rebalance = self._should_rebalance(
                date, last_rebalance, current_allocation, initial_weights
            )

            if should_rebalance:
                # Rebalance portfolio
                rebalance_trades = self._rebalance_portfolio(
                    date=date,
                    holdings=holdings,
                    target_weights=initial_weights,
                    prices={symbol: price_data.loc[date, symbol] for symbol in symbols},
                    portfolio_value=portfolio_value
                )
                trades.extend(rebalance_trades)
                last_rebalance = date

        # Calculate final metrics
        metrics = self._calculate_portfolio_metrics(
            equity_curve=equity_curve,
            trades=trades,
            price_data=price_data,
            symbols=symbols,
            initial_capital=self.initial_capital
        )

        # Calculate correlation matrix
        returns = price_data.pct_change().dropna()
        correlation_matrix = {}
        for sym1 in symbols:
            correlation_matrix[sym1] = {}
            for sym2 in symbols:
                corr = float(returns[sym1].corr(returns[sym2]))
                correlation_matrix[sym1][sym2] = round(corr, 3)

        # Individual asset returns
        individual_returns = {}
        for symbol in symbols:
            initial_price = price_data.loc[start_date, symbol]
            final_price = price_data.loc[end_date, symbol]
            ret = ((final_price - initial_price) / initial_price) * 100
            individual_returns[symbol] = round(ret, 2)

        return PortfolioBacktestResult(
            symbol_list=symbols,
            start_date=start_date,
            end_date=end_date,
            duration_days=(end_date - start_date).days,
            initial_capital=self.initial_capital,
            final_value=portfolio_value,
            metrics=metrics,
            equity_curve=equity_curve,
            allocations=allocations,
            trades=trades,
            correlation_matrix=correlation_matrix,
            individual_returns=individual_returns
        )

    def _should_rebalance(
        self,
        current_date: datetime,
        last_rebalance: datetime,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float]
    ) -> bool:
        """Determine if portfolio should be rebalanced"""

        if self.rebalance_frequency == RebalanceFrequency.NEVER:
            return False

        # Check time-based rebalancing
        days_since_rebalance = (current_date - last_rebalance).days

        if self.rebalance_frequency == RebalanceFrequency.DAILY and days_since_rebalance >= 1:
            return True
        elif self.rebalance_frequency == RebalanceFrequency.WEEKLY and days_since_rebalance >= 7:
            return True
        elif self.rebalance_frequency == RebalanceFrequency.MONTHLY and days_since_rebalance >= 30:
            return True
        elif self.rebalance_frequency == RebalanceFrequency.QUARTERLY and days_since_rebalance >= 90:
            return True

        # Check threshold-based rebalancing
        max_drift = max(
            abs(current_weights.get(symbol, 0) - target_weights.get(symbol, 0))
            for symbol in target_weights.keys()
        )

        return max_drift > self.rebalance_threshold

    def _rebalance_portfolio(
        self,
        date: datetime,
        holdings: Dict[str, float],
        target_weights: Dict[str, float],
        prices: Dict[str, float],
        portfolio_value: float
    ) -> List[PortfolioTrade]:
        """Rebalance portfolio to target weights"""
        trades = []

        for symbol, target_weight in target_weights.items():
            target_value = portfolio_value * target_weight
            current_value = holdings.get(symbol, 0) * prices[symbol]
            diff_value = target_value - current_value

            if abs(diff_value) > portfolio_value * 0.01:  # Only trade if difference > 1%
                shares_to_trade = diff_value / prices[symbol]
                action = "BUY" if shares_to_trade > 0 else "SELL"

                # Update holdings
                holdings[symbol] = holdings.get(symbol, 0) + shares_to_trade

                # Record trade
                commission_cost = abs(diff_value) * self.commission
                trades.append(PortfolioTrade(
                    timestamp=date,
                    symbol=symbol,
                    action=action,
                    shares=abs(shares_to_trade),
                    price=prices[symbol],
                    value=abs(diff_value),
                    commission=commission_cost,
                    reason="rebalance"
                ))

        return trades

    def _calculate_portfolio_metrics(
        self,
        equity_curve: List[Dict],
        trades: List[PortfolioTrade],
        price_data: pd.DataFrame,
        symbols: List[str],
        initial_capital: float
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""

        # Extract values
        values = [point["portfolio_value"] for point in equity_curve]
        final_value = values[-1]

        # Total return
        total_return = ((final_value - initial_capital) / initial_capital) * 100

        # Calculate returns series
        returns = pd.Series(values).pct_change().dropna()

        # Annualized return
        days = len(values)
        annualized_return = ((final_value / initial_capital) ** (252 / days) - 1) * 100

        # Volatility (annualized)
        volatility = returns.std() * np.sqrt(252) * 100

        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        excess_return = (annualized_return / 100) - risk_free_rate
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else volatility / 100
        sortino_ratio = excess_return / downside_std if downside_std > 0 else 0

        # Max drawdown
        max_dd = min([point["drawdown"] for point in equity_curve])

        # Calmar ratio
        calmar_ratio = (annualized_return / abs(max_dd)) if max_dd != 0 else 0

        # Win rate (based on daily returns)
        win_rate = (returns > 0).sum() / len(returns) * 100 if len(returns) > 0 else 0

        # Average correlation
        price_returns = price_data.pct_change().dropna()
        corr_matrix = price_returns.corr()
        avg_correlation = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()

        # Diversification ratio (simplified)
        individual_vols = price_returns.std() * np.sqrt(252)
        weighted_avg_vol = individual_vols.mean()
        portfolio_vol = volatility / 100
        diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0

        # Turnover
        total_trade_value = sum(abs(t.value) for t in trades)
        turnover = (total_trade_value / 2) / initial_capital  # Divide by 2 (buy + sell = 2x)
        annual_turnover = turnover * (252 / days)

        # Best/worst assets
        asset_returns = {
            symbol: ((price_data[symbol].iloc[-1] - price_data[symbol].iloc[0]) / price_data[symbol].iloc[0]) * 100
            for symbol in symbols
        }
        best_asset = max(asset_returns, key=asset_returns.get)
        worst_asset = min(asset_returns, key=asset_returns.get)

        # Asset contributions (simplified - based on equal weight assumption)
        equal_weight = 1.0 / len(symbols)
        asset_contributions = {
            symbol: round(ret * equal_weight, 2)
            for symbol, ret in asset_returns.items()
        }

        return PortfolioMetrics(
            total_return=round(total_return, 2),
            annualized_return=round(annualized_return, 2),
            volatility=round(volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            sortino_ratio=round(sortino_ratio, 2),
            max_drawdown=round(max_dd, 2),
            calmar_ratio=round(calmar_ratio, 2),
            win_rate=round(win_rate, 2),
            avg_correlation=round(avg_correlation, 3),
            diversification_ratio=round(diversification_ratio, 2),
            turnover=round(annual_turnover, 2),
            num_rebalances=len([t for t in trades if t.reason == "rebalance"]),
            best_asset=best_asset,
            worst_asset=worst_asset,
            asset_contributions=asset_contributions
        )

    async def calculate_efficient_frontier(
        self,
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str],
        num_portfolios: int = 100
    ) -> List[Dict]:
        """
        Calculate efficient frontier - set of optimal portfolios

        Returns list of portfolios with varying risk/return profiles
        """
        # Align price data
        aligned = self._align_price_data(price_data, symbols)
        returns = aligned.pct_change().dropna()

        # Calculate mean returns and covariance
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252

        frontier = []

        # Generate random portfolios
        for _ in range(num_portfolios):
            weights = np.random.random(len(symbols))
            weights = weights / weights.sum()

            # Portfolio metrics
            port_return = np.dot(weights, mean_returns)
            port_std = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            sharpe = port_return / port_std if port_std > 0 else 0

            frontier.append({
                "risk": round(float(port_std) * 100, 2),
                "return": round(float(port_return) * 100, 2),
                "sharpe": round(float(sharpe), 2),
                "weights": {symbol: round(float(w), 4) for symbol, w in zip(symbols, weights)}
            })

        # Sort by Sharpe ratio
        frontier.sort(key=lambda x: x["sharpe"], reverse=True)

        return frontier
