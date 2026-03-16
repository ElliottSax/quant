---
title: "DeFi Quantitative Strategies: Yield Farming and Arbitrage"
description: "Build quantitative DeFi strategies for yield farming, DEX arbitrage, liquidation bots, and cross-chain arbitrage with Python and Web3."
date: "2026-04-20"
author: "Dr. James Chen"
category: "Trading Strategies"
tags: ["DeFi", "yield farming", "crypto arbitrage", "AMM", "blockchain"]
keywords: ["DeFi quantitative strategies", "yield farming optimization", "DEX arbitrage"]
---
# DeFi Quantitative Strategies: Yield Farming and Arbitrage

Decentralized finance (DeFi) has created a new frontier for [quantitative trading](/blog/crypto-quant-trading-strategies). The transparency of on-chain data, the programmability of smart contracts, and the structural inefficiencies of automated market makers (AMMs) present opportunities that are qualitatively different from traditional finance. While the risk profile is also different -- [smart contract risk](/blog/smart-contract-risk-management), [impermanent loss](/blog/impermanent-loss-mitigation), MEV extraction -- the quantitative toolkit for analyzing and exploiting these opportunities is remarkably similar to traditional quant methods.

This guide covers the primary DeFi quantitative strategies: yield farming optimization, DEX arbitrage, liquidation strategies, and cross-protocol opportunities.

## Key Takeaways

- **DeFi arbitrage is fundamentally different** from traditional arbitrage because transactions are visible in the mempool before execution.
- **Impermanent loss is the cost of passive market making** in AMMs and must be quantified before providing liquidity.
- **Yield farming optimization** requires modeling APY decay, token emission schedules, and protocol risk.
- **MEV (Maximal Extractable Value)** creates both opportunities and threats for on-chain strategies.

## AMM Mathematics and Impermanent Loss

Understanding constant-product AMM mechanics is essential for any DeFi strategy.

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass
class ConstantProductAMM:
    """
    Uniswap v2 style constant product AMM.
    Invariant: x * y = k

    Where:
        x: reserve of token A
        y: reserve of token B
        k: constant product
    """
    reserve_a: float
    reserve_b: float
    fee: float = 0.003  # 0.3% swap fee

    @property
    def k(self) -> float:
        return self.reserve_a * self.reserve_b

    @property
    def price(self) -> float:
        """Price of token A in terms of token B."""
        return self.reserve_b / self.reserve_a

    def swap_a_for_b(self, amount_a: float) -> float:
        """Swap token A for token B. Returns amount of B received."""
        amount_a_after_fee = amount_a * (1 - self.fee)
        new_reserve_a = self.reserve_a + amount_a_after_fee
        new_reserve_b = self.k / new_reserve_a
        amount_b_out = self.reserve_b - new_reserve_b

        self.reserve_a = new_reserve_a + amount_a * self.fee
        self.reserve_b = new_reserve_b

        return amount_b_out

    def swap_b_for_a(self, amount_b: float) -> float:
        """Swap token B for token A. Returns amount of A received."""
        amount_b_after_fee = amount_b * (1 - self.fee)
        new_reserve_b = self.reserve_b + amount_b_after_fee
        new_reserve_a = self.k / new_reserve_b
        amount_a_out = self.reserve_a - new_reserve_a

        self.reserve_a = new_reserve_a
        self.reserve_b = new_reserve_b + amount_b * self.fee

        return amount_a_out

    def price_impact(self, amount_a: float) -> float:
        """Compute price impact of a swap as a percentage."""
        price_before = self.price
        # Simulate swap without modifying state
        amount_a_after_fee = amount_a * (1 - self.fee)
        new_reserve_a = self.reserve_a + amount_a_after_fee
        new_reserve_b = self.k / new_reserve_a
        effective_price = (self.reserve_b - new_reserve_b) / amount_a
        price_after = new_reserve_b / new_reserve_a

        return (price_after - price_before) / price_before


