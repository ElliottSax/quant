"""
Pre-built trading strategies for stock prediction.

Implements common trading strategies:
- RSI Mean Reversion
- MACD Momentum
- Moving Average Crossover
- Bollinger Bands Breakout
- Multi-Factor Ensemble
"""

import logging
from typing import Dict, Optional, List
from enum import Enum
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class StrategySignal(str, Enum):
    """Strategy signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradingStrategy:
    """Base class for trading strategies."""

    def __init__(self, name: str):
        self.name = name

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """
        Generate trading signal.

        Args:
            df: DataFrame with OHLC data
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal, confidence, reasoning
        """
        raise NotImplementedError


class RSIMeanReversionStrategy(TradingStrategy):
    """
    RSI Mean Reversion Strategy.

    Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).
    """

    def __init__(
        self,
        oversold: int = 30,
        overbought: int = 70
    ):
        super().__init__("RSI Mean Reversion")
        self.oversold = oversold
        self.overbought = overbought

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """Generate RSI-based signal."""
        rsi = indicators['current'].get('rsi')

        if rsi is None:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.0,
                "reasoning": "RSI not available"
            }

        if rsi < self.oversold:
            confidence = min(1.0, (self.oversold - rsi) / self.oversold)
            return {
                "signal": StrategySignal.BUY,
                "confidence": confidence,
                "reasoning": f"RSI at {rsi:.2f} (oversold < {self.oversold})",
                "rsi": rsi
            }
        elif rsi > self.overbought:
            confidence = min(1.0, (rsi - self.overbought) / (100 - self.overbought))
            return {
                "signal": StrategySignal.SELL,
                "confidence": confidence,
                "reasoning": f"RSI at {rsi:.2f} (overbought > {self.overbought})",
                "rsi": rsi
            }
        else:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": f"RSI at {rsi:.2f} (neutral zone)",
                "rsi": rsi
            }


class MACDMomentumStrategy(TradingStrategy):
    """
    MACD Momentum Strategy.

    Buy when MACD crosses above signal line, sell when crosses below.
    """

    def __init__(self):
        super().__init__("MACD Momentum")

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """Generate MACD-based signal."""
        macd = indicators['current'].get('macd')
        macd_signal = indicators['current'].get('macd_signal')
        macd_hist = indicators['current'].get('macd_hist')

        if None in [macd, macd_signal, macd_hist]:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.0,
                "reasoning": "MACD indicators not available"
            }

        # Get previous histogram to detect crossover
        try:
            macd_series = indicators['trend'].get('macd_hist')
            if macd_series is not None and len(macd_series) > 1:
                prev_hist = macd_series.iloc[-2]

                # Bullish crossover
                if prev_hist < 0 and macd_hist > 0:
                    return {
                        "signal": StrategySignal.BUY,
                        "confidence": min(1.0, abs(macd_hist) / 2.0),
                        "reasoning": "MACD bullish crossover",
                        "macd": macd,
                        "signal_line": macd_signal,
                        "histogram": macd_hist
                    }

                # Bearish crossover
                elif prev_hist > 0 and macd_hist < 0:
                    return {
                        "signal": StrategySignal.SELL,
                        "confidence": min(1.0, abs(macd_hist) / 2.0),
                        "reasoning": "MACD bearish crossover",
                        "macd": macd,
                        "signal_line": macd_signal,
                        "histogram": macd_hist
                    }

        except:
            pass

        # No crossover, check current position
        if macd_hist > 0:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": "MACD above signal (bullish momentum)",
                "macd": macd,
                "signal_line": macd_signal
            }
        else:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": "MACD below signal (bearish momentum)",
                "macd": macd,
                "signal_line": macd_signal
            }


class MovingAverageCrossoverStrategy(TradingStrategy):
    """
    Moving Average Crossover Strategy.

    Buy when short MA crosses above long MA (Golden Cross).
    Sell when short MA crosses below long MA (Death Cross).
    """

    def __init__(
        self,
        short_period: int = 20,
        long_period: int = 50
    ):
        super().__init__("MA Crossover")
        self.short_period = short_period
        self.long_period = long_period

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """Generate MA crossover signal."""
        sma_short = indicators['current'].get(f'sma_{self.short_period}')
        sma_long = indicators['current'].get(f'sma_{self.long_period}')

        if None in [sma_short, sma_long]:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.0,
                "reasoning": "Moving averages not available"
            }

        try:
            # Get previous values to detect crossover
            sma_short_series = indicators['trend'].get(f'sma_{self.short_period}')
            sma_long_series = indicators['trend'].get(f'sma_{self.long_period}')

            if sma_short_series is not None and len(sma_short_series) > 1:
                prev_short = sma_short_series.iloc[-2]
                prev_long = sma_long_series.iloc[-2]

                # Golden Cross (bullish)
                if prev_short < prev_long and sma_short > sma_long:
                    spread = (sma_short - sma_long) / sma_long
                    return {
                        "signal": StrategySignal.BUY,
                        "confidence": min(1.0, spread * 10),
                        "reasoning": "Golden Cross detected",
                        "sma_short": sma_short,
                        "sma_long": sma_long
                    }

                # Death Cross (bearish)
                elif prev_short > prev_long and sma_short < sma_long:
                    spread = (sma_long - sma_short) / sma_long
                    return {
                        "signal": StrategySignal.SELL,
                        "confidence": min(1.0, spread * 10),
                        "reasoning": "Death Cross detected",
                        "sma_short": sma_short,
                        "sma_long": sma_long
                    }

        except:
            pass

        # No crossover, check current position
        if sma_short > sma_long:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": f"SMA {self.short_period} above SMA {self.long_period} (uptrend)",
                "sma_short": sma_short,
                "sma_long": sma_long
            }
        else:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": f"SMA {self.short_period} below SMA {self.long_period} (downtrend)",
                "sma_short": sma_short,
                "sma_long": sma_long
            }


class BollingerBandsStrategy(TradingStrategy):
    """
    Bollinger Bands Breakout Strategy.

    Buy when price breaks below lower band (oversold).
    Sell when price breaks above upper band (overbought).
    """

    def __init__(self):
        super().__init__("Bollinger Bands")

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """Generate Bollinger Bands signal."""
        current_price = float(df['Close'].iloc[-1])
        bb_upper = indicators['current'].get('bb_upper')
        bb_lower = indicators['current'].get('bb_lower')
        bb_middle = indicators['current'].get('bb_middle')

        if None in [bb_upper, bb_lower, bb_middle]:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.0,
                "reasoning": "Bollinger Bands not available"
            }

        # Calculate position within bands
        band_width = bb_upper - bb_lower
        position = (current_price - bb_lower) / band_width if band_width > 0 else 0.5

        # Below lower band (oversold)
        if current_price < bb_lower:
            distance = (bb_lower - current_price) / bb_lower
            return {
                "signal": StrategySignal.BUY,
                "confidence": min(1.0, distance * 20),
                "reasoning": f"Price below lower BB (oversold)",
                "price": current_price,
                "bb_lower": bb_lower,
                "bb_upper": bb_upper,
                "position_in_bands": position
            }

        # Above upper band (overbought)
        elif current_price > bb_upper:
            distance = (current_price - bb_upper) / bb_upper
            return {
                "signal": StrategySignal.SELL,
                "confidence": min(1.0, distance * 20),
                "reasoning": f"Price above upper BB (overbought)",
                "price": current_price,
                "bb_lower": bb_lower,
                "bb_upper": bb_upper,
                "position_in_bands": position
            }

        # Within bands
        else:
            return {
                "signal": StrategySignal.HOLD,
                "confidence": 0.5,
                "reasoning": f"Price within BB (neutral)",
                "price": current_price,
                "bb_lower": bb_lower,
                "bb_upper": bb_upper,
                "position_in_bands": round(position, 2)
            }


class MultiFactorEnsembleStrategy(TradingStrategy):
    """
    Multi-Factor Ensemble Strategy.

    Combines signals from multiple strategies with weighted voting.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None
    ):
        super().__init__("Multi-Factor Ensemble")

        # Initialize sub-strategies
        self.strategies = {
            "rsi": RSIMeanReversionStrategy(),
            "macd": MACDMomentumStrategy(),
            "ma_crossover": MovingAverageCrossoverStrategy(),
            "bollinger": BollingerBandsStrategy()
        }

        # Default weights (equal)
        self.weights = weights or {
            "rsi": 1.0,
            "macd": 1.0,
            "ma_crossover": 1.0,
            "bollinger": 1.0
        }

    def generate_signal(
        self,
        df: pd.DataFrame,
        indicators: Dict
    ) -> Dict[str, any]:
        """Generate ensemble signal."""
        signals = {}
        confidences = {}

        # Get signals from all strategies
        for name, strategy in self.strategies.items():
            try:
                result = strategy.generate_signal(df, indicators)
                signals[name] = result["signal"]
                confidences[name] = result["confidence"]
            except Exception as e:
                logger.warning(f"Strategy {name} failed: {e}")
                signals[name] = StrategySignal.HOLD
                confidences[name] = 0.0

        # Calculate weighted votes
        buy_score = sum(
            self.weights[name] * confidences[name]
            for name, signal in signals.items()
            if signal == StrategySignal.BUY
        )
        sell_score = sum(
            self.weights[name] * confidences[name]
            for name, signal in signals.items()
            if signal == StrategySignal.SELL
        )
        total_weight = sum(self.weights.values())

        # Determine overall signal
        buy_pct = buy_score / total_weight if total_weight > 0 else 0
        sell_pct = sell_score / total_weight if total_weight > 0 else 0

        if buy_pct > 0.5:
            signal = StrategySignal.BUY
            confidence = buy_pct
            reasoning = f"Ensemble BUY ({buy_pct:.1%} weighted vote)"
        elif sell_pct > 0.5:
            signal = StrategySignal.SELL
            confidence = sell_pct
            reasoning = f"Ensemble SELL ({sell_pct:.1%} weighted vote)"
        else:
            signal = StrategySignal.HOLD
            confidence = max(buy_pct, sell_pct)
            reasoning = f"Ensemble HOLD (no clear consensus)"

        return {
            "signal": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "individual_signals": {k: v.value for k, v in signals.items()},
            "individual_confidences": confidences,
            "buy_score": round(buy_pct, 3),
            "sell_score": round(sell_pct, 3)
        }


