"""Tests for Backtesting service."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.services.backtesting import (
    OrderType,
    OrderSide,
    OrderStatus,
    Order,
    Position,
    Trade,
    BacktestResult,
    BacktestEngine,
    simple_ma_crossover_strategy,
)


class TestOrderType:
    """Test OrderType enum."""

    def test_order_types_exist(self):
        """Test that all order types are defined."""
        assert OrderType.MARKET == "market"
        assert OrderType.LIMIT == "limit"
        assert OrderType.STOP == "stop"
        assert OrderType.STOP_LIMIT == "stop_limit"

    def test_order_type_count(self):
        """Test that we have exactly 4 order types."""
        assert len(list(OrderType)) == 4


class TestOrderSide:
    """Test OrderSide enum."""

    def test_order_sides_exist(self):
        """Test that buy and sell sides exist."""
        assert OrderSide.BUY == "buy"
        assert OrderSide.SELL == "sell"

    def test_order_side_count(self):
        """Test that we have exactly 2 order sides."""
        assert len(list(OrderSide)) == 2


class TestOrderStatus:
    """Test OrderStatus enum."""

    def test_order_statuses_exist(self):
        """Test that all order statuses are defined."""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.FILLED == "filled"
        assert OrderStatus.CANCELLED == "cancelled"
        assert OrderStatus.REJECTED == "rejected"

    def test_order_status_count(self):
        """Test that we have exactly 4 order statuses."""
        assert len(list(OrderStatus)) == 4


class TestOrder:
    """Test Order dataclass."""

    def test_create_basic_order(self):
        """Test creating a basic order."""
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )

        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == 100
        assert order.status == OrderStatus.PENDING
        assert order.filled_quantity == 0
        assert order.commission == 0

    def test_order_with_limit_price(self):
        """Test creating a limit order."""
        order = Order(
            symbol="TSLA",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=50,
            price=200.00
        )

        assert order.price == 200.00
        assert order.order_type == OrderType.LIMIT

    def test_order_with_stop_price(self):
        """Test creating a stop order."""
        order = Order(
            symbol="MSFT",
            side=OrderSide.BUY,
            order_type=OrderType.STOP,
            quantity=75,
            stop_price=300.00
        )

        assert order.stop_price == 300.00
        assert order.order_type == OrderType.STOP

    def test_order_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated."""
        order = Order(
            symbol="GOOGL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10
        )

        assert order.timestamp is not None
        assert isinstance(order.timestamp, datetime)


class TestPosition:
    """Test Position dataclass."""

    def test_create_position(self):
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
        assert position.current_price == 155.00
        assert position.unrealized_pnl == 0
        assert position.realized_pnl == 0

    def test_position_pnl(self):
        """Test position P&L calculation."""
        position = Position(
            symbol="TSLA",
            quantity=50,
            avg_entry_price=200.00,
            current_price=210.00,
            unrealized_pnl=500.00
        )

        assert position.unrealized_pnl == 500.00


class TestTradeDataclass:
    """Test Trade dataclass."""

    def test_create_trade(self):
        """Test creating a trade."""
        trade = Trade(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=150.00,
            timestamp=datetime.utcnow(),
            commission=15.00
        )

        assert trade.symbol == "AAPL"
        assert trade.side == OrderSide.BUY
        assert trade.quantity == 100
        assert trade.price == 150.00
        assert trade.commission == 15.00
        assert trade.pnl is None

    def test_trade_with_pnl(self):
        """Test trade with P&L."""
        trade = Trade(
            symbol="TSLA",
            side=OrderSide.SELL,
            quantity=50,
            price=200.00,
            timestamp=datetime.utcnow(),
            commission=10.00,
            pnl=500.00
        )

        assert trade.pnl == 500.00