def impermanent_loss(
    price_ratio: float,
) -> float:
    """
    Calculate impermanent loss for a constant-product AMM LP position.

    Args:
        price_ratio: new_price / initial_price (e.g., 2.0 for 100% increase)

    Returns:
        IL as a negative fraction (e.g., -0.056 for 5.6% loss)
    """
    # Value of LP position vs holding
    lp_value_ratio = 2 * np.sqrt(price_ratio) / (1 + price_ratio)
    il = lp_value_ratio - 1
    return il


def il_analysis(
    price_changes: np.ndarray = None,
) -> pd.DataFrame:
    """Compute IL across a range of price changes."""
    if price_changes is None:
        price_changes = np.array([
            0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0
        ])

    results = []
    for p in price_changes:
        il = impermanent_loss(p)
        results.append({
            "price_change": f"{(p-1)*100:+.0f}%",
            "price_ratio": p,
            "impermanent_loss": il,
            "il_pct": f"{il*100:.2f}%",
        })

    df = pd.DataFrame(results)
    print("Impermanent Loss vs Price Change:")
    print(df.to_string(index=False))
    return df
```

## DEX Arbitrage

Arbitrage between decentralized exchanges exploits price discrepancies across different liquidity pools.

```python
class DEXArbitrage:
    """
    Identify and execute arbitrage between DEX pools.
    """

    def __init__(self, pools: dict[str, ConstantProductAMM]):
        self.pools = pools

    def find_arbitrage(
        self, token_a: str = "ETH", token_b: str = "USDC"
    ) -> dict:
        """
        Find arbitrage opportunities across pools.
        """
        prices = {}
        for name, pool in self.pools.items():
            prices[name] = pool.price

        if len(prices) < 2:
            return {"opportunity": False}

        # Find cheapest buy and most expensive sell
        cheapest = min(prices, key=prices.get)
        expensive = max(prices, key=prices.get)

        spread = prices[expensive] / prices[cheapest] - 1

        # Account for fees (both pools charge fees)
        pool_a_fee = self.pools[cheapest].fee
        pool_b_fee = self.pools[expensive].fee
        net_spread = spread - pool_a_fee - pool_b_fee

        if net_spread <= 0:
            return {
                "opportunity": False,
                "gross_spread": spread,
                "net_spread": net_spread,
            }

        # Optimal trade size (considering price impact)
        optimal_size = self._optimal_arb_size(
            self.pools[cheapest], self.pools[expensive]
        )

        return {
            "opportunity": True,
            "buy_on": cheapest,
            "sell_on": expensive,
            "buy_price": prices[cheapest],
            "sell_price": prices[expensive],
            "gross_spread": spread,
            "net_spread": net_spread,
            "optimal_size": optimal_size,
            "expected_profit": optimal_size * net_spread * prices[cheapest],
        }

    def _optimal_arb_size(
        self,
        buy_pool: ConstantProductAMM,
        sell_pool: ConstantProductAMM,
    ) -> float:
        """
        Find optimal arbitrage size considering price impact.
        Trade until marginal profit = 0.
        """
        # Binary search for optimal size
        low, high = 0, min(buy_pool.reserve_a, sell_pool.reserve_a) * 0.1
        best_size = 0
        best_profit = 0

        for _ in range(50):
            mid = (low + high) / 2

            # Simulate: buy on cheap pool, sell on expensive pool
            buy_cost = self._simulate_buy_cost(buy_pool, mid)
            sell_revenue = self._simulate_sell_revenue(sell_pool, mid)
            profit = sell_revenue - buy_cost

            if profit > best_profit:
                best_profit = profit
                best_size = mid
                low = mid
            else:
                high = mid

        return best_size

    def _simulate_buy_cost(
        self, pool: ConstantProductAMM, amount_a: float
    ) -> float:
        """Cost in token B to buy amount_a of token A."""
        amount_a_after_fee = amount_a * (1 - pool.fee)
        new_reserve_a = pool.reserve_a - amount_a
        if new_reserve_a <= 0:
            return float("inf")
        new_reserve_b = pool.k / new_reserve_a
        return new_reserve_b - pool.reserve_b

    def _simulate_sell_revenue(
        self, pool: ConstantProductAMM, amount_a: float
    ) -> float:
        """Revenue in token B from selling amount_a of token A."""
        amount_a_after_fee = amount_a * (1 - pool.fee)
        new_reserve_a = pool.reserve_a + amount_a_after_fee
        new_reserve_b = pool.k / new_reserve_a
        return pool.reserve_b - new_reserve_b


