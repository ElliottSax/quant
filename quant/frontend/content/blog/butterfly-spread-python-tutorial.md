---
title: 'Butterfly Spread Python Tutorial: Neutral Options Strategy'
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
slug: butterfly-spread-python-tutorial
published_date: '2026-03-20'
last_updated: '2026-03-20'
---

# Butterfly Spread Python Tutorial: Neutral Options Strategy

The butterfly spread is a limited-risk, defined-profit strategy perfect for neutral markets. This tutorial covers implementation and optimization of butterfly spreads.

## Butterfly Spread Mechanics

A butterfly spread consists of:
- 1 long call/put at lower strike (ATM - width)
- 2 short calls/puts at middle strike (ATM)
- 1 long call/put at higher strike (ATM + width)

The resulting position has:
- Limited max profit (middle strike spread width minus cost)
- Limited max loss (net debit paid)
- Highest profit when underlying stays near middle strike

## Building Butterfly Spread Bots

```python
import numpy as np
from scipy.special import norm
from typing import Dict, List, Tuple
import logging
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ButterflySpreadBuilder:
    """Build optimized butterfly spreads"""

    def __init__(self, S: float, r: float = 0.05):
        self.S = S
        self.r = r

    def black_scholes_call(self, S: float, K: float, T: float, sigma: float) -> float:
        """Calculate call price using Black-Scholes"""

        d1 = (np.log(S / K) + (self.r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        return S * norm.cdf(d1) - K * np.exp(-self.r * T) * norm.cdf(d2)

    def design_butterfly_spread(self, K: float, T: float, sigma: float,
                               spread_width: float = 5) -> Dict:
        """Design optimal butterfly spread"""

        # Strikes
        K_low = K - spread_width
        K_mid = K
        K_high = K + spread_width

        # Prices
        C_low = self.black_scholes_call(self.S, K_low, T, sigma)
        C_mid = self.black_scholes_call(self.S, K_mid, T, sigma)
        C_high = self.black_scholes_call(self.S, K_high, T, sigma)

        # Net cost
        net_debit = C_low - 2 * C_mid + C_high

        # Max profit
        max_profit = spread_width - net_debit

        # Max loss
        max_loss = net_debit

        # Breakevens
        be_low = K_low + net_debit
        be_high = K_high - net_debit

        return {
            'strikes': {
                'long': K_low,
                'short': K_mid,
                'short_qty': 2,
                'long_high': K_high
            },
            'prices': {
                'long': C_low,
                'short': C_mid,
                'long_high': C_high
            },
            'net_debit': net_debit,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakevens': (be_low, be_high),
            'profit_range': (be_low, be_high),
            'roi': (max_profit / max_loss) if max_loss > 0 else float('inf')
        }

    def calculate_butterfly_pnl(self, current_S: float, K: float,
                               T: float, sigma: float,
                               spread_width: float) -> float:
        """Calculate current P&L for butterfly"""

        K_low = K - spread_width
        K_mid = K
        K_high = K + spread_width

        C_low = self.black_scholes_call(current_S, K_low, T, sigma)
        C_mid = self.black_scholes_call(current_S, K_mid, T, sigma)
        C_high = self.black_scholes_call(current_S, K_high, T, sigma)

        pnl = C_low - 2 * C_mid + C_high

        return pnl

    def identify_optimal_strikes(self, T: float, sigma: float) -> Dict:
        """Identify optimal middle strike for butterfly"""

        # Test range of strikes
        K_range = np.linspace(self.S * 0.95, self.S * 1.05, 11)

        best_butterfly = None
        best_roi = 0

        for K in K_range:
            butterfly = self.design_butterfly_spread(K, T, sigma)

            if butterfly['roi'] > best_roi:
                best_roi = butterfly['roi']
                best_butterfly = butterfly
                best_butterfly['middle_strike'] = K

        return best_butterfly

    def generate_butterfly_pnl_chart(self, butterfly: Dict,
                                     spot_range: Tuple[float, float] = None) -> pd.DataFrame:
        """Generate P&L chart for butterfly"""

        if spot_range is None:
            spot_range = (self.S * 0.9, self.S * 1.1)

        K = butterfly['strikes']['short']
        K_low = butterfly['strikes']['long']
        K_high = butterfly['strikes']['long_high']

        spots = np.linspace(spot_range[0], spot_range[1], 100)
        pnls = []

        for S in spots:
            # Simplified P&L calculation at expiration
            value_low = max(S - K_low, 0)
            value_mid = max(S - K, 0) * 2
            value_high = max(S - K_high, 0)

            pnl = value_low - value_mid + value_high - butterfly['net_debit']

            pnls.append({
                'spot': S,
                'pnl': pnl,
                'profit': max(pnl, 0),
                'loss': min(pnl, 0)
            })

        return pd.DataFrame(pnls)
```