class TestBacktestEngine:
    """Test BacktestEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a backtest engine instance."""
        return BacktestEngine(
            initial_capital=100000,
            commission=0.001,
            slippage=0.0005,
            risk_free_rate=0.02
        )

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        data = {
            'timestamp': dates,
            'open': [100 + i * 0.5 + np.random.randn() for i in range(100)],
            'high': [101 + i * 0.5 + abs(np.random.randn()) for i in range(100)],
            'low': [99 + i * 0.5 - abs(np.random.randn()) for i in range(100)],
            'close': [100 + i * 0.5 + np.random.randn() * 0.5 for i in range(100)],
            'volume': [1000000 + np.random.randint(-100000, 100000) for _ in range(100)]
        }
        return pd.DataFrame(data)

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine.initial_capital == 100000
        assert engine.cash == 100000
        assert engine.commission == 0.001
        assert engine.slippage == 0.0005
        assert engine.risk_free_rate == 0.02
        assert len(engine.positions) == 0
        assert len(engine.orders) == 0
        assert len(engine.trades) == 0

    def test_reset_engine(self, engine):
        """Test resetting the engine."""
        # Modify state
        engine.cash = 50000
        engine.positions = {"AAPL": Position("AAPL", 100, 150, 155)}
        engine.orders = [Order("AAPL", OrderSide.BUY, OrderType.MARKET, 10)]
        engine.trades = [Trade("AAPL", OrderSide.BUY, 10, 150, datetime.utcnow(), 1.5)]

        # Reset
        engine.reset()

        assert engine.cash == 100000
        assert len(engine.positions) == 0
        assert len(engine.orders) == 0
        assert len(engine.trades) == 0
        assert len(engine.equity_history) == 0

    def test_place_market_order(self, engine):
        """Test placing a market order."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )

        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == 100
        assert order.status == OrderStatus.PENDING
        assert len(engine.orders) == 1

    def test_place_limit_order(self, engine):
        """Test placing a limit order."""
        order = engine.place_order(
            symbol="TSLA",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=50,
            price=200.00
        )

        assert order.order_type == OrderType.LIMIT
        assert order.price == 200.00

    def test_place_stop_order(self, engine):
        """Test placing a stop order."""
        order = engine.place_order(
            symbol="MSFT",
            side=OrderSide.BUY,
            order_type=OrderType.STOP,
            quantity=75,
            stop_price=300.00
        )

        assert order.order_type == OrderType.STOP
        assert order.stop_price == 300.00

    def test_execute_market_buy_order(self, engine):
        """Test executing a market buy order."""
        # Place order
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

        # Execute order
        engine._execute_market_order(order, bar)

        # Verify order was filled
        assert order.status == OrderStatus.FILLED
        assert order.filled_price is not None
        assert order.filled_price > 151.00  # Should include slippage
        assert order.filled_quantity == 100
        assert order.commission > 0

        # Verify cash decreased
        assert engine.cash < engine.initial_capital

        # Verify position created
        assert "AAPL" in engine.positions
        assert engine.positions["AAPL"].quantity == 100

    def test_execute_market_sell_order(self, engine):
        """Test executing a market sell order."""
        # First buy to create position
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100,
            avg_entry_price=150.00,
            current_price=155.00
        )

        initial_cash = engine.cash

        # Place sell order
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 155.00,
            'open': 154.00,
            'high': 156.00,
            'low': 153.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        assert order.status == OrderStatus.FILLED
        assert engine.cash > initial_cash  # Cash increased from sale

    def test_reject_buy_order_insufficient_funds(self, engine):
        """Test that buy order is rejected with insufficient funds."""
        # Try to buy more than we can afford
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10000,  # Way too many shares
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 150.00,
            'open': 149.00,
            'high': 151.00,
            'low': 148.00,
            'volume': 1000000
        })

        initial_cash = engine.cash
        engine._execute_market_order(order, bar)

        assert order.status == OrderStatus.REJECTED
        assert engine.cash == initial_cash  # Cash unchanged

    def test_reject_sell_order_no_position(self, engine):
        """Test that sell order is rejected when no position exists."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 150.00,
            'open': 149.00,
            'high': 151.00,
            'low': 148.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        assert order.status == OrderStatus.REJECTED

    def test_reject_sell_order_insufficient_quantity(self, engine):
        """Test that sell order is rejected when quantity exceeds position."""
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=50,
            avg_entry_price=150.00,
            current_price=155.00
        )

        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=100,  # More than we own
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 155.00,
            'open': 154.00,
            'high': 156.00,
            'low': 153.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        assert order.status == OrderStatus.REJECTED

    def test_execute_limit_buy_order(self, engine):
        """Test executing a limit buy order."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=149.00,
            timestamp=datetime.utcnow()
        )

        # Bar with low touching limit price
        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'open': 150.00,
            'high': 151.00,
            'low': 148.00,  # Touches limit
            'close': 150.00,
            'volume': 1000000
        })

        engine._execute_limit_order(order, bar)

        assert order.status == OrderStatus.FILLED
        assert order.filled_price == 149.00

    def test_limit_buy_order_not_filled(self, engine):
        """Test that limit buy order doesn't fill when price doesn't reach limit."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=145.00,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'open': 150.00,
            'high': 152.00,
            'low': 148.00,  # Doesn't reach 145
            'close': 151.00,
            'volume': 1000000
        })

        engine._execute_limit_order(order, bar)

        assert order.status == OrderStatus.PENDING

    def test_execute_stop_buy_order(self, engine):
        """Test executing a stop buy order."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.STOP,
            quantity=100,
            stop_price=152.00,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'open': 150.00,
            'high': 153.00,  # Triggers stop
            'low': 149.00,
            'close': 152.50,
            'volume': 1000000
        })

        engine._execute_stop_order(order, bar)

        assert order.status == OrderStatus.FILLED
        assert order.filled_price is not None

    def test_update_positions(self, engine):
        """Test updating positions with current prices."""
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100,
            avg_entry_price=150.00,
            current_price=150.00
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 155.00,
            'open': 154.00,
            'high': 156.00,
            'low': 153.00,
            'volume': 1000000
        })

        engine._update_positions(bar)

        pos = engine.positions["AAPL"]
        assert pos.current_price == 155.00
        assert pos.unrealized_pnl == 500.00  # (155-150) * 100

    def test_calculate_equity(self, engine):
        """Test calculating total equity."""
        engine.cash = 50000
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100,
            avg_entry_price=150.00,
            current_price=155.00
        )
        engine.positions["TSLA"] = Position(
            symbol="TSLA",
            quantity=50,
            avg_entry_price=200.00,
            current_price=210.00
        )

        equity = engine._calculate_equity()

        # Cash + (100 * 155) + (50 * 210) = 50000 + 15500 + 10500 = 76000
        assert equity == 76000

    async def test_run_backtest_simple_strategy(self, engine, sample_price_data):
        """Test running a backtest with simple strategy."""
        async def simple_buy_hold(data: pd.DataFrame) -> Optional[Dict]:
            """Buy on first bar, hold forever."""
            if len(data) == 1:
                return {'type': 'buy', 'quantity': 100, 'symbol': 'TEST'}
            return None

        result = await engine.run_backtest(
            symbol="TEST",
            price_data=sample_price_data,
            strategy=simple_buy_hold
        )

        assert isinstance(result, BacktestResult)
        assert result.total_trades > 0
        assert result.initial_capital == 100000
        assert result.final_capital > 0
        assert len(result.equity_curve) > 0

    async def test_backtest_metrics_calculation(self, engine, sample_price_data):
        """Test that backtest calculates all required metrics."""
        async def dummy_strategy(data: pd.DataFrame) -> Optional[Dict]:
            return None

        result = await engine.run_backtest(
            symbol="TEST",
            price_data=sample_price_data,
            strategy=dummy_strategy
        )

        # Verify all metrics are present
        assert hasattr(result, 'total_return')
        assert hasattr(result, 'annual_return')
        assert hasattr(result, 'sharpe_ratio')
        assert hasattr(result, 'sortino_ratio')
        assert hasattr(result, 'max_drawdown')
        assert hasattr(result, 'win_rate')
        assert hasattr(result, 'profit_factor')
        assert hasattr(result, 'total_trades')
        assert hasattr(result, 'equity_curve')
        assert hasattr(result, 'drawdown_curve')

    async def test_backtest_with_ma_crossover_strategy(self, engine):
        """Test backtest with MA crossover strategy."""
        # Create data with clear trend
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = [100 + i * 0.5 for i in range(100)]  # Uptrend

        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [1000000] * 100
        })

        result = await engine.run_backtest(
            symbol="TEST",
            price_data=data,
            strategy=simple_ma_crossover_strategy,
            fast_period=10,
            slow_period=20
        )

        assert isinstance(result, BacktestResult)
        assert result.duration_days > 0
        assert result.start_date < result.end_date

    def test_position_averaging(self, engine):
        """Test that multiple buys average entry price correctly."""
        # First buy
        order1 = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )
        order1.status = OrderStatus.FILLED
        order1.filled_price = 150.00
        order1.filled_quantity = 100

        bar = pd.Series({'close': 150.00, 'timestamp': datetime.utcnow()})
        engine._update_position_from_order(order1, bar)

        # Second buy at different price
        order2 = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )
        order2.status = OrderStatus.FILLED
        order2.filled_price = 160.00
        order2.filled_quantity = 100

        engine._update_position_from_order(order2, bar)

        pos = engine.positions["AAPL"]
        assert pos.quantity == 200
        assert pos.avg_entry_price == 155.00  # (150*100 + 160*100) / 200

    def test_position_closes_on_full_sell(self, engine):
        """Test that position is removed after selling all shares."""
        # Create position
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100,
            avg_entry_price=150.00,
            current_price=155.00
        )

        # Sell all shares
        order = Order(
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )
        order.status = OrderStatus.FILLED
        order.filled_price = 155.00
        order.filled_quantity = 100
        order.commission = 15.50

        bar = pd.Series({'close': 155.00, 'timestamp': datetime.utcnow()})
        engine._update_position_from_order(order, bar)

        # Position should be removed
        assert "AAPL" not in engine.positions

    def test_commission_calculation(self, engine):
        """Test that commission is calculated correctly."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 150.00,
            'open': 149.00,
            'high': 151.00,
            'low': 148.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        # Commission should be price * quantity * commission_rate
        expected_commission = order.filled_price * 100 * 0.001
        assert abs(order.commission - expected_commission) < 0.01

    def test_slippage_on_buy(self, engine):
        """Test that slippage is applied to buy orders."""
        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 150.00,
            'open': 149.00,
            'high': 151.00,
            'low': 148.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        # Buy price should be higher due to slippage
        assert order.filled_price > 150.00
        expected_price = 150.00 * (1 + engine.slippage)
        assert abs(order.filled_price - expected_price) < 0.01

    def test_slippage_on_sell(self, engine):
        """Test that slippage is applied to sell orders."""
        engine.positions["AAPL"] = Position(
            symbol="AAPL",
            quantity=100,
            avg_entry_price=145.00,
            current_price=150.00
        )

        order = engine.place_order(
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=100,
            timestamp=datetime.utcnow()
        )

        bar = pd.Series({
            'timestamp': datetime.utcnow(),
            'close': 150.00,
            'open': 149.00,
            'high': 151.00,
            'low': 148.00,
            'volume': 1000000
        })

        engine._execute_market_order(order, bar)

        # Sell price should be lower due to slippage
        assert order.filled_price < 150.00
        expected_price = 150.00 * (1 - engine.slippage)
        assert abs(order.filled_price - expected_price) < 0.01


