"""
Trading Strategy Library

Pre-built strategies for backtesting platform.
Revenue model: Basic strategies free, advanced strategies premium ($29/mo).
"""

from typing import Optional, Dict
import pandas as pd
import numpy as np


# ==================== FREE TIER STRATEGIES ====================

async def ma_crossover_strategy(
    data: pd.DataFrame,
    fast_period: int = 20,
    slow_period: int = 50
) -> Optional[Dict]:
    """
    Simple Moving Average Crossover (FREE)

    Buy when fast MA crosses above slow MA.
    Sell when fast MA crosses below slow MA.

    Classic trend-following strategy. Good for trending markets.
    """
    if len(data) < slow_period:
        return None

    fast_ma = data['close'].rolling(fast_period).mean().iloc[-1]
    slow_ma = data['close'].rolling(slow_period).mean().iloc[-1]
    prev_fast_ma = data['close'].rolling(fast_period).mean().iloc[-2]
    prev_slow_ma = data['close'].rolling(slow_period).mean().iloc[-2]

    # Crossover detection
    if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
        return {'type': 'buy', 'quantity': 100, 'reason': 'Bullish MA crossover'}
    elif prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
        return {'type': 'sell', 'quantity': 100, 'reason': 'Bearish MA crossover'}

    return None


async def rsi_strategy(
    data: pd.DataFrame,
    rsi_period: int = 14,
    oversold: float = 30,
    overbought: float = 70
) -> Optional[Dict]:
    """
    RSI Mean Reversion (FREE)

    Buy when RSI < oversold threshold.
    Sell when RSI > overbought threshold.

    Contrarian strategy for range-bound markets.
    """
    if len(data) < rsi_period + 1:
        return None

    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]

    if current_rsi < oversold:
        return {'type': 'buy', 'quantity': 100, 'reason': f'RSI oversold: {current_rsi:.1f}'}
    elif current_rsi > overbought:
        return {'type': 'sell', 'quantity': 100, 'reason': f'RSI overbought: {current_rsi:.1f}'}

    return None