## Dynamic Butterfly Management

```python
class ButterflySpreadManager:
    """Manage butterfly spread positions"""

    def __init__(self):
        self.positions = []
        self.adjustments = []

    def add_butterfly_position(self, butterfly: Dict, quantity: int = 1):
        """Add butterfly position to portfolio"""

        self.positions.append({
            'timestamp': datetime.now(),
            'butterfly': butterfly,
            'quantity': quantity,
            'status': 'open',
            'adjustments_count': 0
        })

    def monitor_butterfly_position(self, position: Dict,
                                  current_S: float, current_T: float,
                                  current_sigma: float) -> Dict:
        """Monitor butterfly position for adjustments"""

        butterfly = position['butterfly']
        K_low = butterfly['strikes']['long']
        K_mid = butterfly['strikes']['short']
        K_high = butterfly['strikes']['long_high']

        # Calculate distance from optimal
        distance_from_mid = abs(current_S - K_mid)
        spread_width = K_mid - K_low

        # Check if underlying is moving away from profitable zone
        if distance_from_mid > spread_width * 1.5:
            return {
                'action': 'consider_adjustment',
                'reason': 'underlying moving away from profitable zone',
                'current_S': current_S,
                'mid_strike': K_mid,
                'recommendation': 'consider closing or adjusting to iron butterfly'
            }

        # Check time decay
        time_decay_multiplier = current_T / butterfly.get('T', 0.25)

        if current_T < 0.5 / 365:  # Less than 12 hours to expiration
            return {
                'action': 'prepare_to_close',
                'reason': 'near expiration',
                'current_T': current_T,
                'recommendation': 'close position to capture remaining theta'
            }

        return {
            'action': 'hold',
            'reason': 'position within parameters'
        }

    def adjust_butterfly_to_iron_condor(self, butterfly: Dict,
                                       adjustment_width: float = 5) -> Dict:
        """Convert butterfly to iron condor (wider spreads)"""

        K = butterfly['strikes']['short']
        spread_width = butterfly['strikes']['long_high'] - butterfly['strikes']['long']

        # Add iron condor wings
        put_spread = (K - adjustment_width, K - adjustment_width - spread_width)
        call_spread = (K + adjustment_width, K + adjustment_width + spread_width)

        return {
            'original_butterfly': butterfly,
            'added_puts': put_spread,
            'added_calls': call_spread,
            'new_strategy': 'iron_butterfly',
            'benefit': 'additional income from wider spreads'
        }

    def calculate_adjustment_cost(self, position: Dict,
                                 current_S: float) -> float:
        """Calculate cost to adjust butterfly"""

        # Cost to close butterfly and open new one
        # Simplified calculation

        return position['butterfly']['net_debit'] * 0.1  # Estimate 10% of initial debit

    def execute_butterfly_adjustments(self, position: Dict,
                                     current_market_data: Dict) -> List[Dict]:
        """Execute recommended adjustments"""

        adjustments = []

        S = current_market_data['spot']
        T = current_market_data['time_to_expiry']
        K = position['butterfly']['strikes']['short']

        # Adjustment 1: Roll if underlying moved significantly
        distance = abs(S - K)
        spread_width = position['butterfly']['strikes']['long_high'] - position['butterfly']['strikes']['long']

        if distance > spread_width:
            # Roll to new butterfly centered at current spot
            roll_adjustment = {
                'type': 'roll',
                'from_strike': K,
                'to_strike': S,
                'rationale': 'center butterfly on current spot'
            }
            adjustments.append(roll_adjustment)

        # Adjustment 2: Close if time decay is excessive
        if T < 0.02:  # Less than 5 days
            close_adjustment = {
                'type': 'close',
                'reason': 'high time decay near expiration'
            }
            adjustments.append(close_adjustment)

        return adjustments
```