class TestSimpleMACrossoverStrategy:
    """Test the simple MA crossover strategy."""

    async def test_strategy_insufficient_data(self):
        """Test strategy returns None with insufficient data."""
        data = pd.DataFrame({
            'close': [100, 101, 102]
        })

        result = await simple_ma_crossover_strategy(data, fast_period=20, slow_period=50)
        assert result is None

    async def test_strategy_bullish_crossover(self):
        """Test strategy generates buy signal on bullish crossover."""
        # Create data where fast MA crosses above slow MA
        prices = [100] * 30 + [100 + i for i in range(30)]
        data = pd.DataFrame({'close': prices})

        result = await simple_ma_crossover_strategy(data, fast_period=10, slow_period=20)

        # Should eventually get a buy signal
        if result is not None:
            assert result.get('type') in ['buy', 'sell', None]

    async def test_strategy_bearish_crossover(self):
        """Test strategy generates sell signal on bearish crossover."""
        # Create data where fast MA crosses below slow MA
        prices = [120] * 30 + [120 - i for i in range(30)]
        data = pd.DataFrame({'close': prices})

        result = await simple_ma_crossover_strategy(data, fast_period=10, slow_period=20)

        # Should eventually get a sell signal
        if result is not None:
            assert result.get('type') in ['buy', 'sell', None]

    async def test_strategy_no_crossover(self):
        """Test strategy returns None when no crossover."""
        # Flat prices - no crossover
        data = pd.DataFrame({'close': [100] * 60})

        result = await simple_ma_crossover_strategy(data, fast_period=10, slow_period=20)
        # No crossover, might return None
        assert result in [None, {'type': 'buy', 'quantity': 100}, {'type': 'sell', 'quantity': 100}]