async def bollinger_breakout_strategy(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> Optional[Dict]:
    """
    Bollinger Bands Breakout (FREE)

    Buy when price breaks above upper band.
    Sell when price breaks below lower band.

    Volatility breakout strategy.
    """
    if len(data) < period:
        return None

    # Calculate Bollinger Bands
    ma = data['close'].rolling(period).mean()
    std = data['close'].rolling(period).std()
    upper_band = ma + (std * std_dev)
    lower_band = ma - (std * std_dev)

    current_price = data['close'].iloc[-1]
    current_upper = upper_band.iloc[-1]
    current_lower = lower_band.iloc[-1]
    prev_price = data['close'].iloc[-2]

    # Breakout detection
    if prev_price <= current_upper and current_price > current_upper:
        return {'type': 'buy', 'quantity': 100, 'reason': 'Upper Bollinger breakout'}
    elif prev_price >= current_lower and current_price < current_lower:
        return {'type': 'sell', 'quantity': 100, 'reason': 'Lower Bollinger breakout'}

    return None


# ==================== PREMIUM TIER STRATEGIES ($29/mo) ====================

async def macd_strategy(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Optional[Dict]:
    """
    MACD Indicator Strategy (PREMIUM)

    Buy when MACD crosses above signal line.
    Sell when MACD crosses below signal line.

    Momentum strategy with trend confirmation.
    """
    if len(data) < slow_period + signal_period:
        return None

    # Calculate MACD
    ema_fast = data['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()

    current_macd = macd.iloc[-1]
    current_signal = signal.iloc[-1]
    prev_macd = macd.iloc[-2]
    prev_signal = signal.iloc[-2]

    # Crossover detection
    if prev_macd <= prev_signal and current_macd > current_signal:
        return {'type': 'buy', 'quantity': 100, 'reason': 'Bullish MACD crossover'}
    elif prev_macd >= prev_signal and current_macd < current_signal:
        return {'type': 'sell', 'quantity': 100, 'reason': 'Bearish MACD crossover'}

    return None


async def mean_reversion_zscore_strategy(
    data: pd.DataFrame,
    lookback: int = 20,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.5
) -> Optional[Dict]:
    """
    Z-Score Mean Reversion (PREMIUM)

    Buy when Z-score < -entry_threshold (oversold).
    Sell when Z-score > entry_threshold (overbought).
    Exit when Z-score crosses exit_threshold.

    Statistical arbitrage strategy.
    """
    if len(data) < lookback:
        return None

    # Calculate Z-score
    ma = data['close'].rolling(lookback).mean()
    std = data['close'].rolling(lookback).std()
    zscore = (data['close'] - ma) / std

    current_z = zscore.iloc[-1]

    if current_z < -entry_threshold:
        return {'type': 'buy', 'quantity': 100, 'reason': f'Z-score oversold: {current_z:.2f}'}
    elif current_z > entry_threshold:
        return {'type': 'sell', 'quantity': 100, 'reason': f'Z-score overbought: {current_z:.2f}'}
    elif abs(current_z) < exit_threshold:
        # Close position when price reverts to mean
        return {'type': 'close', 'reason': f'Mean reversion complete: {current_z:.2f}'}

    return None


async def momentum_strategy(
    data: pd.DataFrame,
    lookback: int = 20,
    momentum_threshold: float = 0.05
) -> Optional[Dict]:
    """
    Momentum Strategy (PREMIUM)

    Buy when price momentum > threshold.
    Sell when price momentum < -threshold.

    Follows strong price trends.
    """
    if len(data) < lookback + 1:
        return None

    # Calculate momentum (rate of change)
    momentum = data['close'].pct_change(lookback).iloc[-1]

    if momentum > momentum_threshold:
        return {'type': 'buy', 'quantity': 100, 'reason': f'Strong upward momentum: {momentum*100:.1f}%'}
    elif momentum < -momentum_threshold:
        return {'type': 'sell', 'quantity': 100, 'reason': f'Strong downward momentum: {momentum*100:.1f}%'}

    return None


async def triple_ema_strategy(
    data: pd.DataFrame,
    short_period: int = 8,
    medium_period: int = 21,
    long_period: int = 55
) -> Optional[Dict]:
    """
    Triple EMA Strategy (PREMIUM)

    Buy when short > medium > long (all aligned bullish).
    Sell when short < medium < long (all aligned bearish).

    Strong trend confirmation strategy.
    """
    if len(data) < long_period:
        return None

    # Calculate EMAs
    ema_short = data['close'].ewm(span=short_period, adjust=False).mean().iloc[-1]
    ema_medium = data['close'].ewm(span=medium_period, adjust=False).mean().iloc[-1]
    ema_long = data['close'].ewm(span=long_period, adjust=False).mean().iloc[-1]

    # Check alignment
    bullish_alignment = ema_short > ema_medium > ema_long
    bearish_alignment = ema_short < ema_medium < ema_long

    if bullish_alignment:
        return {'type': 'buy', 'quantity': 100, 'reason': 'Bullish EMA alignment'}
    elif bearish_alignment:
        return {'type': 'sell', 'quantity': 100, 'reason': 'Bearish EMA alignment'}

    return None


# ==================== ENTERPRISE TIER STRATEGIES ($99/mo) ====================

async def ichimoku_cloud_strategy(
    data: pd.DataFrame,
    conversion_period: int = 9,
    base_period: int = 26,
    span_b_period: int = 52,
    displacement: int = 26
) -> Optional[Dict]:
    """
    Ichimoku Cloud Strategy (ENTERPRISE)

    Complete trend-following system with multiple confirmations.
    Buy/sell based on price relationship to cloud and line crossovers.

    Professional-grade strategy used by institutional traders.
    """
    if len(data) < span_b_period + displacement:
        return None

    # Calculate Ichimoku components
    high_prices = data['high']
    low_prices = data['low']

    # Conversion Line (Tenkan-sen)
    conversion_line = (
        high_prices.rolling(conversion_period).max() +
        low_prices.rolling(conversion_period).min()
    ) / 2

    # Base Line (Kijun-sen)
    base_line = (
        high_prices.rolling(base_period).max() +
        low_prices.rolling(base_period).min()
    ) / 2

    # Leading Span A (Senkou Span A)
    span_a = ((conversion_line + base_line) / 2).shift(displacement)

    # Leading Span B (Senkou Span B)
    span_b = (
        (high_prices.rolling(span_b_period).max() +
         low_prices.rolling(span_b_period).min()) / 2
    ).shift(displacement)

    # Current values
    current_price = data['close'].iloc[-1]
    current_conversion = conversion_line.iloc[-1]
    current_base = base_line.iloc[-1]
    current_span_a = span_a.iloc[-1]
    current_span_b = span_b.iloc[-1]

    # Cloud analysis
    cloud_top = max(current_span_a, current_span_b)
    cloud_bottom = min(current_span_a, current_span_b)

    # Bullish: price above cloud, conversion > base
    if current_price > cloud_top and current_conversion > current_base:
        return {'type': 'buy', 'quantity': 100, 'reason': 'Ichimoku bullish (above cloud)'}
    # Bearish: price below cloud, conversion < base
    elif current_price < cloud_bottom and current_conversion < current_base:
        return {'type': 'sell', 'quantity': 100, 'reason': 'Ichimoku bearish (below cloud)'}

    return None


async def multi_timeframe_strategy(
    data: pd.DataFrame,
    short_ma: int = 20,
    long_ma: int = 50,
    higher_tf_ma: int = 200
) -> Optional[Dict]:
    """
    Multi-Timeframe Trend Strategy (ENTERPRISE)

    Confirms trends across multiple timeframes.
    Only trades when all timeframes align.

    Reduces false signals significantly.
    """
    if len(data) < higher_tf_ma:
        return None

    # Short-term trend
    short_sma = data['close'].rolling(short_ma).mean().iloc[-1]

    # Medium-term trend
    long_sma = data['close'].rolling(long_ma).mean().iloc[-1]

    # Long-term trend
    higher_tf_sma = data['close'].rolling(higher_tf_ma).mean().iloc[-1]

    current_price = data['close'].iloc[-1]

    # All timeframes bullish
    if current_price > short_sma > long_sma > higher_tf_sma:
        return {
            'type': 'buy',
            'quantity': 100,
            'reason': 'Multi-timeframe bullish alignment'
        }
    # All timeframes bearish
    elif current_price < short_sma < long_sma < higher_tf_sma:
        return {
            'type': 'sell',
            'quantity': 100,
            'reason': 'Multi-timeframe bearish alignment'
        }

    return None


async def volatility_breakout_atr_strategy(
    data: pd.DataFrame,
    atr_period: int = 14,
    breakout_multiplier: float = 2.0
) -> Optional[Dict]:
    """
    ATR Volatility Breakout (ENTERPRISE)

    Trades breakouts based on Average True Range.
    Adapts to current market volatility.

    Dynamic stop-loss and position sizing.
    """
    if len(data) < atr_period + 1:
        return None

    # Calculate True Range
    high = data['high']
    low = data['low']
    close = data['close']

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Average True Range
    atr = tr.rolling(atr_period).mean()
    current_atr = atr.iloc[-1]

    # Breakout levels
    current_close = close.iloc[-1]
    prev_high = high.iloc[-2]
    prev_low = low.iloc[-2]

    breakout_threshold = current_atr * breakout_multiplier

    # Upside breakout
    if current_close > prev_high + breakout_threshold:
        return {
            'type': 'buy',
            'quantity': 100,
            'reason': f'Volatility breakout (ATR: {current_atr:.2f})',
            'stop_loss': current_close - (current_atr * 2)
        }
    # Downside breakout
    elif current_close < prev_low - breakout_threshold:
        return {
            'type': 'sell',
            'quantity': 100,
            'reason': f'Volatility breakdown (ATR: {current_atr:.2f})',
            'stop_loss': current_close + (current_atr * 2)
        }

    return None


# Strategy registry for API
STRATEGY_REGISTRY = {
    # Free tier
    'ma_crossover': {
        'function': ma_crossover_strategy,
        'tier': 'free',
        'category': 'trend_following',
        'description': 'Simple Moving Average Crossover - classic trend following',
    },
    'rsi': {
        'function': rsi_strategy,
        'tier': 'free',
        'category': 'mean_reversion',
        'description': 'RSI Mean Reversion - contrarian indicator',
    },
    'bollinger_breakout': {
        'function': bollinger_breakout_strategy,
        'tier': 'free',
        'category': 'volatility_breakout',
        'description': 'Bollinger Bands Breakout - volatility expansion',
    },

    # Premium tier ($29/mo)
    'macd': {
        'function': macd_strategy,
        'tier': 'premium',
        'category': 'momentum',
        'description': 'MACD Indicator - momentum with trend confirmation',
    },
    'mean_reversion_zscore': {
        'function': mean_reversion_zscore_strategy,
        'tier': 'premium',
        'category': 'statistical_arbitrage',
        'description': 'Z-Score Mean Reversion - statistical trading',
    },
    'momentum': {
        'function': momentum_strategy,
        'tier': 'premium',
        'category': 'momentum',
        'description': 'Momentum Strategy - ride strong trends',
    },
    'triple_ema': {
        'function': triple_ema_strategy,
        'tier': 'premium',
        'category': 'trend_following',
        'description': 'Triple EMA - strong trend confirmation',
    },

    # Enterprise tier ($99/mo)
    'ichimoku_cloud': {
        'function': ichimoku_cloud_strategy,
        'tier': 'enterprise',
        'category': 'professional',
        'description': 'Ichimoku Cloud - institutional-grade system',
    },
    'multi_timeframe': {
        'function': multi_timeframe_strategy,
        'tier': 'enterprise',
        'category': 'professional',
        'description': 'Multi-Timeframe Trend - reduce false signals',
    },
    'volatility_breakout_atr': {
        'function': volatility_breakout_atr_strategy,
        'tier': 'enterprise',
        'category': 'professional',
        'description': 'ATR Volatility Breakout - adaptive trading',
    },
}


def get_strategy(strategy_name: str):
    """Get strategy by name"""
    return STRATEGY_REGISTRY.get(strategy_name)


def get_strategies_by_tier(tier: str):
    """Get all strategies for a subscription tier"""
    return {
        name: info for name, info in STRATEGY_REGISTRY.items()
        if _tier_includes(tier, info['tier'])
    }


def _tier_includes(user_tier: str, strategy_tier: str) -> bool:
    """Check if user tier includes access to strategy"""
    tier_hierarchy = {'free': 0, 'premium': 1, 'enterprise': 2}
    user_level = tier_hierarchy.get(user_tier, 0)
    strategy_level = tier_hierarchy.get(strategy_tier, 0)
    return user_level >= strategy_level