# Example
pool_uniswap = ConstantProductAMM(reserve_a=1000, reserve_b=2_000_000, fee=0.003)
pool_sushi = ConstantProductAMM(reserve_a=800, reserve_b=1_640_000, fee=0.003)

arb = DEXArbitrage({"uniswap": pool_uniswap, "sushiswap": pool_sushi})
result = arb.find_arbitrage()
print(f"Arbitrage opportunity: {result['opportunity']}")
if result["opportunity"]:
    print(f"  Buy on: {result['buy_on']} at {result['buy_price']:.2f}")
    print(f"  Sell on: {result['sell_on']} at {result['sell_price']:.2f}")
    print(f"  Net spread: {result['net_spread']:.4%}")
```

## Yield Farming Optimization

```python
class YieldFarmOptimizer:
    """
    Optimize yield farming allocations across protocols.
    """

    def __init__(self):
        self.opportunities = []

    def add_opportunity(
        self,
        protocol: str,
        pool: str,
        base_apy: float,
        reward_apy: float,
        tvl: float,
        il_risk: float,  # 0-1 scale
        smart_contract_risk: float,  # 0-1 scale
        chain: str = "ethereum",
    ):
        """Register a yield farming opportunity."""
        self.opportunities.append({
            "protocol": protocol,
            "pool": pool,
            "base_apy": base_apy,
            "reward_apy": reward_apy,
            "total_apy": base_apy + reward_apy,
            "tvl": tvl,
            "il_risk": il_risk,
            "sc_risk": smart_contract_risk,
            "chain": chain,
        })

    def risk_adjusted_ranking(self) -> pd.DataFrame:
        """
        Rank opportunities by risk-adjusted yield.
        Discounts APY by impermanent loss risk and smart contract risk.
        """
        df = pd.DataFrame(self.opportunities)

        # Risk-adjusted APY
        df["risk_discount"] = 1 - 0.3 * df["il_risk"] - 0.5 * df["sc_risk"]
        df["risk_adjusted_apy"] = df["total_apy"] * df["risk_discount"]

        # TVL stability factor (higher TVL = more stable)
        df["tvl_score"] = np.log10(df["tvl"].clip(lower=1)) / 10
        df["final_score"] = df["risk_adjusted_apy"] * (0.7 + 0.3 * df["tvl_score"])

        return df.sort_values("final_score", ascending=False)

    def optimal_allocation(
        self,
        capital: float,
        max_per_protocol: float = 0.25,
        max_per_chain: float = 0.50,
    ) -> pd.DataFrame:
        """
        Compute optimal allocation across opportunities.
        """
        ranked = self.risk_adjusted_ranking()

        allocations = []
        remaining = capital
        protocol_exposure = {}
        chain_exposure = {}

        for _, row in ranked.iterrows():
            # Check concentration limits
            protocol = row["protocol"]
            chain = row["chain"]

            protocol_used = protocol_exposure.get(protocol, 0)
            chain_used = chain_exposure.get(chain, 0)

            max_protocol_alloc = capital * max_per_protocol - protocol_used
            max_chain_alloc = capital * max_per_chain - chain_used
            max_alloc = min(remaining, max_protocol_alloc, max_chain_alloc)

            if max_alloc <= 0:
                continue

            # Allocate proportional to risk-adjusted APY
            allocation = min(max_alloc, remaining * 0.3)  # Max 30% in one pool

            protocol_exposure[protocol] = protocol_used + allocation
            chain_exposure[chain] = chain_used + allocation
            remaining -= allocation

            allocations.append({
                "protocol": protocol,
                "pool": row["pool"],
                "chain": chain,
                "allocation": allocation,
                "allocation_pct": allocation / capital,
                "expected_apy": row["risk_adjusted_apy"],
                "expected_annual_yield": allocation * row["risk_adjusted_apy"],
            })

            if remaining <= capital * 0.05:
                break

        result = pd.DataFrame(allocations)

        total_yield = result["expected_annual_yield"].sum()
        blended_apy = total_yield / capital

        print(f"Yield Farm Allocation (${capital:,.0f} capital):")
        print(f"{'Protocol':>15s} {'Pool':>20s} {'Alloc':>10s} {'APY':>8s}")
        for _, row in result.iterrows():
            print(f"{row['protocol']:>15s} {row['pool']:>20s} "
                  f"${row['allocation']:>9,.0f} {row['expected_apy']:>7.1%}")
        print(f"\nBlended APY: {blended_apy:.1%}")
        print(f"Expected Annual Yield: ${total_yield:,.0f}")

        return result
