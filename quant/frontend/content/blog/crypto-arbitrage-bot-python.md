---
title: 'Crypto Arbitrage Bot with Python: Profit from Price Discrepancies'
slug: crypto-arbitrage-bot-python
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-04-16'
last_updated: '2026-04-16'
---

# Crypto Arbitrage Bot with Python: Profit from Price Discrepancies

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

Cryptocurrency markets are highly fragmented across multiple exchanges, creating regular arbitrage opportunities. This guide shows how to build an automated bot that identifies and exploits price discrepancies across crypto exchanges using Python. We'll cover exchange APIs, real-time price monitoring, and execution strategies.

## Setting Up Exchange Connections

```python
import ccxt
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import aiohttp
import json
from dataclasses import dataclass

@dataclass
class PriceQuote:
    """Represents a price quote from an exchange"""
    exchange: str
    symbol: str
    bid: float
    ask: float
    bid_volume: float
    ask_volume: float
    timestamp: datetime
    min_order_amount: float

class ExchangeConnector:
    """Connect to multiple crypto exchanges"""

    def __init__(self):
        self.exchanges = {}
        self.initialize_exchanges()

    def initialize_exchanges(self):
        """Initialize connections to major exchanges"""
        exchange_names = ['binance', 'kraken', 'coinbase', 'bitfinex', 'bybit']

        for name in exchange_names:
            try:
                exchange_class = getattr(ccxt, name)
                self.exchanges[name] = exchange_class({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
            except Exception as e:
                print(f"Failed to initialize {name}: {e}")

    async def fetch_ticker(self, exchange: str, symbol: str) -> PriceQuote:
        """Fetch ticker data from exchange"""
        try:
            exchange_obj = self.exchanges[exchange]
            ticker = await exchange_obj.fetch_ticker(symbol)

            return PriceQuote(
                exchange=exchange,
                symbol=symbol,
                bid=ticker.get('bid', 0),
                ask=ticker.get('ask', 0),
                bid_volume=ticker.get('bidVolume', 0),
                ask_volume=ticker.get('askVolume', 0),
                timestamp=datetime.now(),
                min_order_amount=exchange_obj.limits.get('amount', {}).get('min', 0.001)
            )

        except Exception as e:
            print(f"Error fetching {symbol} from {exchange}: {e}")
            return None

    async def fetch_all_tickers(self, symbol: str) -> List[PriceQuote]:
        """Fetch ticker from all exchanges"""
        tasks = []

        for exchange_name in self.exchanges.keys():
            task = self.fetch_ticker(exchange_name, symbol)
            tasks.append(task)

        quotes = await asyncio.gather(*tasks)
        return [q for q in quotes if q is not None]

    async def get_balance(self, exchange: str, asset: str) -> float:
        """Get balance of asset on exchange"""
        try:
            exchange_obj = self.exchanges[exchange]
            balance = await exchange_obj.fetch_balance()
            return balance[asset]['free']

        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0

    async def get_trading_fees(self, exchange: str) -> Dict:
        """Get trading fees for exchange"""
        try:
            exchange_obj = self.exchanges[exchange]
            fees = exchange_obj.describe().get('fees', {})
            return fees

        except Exception as e:
            print(f"Error fetching fees: {e}")
            return {}

class OrderBook:
    """Manage order book data across exchanges"""

    def __init__(self):
        self.order_books = {}
        self.update_times = {}

    def update_orderbook(self, exchange: str, symbol: str, orderbook_data: Dict):
        """Update order book for symbol"""
        key = f"{exchange}_{symbol}"
        self.order_books[key] = orderbook_data
        self.update_times[key] = datetime.now()

    def get_best_prices(self, symbol: str) -> Dict:
        """Get best bid and ask across exchanges"""
        best_bids = []
        best_asks = []

        for key, orderbook in self.order_books.items():
            if symbol in key:
                if 'bids' in orderbook and orderbook['bids']:
                    best_bids.append({
                        'exchange': key.split('_')[0],
                        'price': orderbook['bids'][0][0],
                        'volume': orderbook['bids'][0][1]
                    })

                if 'asks' in orderbook and orderbook['asks']:
                    best_asks.append({
                        'exchange': key.split('_')[0],
                        'price': orderbook['asks'][0][0],
                        'volume': orderbook['asks'][0][1]
                    })

        best_bid = max(best_bids, key=lambda x: x['price']) if best_bids else None
        best_ask = min(best_asks, key=lambda x: x['price']) if best_asks else None

        return {'best_bid': best_bid, 'best_ask': best_ask}
```

