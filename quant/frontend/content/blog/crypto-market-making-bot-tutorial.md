---
title: 'Crypto Market Making Bot: Build High-Frequency Trading Systems'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: crypto-market-making-bot-tutorial
published_date: '2026-04-16'
last_updated: '2026-04-16'
---

# Crypto Market Making Bot: Build High-Frequency Trading Systems

Market making provides liquidity to exchanges while generating profits from the bid-ask spread. This guide covers building sophisticated market-making bots that manage inventory and dynamically adjust quotes.

## Market Making Fundamentals

Market makers profit by buying at the bid and selling at the ask, keeping the difference. Success requires:
- Accurate mid-price estimation
- Inventory management to avoid large directional exposure
- Quick response to changing market conditions
- Risk management to prevent losses

## Building the Core Market Making Bot

```python
import ccxt
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Quote:
    """Market maker quote"""
    timestamp: datetime
    symbol: str
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
    mid_price: float
    spread: float

class InventoryLevel(Enum):
    """Inventory classification"""
    LONG = "LONG"
    NEUTRAL = "NEUTRAL"
    SHORT = "SHORT"

class MarketMakingBot:
    """Core market making bot implementation"""

    def __init__(self, exchange, symbol: str = 'BTC/USDT',
                 target_spread: float = 0.0005, inventory_limit: float = 10.0):
        """
        Initialize market making bot

        Args:
            exchange: CCXT exchange instance
            symbol: Trading pair
            target_spread: Target bid-ask spread (0.05%)
            inventory_limit: Max position size in base currency
        """
        self.exchange = exchange
        self.symbol = symbol
        self.target_spread = target_spread
        self.inventory_limit = inventory_limit

        self.current_inventory = 0
        self.active_orders = {}
        self.quote_history = []
        self.pnl = 0

    async def get_market_data(self) -> Dict:
        """Fetch current market data"""

        try:
            # Get last trade price
            ticker = await self.exchange.fetch_ticker(self.symbol)

            # Get order book
            orderbook = await self.exchange.fetch_order_book(self.symbol, limit=20)

            return {
                'last_price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'orderbook': orderbook,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return None

    def estimate_fair_price(self, market_data: Dict) -> float:
        """Estimate fair price from market data"""

        orderbook = market_data['orderbook']

        # Calculate weighted mid-price from top of book
        best_bid = orderbook['bids'][0][0] if orderbook['bids'] else market_data['bid']
        best_ask = orderbook['asks'][0][0] if orderbook['asks'] else market_data['ask']

        # Simple mid-price
        fair_price = (best_bid + best_ask) / 2

        # Adjust for inventory
        inventory_adjustment = self._calculate_inventory_adjustment(fair_price)
        fair_price += inventory_adjustment

        return fair_price

    def _calculate_inventory_adjustment(self, fair_price: float) -> float:
        """Adjust fair price based on inventory"""

        inventory_ratio = self.current_inventory / self.inventory_limit

        # If we're long, increase bid (want to sell), decrease ask (encourage buying)
        if inventory_ratio > 0:
            return fair_price * 0.0002 * inventory_ratio

        # If we're short, increase ask (want to sell), decrease bid (discourage selling)
        elif inventory_ratio < 0:
            return fair_price * 0.0002 * inventory_ratio

        return 0

    def calculate_quotes(self, fair_price: float,
                        spread_multiplier: float = 1.0) -> Tuple[float, float, float, float]:
        """Calculate bid and ask quotes"""

        # Adjust spread based on market conditions
        spread = self.target_spread * spread_multiplier

        bid_price = fair_price * (1 - spread / 2)
        ask_price = fair_price * (1 + spread / 2)

        # Calculate sizes
        bid_size = self._calculate_order_size('BID')
        ask_size = self._calculate_order_size('ASK')

        return bid_price, ask_price, bid_size, ask_size

    def _calculate_order_size(self, side: str) -> float:
        """Calculate order size based on inventory"""

        max_size = self.inventory_limit / 4  # Max 25% of limit per order

        if side == 'BID':
            # If short, increase bid size to reduce short
            if self.current_inventory < 0:
                return max_size * (1 + abs(self.current_inventory) / self.inventory_limit)
            else:
                return max_size

        elif side == 'ASK':
            # If long, increase ask size to reduce long
            if self.current_inventory > 0:
                return max_size * (1 + self.current_inventory / self.inventory_limit)
            else:
                return max_size

        return max_size

    async def update_quotes(self):
        """Update market quotes continuously"""

        while True:
            try:
                # Get market data
                market_data = await self.get_market_data()

                if not market_data:
                    await asyncio.sleep(1)
                    continue

                # Estimate fair price
                fair_price = self.estimate_fair_price(market_data)

                # Calculate volatility to adjust spreads
                spread_multiplier = self._get_spread_multiplier(market_data)

                # Generate quotes
                bid_price, ask_price, bid_size, ask_size = self.calculate_quotes(
                    fair_price, spread_multiplier
                )

                quote = Quote(
                    timestamp=datetime.now(),
                    symbol=self.symbol,
                    bid_price=bid_price,
                    bid_size=bid_size,
                    ask_price=ask_price,
                    ask_size=ask_size,
                    mid_price=fair_price,
                    spread=(ask_price - bid_price) / fair_price
                )

                self.quote_history.append(quote)

                # Cancel old orders
                await self._cancel_all_orders()

                # Place new orders
                await self._place_orders(quote)

                logger.info(f"Quotes updated: Bid ${bid_price:.2f} ({bid_size:.4f}), "
                           f"Ask ${ask_price:.2f} ({ask_size:.4f}), "
                           f"Spread {quote.spread*100:.2f}bps, "
                           f"Inventory: {self.current_inventory:.4f}")

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Quote update error: {e}")
                await asyncio.sleep(1)

    def _get_spread_multiplier(self, market_data: Dict) -> float:
        """Adjust spread multiplier based on volatility"""

        if len(self.quote_history) < 20:
            return 1.0

        # Calculate recent volatility
        prices = [q.mid_price for q in self.quote_history[-20:]]
        returns = np.diff(np.log(prices))
        volatility = np.std(returns)

        # Increase spread in high volatility
        if volatility > 0.001:
            return 2.0
        elif volatility > 0.0005:
            return 1.5

        return 1.0

    async def _cancel_all_orders(self):
        """Cancel all active orders"""

        try:
            for order_id in list(self.active_orders.keys()):
                await self.exchange.cancel_order(order_id, self.symbol)
                del self.active_orders[order_id]

        except Exception as e:
            logger.warning(f"Failed to cancel orders: {e}")

    async def _place_orders(self, quote: Quote):
        """Place new bid and ask orders"""

        try:
            # Place bid order
            bid_order = await self.exchange.create_limit_buy_order(
                self.symbol,
                quote.bid_size,
                quote.bid_price
            )

            self.active_orders[bid_order['id']] = {
                'side': 'BUY',
                'price': quote.bid_price,
                'size': quote.bid_size
            }

            # Place ask order
            ask_order = await self.exchange.create_limit_sell_order(
                self.symbol,
                quote.ask_size,
                quote.ask_price
            )

            self.active_orders[ask_order['id']] = {
                'side': 'SELL',
                'price': quote.ask_price,
                'size': quote.ask_size
            }

        except Exception as e:
            logger.error(f"Failed to place orders: {e}")

    async def process_fill(self, order_id: str, filled_size: float, price: float):
        """Process order fills and update inventory"""

        if order_id not in self.active_orders:
            return

        order = self.active_orders[order_id]

        if order['side'] == 'BUY':
            self.current_inventory += filled_size
        else:
            self.current_inventory -= filled_size

        # Update PNL (simplified)
        mid_price = self.quote_history[-1].mid_price if self.quote_history else price
        spread_profit = abs(price - mid_price) * filled_size

        self.pnl += spread_profit

        logger.info(f"Fill: {order['side']} {filled_size} @ ${price}, "
                   f"Inventory: {self.current_inventory:.4f}, "
                   f"Spread Profit: ${spread_profit:.2f}")

        del self.active_orders[order_id]
```