```

## Liquidation Strategies

Monitor lending protocols for undercollateralized positions and execute profitable liquidations.

```python
class LiquidationMonitor:
    """
    Monitor lending protocol positions for liquidation opportunities.
    """

    def __init__(
        self,
        liquidation_bonus: float = 0.05,  # 5% bonus
        gas_cost_usd: float = 50,          # Estimated gas cost
    ):
        self.bonus = liquidation_bonus
        self.gas_cost = gas_cost_usd

    def check_position(
        self,
        collateral_value: float,
        debt_value: float,
        liquidation_threshold: float = 0.825,
        close_factor: float = 0.5,
    ) -> dict:
        """
        Check if a position is eligible for liquidation.
        """
        health_factor = (collateral_value * liquidation_threshold) / max(debt_value, 0.01)

        is_liquidatable = health_factor < 1.0

        if not is_liquidatable:
            return {
                "liquidatable": False,
                "health_factor": health_factor,
                "buffer": (health_factor - 1) * 100,
            }

        # Maximum liquidation amount
        max_repay = debt_value * close_factor
        liquidation_bonus_value = max_repay * self.bonus

        # Profit calculation
        gross_profit = liquidation_bonus_value
        net_profit = gross_profit - self.gas_cost

        return {
            "liquidatable": True,
            "health_factor": health_factor,
            "max_repay": max_repay,
            "collateral_seized": max_repay * (1 + self.bonus),
            "gross_profit": gross_profit,
            "gas_cost": self.gas_cost,
            "net_profit": net_profit,
            "profitable": net_profit > 0,
            "roi": net_profit / max_repay if max_repay > 0 else 0,
        }

    def find_at_risk_positions(
        self,
        positions: pd.DataFrame,
        price_drop_scenarios: list[float] = None,
    ) -> pd.DataFrame:
        """
        Identify positions that would become liquidatable
        under various price drop scenarios.
        """
        if price_drop_scenarios is None:
            price_drop_scenarios = [0.05, 0.10, 0.15, 0.20, 0.30]

        results = []
        for _, pos in positions.iterrows():
            for drop in price_drop_scenarios:
                stressed_collateral = pos["collateral_value"] * (1 - drop)
                check = self.check_position(
                    stressed_collateral,
                    pos["debt_value"],
                    pos.get("liq_threshold", 0.825),
                )

                if check["liquidatable"] and check["profitable"]:
                    results.append({
                        "position_id": pos.get("id", "unknown"),
                        "price_drop": drop,
                        "health_factor": check["health_factor"],
                        "net_profit": check["net_profit"],
                        "collateral_value": stressed_collateral,
                    })

        return pd.DataFrame(results)
```

## Cross-Chain Arbitrage

```python
class CrossChainArbitrage:
    """
    Identify price discrepancies across chains.
    """

    def __init__(self, bridge_cost: float = 20, bridge_time_minutes: int = 15):
        self.bridge_cost = bridge_cost
        self.bridge_time = bridge_time_minutes

    def analyze_opportunity(
        self,
        token: str,
        chain_prices: dict[str, float],
        chain_liquidity: dict[str, float],
        trade_size: float,
    ) -> dict:
        """
        Analyze cross-chain arbitrage for a token.
        """
        if len(chain_prices) < 2:
            return {"opportunity": False}

        cheapest_chain = min(chain_prices, key=chain_prices.get)
        expensive_chain = max(chain_prices, key=chain_prices.get)

        price_diff = chain_prices[expensive_chain] - chain_prices[cheapest_chain]
        pct_diff = price_diff / chain_prices[cheapest_chain]

        # Costs
        buy_impact = trade_size / max(chain_liquidity.get(cheapest_chain, 1e6), 1) * 0.003
        sell_impact = trade_size / max(chain_liquidity.get(expensive_chain, 1e6), 1) * 0.003
        total_cost = self.bridge_cost + (buy_impact + sell_impact) * trade_size

        net_profit = price_diff * trade_size - total_cost

        return {
            "opportunity": net_profit > 0,
            "token": token,
            "buy_chain": cheapest_chain,
            "sell_chain": expensive_chain,
            "price_diff_pct": pct_diff,
            "gross_profit": price_diff * trade_size,
            "costs": total_cost,
            "net_profit": net_profit,
            "bridge_time_min": self.bridge_time,
            "risk": "Price may move during bridge transit",
        }