## Arbitrage Opportunity Detection

```python
class ArbitrageDetector:
    """Identify arbitrage opportunities"""

    def __init__(self, min_profit_threshold: float = 0.01):  # 1% minimum
        self.min_profit_threshold = min_profit_threshold
        self.opportunities = []

    def find_simple_arbitrage(self, quotes: List[PriceQuote]) -> List[Dict]:
        """Find simple buy-sell arbitrage"""
        opportunities = []

        # Group by exchange pairs
        for i, sell_quote in enumerate(quotes):
            for j, buy_quote in enumerate(quotes):
                if i == j:
                    continue

                # Can we buy on exchange i and sell on exchange j for profit?
                profit = self.calculate_profit(
                    buy_exchange=sell_quote.exchange,
                    buy_price=sell_quote.ask,
                    sell_exchange=buy_quote.exchange,
                    sell_price=buy_quote.bid
                )

                if profit > self.min_profit_threshold:
                    opportunities.append({
                        'type': 'simple_arbitrage',
                        'symbol': sell_quote.symbol,
                        'buy_exchange': sell_quote.exchange,
                        'buy_price': sell_quote.ask,
                        'sell_exchange': buy_quote.exchange,
                        'sell_price': buy_quote.bid,
                        'profit_pct': profit,
                        'timestamp': datetime.now()
                    })

        return opportunities

    def find_triangular_arbitrage(self, symbols: List[str],
                                  exchange: str, quotes: Dict) -> List[Dict]:
        """Find triangular arbitrage (ABC -> BCA -> CAB -> ABC)"""
        if len(symbols) < 3:
            return []

        opportunities = []

        # Example: BTC/USD -> ETH/USD -> BTC/ETH
        btc_price = quotes.get('BTC/USD', {}).get('ask', 0)
        eth_price = quotes.get('ETH/USD', {}).get('ask', 0)
        btc_eth_price = quotes.get('BTC/ETH', {}).get('ask', 0)

        if btc_price == 0 or eth_price == 0 or btc_eth_price == 0:
            return []

        # Check if triangle is profitable
        implied_btc_eth = btc_price / eth_price
        profit = (implied_btc_eth - btc_eth_price) / btc_eth_price

        if profit > self.min_profit_threshold:
            opportunities.append({
                'type': 'triangular_arbitrage',
                'exchange': exchange,
                'path': ['BTC/USD', 'ETH/USD', 'BTC/ETH'],
                'profit_pct': profit,
                'timestamp': datetime.now()
            })

        return opportunities

    def calculate_profit(self, buy_exchange: str, buy_price: float,
                        sell_exchange: str, sell_price: float,
                        trading_fee: float = 0.001) -> float:
        """Calculate profit percentage after fees"""
        total_cost = buy_price * (1 + trading_fee)
        proceeds = sell_price * (1 - trading_fee)

        profit = (proceeds - total_cost) / total_cost

        return profit

    def filter_by_volume(self, opportunities: List[Dict],
                        min_volume: float = 1.0) -> List[Dict]:
        """Filter opportunities by sufficient volume"""
        filtered = []

        for opp in opportunities:
            if 'buy_volume' in opp and 'sell_volume' in opp:
                if opp['buy_volume'] >= min_volume and opp['sell_volume'] >= min_volume:
                    filtered.append(opp)

        return filtered
```

## Execution Engine

