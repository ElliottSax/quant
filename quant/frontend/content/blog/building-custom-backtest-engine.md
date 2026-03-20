---
title: Building a Custom Backtesting Engine from Scratch
slug: building-custom-backtest-engine
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-03-20'
last_updated: '2026-03-20'
---

# Building a Custom Backtesting Engine from Scratch

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

While existing frameworks like Backtrader and VectorBT are powerful, building a custom backtesting engine offers unparalleled flexibility, control, and optimization for specific trading scenarios. A custom engine allows you to implement domain-specific logic, integrate with proprietary systems, and optimize for your exact requirements without framework constraints.

This guide covers architecting and implementing a production-grade custom backtesting engine from fundamental principles.

## Core Architecture Design

```python
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import heapq

class OrderType(Enum):
    """Order type enumeration."""
    MARKET = 1
    LIMIT = 2
    STOP = 3
    STOP_LIMIT = 4

class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = 1
    FILLED = 2
    PARTIAL = 3
    CANCELLED = 4
    REJECTED = 5

class OrderSide(Enum):
    """Order side enumeration."""
    BUY = 1
    SELL = -1

@dataclass
class Order:
    """Represents a trading order."""
    order_id: int
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    timestamp: Optional[datetime] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_fill_price: float = 0.0
    fills: List[Dict] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Check if order is complete."""
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED,
                              OrderStatus.REJECTED]

@dataclass
class Trade:
    """Represents a completed trade."""
    trade_id: int
    symbol: str
    entry_timestamp: datetime
    exit_timestamp: Optional[datetime] = None
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: int = 0
    entry_side: OrderSide = OrderSide.BUY
    pnl: float = 0.0
    pnl_pct: float = 0.0
    duration: timedelta = None

class DataFeed:
    """Abstracts market data source."""

    def __init__(self, data: pd.DataFrame, symbol: str):
        self.data = data.sort_index()
        self.symbol = symbol
        self.current_row = 0

    def __iter__(self):
        """Iterate over data."""
        return iter(self.data.iterrows())

    def get_current_bar(self, bar_index: int) -> Dict:
        """Get bar at index."""
        if bar_index >= len(self.data):
            return {}

        row = self.data.iloc[bar_index]
        return {
            'timestamp': self.data.index[bar_index],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume']
        }

    def get_price_at(self, timestamp: datetime) -> Optional[float]:
        """Get price at specific timestamp."""
        if timestamp in self.data.index:
            return self.data.loc[timestamp, 'close']
        return None

class ExecutionEngine:
    """Handles order execution and fills."""

    def __init__(self, commission_rate: float = 0.001):
        self.commission_rate = commission_rate
        self.pending_orders: deque = deque()
        self.order_history: List[Order] = []

    def submit_order(self, order: Order) -> bool:
        """Submit order for execution."""
        self.pending_orders.append(order)
        return True

    def process_market_order(self, order: Order, bar: Dict) -> Dict:
        """Process market order execution."""
        execution_price = bar['close']
        commission = abs(order.quantity) * execution_price * self.commission_rate

        fill = {
            'timestamp': bar['timestamp'],
            'quantity': order.quantity,
            'price': execution_price,
            'commission': commission,
            'total_cost': abs(order.quantity) * execution_price + commission
        }

        return fill

    def process_limit_order(self, order: Order, bar: Dict) -> Optional[Dict]:
        """Process limit order execution."""
        if order.side == OrderSide.BUY:
            if bar['low'] <= order.price:
                execution_price = min(order.price, bar['open'])
            else:
                return None
        else:  # SELL
            if bar['high'] >= order.price:
                execution_price = max(order.price, bar['open'])
            else:
                return None

        commission = abs(order.quantity) * execution_price * self.commission_rate

        fill = {
            'timestamp': bar['timestamp'],
            'quantity': order.quantity,
            'price': execution_price,
            'commission': commission,
            'total_cost': abs(order.quantity) * execution_price + commission
        }

        return fill

    def process_stop_order(self, order: Order, bar: Dict) -> Optional[Dict]:
        """Process stop order execution."""
        if order.side == OrderSide.BUY:
            if bar['high'] >= order.stop_price:
                execution_price = bar['open']
            else:
                return None
        else:
            if bar['low'] <= order.stop_price:
                execution_price = bar['open']
            else:
                return None

        commission = abs(order.quantity) * execution_price * self.commission_rate

        fill = {
            'timestamp': bar['timestamp'],
            'quantity': order.quantity,
            'price': execution_price,
            'commission': commission
        }

        return fill

class Portfolio:
    """Manages portfolio positions and accounts."""

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, int] = defaultdict(int)
        self.entry_prices: Dict[str, float] = {}
        self.trades: List[Trade] = []
        self.trade_id = 1
        self.equity_history: List[Dict] = []

    def update_position(self, symbol: str, quantity: int, price: float,
                       commission: float):
        """Update position after fill."""
        self.cash -= quantity * price + commission

        if self.positions[symbol] == 0:
            self.entry_prices[symbol] = price
        else:
            # Weighted average price
            prev_pos = self.positions[symbol]
            self.entry_prices[symbol] = (
                (self.entry_prices[symbol] * prev_pos + price * quantity) /
                (prev_pos + quantity)
            )

        self.positions[symbol] += quantity

        # Close position if quantity becomes 0
        if self.positions[symbol] == 0:
            self.entry_prices.pop(symbol, None)

    def get_position_value(self, symbol: str, current_price: float) -> float:
        """Get current position value."""
        return self.positions[symbol] * current_price

    def get_total_value(self, prices: Dict[str, float]) -> float:
        """Get total portfolio value."""
        position_value = sum(
            self.get_position_value(symbol, prices[symbol])
            for symbol in self.positions if symbol in prices
        )
        return self.cash + position_value

    def record_closed_trade(self, symbol: str, entry_price: float,
                           exit_price: float, quantity: int,
                           entry_ts: datetime, exit_ts: datetime):
        """Record a closed trade."""
        pnl = quantity * (exit_price - entry_price)
        pnl_pct = (exit_price - entry_price) / entry_price

        trade = Trade(
            trade_id=self.trade_id,
            symbol=symbol,
            entry_timestamp=entry_ts,
            exit_timestamp=exit_ts,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            pnl=pnl,
            pnl_pct=pnl_pct,
            duration=exit_ts - entry_ts
        )

        self.trades.append(trade)
        self.trade_id += 1

class CustomBacktester:
    """Custom backtesting engine combining all components."""

    def __init__(self, initial_capital: float, commission_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.portfolio = Portfolio(initial_capital)
        self.execution_engine = ExecutionEngine(commission_rate)

        # Data management
        self.data_feeds: Dict[str, DataFeed] = {}
        self.current_prices: Dict[str, float] = {}
        self.current_timestamp = None

        # State tracking
        self.bar_index = 0
        self.equity_curve = []
        self.daily_returns = []

    def add_data(self, symbol: str, data: pd.DataFrame):
        """Add market data for a symbol."""
        self.data_feeds[symbol] = DataFeed(data, symbol)

    def submit_order(self, symbol: str, side: OrderSide, quantity: int,
                    order_type: OrderType = OrderType.MARKET,
                    price: Optional[float] = None) -> int:
        """Submit order through execution engine."""
        order = Order(
            order_id=len(self.execution_engine.order_history) + 1,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            timestamp=self.current_timestamp
        )

        self.execution_engine.submit_order(order)
        return order.order_id

    def _process_orders(self, bars: Dict[str, Dict]):
        """Process pending orders."""
        while self.execution_engine.pending_orders:
            order = self.execution_engine.pending_orders[0]

            if order.symbol not in bars:
                break

            bar = bars[order.symbol]

            # Try to execute
            if order.order_type == OrderType.MARKET:
                fill = self.execution_engine.process_market_order(order, bar)

            elif order.order_type == OrderType.LIMIT:
                fill = self.execution_engine.process_limit_order(order, bar)

            elif order.order_type == OrderType.STOP:
                fill = self.execution_engine.process_stop_order(order, bar)

            else:
                fill = None

            if fill:
                # Execute fill
                order.fills.append(fill)
                self.portfolio.update_position(
                    order.symbol,
                    order.quantity,
                    fill['price'],
                    fill['commission']
                )
                order.status = OrderStatus.FILLED
                self.execution_engine.pending_orders.popleft()

            else:
                # Can't fill, check if should cancel
                if bar['timestamp'] > order.timestamp + timedelta(days=1):
                    order.status = OrderStatus.CANCELLED
                    self.execution_engine.pending_orders.popleft()
                else:
                    break

    def _update_current_prices(self, bars: Dict[str, Dict]):
        """Update current prices from bars."""
        for symbol, bar in bars.items():
            self.current_prices[symbol] = bar['close']

    def backtest(self, strategy_func: Callable):
        """Run backtest with strategy function."""
        if not self.data_feeds:
            raise ValueError("No data feeds registered")

        # Synchronize bars across all feeds
        all_dates = set()
        for feed in self.data_feeds.values():
            all_dates.update(feed.data.index)

        all_dates = sorted(list(all_dates))

        # Process each bar
        for bar_index, timestamp in enumerate(all_dates):
            self.current_timestamp = timestamp
            self.bar_index = bar_index

            # Get bars for all symbols
            bars = {}
            for symbol, feed in self.data_feeds.items():
                if timestamp in feed.data.index:
                    row = feed.data.loc[timestamp]
                    bars[symbol] = {
                        'timestamp': timestamp,
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    }

            # Update current prices
            self._update_current_prices(bars)

            # Process any pending orders
            self._process_orders(bars)

            # Execute strategy
            strategy_func(self)

            # Record equity
            portfolio_value = self.portfolio.get_total_value(self.current_prices)
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': portfolio_value,
                'cash': self.portfolio.cash
            })

            # Calculate daily return
            if len(self.equity_curve) > 1:
                prev = self.equity_curve[-2]['equity']
                ret = (portfolio_value - prev) / prev
                self.daily_returns.append(ret)

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if not self.equity_curve:
            return {}

        equity = np.array([e['equity'] for e in self.equity_curve])
        returns = np.array(self.daily_returns)

        total_return = (equity[-1] - self.initial_capital) / self.initial_capital
        sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(252)
                 if np.std(returns) > 0 else 0)

        # Drawdown
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak
        max_dd = np.min(drawdown)

        # Win rate
        winning = sum(1 for t in self.portfolio.trades if t.pnl > 0)
        total = len(self.portfolio.trades)

        return {
            'total_return_%': total_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_%': max_dd * 100,
            'final_equity': equity[-1],
            'total_trades': total,
            'winning_trades': winning,
            'win_rate': winning / total if total > 0 else 0
        }

# Example strategy
def simple_ma_strategy(backtester: CustomBacktester):
    """Simple moving average crossover strategy."""
    symbol = 'SPY'

    if symbol not in backtester.data_feeds:
        return

    # Get historical data for calculation
    df = backtester.data_feeds[symbol].data
    current_index = backtester.bar_index

    if current_index < 50:
        return

    historical = df.iloc[:current_index]

    sma20 = historical['close'].rolling(20).mean().iloc[-1]
    sma50 = historical['close'].rolling(50).mean().iloc[-1]
    current_price = backtester.current_prices[symbol]

    # Strategy logic
    if sma20 > sma50 and symbol not in backtester.portfolio.positions:
        backtester.submit_order(symbol, OrderSide.BUY, 10, OrderType.MARKET)

    elif sma20 < sma50 and backtester.portfolio.positions[symbol] > 0:
        backtester.submit_order(symbol, OrderSide.SELL,
                               backtester.portfolio.positions[symbol],
                               OrderType.MARKET)

# Example usage
if __name__ == "__main__":
    backtester = CustomBacktester(initial_capital=100000, commission_rate=0.001)

    # Load data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 1.5)

    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(len(dates)) * 0.001),
        'high': prices * (1 + abs(np.random.randn(len(dates)) * 0.005)),
        'low': prices * (1 - abs(np.random.randn(len(dates)) * 0.005)),
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)

    backtester.add_data('SPY', df)

    # Run backtest
    backtester.backtest(simple_ma_strategy)

    # Print results
    metrics = backtester.get_performance_metrics()
    print("Custom Engine Backtest Results:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
```

## Key Design Principles

1. **Separation of Concerns**: Data feeds, execution engine, portfolio, strategy
2. **Extensibility**: Easy to add new order types, execution algorithms
3. **Auditability**: Complete order and trade history
4. **Performance**: Efficient data structures and algorithms
5. **Testability**: Modular components easily unit tested

## Conclusion

Building a custom backtesting engine provides complete control over trading system behavior. While more complex than using existing frameworks, the flexibility and performance benefits make it worthwhile for serious trading applications.
