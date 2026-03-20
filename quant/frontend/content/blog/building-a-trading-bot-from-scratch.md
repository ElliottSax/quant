---
title: 'Building a Trading Bot from Scratch: A Complete Step-by-Step Guide'
slug: building-a-trading-bot-from-scratch
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-03-20'
last_updated: '2026-03-20'
---

# Building a Trading Bot from Scratch: A Complete Step-by-Step Guide

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

Building a trading bot from scratch allows you to understand every component of your trading system and customize it exactly to your needs. This comprehensive guide covers architecture, data handling, strategy development, and deployment of a production-grade trading bot that you control completely.

## Architecture Overview

A robust trading bot consists of several interconnected components: data ingestion, signal generation, risk management, order execution, and monitoring.

```python
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class OHLCV:
    """Open, High, Low, Close, Volume candle data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class Trade:
    """Represents an executed trade"""
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    timestamp: datetime
    commission: float = 0.0

@dataclass
class Position:
    """Current position for a symbol"""
    symbol: str
    quantity: int
    entry_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
```

## Data Handler Component

The foundation of any trading bot is reliable, real-time data.

```python
import yfinance as yf
import websocket
import json
from threading import Thread

class DataHandler(ABC):
    """Abstract base class for data handlers"""

    @abstractmethod
    async def get_historical_data(self, symbol: str, days: int) -> List[OHLCV]:
        pass

    @abstractmethod
    async def get_realtime_data(self, symbols: List[str], callback):
        pass

class YFinanceDataHandler(DataHandler):
    """Fetch data from Yahoo Finance"""

    async def get_historical_data(self, symbol: str, days: int = 100) -> List[OHLCV]:
        """Fetch historical OHLCV data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = yf.download(symbol, start=start_date, end=end_date, progress=False)

            candles = []
            for idx, row in df.iterrows():
                candle = OHLCV(
                    timestamp=idx.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                )
                candles.append(candle)

            logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return []

    async def get_realtime_data(self, symbols: List[str], callback):
        """Fetch real-time data (polling approach for simplicity)"""
        while True:
            try:
                for symbol in symbols:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='1d')
                    if not data.empty:
                        latest = data.iloc[-1]
                        await callback({
                            'symbol': symbol,
                            'price': float(latest['Close']),
                            'high': float(latest['High']),
                            'low': float(latest['Low']),
                            'volume': float(latest['Volume']),
                            'timestamp': datetime.now()
                        })

                await asyncio.sleep(60)  # Poll every 60 seconds

            except Exception as e:
                logger.error(f"Error in realtime data loop: {e}")
                await asyncio.sleep(60)

class AlpacaDataHandler(DataHandler):
    """Fetch data from Alpaca API"""

    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url

    async def get_historical_data(self, symbol: str, days: int = 100) -> List[OHLCV]:
        """Fetch historical data from Alpaca"""
        import requests

        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key
        }

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        url = f"{self.base_url}/v1/bars?symbols={symbol}&timeframe=1Day&start={start_date.isoformat()}&end={end_date.isoformat()}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            candles = []
            for bar in data['bars'][symbol]:
                candle = OHLCV(
                    timestamp=datetime.fromisoformat(bar['t']),
                    open=float(bar['o']),
                    high=float(bar['h']),
                    low=float(bar['l']),
                    close=float(bar['c']),
                    volume=float(bar['v'])
                )
                candles.append(candle)

            return candles

        except Exception as e:
            logger.error(f"Error fetching Alpaca data: {e}")
            return []
```

## Strategy Development Framework

Trading strategies are the core of your bot. Here's how to structure them.

