#!/usr/bin/env python3
"""Quick test of backtesting service without pytest infrastructure."""

import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.backtesting import (
    OrderType,
    OrderSide,
    OrderStatus,
    Order,
    Position,
    BacktestEngine,
)


def test_order_types():
    """Test that all order types exist."""
    assert OrderType.MARKET == "market"
    assert OrderType.LIMIT == "limit"
    assert OrderType.STOP == "stop"
    assert OrderType.STOP_LIMIT == "stop_limit"
    print("✓ Order types test passed")


def test_order_sides():
    """Test buy and sell sides."""
    assert OrderSide.BUY == "buy"
    assert OrderSide.SELL == "sell"
    print("✓ Order sides test passed")


def test_order_statuses():
    """Test order statuses."""
    assert OrderStatus.PENDING == "pending"
    assert OrderStatus.FILLED == "filled"
    assert OrderStatus.CANCELLED == "cancelled"
    assert OrderStatus.REJECTED == "rejected"
    print("✓ Order statuses test passed")


def test_create_order():
    """Test creating an order."""
    order = Order(
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )

    assert order.symbol == "AAPL"
    assert order.side == OrderSide.BUY
    assert order.quantity == 100
    assert order.status == OrderStatus.PENDING
    print("✓ Create order test passed")


def test_create_position():
    """Test creating a position."""
    position = Position(
        symbol="AAPL",
        quantity=100,
        avg_entry_price=150.00,
        current_price=155.00
    )

    assert position.symbol == "AAPL"
    assert position.quantity == 100
    assert position.avg_entry_price == 150.00
    print("✓ Create position test passed")


def test_backtest_engine_creation():
    """Test creating a backtest engine."""
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )

    assert engine.initial_capital == 100000
    assert engine.cash == 100000
    assert engine.commission == 0.001
    assert len(engine.positions) == 0
    print("✓ BacktestEngine creation test passed")


def test_place_order():
    """Test placing an order."""
    engine = BacktestEngine(initial_capital=100000)

    order = engine.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100
    )

    assert order.symbol == "AAPL"
    assert len(engine.orders) == 1
    print("✓ Place order test passed")


def test_execute_market_buy():
    """Test executing a market buy order."""
    engine = BacktestEngine(initial_capital=100000)

    order = engine.place_order(
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=100,
        timestamp=datetime.utcnow()
    )

    # Create bar data
    bar = pd.Series({
        'timestamp': datetime.utcnow(),
        'open': 150.00,
        'high': 152.00,
        'low': 149.00,
        'close': 151.00,
        'volume': 1000000
    })

    initial_cash = engine.cash
    engine._execute_market_order(order, bar)

    assert order.status == OrderStatus.FILLED
    assert order.filled_price > 151.00  # Includes slippage
    assert engine.cash < initial_cash  # Cash decreased
    assert "AAPL" in engine.positions
    assert engine.positions["AAPL"].quantity == 100
    print("✓ Execute market buy test passed")


async def test_simple_backtest():
    """Test running a simple backtest."""
    engine = BacktestEngine(initial_capital=100000)

    # Create sample price data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    prices = [100 + i * 0.5 for i in range(50)]

    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p + 1 for p in prices],
        'low': [p - 1 for p in prices],
        'close': prices,
        'volume': [1000000] * 50
    })

    # Simple strategy: buy on first day
    async def simple_strategy(df):
        if len(df) == 1:
            return {'type': 'buy', 'quantity': 100, 'symbol': 'TEST'}
        return None

    result = await engine.run_backtest(
        symbol="TEST",
        price_data=data,
        strategy=simple_strategy
    )

    assert result.total_trades > 0
    assert result.initial_capital == 100000
    assert result.final_capital > 0
    assert len(result.equity_curve) > 0
    print("✓ Simple backtest test passed")


if __name__ == "__main__":
    print("Running quick backtesting tests...")
    print()

    # Run sync tests
    test_order_types()
    test_order_sides()
    test_order_statuses()
    test_create_order()
    test_create_position()
    test_backtest_engine_creation()
    test_place_order()
    test_execute_market_buy()

    # Run async test
    asyncio.run(test_simple_backtest())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