## Multi-Level Quote Strategy

```python
class MultiLevelQuoteBot:
    """Place multiple bid/ask quotes at different price levels"""

    def __init__(self, exchange, symbol: str = 'BTC/USDT',
                 num_levels: int = 5, level_spacing: float = 0.0005):
        """
        Initialize multi-level quote bot

        Args:
            exchange: CCXT exchange
            symbol: Trading pair
            num_levels: Number of bid/ask quotes
            level_spacing: Price spacing between levels
        """
        self.exchange = exchange
        self.symbol = symbol
        self.num_levels = num_levels
        self.level_spacing = level_spacing
        self.quotes = {}

    async def place_multi_level_quotes(self, fair_price: float,
                                      base_spread: float = 0.0005):
        """Place multiple quotes at different levels"""

        try:
            # Cancel existing quotes
            await self._cancel_all_quotes()

            quotes = []

            for level in range(self.num_levels):
                # Bid quotes (below mid)
                bid_price = fair_price * (1 - (level + 0.5) * self.level_spacing)
                bid_size = 1.0 / (level + 1)  # Decrease size further out

                bid_order = await self.exchange.create_limit_buy_order(
                    self.symbol, bid_size, bid_price
                )

                quotes.append({
                    'id': bid_order['id'],
                    'side': 'BID',
                    'price': bid_price,
                    'size': bid_size,
                    'level': level + 1
                })

                # Ask quotes (above mid)
                ask_price = fair_price * (1 + (level + 0.5) * self.level_spacing)
                ask_size = 1.0 / (level + 1)

                ask_order = await self.exchange.create_limit_sell_order(
                    self.symbol, ask_size, ask_price
                )

                quotes.append({
                    'id': ask_order['id'],
                    'side': 'ASK',
                    'price': ask_price,
                    'size': ask_size,
                    'level': level + 1
                })

            self.quotes = {q['id']: q for q in quotes}

            logger.info(f"Placed {len(quotes)} quotes around ${fair_price:.2f}")

        except Exception as e:
            logger.error(f"Failed to place multi-level quotes: {e}")

    async def _cancel_all_quotes(self):
        """Cancel all active quotes"""

        try:
            for order_id in list(self.quotes.keys()):
                await self.exchange.cancel_order(order_id, self.symbol)

            self.quotes = {}

        except Exception as e:
            logger.warning(f"Failed to cancel quotes: {e}")
```