```

## MEV Protection and Strategies

```python
class MEVAnalyzer:
    """
    Analyze and protect against MEV extraction.
    """

    @staticmethod
    def estimate_sandwich_cost(
        trade_size: float,
        pool_liquidity: float,
        fee: float = 0.003,
    ) -> float:
        """
        Estimate the cost of a sandwich attack on your trade.
        Attacker front-runs your trade, moving the price against you.
        """
        # Price impact of attacker's front-run
        attacker_size = trade_size * 0.5  # Typical attacker sizing
        price_impact = attacker_size / pool_liquidity
        your_extra_cost = trade_size * price_impact
        return your_extra_cost

    @staticmethod
    def flashbot_protection_savings(
        trade_size: float,
        pool_liquidity: float,
    ) -> dict:
        """
        Estimate savings from using Flashbots (private mempool)
        vs public mempool.
        """
        sandwich_cost = MEVAnalyzer.estimate_sandwich_cost(
            trade_size, pool_liquidity
        )
        flashbot_tip = trade_size * 0.001  # Typical builder tip

        return {
            "public_mempool_cost": sandwich_cost,
            "flashbot_cost": flashbot_tip,
            "savings": sandwich_cost - flashbot_tip,
            "recommendation": (
                "Use Flashbots" if sandwich_cost > flashbot_tip
                else "Public mempool is fine"
            ),
        }
```

## FAQ

### Is DeFi yield farming still profitable in 2026?

Yield farming remains profitable but the landscape has matured significantly. The astronomical APYs of 2020-2021 (1,000%+) have compressed to 5-20% for established protocols. Profitable farming now requires: (1) sophisticated risk assessment of protocol safety, (2) impermanent loss hedging for volatile pairs, (3) gas optimization across multiple chains, and (4) quick rotation into new protocols before yields compress. The edge has shifted from first-mover advantage to [quantitative risk management](/blog/quantitative-risk-management).

### How do I protect against impermanent loss?

Three approaches: (1) provide liquidity to stablecoin pairs (USDC/USDT) where impermanent loss is minimal, (2) use concentrated liquidity positions (Uniswap v3) with tight ranges and active management, (3) hedge with options or [perpetual futures](/blog/perpetual-futures-funding-rate) on the underlying token. Quantitatively, impermanent loss only matters relative to fees earned: if trading fees exceed IL, the position is profitable. Calculate the break-even trading volume before deploying capital.

### What is MEV and why does it matter for DeFi strategies?

Maximal Extractable Value (MEV) is the profit that block producers can extract by reordering, inserting, or censoring transactions within a block. For DeFi traders, MEV primarily manifests as sandwich attacks (your swap is front-run and back-run) and priority gas auctions that increase transaction costs. Use private mempools (Flashbots) for large swaps, set tight slippage limits, and consider splitting large trades across multiple blocks.

### Can I run DeFi arbitrage as a retail trader?

DEX arbitrage is extremely competitive because it is dominated by sophisticated MEV searchers running high-performance infrastructure. Simple two-pool arbitrage is fully extracted by bots within milliseconds of price divergence. Profitable retail approaches focus on: (1) cross-chain arbitrage where bridge latency creates longer windows, (2) long-tail DEXes with less bot competition, (3) complex multi-hop routes that require more sophisticated pathfinding, and (4) new protocol launches before the arbitrage bots arrive.