```python
class TradingStrategy(ABC):
    """Base class for trading strategies"""

    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name
        self.data_points = []

    @abstractmethod
    def calculate_signal(self) -> Optional[str]:
        """
        Generate trading signal: 'BUY', 'SELL', or None
        """
        pass

    def add_candle(self, candle: OHLCV):
        """Add a new candle to analysis"""
        self.data_points.append(candle)

    def get_latest_candles(self, count: int) -> List[OHLCV]:
        """Get the last N candles"""
        return self.data_points[-count:] if len(self.data_points) >= count else self.data_points

class MovingAverageCrossover(TradingStrategy):
    """Simple moving average crossover strategy"""

    def __init__(self, symbol: str, short_window: int = 20, long_window: int = 50):
        super().__init__(symbol, "MA Crossover")
        self.short_window = short_window
        self.long_window = long_window
        self.last_signal = None

    def calculate_signal(self) -> Optional[str]:
        """Generate signal based on MA crossover"""
        if len(self.data_points) < self.long_window:
            return None

        closes = [c.close for c in self.data_points]

        # Calculate moving averages
        sma_short = sum(closes[-self.short_window:]) / self.short_window
        sma_long = sum(closes[-self.long_window:]) / self.long_window

        # Get previous values for crossover detection
        if len(self.data_points) >= self.long_window + 1:
            prev_closes = [c.close for c in self.data_points[-(self.long_window + 1):-1]]
            prev_sma_short = sum(prev_closes[-self.short_window:]) / self.short_window
            prev_sma_long = sum(prev_closes[-self.long_window:]) / self.long_window

            # Golden cross
            if prev_sma_short <= prev_sma_long and sma_short > sma_long:
                signal = 'BUY'
            # Death cross
            elif prev_sma_short >= prev_sma_long and sma_short < sma_long:
                signal = 'SELL'
            else:
                signal = None

            # Avoid repeated signals
            if signal != self.last_signal:
                self.last_signal = signal
                return signal

        return None

class RSIStrategy(TradingStrategy):
    """Relative Strength Index mean reversion strategy"""

    def __init__(self, symbol: str, rsi_period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__(symbol, "RSI Strategy")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def calculate_rsi(self) -> Optional[float]:
        """Calculate RSI indicator"""
        if len(self.data_points) < self.rsi_period:
            return None

        closes = [c.close for c in self.data_points[-self.rsi_period:]]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]

        gains = sum(d for d in deltas if d > 0) / self.rsi_period
        losses = -sum(d for d in deltas if d < 0) / self.rsi_period

        if losses == 0:
            return 100.0 if gains > 0 else 0.0

        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_signal(self) -> Optional[str]:
        """Generate signal based on RSI"""
        rsi = self.calculate_rsi()

        if rsi is None:
            return None

        if rsi < self.oversold:
            return 'BUY'
        elif rsi > self.overbought:
            return 'SELL'

        return None

class CombinedStrategy(TradingStrategy):
    """Combine multiple strategies for more robust signals"""

    def __init__(self, symbol: str, strategies: List[TradingStrategy]):
        super().__init__(symbol, "Combined")
        self.strategies = strategies

    def add_candle(self, candle: OHLCV):
        """Add candle to all strategies"""
        super().add_candle(candle)
        for strategy in self.strategies:
            strategy.add_candle(candle)

    def calculate_signal(self) -> Optional[str]:
        """Generate signal when majority of strategies agree"""
        signals = []
        for strategy in self.strategies:
            signal = strategy.calculate_signal()
            if signal:
                signals.append(signal)

        if not signals:
            return None

        # Require majority agreement
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')

        if buy_count > len(self.strategies) / 2:
            return 'BUY'
        elif sell_count > len(self.strategies) / 2:
            return 'SELL'

        return None
```

## Risk Management System

Proper risk management is essential for long-term profitability.

```python
class RiskManager:
    """Manage portfolio-level and position-level risk"""

    def __init__(self, initial_capital: float, max_drawdown: float = 0.10,
                 max_position_size: float = 0.05, risk_per_trade: float = 0.02):
        self.initial_capital = initial_capital
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade
        self.current_equity = initial_capital
        self.peak_equity = initial_capital
        self.positions = {}

    def update_equity(self, new_equity: float):
        """Update current equity value"""
        self.current_equity = new_equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity

    def get_max_position_size(self, account_value: float, price: float) -> int:
        """Calculate maximum position size"""
        max_dollars = account_value * self.max_position_size
        return int(max_dollars / price)

    def get_position_size_for_risk(self, account_value: float, entry_price: float,
                                   stop_price: float) -> int:
        """Calculate position size based on risk amount"""
        risk_amount = account_value * self.risk_per_trade
        price_risk = abs(entry_price - stop_price)

        if price_risk == 0:
            return 0

        shares = int(risk_amount / price_risk)
        max_shares = self.get_max_position_size(account_value, entry_price)

        return min(shares, max_shares)

    def check_drawdown_limit(self) -> bool:
        """Check if drawdown limit exceeded"""
        drawdown = (self.peak_equity - self.current_equity) / self.peak_equity

        if drawdown > self.max_drawdown:
            logger.warning(f"Drawdown limit exceeded: {drawdown:.2%}")
            return False

        return True

    def can_add_position(self, symbol: str, size: int) -> bool:
        """Check if new position can be added"""
        current_size = self.positions.get(symbol, 0)
        total_exposed = len(self.positions) + (1 if symbol not in self.positions else 0)

        if total_exposed > 10:
            logger.warning("Too many open positions")
            return False

        return True

    def add_position(self, symbol: str, size: int):
        """Record a new position"""
        self.positions[symbol] = size
        logger.info(f"Position added: {symbol} x{size}")

    def remove_position(self, symbol: str):
        """Close a position"""
        if symbol in self.positions:
            del self.positions[symbol]
            logger.info(f"Position closed: {symbol}")
```