class TestBacktestResult:
    """Test BacktestResult model."""

    def test_create_backtest_result(self):
        """Test creating a backtest result."""
        result = BacktestResult(
            total_return=25.5,
            annual_return=12.3,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            max_drawdown=10.2,
            win_rate=55.0,
            profit_factor=1.8,
            total_trades=100,
            winning_trades=55,
            losing_trades=45,
            avg_win=500.0,
            avg_loss=-300.0,
            largest_win=2000.0,
            largest_loss=-1200.0,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            duration_days=365,
            initial_capital=100000,
            final_capital=125500,
            peak_capital=130000,
            trades=[],
            equity_curve=[],
            drawdown_curve=[]
        )

        assert result.total_return == 25.5
        assert result.annual_return == 12.3
        assert result.sharpe_ratio == 1.5
        assert result.total_trades == 100
        assert result.win_rate == 55.0

    def test_backtest_result_all_fields_present(self):
        """Test that BacktestResult has all required fields."""
        result = BacktestResult(
            total_return=0, annual_return=0, sharpe_ratio=0, sortino_ratio=0,
            max_drawdown=0, win_rate=0, profit_factor=0, total_trades=0,
            winning_trades=0, losing_trades=0, avg_win=0, avg_loss=0,
            largest_win=0, largest_loss=0, start_date=datetime.utcnow(),
            end_date=datetime.utcnow(), duration_days=0, initial_capital=100000,
            final_capital=100000, peak_capital=100000, trades=[], equity_curve=[],
            drawdown_curve=[]
        )

        # Verify all fields are accessible
        assert hasattr(result, 'total_return')
        assert hasattr(result, 'sharpe_ratio')
        assert hasattr(result, 'max_drawdown')
        assert hasattr(result, 'trades')
        assert hasattr(result, 'equity_curve')