## Inventory Risk Management

```python
class MarketMakingRiskManager:
    """Manage risks in market making"""

    def __init__(self, max_inventory: float = 10.0,
                 max_inventory_vega: float = 5000):
        """
        Initialize risk manager

        Args:
            max_inventory: Max position size
            max_inventory_vega: Max inventory volatility exposure
        """
        self.max_inventory = max_inventory
        self.max_inventory_vega = max_inventory_vega
        self.inventory_history = []
        self.pnl_history = []

    def check_inventory_limits(self, current_inventory: float) -> bool:
        """Check if inventory is within limits"""

        if abs(current_inventory) > self.max_inventory:
            return False

        return True

    def get_inventory_urgency(self, current_inventory: float) -> float:
        """Calculate how urgently to rebalance inventory"""

        ratio = abs(current_inventory) / self.max_inventory

        if ratio > 0.8:
            return 1.0  # Very urgent
        elif ratio > 0.5:
            return 0.5
        else:
            return 0.0  # Not urgent

    def adjust_quotes_for_inventory(self, current_inventory: float,
                                   fair_price: float,
                                   base_spread: float) -> Tuple[float, float]:
        """Adjust bid/ask based on inventory"""

        urgency = self.get_inventory_urgency(current_inventory)

        if current_inventory > 0:
            # Long inventory - want to sell
            bid_adjust = base_spread * (1 + urgency)
            ask_adjust = base_spread * (1 - urgency)

        else:
            # Short inventory - want to buy
            bid_adjust = base_spread * (1 - urgency)
            ask_adjust = base_spread * (1 + urgency)

        adjusted_bid = fair_price * (1 - bid_adjust / 2)
        adjusted_ask = fair_price * (1 + ask_adjust / 2)

        return adjusted_bid, adjusted_ask
```

## P&L Tracking and Analysis

```python
class MarketMakerAnalytics:
    """Analyze market making performance"""

    def __init__(self):
        self.trades = []
        self.inventory_snapshots = []
        self.quote_events = []

    def log_trade(self, side: str, size: float, price: float,
                 mid_price: float):
        """Log completed trade"""

        spread_profit = (mid_price - price if side == 'SELL' else price - mid_price) * size

        self.trades.append({
            'timestamp': datetime.now(),
            'side': side,
            'size': size,
            'price': price,
            'mid_price': mid_price,
            'spread_profit': spread_profit
        })

    def calculate_daily_metrics(self) -> Dict:
        """Calculate daily performance metrics"""

        if not self.trades:
            return {}

        total_spread_profit = sum(t['spread_profit'] for t in self.trades)
        total_volume = sum(t['size'] for t in self.trades)
        num_trades = len(self.trades)

        return {
            'total_spread_profit': total_spread_profit,
            'total_volume': total_volume,
            'num_trades': num_trades,
            'avg_spread_profit_per_trade': total_spread_profit / num_trades if num_trades > 0 else 0,
            'avg_profit_per_unit_volume': total_spread_profit / total_volume if total_volume > 0 else 0
        }
```

## Conclusion

Successful market making requires careful balance between aggressive quoting to capture volume and defensive quoting to manage inventory and risk. The key metrics to monitor are spread width relative to volatility, inventory turnover, and profit per unit of time exposed.

Start with small position sizes and gradually increase as your bot demonstrates consistent profitability.