```python
class CrossExchangeExecutor:
    """Execute arbitrage trades across exchanges"""

    def __init__(self, exchange_connector: ExchangeConnector):
        self.connector = exchange_connector
        self.executed_trades = []
        self.failed_trades = []

    async def execute_arbitrage(self, opportunity: Dict) -> Dict:
        """Execute arbitrage trade"""
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        symbol = opportunity['symbol']
        buy_price = opportunity['buy_price']
        sell_price = opportunity['sell_price']

        try:
            # Step 1: Check balances
            base_asset = symbol.split('/')[0]
            quote_asset = symbol.split('/')[1]

            buy_balance = await self.connector.get_balance(buy_exchange, quote_asset)
            sell_balance = await self.connector.get_balance(sell_exchange, base_asset)

            if buy_balance == 0:
                return {'status': 'FAILED', 'reason': 'Insufficient balance on buy exchange'}

            # Step 2: Calculate order size
            order_amount = min(buy_balance / buy_price, sell_balance) * 0.95

            if order_amount < 0.001:
                return {'status': 'FAILED', 'reason': 'Order amount too small'}

            # Step 3: Place buy order
            buy_order = await self.place_market_order(
                buy_exchange, symbol, 'buy', order_amount
            )

            if not buy_order or 'status' not in buy_order or buy_order['status'] != 'closed':
                return {'status': 'FAILED', 'reason': 'Buy order failed'}

            # Step 4: Wait for settlement (simplified - in reality use exchange streaming)
            await asyncio.sleep(2)

            # Step 5: Place sell order
            sell_order = await self.place_market_order(
                sell_exchange, symbol, 'sell', order_amount
            )

            if not sell_order or 'status' not in sell_order or sell_order['status'] != 'closed':
                return {'status': 'FAILED', 'reason': 'Sell order failed'}

            # Step 6: Calculate actual profit
            actual_profit = (sell_order['average'] - buy_order['average']) * order_amount

            result = {
                'status': 'SUCCESS',
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'symbol': symbol,
                'amount': order_amount,
                'buy_price': buy_order['average'],
                'sell_price': sell_order['average'],
                'profit': actual_profit,
                'profit_pct': (sell_order['average'] - buy_order['average']) / buy_order['average'],
                'timestamp': datetime.now()
            }

            self.executed_trades.append(result)
            return result

        except Exception as e:
            error_result = {
                'status': 'FAILED',
                'reason': str(e),
                'timestamp': datetime.now()
            }
            self.failed_trades.append(error_result)
            return error_result

    async def place_market_order(self, exchange: str, symbol: str,
                                side: str, amount: float) -> Dict:
        """Place market order on exchange"""
        try:
            exchange_obj = self.connector.exchanges[exchange]
            order = await exchange_obj.create_market_order(symbol, side, amount)
            return order

        except Exception as e:
            print(f"Error placing order on {exchange}: {e}")
            return None

    async def place_limit_order(self, exchange: str, symbol: str,
                               side: str, amount: float, price: float) -> Dict:
        """Place limit order on exchange"""
        try:
            exchange_obj = self.connector.exchanges[exchange]
            order = await exchange_obj.create_limit_order(symbol, side, amount, price)
            return order

        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None
```

## Risk Management

```python
class CryptoRiskManager:
    """Manage risks in crypto arbitrage"""

    def __init__(self, max_trade_size: float = 1.0, max_daily_loss: float = 100):
        self.max_trade_size = max_trade_size
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0
        self.trades_today = 0

    def validate_trade(self, opportunity: Dict, balance: float) -> bool:
        """Validate trade before execution"""
        # Check size
        required_capital = opportunity['buy_price'] * self.max_trade_size
        if required_capital > balance:
            return False

        # Check daily loss limit
        if self.daily_pnl < -self.max_daily_loss:
            return False

        # Check profit minimum
        if opportunity['profit_pct'] < 0.005:  # Less than 0.5%
            return False

        return True

    def update_daily_pnl(self, trade_result: Dict):
        """Update daily P&L"""
        if trade_result['status'] == 'SUCCESS':
            self.daily_pnl += trade_result['profit']
            self.trades_today += 1

    def should_stop_trading(self) -> bool:
        """Determine if should stop trading"""
        return self.daily_pnl < -self.max_daily_loss

class LatencyMonitor:
    """Monitor execution latency"""

    def __init__(self):
        self.latencies = []

    def record_latency(self, start_time: datetime, end_time: datetime):
        """Record trade latency"""
        latency_ms = (end_time - start_time).total_seconds() * 1000
        self.latencies.append(latency_ms)

    def get_stats(self) -> Dict:
        """Get latency statistics"""
        if not self.latencies:
            return {}

        return {
            'avg_latency_ms': pd.Series(self.latencies).mean(),
            'median_latency_ms': pd.Series(self.latencies).median(),
            'p95_latency_ms': pd.Series(self.latencies).quantile(0.95),
            'max_latency_ms': max(self.latencies)
        }
```

