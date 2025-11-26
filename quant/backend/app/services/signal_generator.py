"""
Real-Time Trading Signal Generator

Generates trading signals using AI providers, technical indicators,
and machine learning models.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import numpy as np
from pydantic import BaseModel

from app.ml.ensemble import EnsemblePredictor
from app.core.cache import cache_result


class SignalType(str, Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class SignalConfidence(str, Enum):
    """Signal confidence levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TradingSignal(BaseModel):
    """Trading signal model"""
    symbol: str
    signal_type: SignalType
    confidence: SignalConfidence
    confidence_score: float  # 0-1
    price: float
    timestamp: datetime
    indicators: Dict[str, float]
    risk_score: float  # 0-100
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    sources: List[str]  # Which models/indicators contributed


class SignalGenerator:
    """Generate trading signals using multiple methods"""

    def __init__(self, ensemble_predictor: Optional[EnsemblePredictor] = None):
        self.ensemble = ensemble_predictor

    async def generate_signal(
        self,
        symbol: str,
        price_data: List[float],
        volume_data: Optional[List[float]] = None,
        timestamps: Optional[List[datetime]] = None,
        use_ai: bool = True
    ) -> TradingSignal:
        """
        Generate comprehensive trading signal

        Args:
            symbol: Stock/asset symbol
            price_data: Historical price data
            volume_data: Historical volume data
            timestamps: Timestamps for data points
            use_ai: Whether to use AI providers for analysis

        Returns:
            TradingSignal with all analysis
        """
        # Calculate technical indicators
        indicators = self._calculate_indicators(price_data, volume_data)

        # Get ML predictions if ensemble available
        ml_prediction = None
        if self.ensemble and len(price_data) >= 30:
            try:
                ml_prediction = await self._get_ml_prediction(price_data)
            except Exception as e:
                print(f"ML prediction failed: {e}")

        # Combine signals from multiple sources
        signal_scores = self._combine_signals(indicators, ml_prediction)

        # Determine final signal
        signal_type, confidence, confidence_score = self._determine_signal(signal_scores)

        # Calculate risk metrics
        risk_score = self._calculate_risk(price_data, signal_type)

        # Calculate target and stop loss
        current_price = price_data[-1]
        target, stop_loss = self._calculate_levels(current_price, signal_type, risk_score)

        # Generate reasoning
        reasoning = self._generate_reasoning(indicators, signal_type, signal_scores)

        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            confidence_score=confidence_score,
            price=current_price,
            timestamp=timestamps[-1] if timestamps else datetime.utcnow(),
            indicators=indicators,
            risk_score=risk_score,
            target_price=target,
            stop_loss=stop_loss,
            reasoning=reasoning,
            sources=list(signal_scores.keys())
        )

    def _calculate_indicators(
        self,
        prices: List[float],
        volumes: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """Calculate technical indicators"""
        prices_arr = np.array(prices)

        indicators = {}

        # Simple Moving Averages
        if len(prices) >= 20:
            indicators['sma_20'] = np.mean(prices_arr[-20:])
        if len(prices) >= 50:
            indicators['sma_50'] = np.mean(prices_arr[-50:])
        if len(prices) >= 200:
            indicators['sma_200'] = np.mean(prices_arr[-200:])

        # Exponential Moving Average
        if len(prices) >= 12:
            indicators['ema_12'] = self._calculate_ema(prices_arr, 12)
        if len(prices) >= 26:
            indicators['ema_26'] = self._calculate_ema(prices_arr, 26)

        # MACD
        if 'ema_12' in indicators and 'ema_26' in indicators:
            indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
            if len(prices) >= 35:
                macd_line = [indicators['ema_12'] - indicators['ema_26']]
                indicators['macd_signal'] = self._calculate_ema(np.array(macd_line), 9)

        # RSI
        if len(prices) >= 14:
            indicators['rsi'] = self._calculate_rsi(prices_arr, 14)

        # Bollinger Bands
        if len(prices) >= 20:
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices_arr, 20)
            indicators['bb_upper'] = bb_upper
            indicators['bb_middle'] = bb_middle
            indicators['bb_lower'] = bb_lower
            indicators['bb_position'] = (prices_arr[-1] - bb_lower) / (bb_upper - bb_lower)

        # ATR (Average True Range)
        if len(prices) >= 14:
            indicators['atr'] = self._calculate_atr(prices_arr, 14)

        # Volume indicators
        if volumes and len(volumes) >= 20:
            volumes_arr = np.array(volumes)
            indicators['volume_sma_20'] = np.mean(volumes_arr[-20:])
            indicators['volume_ratio'] = volumes_arr[-1] / indicators['volume_sma_20']

        # Momentum
        if len(prices) >= 10:
            indicators['momentum_10'] = (prices_arr[-1] / prices_arr[-10] - 1) * 100

        # Volatility
        if len(prices) >= 20:
            returns = np.diff(prices_arr[-20:]) / prices_arr[-21:-1]
            indicators['volatility'] = np.std(returns) * 100

        return indicators

    def _calculate_ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return float(ema)

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    def _calculate_bollinger_bands(
        self,
        prices: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        middle = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return float(upper), float(middle), float(lower)

    def _calculate_atr(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range"""
        high_low = np.diff(prices[-period:])
        true_range = np.abs(high_low)
        atr = np.mean(true_range)
        return float(atr)

    async def _get_ml_prediction(self, prices: List[float]) -> Dict[str, float]:
        """Get ML model predictions"""
        # This would integrate with the ensemble predictor
        # Simplified for now
        return {
            'trend_score': 0.0,  # -1 to 1
            'prediction_confidence': 0.0
        }

    def _combine_signals(
        self,
        indicators: Dict[str, float],
        ml_prediction: Optional[Dict[str, float]]
    ) -> Dict[str, float]:
        """Combine signals from multiple sources"""
        scores = {}

        # RSI signal
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi < 30:
                scores['rsi'] = 1.0  # Oversold - buy
            elif rsi > 70:
                scores['rsi'] = -1.0  # Overbought - sell
            else:
                scores['rsi'] = (50 - rsi) / 20  # Linear scaling

        # MACD signal
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd_diff = indicators['macd'] - indicators['macd_signal']
            scores['macd'] = np.tanh(macd_diff * 10)  # Normalized

        # Moving average crossover
        if 'sma_20' in indicators and 'sma_50' in indicators:
            ma_diff = (indicators['sma_20'] - indicators['sma_50']) / indicators['sma_50']
            scores['ma_crossover'] = np.tanh(ma_diff * 20)

        # Bollinger Bands
        if 'bb_position' in indicators:
            bb_pos = indicators['bb_position']
            if bb_pos < 0.2:
                scores['bollinger'] = 1.0
            elif bb_pos > 0.8:
                scores['bollinger'] = -1.0
            else:
                scores['bollinger'] = 0.5 - bb_pos

        # Momentum
        if 'momentum_10' in indicators:
            momentum = indicators['momentum_10']
            scores['momentum'] = np.tanh(momentum / 10)

        # Volume
        if 'volume_ratio' in indicators:
            vol_ratio = indicators['volume_ratio']
            if vol_ratio > 1.5:
                scores['volume'] = 0.3  # High volume confirmation
            elif vol_ratio < 0.5:
                scores['volume'] = -0.2  # Low volume warning

        # ML prediction
        if ml_prediction:
            scores['ml_model'] = ml_prediction.get('trend_score', 0.0)

        return scores

    def _determine_signal(
        self,
        signal_scores: Dict[str, float]
    ) -> Tuple[SignalType, SignalConfidence, float]:
        """Determine final signal from combined scores"""
        if not signal_scores:
            return SignalType.HOLD, SignalConfidence.LOW, 0.5

        # Weighted average
        weights = {
            'rsi': 0.2,
            'macd': 0.2,
            'ma_crossover': 0.15,
            'bollinger': 0.15,
            'momentum': 0.15,
            'volume': 0.05,
            'ml_model': 0.1
        }

        weighted_score = 0.0
        total_weight = 0.0

        for indicator, score in signal_scores.items():
            weight = weights.get(indicator, 0.1)
            weighted_score += score * weight
            total_weight += weight

        if total_weight > 0:
            weighted_score /= total_weight

        # Determine signal type
        if weighted_score > 0.6:
            signal = SignalType.STRONG_BUY
        elif weighted_score > 0.2:
            signal = SignalType.BUY
        elif weighted_score < -0.6:
            signal = SignalType.STRONG_SELL
        elif weighted_score < -0.2:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD

        # Determine confidence
        confidence_score = abs(weighted_score)
        if confidence_score > 0.8:
            confidence = SignalConfidence.VERY_HIGH
        elif confidence_score > 0.6:
            confidence = SignalConfidence.HIGH
        elif confidence_score > 0.4:
            confidence = SignalConfidence.MEDIUM
        elif confidence_score > 0.2:
            confidence = SignalConfidence.LOW
        else:
            confidence = SignalConfidence.VERY_LOW

        return signal, confidence, confidence_score

    def _calculate_risk(self, prices: List[float], signal_type: SignalType) -> float:
        """Calculate risk score (0-100)"""
        prices_arr = np.array(prices)

        # Volatility risk
        if len(prices) >= 20:
            returns = np.diff(prices_arr[-20:]) / prices_arr[-21:-1]
            volatility = np.std(returns)
            volatility_risk = min(volatility * 1000, 50)  # 0-50
        else:
            volatility_risk = 25

        # Drawdown risk
        if len(prices) >= 50:
            peak = np.max(prices_arr[-50:])
            current = prices_arr[-1]
            drawdown = (peak - current) / peak
            drawdown_risk = drawdown * 100  # 0-100
        else:
            drawdown_risk = 0

        # Signal risk (opposite signals are risky)
        if signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            signal_risk = 10  # Lower risk for strong signals
        elif signal_type == SignalType.HOLD:
            signal_risk = 30  # Medium risk
        else:
            signal_risk = 20

        total_risk = (volatility_risk * 0.5 + drawdown_risk * 0.3 + signal_risk * 0.2)
        return min(max(total_risk, 0), 100)

    def _calculate_levels(
        self,
        current_price: float,
        signal_type: SignalType,
        risk_score: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate target and stop loss levels"""
        if signal_type == SignalType.HOLD:
            return None, None

        # Risk-adjusted targets
        risk_factor = risk_score / 100

        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            # Buy targets
            if signal_type == SignalType.STRONG_BUY:
                target_pct = 0.10 - (risk_factor * 0.05)  # 5-10%
                stop_pct = 0.03 + (risk_factor * 0.02)    # 3-5%
            else:
                target_pct = 0.05 - (risk_factor * 0.02)  # 3-5%
                stop_pct = 0.02 + (risk_factor * 0.015)   # 2-3.5%

            target = current_price * (1 + target_pct)
            stop_loss = current_price * (1 - stop_pct)
        else:
            # Sell targets
            if signal_type == SignalType.STRONG_SELL:
                target_pct = 0.10 - (risk_factor * 0.05)
                stop_pct = 0.03 + (risk_factor * 0.02)
            else:
                target_pct = 0.05 - (risk_factor * 0.02)
                stop_pct = 0.02 + (risk_factor * 0.015)

            target = current_price * (1 - target_pct)
            stop_loss = current_price * (1 + stop_pct)

        return round(target, 2), round(stop_loss, 2)

    def _generate_reasoning(
        self,
        indicators: Dict[str, float],
        signal_type: SignalType,
        signal_scores: Dict[str, float]
    ) -> str:
        """Generate human-readable reasoning for signal"""
        reasons = []

        # RSI reasoning
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi < 30:
                reasons.append(f"RSI at {rsi:.1f} indicates oversold conditions")
            elif rsi > 70:
                reasons.append(f"RSI at {rsi:.1f} indicates overbought conditions")

        # MACD reasoning
        if 'macd' in signal_scores and abs(signal_scores['macd']) > 0.3:
            if signal_scores['macd'] > 0:
                reasons.append("MACD shows bullish momentum")
            else:
                reasons.append("MACD shows bearish momentum")

        # MA reasoning
        if 'ma_crossover' in signal_scores and abs(signal_scores['ma_crossover']) > 0.2:
            if signal_scores['ma_crossover'] > 0:
                reasons.append("Short-term MA above long-term MA (bullish)")
            else:
                reasons.append("Short-term MA below long-term MA (bearish)")

        # Bollinger reasoning
        if 'bb_position' in indicators:
            bb_pos = indicators['bb_position']
            if bb_pos < 0.2:
                reasons.append("Price near lower Bollinger Band (potential bounce)")
            elif bb_pos > 0.8:
                reasons.append("Price near upper Bollinger Band (potential reversal)")

        # Volume reasoning
        if 'volume_ratio' in indicators:
            vol_ratio = indicators['volume_ratio']
            if vol_ratio > 1.5:
                reasons.append(f"High volume ({vol_ratio:.1f}x average) confirms trend")

        if not reasons:
            reasons.append("Multiple technical indicators suggest this signal")

        return ". ".join(reasons)


# Global instance
_signal_generator: Optional[SignalGenerator] = None


def get_signal_generator() -> SignalGenerator:
    """Get or create signal generator instance"""
    global _signal_generator
    if _signal_generator is None:
        _signal_generator = SignalGenerator()
    return _signal_generator