## Butterfly Portfolio Optimization

```python
class ButterflyPortfolioOptimizer:
    """Optimize portfolio of butterfly spreads"""

    def __init__(self):
        self.butterflies = []
        self.optimization_history = []

    def create_butterfly_ladder(self, S: float, strikes: List[float],
                               T: float, sigma: float,
                               spread_width: float = 5) -> List[Dict]:
        """Create ladder of butterflies at different strikes"""

        builder = ButterflySpreadBuilder(S)
        butterflies = []

        for K in strikes:
            butterfly = builder.design_butterfly_spread(K, T, sigma, spread_width)
            butterfly['middle_strike'] = K
            butterflies.append(butterfly)

        return butterflies

    def calculate_portfolio_metrics(self, butterflies: List[Dict]) -> Dict:
        """Calculate metrics for butterfly portfolio"""

        total_debit = sum(b['net_debit'] for b in butterflies)
        total_max_profit = sum(b['max_profit'] for b in butterflies)
        avg_roi = np.mean([b['roi'] for b in butterflies if not np.isinf(b['roi'])])

        # Calculate coverage
        strikes = [b['middle_strike'] for b in butterflies]
        coverage = max(strikes) - min(strikes)

        return {
            'num_butterflies': len(butterflies),
            'total_debit': total_debit,
            'total_max_profit': total_max_profit,
            'average_roi': avg_roi,
            'strike_coverage': coverage,
            'margin_efficiency': total_max_profit / total_debit if total_debit > 0 else 0
        }

    def optimize_butterfly_spacing(self, S: float, T: float, sigma: float,
                                   num_butterflies: int = 3) -> List[float]:
        """Find optimal spacing for butterfly strikes"""

        # Use optimization to find best spacing
        # Simplified: evenly spaced approach

        width = S * 0.1  # 10% range
        step = width / (num_butterflies + 1)

        strikes = [S - width/2 + step * (i + 1) for i in range(num_butterflies)]

        return strikes

    def hedge_butterfly_portfolio(self, butterflies: List[Dict],
                                 portfolio_delta: float) -> Dict:
        """Recommend hedges for butterfly portfolio"""

        # Butterflies are delta neutral, but slight adjustments may be needed

        if abs(portfolio_delta) > 10:
            hedge_size = portfolio_delta
            return {
                'hedge_type': 'index_futures' if portfolio_delta > 0 else 'short_futures',
                'size': abs(hedge_size),
                'rationale': f"Delta is {portfolio_delta}"
            }

        return {'hedge_needed': False}
```

## Backtesting Butterfly Strategies

```python
class ButterflyBacktester:
    """Backtest butterfly spread strategies"""

    def __init__(self):
        self.results = []

    def backtest_butterfly_strategy(self, price_data: pd.DataFrame,
                                   expiration_days: int = 30,
                                   rebalance_frequency: int = 7) -> Dict:
        """Backtest butterfly spread strategy"""

        results = {
            'trades': [],
            'total_pnl': 0,
            'num_trades': 0,
            'win_rate': 0
        }

        # Trade setup every rebalance_frequency days
        for i in range(0, len(price_data) - expiration_days, rebalance_frequency):

            entry_price = price_data.iloc[i]['close']
            entry_idx = i
            exit_idx = min(i + expiration_days, len(price_data) - 1)
            exit_price = price_data.iloc[exit_idx]['close']

            # Simplified P&L: profit if within profitable range
            if abs(exit_price - entry_price) < entry_price * 0.05:  # Within 5%
                trade_pnl = 100  # Fixed max profit example
                winner = True
            else:
                trade_pnl = -50  # Fixed max loss example
                winner = False

            results['trades'].append({
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl': trade_pnl,
                'winner': winner
            })

            results['total_pnl'] += trade_pnl
            results['num_trades'] += 1

        if results['num_trades'] > 0:
            results['win_rate'] = sum(1 for t in results['trades'] if t['winner']) / results['num_trades']

        return results
```

## Conclusion

Butterfly spreads are excellent for neutral markets with limited risk. The key to success is proper selection of strikes, monitoring for adjustments, and disciplined position management. Always keep risk to the debit paid and exit when the underlying moves significantly from your center strike.