## Complete Arbitrage Bot

```python
class CryptoArbitrageBot:
    """Complete arbitrage bot"""

    def __init__(self, symbols: List[str] = None, check_interval: int = 5):
        self.symbols = symbols or ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        self.check_interval = check_interval
        self.connector = ExchangeConnector()
        self.detector = ArbitrageDetector(min_profit_threshold=0.01)
        self.executor = CrossExchangeExecutor(self.connector)
        self.risk_manager = CryptoRiskManager()
        self.latency_monitor = LatencyMonitor()
        self.running = False

    async def run(self):
        """Run arbitrage bot continuously"""
        self.running = True

        while self.running:
            try:
                start_time = datetime.now()

                # Fetch prices from all exchanges
                for symbol in self.symbols:
                    quotes = await self.connector.fetch_all_tickers(symbol)

                    # Find opportunities
                    opportunities = self.detector.find_simple_arbitrage(quotes)

                    # Execute profitable opportunities
                    for opp in opportunities:
                        if self.risk_manager.validate_trade(opp, 10000):
                            result = await self.executor.execute_arbitrage(opp)
                            self.risk_manager.update_daily_pnl(result)

                            end_time = datetime.now()
                            self.latency_monitor.record_latency(start_time, end_time)

                            print(f"Trade executed: {result}")

                    # Check if should stop
                    if self.risk_manager.should_stop_trading():
                        print("Daily loss limit reached, stopping")
                        self.stop()

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the bot"""
        self.running = False

    def get_performance_report(self) -> Dict:
        """Get performance metrics"""
        return {
            'executed_trades': len(self.executor.executed_trades),
            'failed_trades': len(self.executor.failed_trades),
            'daily_pnl': self.risk_manager.daily_pnl,
            'latency_stats': self.latency_monitor.get_stats(),
            'recent_trades': self.executor.executed_trades[-5:]
        }
```

## Backtesting Arbitrage Strategies

```python
class CryptoArbitrageBacktester:
    """Backtest arbitrage strategies"""

    def __init__(self, bot: CryptoArbitrageBot, historical_data: Dict):
        self.bot = bot
        self.historical_data = historical_data

    async def run_backtest(self) -> Dict:
        """Run backtest on historical data"""
        # Simulate with historical price data
        total_profit = 0
        trade_count = 0

        for symbol, price_data in self.historical_data.items():
            for i in range(1, len(price_data)):
                prev_price = price_data[i-1]
                curr_price = price_data[i]

                # Simulate simple spread
                if curr_price > prev_price * 1.01:  # 1% price increase
                    profit = prev_price * 0.01 - (prev_price * 0.002)  # 0.2% fees
                    total_profit += profit
                    trade_count += 1

        return {
            'total_profit': total_profit,
            'trade_count': trade_count,
            'avg_profit_per_trade': total_profit / trade_count if trade_count > 0 else 0
        }

# Run the bot
async def main():
    bot = CryptoArbitrageBot(['BTC/USDT', 'ETH/USDT'])
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Conclusion

Crypto arbitrage requires monitoring multiple exchanges, fast execution, and strict risk management. The fragmented nature of cryptocurrency markets creates regular opportunities for profitable trading. Key success factors:

1. Real-time price monitoring across exchanges
2. Rapid execution to minimize slippage
3. Careful fee accounting
4. Position management across exchange wallets
5. Continuous profitability monitoring

While simple arbitrage is becoming less profitable due to increased competition and improved market efficiency, triangular and cross-exchange arbitrage opportunities still exist for traders with robust infrastructure and careful risk management.