## Order Execution Engine

The execution engine handles order placement and tracking.

```python
class OrderExecutor(ABC):
    """Abstract order execution interface"""

    @abstractmethod
    async def place_market_order(self, symbol: str, side: str, quantity: int) -> str:
        pass

    @abstractmethod
    async def place_limit_order(self, symbol: str, side: str, quantity: int, price: float) -> str:
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        pass

class SimulatedExecutor(OrderExecutor):
    """Simulated order execution for backtesting"""

    def __init__(self):
        self.orders = {}
        self.next_order_id = 1
        self.balance = 100000
        self.positions = {}

    async def place_market_order(self, symbol: str, side: str, quantity: int) -> str:
        """Place a market order (simulated)"""
        order_id = str(self.next_order_id)
        self.next_order_id += 1

        self.orders[order_id] = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': 'MARKET',
            'status': 'FILLED',
            'timestamp': datetime.now()
        }

        logger.info(f"Order {order_id}: {side} {quantity} {symbol}")
        return order_id

    async def place_limit_order(self, symbol: str, side: str, quantity: int, price: float) -> str:
        """Place a limit order"""
        order_id = str(self.next_order_id)
        self.next_order_id += 1

        self.orders[order_id] = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'type': 'LIMIT',
            'status': 'PENDING',
            'timestamp': datetime.now()
        }

        logger.info(f"Order {order_id}: {side} {quantity} {symbol} @ {price}")
        return order_id

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'CANCELLED'
            logger.info(f"Order {order_id} cancelled")
            return True
        return False

class AlpacaExecutor(OrderExecutor):
    """Live order execution via Alpaca"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        import requests
        self.session = requests.Session()
        self.base_url = "https://api.alpaca.markets/v2"

        self.session.headers.update({
            'APCA-API-KEY-ID': api_key,
            'APCA-API-SECRET-KEY': secret_key
        })

    async def place_market_order(self, symbol: str, side: str, quantity: int) -> str:
        """Place live market order"""
        data = {
            'symbol': symbol,
            'qty': quantity,
            'side': side.lower(),
            'type': 'market',
            'time_in_force': 'day'
        }

        try:
            response = self.session.post(f"{self.base_url}/orders", json=data)
            response.raise_for_status()
            order = response.json()
            logger.info(f"Order placed: {order['id']}")
            return order['id']

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None

    async def place_limit_order(self, symbol: str, side: str, quantity: int, price: float) -> str:
        """Place limit order"""
        data = {
            'symbol': symbol,
            'qty': quantity,
            'side': side.lower(),
            'type': 'limit',
            'limit_price': price,
            'time_in_force': 'day'
        }

        try:
            response = self.session.post(f"{self.base_url}/orders", json=data)
            response.raise_for_status()
            order = response.json()
            return order['id']

        except Exception as e:
            logger.error(f"Failed to place limit order: {e}")
            return None

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.session.delete(f"{self.base_url}/orders/{order_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return False
```

## Main Trading Bot Orchestrator

Now let's bring everything together into the main bot.

