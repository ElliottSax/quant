"""
Backtesting Engine

Simulate trading strategies on historical data and calculate performance metrics.
"""

from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import numpy as np
import pandas as pd
from dataclasses import dataclass, field


class OrderType(str, Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Trading order"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_quantity: float = 0
    commission: float = 0


@dataclass
class Position:
    """Trading position"""
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float = 0
    realized_pnl: float = 0


@dataclass
class Trade:
    """Executed trade"""
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    commission: float
    pnl: Optional[float] = None


class BacktestResult(BaseModel):
    """Backtesting results"""
    # Performance metrics
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float

    # Time metrics
    start_date: datetime
    end_date: datetime
    duration_days: int

    # Capital metrics
    initial_capital: float
    final_capital: float
    peak_capital: float

    # Additional metrics
    trades: List[Dict]
    equity_curve: List[Dict]
    drawdown_curve: List[Dict]


class BacktestEngine:
    """
    Backtesting engine for trading strategies

    Simulates strategy execution on historical data with realistic
    trading costs and slippage.
    """

    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 0.1% commission
        slippage: float = 0.0005,    # 0.05% slippage
        risk_free_rate: float = 0.02  # 2% annual risk-free rate
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_free_rate = risk_free_rate

        # State variables
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.equity_history: List[Tuple[datetime, float]] = []

    def reset(self):
        """Reset backtest state"""
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        self.equity_history = []

    async def run_backtest(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        strategy: Callable,
        **strategy_params
    ) -> BacktestResult:
        """
        Run backtest with given strategy

        Args:
            symbol: Trading symbol
            price_data: DataFrame with columns: timestamp, open, high, low, close, volume
            strategy: Strategy function that returns signals
            **strategy_params: Additional parameters for strategy

        Returns:
            BacktestResult with comprehensive metrics
        """
        self.reset()

        # Ensure data is sorted by timestamp
        price_data = price_data.sort_values('timestamp').reset_index(drop=True)

        # Run strategy on each bar
        for idx in range(len(price_data)):
            current_bar = price_data.iloc[idx]
            timestamp = current_bar['timestamp']

            # Get historical data up to current bar
            historical_data = price_data.iloc[:idx+1]

            # Generate signal from strategy
            signal = await strategy(historical_data, **strategy_params)

            # Process signal
            if signal:
                self._process_signal(signal, current_bar)

            # Update positions with current prices
            self._update_positions(current_bar)

            # Process pending orders
            self._process_orders(current_bar)

            # Record equity
            equity = self._calculate_equity()
            self.equity_history.append((timestamp, equity))

        # Calculate final metrics
        return self._calculate_metrics(price_data)

    def _process_signal(self, signal: Dict, bar: pd.Series):
        """Process trading signal"""
        symbol = bar.name if hasattr(bar, 'name') else signal.get('symbol', 'UNKNOWN')
        signal_type = signal.get('type')  # 'buy' or 'sell'
        quantity = signal.get('quantity', 0)

        if signal_type == 'buy':
            self.place_order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                timestamp=bar['timestamp']
            )
        elif signal_type == 'sell':
            self.place_order(
                symbol=symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=quantity,
                timestamp=bar['timestamp']
            )

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ) -> Order:
        """Place trading order"""
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            timestamp=timestamp or datetime.utcnow()
        )
        self.orders.append(order)
        return order

    def _process_orders(self, bar: pd.Series):
        """Process pending orders"""
        for order in self.orders:
            if order.status == OrderStatus.PENDING:
                if order.order_type == OrderType.MARKET:
                    self._execute_market_order(order, bar)
                elif order.order_type == OrderType.LIMIT:
                    self._execute_limit_order(order, bar)
                elif order.order_type == OrderType.STOP:
                    self._execute_stop_order(order, bar)

    def _execute_market_order(self, order: Order, bar: pd.Series):
        """Execute market order"""
        # Use close price with slippage
        execution_price = bar['close']
        if order.side == OrderSide.BUY:
            execution_price *= (1 + self.slippage)
        else:
            execution_price *= (1 - self.slippage)

        # Calculate commission
        commission = execution_price * order.quantity * self.commission

        # Check if we have enough cash (for buy orders)
        if order.side == OrderSide.BUY:
            total_cost = execution_price * order.quantity + commission
            if total_cost > self.cash:
                order.status = OrderStatus.REJECTED
                return
            self.cash -= total_cost
        else:
            # Sell order
            if order.symbol not in self.positions:
                order.status = OrderStatus.REJECTED
                return
            if self.positions[order.symbol].quantity < order.quantity:
                order.status = OrderStatus.REJECTED
                return
            proceeds = execution_price * order.quantity - commission
            self.cash += proceeds

        # Fill order
        order.filled_price = execution_price
        order.filled_quantity = order.quantity
        order.commission = commission
        order.status = OrderStatus.FILLED

        # Update position
        self._update_position_from_order(order, bar)

        # Record trade
        trade = Trade(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            timestamp=bar['timestamp'],
            commission=commission
        )
        self.trades.append(trade)

    def _execute_limit_order(self, order: Order, bar: pd.Series):
        """Execute limit order"""
        # Check if price reached limit
        if order.side == OrderSide.BUY and bar['low'] <= order.price:
            execution_price = order.price
            self._fill_order(order, execution_price, bar)
        elif order.side == OrderSide.SELL and bar['high'] >= order.price:
            execution_price = order.price
            self._fill_order(order, execution_price, bar)

    def _execute_stop_order(self, order: Order, bar: pd.Series):
        """Execute stop order"""
        # Check if stop price reached
        if order.side == OrderSide.BUY and bar['high'] >= order.stop_price:
            execution_price = max(bar['open'], order.stop_price) * (1 + self.slippage)
            self._fill_order(order, execution_price, bar)
        elif order.side == OrderSide.SELL and bar['low'] <= order.stop_price:
            execution_price = min(bar['open'], order.stop_price) * (1 - self.slippage)
            self._fill_order(order, execution_price, bar)

    def _fill_order(self, order: Order, execution_price: float, bar: pd.Series):
        """Fill order at given price"""
        commission = execution_price * order.quantity * self.commission

        if order.side == OrderSide.BUY:
            total_cost = execution_price * order.quantity + commission
            if total_cost <= self.cash:
                self.cash -= total_cost
                order.status = OrderStatus.FILLED
                order.filled_price = execution_price
                order.filled_quantity = order.quantity
                order.commission = commission
                self._update_position_from_order(order, bar)
        else:
            if order.symbol in self.positions:
                if self.positions[order.symbol].quantity >= order.quantity:
                    proceeds = execution_price * order.quantity - commission
                    self.cash += proceeds
                    order.status = OrderStatus.FILLED
                    order.filled_price = execution_price
                    order.filled_quantity = order.quantity
                    order.commission = commission
                    self._update_position_from_order(order, bar)

    def _update_position_from_order(self, order: Order, bar: pd.Series):
        """Update position from filled order"""
        if order.side == OrderSide.BUY:
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                total_cost = pos.avg_entry_price * pos.quantity + order.filled_price * order.quantity
                pos.quantity += order.quantity
                pos.avg_entry_price = total_cost / pos.quantity
            else:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_entry_price=order.filled_price,
                    current_price=bar['close']
                )
        else:  # SELL
            if order.symbol in self.positions:
                pos = self.positions[order.symbol]
                pnl = (order.filled_price - pos.avg_entry_price) * order.quantity - order.commission
                pos.realized_pnl += pnl
                pos.quantity -= order.quantity

                if pos.quantity <= 0:
                    del self.positions[order.symbol]

    def _update_positions(self, bar: pd.Series):
        """Update all positions with current prices"""
        for symbol, position in self.positions.items():
            position.current_price = bar['close']
            position.unrealized_pnl = (
                (position.current_price - position.avg_entry_price) * position.quantity
            )

    def _calculate_equity(self) -> float:
        """Calculate total equity"""
        equity = self.cash
        for position in self.positions.values():
            equity += position.current_price * position.quantity
        return equity

    def _calculate_metrics(self, price_data: pd.DataFrame) -> BacktestResult:
        """Calculate comprehensive performance metrics"""
        if not self.equity_history:
            raise ValueError("No equity history available")

        # Convert equity history to arrays
        timestamps = [t for t, _ in self.equity_history]
        equity_values = [e for _, e in self.equity_history]

        # Basic metrics
        final_equity = equity_values[-1]
        total_return = (final_equity / self.initial_capital - 1) * 100

        # Calculate returns
        returns = np.diff(equity_values) / equity_values[:-1]

        # Time metrics
        start_date = timestamps[0]
        end_date = timestamps[-1]
        duration_days = (end_date - start_date).days
        duration_years = duration_days / 365.25

        # Annual return
        annual_return = ((final_equity / self.initial_capital) ** (1 / duration_years) - 1) * 100 if duration_years > 0 else 0

        # Sharpe ratio
        excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        sharpe_ratio = (np.mean(excess_returns) / np.std(excess_returns)) * np.sqrt(252) if np.std(excess_returns) > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino_ratio = (np.mean(excess_returns) / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        # Max drawdown
        peak = equity_values[0]
        max_drawdown = 0
        drawdown_curve = []

        for i, equity in enumerate(equity_values):
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
            drawdown_curve.append({
                'timestamp': timestamps[i],
                'drawdown': drawdown,
                'peak': peak
            })

        # Trade statistics
        winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl and t.pnl < 0]

        win_rate = len(winning_trades) / len(self.trades) * 100 if self.trades else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Largest win/loss
        largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
        largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0

        # Format equity curve
        equity_curve = [
            {'timestamp': t, 'equity': e}
            for t, e in zip(timestamps, equity_values)
        ]

        # Format trades
        trades_dict = [
            {
                'symbol': t.symbol,
                'side': t.side,
                'quantity': t.quantity,
                'price': t.price,
                'timestamp': t.timestamp,
                'commission': t.commission,
                'pnl': t.pnl
            }
            for t in self.trades
        ]

        return BacktestResult(
            total_return=round(total_return, 2),
            annual_return=round(annual_return, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            sortino_ratio=round(sortino_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            win_rate=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            largest_win=round(largest_win, 2),
            largest_loss=round(largest_loss, 2),
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            initial_capital=self.initial_capital,
            final_capital=round(final_equity, 2),
            peak_capital=round(peak, 2),
            trades=trades_dict,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve
        )


# Example strategy functions
async def simple_ma_crossover_strategy(data: pd.DataFrame, fast_period: int = 20, slow_period: int = 50) -> Optional[Dict]:
    """Simple moving average crossover strategy"""
    if len(data) < slow_period:
        return None

    # Calculate MAs
    fast_ma = data['close'].rolling(fast_period).mean().iloc[-1]
    slow_ma = data['close'].rolling(slow_period).mean().iloc[-1]
    prev_fast_ma = data['close'].rolling(fast_period).mean().iloc[-2]
    prev_slow_ma = data['close'].rolling(slow_period).mean().iloc[-2]

    # Detect crossover
    if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
        return {'type': 'buy', 'quantity': 100}
    elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
        return {'type': 'sell', 'quantity': 100}

    return None