class StrategyFactory:
    """Factory for creating trading strategies."""

    @staticmethod
    def create_strategy(
        strategy_name: str,
        **kwargs
    ) -> TradingStrategy:
        """
        Create strategy by name.

        Args:
            strategy_name: Name of strategy
            **kwargs: Strategy-specific parameters

        Returns:
            TradingStrategy instance
        """
        strategies = {
            "rsi": RSIMeanReversionStrategy,
            "macd": MACDMomentumStrategy,
            "ma_crossover": MovingAverageCrossoverStrategy,
            "bollinger": BollingerBandsStrategy,
            "ensemble": MultiFactorEnsembleStrategy
        }

        strategy_class = strategies.get(strategy_name.lower())
        if not strategy_class:
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Available: {', '.join(strategies.keys())}"
            )

        return strategy_class(**kwargs)

    @staticmethod
    def list_strategies() -> List[Dict[str, str]]:
        """List available strategies with descriptions."""
        return [
            {
                "name": "rsi",
                "description": "RSI Mean Reversion - Buy oversold, sell overbought",
                "type": "mean_reversion"
            },
            {
                "name": "macd",
                "description": "MACD Momentum - Follow momentum crossovers",
                "type": "momentum"
            },
            {
                "name": "ma_crossover",
                "description": "Moving Average Crossover - Golden/Death cross signals",
                "type": "trend_following"
            },
            {
                "name": "bollinger",
                "description": "Bollinger Bands - Breakout strategy",
                "type": "volatility"
            },
            {
                "name": "ensemble",
                "description": "Multi-Factor Ensemble - Weighted combination of all strategies",
                "type": "ensemble"
            }
        ]