```python
class TradingBot:
    """Main trading bot orchestrator"""

    def __init__(self, symbols: List[str], initial_capital: float = 100000):
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.current_equity = initial_capital
        self.data_handler = YFinanceDataHandler()
        self.executor = SimulatedExecutor()
        self.risk_manager = RiskManager(initial_capital)
        self.strategies = {}
        self.trades = []
        self.running = False

        # Initialize strategies for each symbol
        for symbol in symbols:
            self.strategies[symbol] = CombinedStrategy(
                symbol,
                [
                    MovingAverageCrossover(symbol),
                    RSIStrategy(symbol)
                ]
            )

    async def fetch_and_update_data(self):
        """Fetch data and update all strategies"""
        for symbol in self.symbols:
            candles = await self.data_handler.get_historical_data(symbol, days=100)

            for candle in candles:
                self.strategies[symbol].add_candle(candle)

    async def process_symbol(self, symbol: str):
        """Process trading signal for a single symbol"""
        strategy = self.strategies[symbol]
        signal = strategy.calculate_signal()

        if signal is None:
            return

        current_price = strategy.data_points[-1].close if strategy.data_points else 0
        account_value = self.current_equity

        if signal == 'BUY':
            # Calculate position size
            stop_price = current_price * 0.97
            qty = self.risk_manager.get_position_size_for_risk(
                account_value, current_price, stop_price
            )

            if qty > 0 and self.risk_manager.can_add_position(symbol, qty):
                order_id = await self.executor.place_market_order(symbol, 'BUY', qty)

                if order_id:
                    self.risk_manager.add_position(symbol, qty)
                    self.trades.append({
                        'symbol': symbol,
                        'side': 'BUY',
                        'quantity': qty,
                        'price': current_price,
                        'timestamp': datetime.now()
                    })

                    logger.info(f"BUY signal: {symbol} x{qty} @ {current_price}")

        elif signal == 'SELL':
            if symbol in self.risk_manager.positions:
                qty = self.risk_manager.positions[symbol]
                order_id = await self.executor.place_market_order(symbol, 'SELL', qty)

                if order_id:
                    self.risk_manager.remove_position(symbol)
                    self.trades.append({
                        'symbol': symbol,
                        'side': 'SELL',
                        'quantity': qty,
                        'price': current_price,
                        'timestamp': datetime.now()
                    })

                    logger.info(f"SELL signal: {symbol} x{qty} @ {current_price}")

    async def run(self):
        """Main trading loop"""
        self.running = True
        logger.info("Trading bot started")

        # Initial data fetch
        await self.fetch_and_update_data()

        while self.running:
            try:
                # Update data
                await self.fetch_and_update_data()

                # Check risk limits
                if not self.risk_manager.check_drawdown_limit():
                    logger.warning("Stopping bot due to drawdown limit")
                    break

                # Process each symbol
                for symbol in self.symbols:
                    await self.process_symbol(symbol)

                # Log status
                logger.info(f"Equity: ${self.current_equity:.2f}")

                # Wait before next iteration
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the trading bot"""
        self.running = False
        logger.info("Trading bot stopped")

    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        total_trades = len(self.trades)
        buy_trades = [t for t in self.trades if t['side'] == 'BUY']
        sell_trades = [t for t in self.trades if t['side'] == 'SELL']

        return {
            'total_trades': total_trades,
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'current_equity': self.current_equity,
            'total_return': (self.current_equity - self.initial_capital) / self.initial_capital,
            'positions': self.risk_manager.positions
        }

# Run the bot
async def main():
    bot = TradingBot(['AAPL', 'MSFT', 'GOOGL', 'TSLA'])

    # Run for a period or until interrupted
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot interrupted")
    finally:
        bot.stop()
        report = bot.get_performance_report()
        print("\n=== Performance Report ===")
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

## Backtesting Framework

Test your bot thoroughly before deploying real capital.

```python
class Backtester:
    """Backtest trading bot performance"""

    def __init__(self, bot: TradingBot, start_date: datetime, end_date: datetime):
        self.bot = bot
        self.start_date = start_date
        self.end_date = end_date
        self.equity_curve = []

    async def run_backtest(self) -> Dict:
        """Run complete backtest"""
        logger.info(f"Starting backtest: {self.start_date} to {self.end_date}")

        await self.bot.run()

        report = self.bot.get_performance_report()
        report['start_date'] = self.start_date.isoformat()
        report['end_date'] = self.end_date.isoformat()

        return report
```

## Conclusion

Building a trading bot from scratch gives you complete control and deep understanding of every component. Start simple with a single strategy and one symbol, test thoroughly, and gradually increase complexity. The architecture provided here scales to handle multiple strategies, symbols, and asset classes.

Key principles:
- Separate concerns: data, strategy, execution, risk management
- Test extensively before deploying capital
- Monitor performance continuously
- Implement strict risk controls
- Iterate and improve based on real results

With this foundation, you can build trading systems that match your trading style and market outlook.
