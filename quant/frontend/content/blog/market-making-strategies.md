---
title: "Market Making Strategies: Providing Liquidity for Profit"
description: "Build quantitative market making strategies. Inventory management, quote optimization, adverse selection, and risk controls for automated market makers."
date: "2026-04-15"
author: "Dr. James Chen"
category: "Trading Strategies"
tags: ["market making", "liquidity provision", "bid-ask spread", "inventory management", "HFT"]
keywords: ["market making strategies", "automated market maker", "liquidity provision trading"]
---
# Market Making Strategies: Providing Liquidity for Profit

Market makers earn the bid-ask spread by continuously quoting prices at which they are willing to buy and sell. In exchange for providing liquidity to other participants, market makers capture a small profit on each transaction. While the per-trade profit is tiny (often fractions of a cent), the high volume of transactions makes market making one of the most consistently profitable [trading strategies](/blog/backtesting-trading-strategies) when executed well.

The challenge is managing inventory risk (accumulating unwanted positions) and adverse selection (trading against informed counterparties who know something you don't). This guide covers the quantitative models and risk controls that separate profitable market makers from those who donate money to informed traders.

## Key Takeaways

- **Market making profits come from the bid-ask spread**, not from directional views. The goal is to buy at the bid and sell at the ask repeatedly.
- **Inventory management is the core challenge.** Accumulating a large position exposes the market maker to directional risk.
- **Adverse selection** from informed traders is the primary cost. Adjusting quotes based on order flow toxicity reduces this cost.
- **Risk controls are non-negotiable.** Position limits, loss limits, and kill switches prevent catastrophic losses.

## Quote Pricing Model

The Avellaneda-Stoikov model provides the theoretical foundation for optimal market making quotes.

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AvellanedaStoikov:
    """
    Avellaneda-Stoikov optimal market making model.

    The model computes the reservation price (fair value adjusted
    for inventory) and the optimal bid-ask spread as functions of:
    - Current inventory
    - Volatility
    - Risk aversion
    - Time horizon
    """
    sigma: float = 0.02         # Volatility (per period)
    gamma: float = 0.1          # Risk aversion
    kappa: float = 1.5          # Order arrival intensity
    T: float = 1.0              # Time horizon
    dt: float = 1/390           # Time step (1 minute in 6.5hr day)

    def reservation_price(
        self, mid: float, inventory: int, t: float
    ) -> float:
        """
        Compute the reservation price (indifference price).
        Adjusted downward when long, upward when short.

        r(s,q,t) = s - q * gamma * sigma^2 * (T - t)
        """
        return mid - inventory * self.gamma * self.sigma**2 * (self.T - t)

    def optimal_spread(self, t: float) -> float:
        """
        Compute the optimal bid-ask spread.

        delta(t) = gamma * sigma^2 * (T - t) + (2/gamma) * ln(1 + gamma/kappa)
        """
        return (
            self.gamma * self.sigma**2 * (self.T - t)
            + (2 / self.gamma) * np.log(1 + self.gamma / self.kappa)
        )

    def compute_quotes(
        self, mid: float, inventory: int, t: float
    ) -> dict:
        """Compute optimal bid and ask quotes."""
        r = self.reservation_price(mid, inventory, t)
        spread = self.optimal_spread(t)

        bid = r - spread / 2
        ask = r + spread / 2

        return {
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "reservation_price": r,
            "spread": spread,
            "inventory_adjustment": mid - r,
        }


class MarketMaker:
    """
    Automated market making engine with inventory management.
    """

    def __init__(
        self,
        model: AvellanedaStoikov = None,
        max_inventory: int = 100,
        max_loss: float = 1000,
        min_spread_bps: float = 2.0,
    ):
        self.model = model or AvellanedaStoikov()
        self.max_inventory = max_inventory
        self.max_loss = max_loss
        self.min_spread_bps = min_spread_bps

        # State
        self.inventory = 0
        self.pnl = 0
        self.avg_cost = 0
        self.trade_count = 0
        self.quote_history = []
        self.trade_history = []

    def generate_quotes(
        self, mid: float, t: float
    ) -> dict:
        """Generate bid/ask quotes with risk controls."""

        # Base quotes from model
        quotes = self.model.compute_quotes(mid, self.inventory, t)

        # Enforce minimum spread
        min_spread = mid * self.min_spread_bps / 10_000
        if quotes["spread"] < min_spread:
            adjustment = (min_spread - quotes["spread"]) / 2
            quotes["bid"] -= adjustment
            quotes["ask"] += adjustment
            quotes["spread"] = min_spread

        # Inventory skew: widen the side that would increase inventory
        if self.inventory >= self.max_inventory:
            quotes["bid"] = 0  # Stop buying
        elif self.inventory <= -self.max_inventory:
            quotes["ask"] = float("inf")  # Stop selling

        # Loss limit
        unrealized = self.inventory * (mid - self.avg_cost) if self.inventory != 0 else 0
        total_pnl = self.pnl + unrealized
        if total_pnl < -self.max_loss:
            quotes["bid"] = 0
            quotes["ask"] = float("inf")
            quotes["halted"] = True
        else:
            quotes["halted"] = False

        self.quote_history.append({
            "t": t, "mid": mid,
            "bid": quotes["bid"], "ask": quotes["ask"],
            "inventory": self.inventory, "pnl": total_pnl,
        })

        return quotes

    def process_fill(
        self, price: float, quantity: int, side: str
    ):
        """Process a trade fill."""
        if side == "buy":
            # We bought (someone hit our bid)
            if self.inventory >= 0:
                total_cost = self.avg_cost * self.inventory + price * quantity
                self.inventory += quantity
                self.avg_cost = total_cost / self.inventory if self.inventory > 0 else 0
            else:
                # Closing short position
                self.pnl += (self.avg_cost - price) * min(quantity, abs(self.inventory))
                self.inventory += quantity
                if self.inventory > 0:
                    self.avg_cost = price
        elif side == "sell":
            # We sold (someone lifted our ask)
            if self.inventory <= 0:
                total_cost = abs(self.avg_cost * self.inventory) + price * quantity
                self.inventory -= quantity
                self.avg_cost = total_cost / abs(self.inventory) if self.inventory != 0 else 0
            else:
                # Closing long position
                self.pnl += (price - self.avg_cost) * min(quantity, self.inventory)
                self.inventory -= quantity
                if self.inventory < 0:
                    self.avg_cost = price

        self.trade_count += 1
        self.trade_history.append({
            "price": price, "quantity": quantity, "side": side,
            "inventory_after": self.inventory, "pnl_after": self.pnl,
        })
```

## Adverse Selection Detection

Detecting when incoming order flow is toxic (informed) is critical for survival.

```python
class AdverseSelectionDetector:
    """
    Detect adverse selection (informed flow) from order flow patterns.
    """

    def __init__(self, lookback: int = 100):
        self.lookback = lookback
        self.trades = []

    def add_trade(
        self, price: float, quantity: int, side: str,
        mid_before: float, mid_after: float
    ):
        """Record a trade for analysis."""
        self.trades.append({
            "price": price,
            "quantity": quantity,
            "side": side,
            "mid_before": mid_before,
            "mid_after": mid_after,
            "adverse_move": (
                (mid_after - price) if side == "buy"
                else (price - mid_after)
            ),
        })

    def compute_vpin(self, volume_buckets: pd.Series) -> pd.Series:
        """
        Volume-Synchronized Probability of Informed Trading (VPIN).
        Measures the imbalance between buy and sell volume.

        High VPIN = high probability of informed trading.
        """
        bucket_size = volume_buckets.median()

        buy_volume = volume_buckets.where(volume_buckets > 0, 0)
        sell_volume = volume_buckets.where(volume_buckets < 0, 0).abs()

        # Rolling VPIN
        n = self.lookback
        vpin = (
            (buy_volume.rolling(n).sum() - sell_volume.rolling(n).sum()).abs()
            / (buy_volume.rolling(n).sum() + sell_volume.rolling(n).sum())
        )

        return vpin

    def compute_toxicity_score(self) -> float:
        """
        Compute a toxicity score from recent trades.
        High score = high adverse selection risk.
        """
        if len(self.trades) < 10:
            return 0.5

        recent = self.trades[-self.lookback:]
        df = pd.DataFrame(recent)

        # 1. Adverse move ratio (how often does mid move against us)
        adverse_pct = (df["adverse_move"] < 0).mean()

        # 2. Average adverse move magnitude
        avg_adverse = df["adverse_move"].mean()

        # 3. Buy/sell imbalance
        buy_vol = df[df["side"] == "buy"]["quantity"].sum()
        sell_vol = df[df["side"] == "sell"]["quantity"].sum()
        total_vol = buy_vol + sell_vol
        imbalance = abs(buy_vol - sell_vol) / max(total_vol, 1)

        # Composite toxicity score [0, 1]
        toxicity = 0.4 * adverse_pct + 0.3 * imbalance + 0.3 * min(1, abs(avg_adverse) * 100)

        return np.clip(toxicity, 0, 1)

    def adjust_spread(
        self, base_spread: float, toxicity: float
    ) -> float:
        """Widen spread when toxicity is high."""
        # Multiply spread by toxicity factor
        multiplier = 1 + 2 * max(0, toxicity - 0.3)
        return base_spread * multiplier
```

## Market Making Simulation

```python
def simulate_market_making(
    prices: pd.Series,
    volatility: float = 0.02,
    n_steps: int = 390,
    fill_probability: float = 0.3,
) -> dict:
    """
    Simulate a full day of market making.
    """
    mm = MarketMaker(
        model=AvellanedaStoikov(sigma=volatility, gamma=0.1, kappa=1.5),
        max_inventory=50,
        max_loss=500,
    )

    np.random.seed(42)

    for i in range(min(n_steps, len(prices))):
        mid = prices.iloc[i]
        t = i / n_steps

        # Generate quotes
        quotes = mm.generate_quotes(mid, t)

        if quotes.get("halted", False):
            continue

        # Simulate random fills
        if np.random.random() < fill_probability:
            # Someone hits our bid (we buy)
            if quotes["bid"] > 0:
                fill_price = quotes["bid"]
                mm.process_fill(fill_price, 1, "buy")

        if np.random.random() < fill_probability:
            # Someone lifts our ask (we sell)
            if quotes["ask"] < float("inf"):
                fill_price = quotes["ask"]
                mm.process_fill(fill_price, 1, "sell")

    # Final P&L (mark to market)
    final_mid = prices.iloc[-1]
    unrealized = mm.inventory * (final_mid - mm.avg_cost) if mm.inventory != 0 else 0
    total_pnl = mm.pnl + unrealized

    quote_df = pd.DataFrame(mm.quote_history)
    trade_df = pd.DataFrame(mm.trade_history) if mm.trade_history else pd.DataFrame()

    results = {
        "total_pnl": total_pnl,
        "realized_pnl": mm.pnl,
        "unrealized_pnl": unrealized,
        "final_inventory": mm.inventory,
        "total_trades": mm.trade_count,
        "avg_spread": quote_df["ask"].mean() - quote_df["bid"].mean() if len(quote_df) > 0 else 0,
        "max_inventory": quote_df["inventory"].abs().max() if len(quote_df) > 0 else 0,
        "quotes": quote_df,
        "trades": trade_df,
    }

    print(f"Market Making Simulation Results:")
    print(f"  Total P&L: ${total_pnl:.2f}")
    print(f"  Realized: ${mm.pnl:.2f} | Unrealized: ${unrealized:.2f}")
    print(f"  Total Trades: {mm.trade_count}")
    print(f"  Final Inventory: {mm.inventory}")
    print(f"  Max Inventory: {results['max_inventory']}")

    return results
```

## Risk Controls

```python
@dataclass
class MarketMakingRiskLimits:
    """Hard risk limits for market making operations."""
    max_position: int = 100
    max_notional: float = 500_000
    max_daily_loss: float = 5_000
    max_drawdown: float = 10_000
    max_message_rate: int = 100    # Orders per second
    kill_switch_loss: float = 20_000  # Emergency shutdown

    def check_limits(
        self, position: int, notional: float,
        daily_pnl: float, drawdown: float,
        message_rate: int,
    ) -> dict:
        """Check all risk limits and return violations."""
        violations = []

        if abs(position) > self.max_position:
            violations.append(f"Position limit: {position} > {self.max_position}")
        if abs(notional) > self.max_notional:
            violations.append(f"Notional limit: {notional} > {self.max_notional}")
        if daily_pnl < -self.max_daily_loss:
            violations.append(f"Daily loss limit: {daily_pnl} < -{self.max_daily_loss}")
        if drawdown > self.max_drawdown:
            violations.append(f"Drawdown limit: {drawdown} > {self.max_drawdown}")
        if message_rate > self.max_message_rate:
            violations.append(f"Message rate: {message_rate} > {self.max_message_rate}")

        kill_switch = daily_pnl < -self.kill_switch_loss

        return {
            "violations": violations,
            "n_violations": len(violations),
            "kill_switch": kill_switch,
            "can_trade": len(violations) == 0 and not kill_switch,
        }
```

## FAQ

### How much capital do I need to start market making?

For equities, institutional market makers typically deploy $10-100 million per strategy. For [crypto market making](/blog/crypto-market-making-guide) on centralized exchanges, $50,000-500,000 is sufficient to start due to lower regulatory barriers and wider spreads. The minimum capital depends on the margin requirements, position limits, and the spread-to-risk ratio of the instruments you trade. You need enough capital to absorb inventory risk during adverse periods without breaching risk limits.

### What is the biggest risk in market making?

Adverse selection is the primary ongoing risk: trading against informed counterparties who know more about the fair value than you do. However, the catastrophic risk is a technology failure or flash crash that prevents you from canceling stale quotes, resulting in massive unwanted inventory at unfavorable prices. This is why kill switches and position limits are non-negotiable.

### How do market makers handle inventory risk?

Market makers use several techniques: (1) skewing quotes to discourage trades that would increase inventory (lowering the bid when long, raising the ask when short), (2) hedging residual inventory with correlated instruments (ETFs, futures), (3) time-based urgency (more aggressive liquidation as end of day approaches), and (4) portfolio-level netting across correlated names.

### Can retail traders be market makers?

In traditional equity markets, designated market making requires regulatory approval and significant infrastructure. However, in crypto markets and DeFi, anyone can provide liquidity. On centralized crypto exchanges, you can run market making bots via API. In DeFi, providing liquidity to automated market makers (Uniswap, Curve) is a form of passive market making, though with different risk profiles ([impermanent loss](/blog/impermanent-loss-mitigation)).
