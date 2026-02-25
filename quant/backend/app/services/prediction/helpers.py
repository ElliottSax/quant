"""
Helper utilities for prediction services.

Provides common functions for data processing, validation, and formatting.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PredictionHelpers:
    """Helper functions for prediction operations."""

    @staticmethod
    def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate stock ticker symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not symbol:
            return False, "Symbol cannot be empty"

        symbol = symbol.upper().strip()

        if len(symbol) > 10:
            return False, "Symbol too long (max 10 characters)"

        if not symbol.isalnum():
            return False, "Symbol must contain only letters and numbers"

        return True, None

    @staticmethod
    def calculate_price_change(
        current_price: float,
        previous_price: float
    ) -> Dict[str, float]:
        """
        Calculate price change metrics.

        Args:
            current_price: Current price
            previous_price: Previous price

        Returns:
            Dict with change, change_percent, direction
        """
        change = current_price - previous_price
        change_percent = (change / previous_price * 100) if previous_price != 0 else 0

        return {
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "direction": "UP" if change > 0 else "DOWN" if change < 0 else "NEUTRAL"
        }

    @staticmethod
    def calculate_confidence_tier(confidence: float) -> str:
        """
        Convert confidence score to tier.

        Args:
            confidence: Confidence score (0.0 to 1.0)

        Returns:
            Tier: "high", "medium", or "low"
        """
        if confidence >= 0.70:
            return "high"
        elif confidence >= 0.50:
            return "medium"
        else:
            return "low"

    @staticmethod
    def format_price(price: float, decimals: int = 2) -> str:
        """
        Format price for display.

        Args:
            price: Price value
            decimals: Number of decimal places

        Returns:
            Formatted price string
        """
        return f"${price:,.{decimals}f}"

    @staticmethod
    def calculate_returns(
        prices: List[float],
        periods: int = 1
    ) -> np.ndarray:
        """
        Calculate returns over specified periods.

        Args:
            prices: List of prices
            periods: Number of periods for return calculation

        Returns:
            Array of returns
        """
        prices_array = np.array(prices)
        returns = np.diff(prices_array, n=periods) / prices_array[:-periods]
        return returns

    @staticmethod
    def calculate_volatility(
        returns: np.ndarray,
        window: int = 20,
        annualize: bool = True
    ) -> float:
        """
        Calculate volatility from returns.

        Args:
            returns: Array of returns
            window: Rolling window size
            annualize: Whether to annualize volatility

        Returns:
            Volatility value
        """
        vol = np.std(returns[-window:])
        if annualize:
            vol *= np.sqrt(252)  # Trading days per year
        return float(vol)

    @staticmethod
    def detect_trend(
        prices: pd.Series,
        sma_short: int = 20,
        sma_long: int = 50
    ) -> str:
        """
        Detect price trend using moving averages.

        Args:
            prices: Price series
            sma_short: Short-term SMA period
            sma_long: Long-term SMA period

        Returns:
            Trend: "uptrend", "downtrend", or "sideways"
        """
        if len(prices) < sma_long:
            return "insufficient_data"

        sma_short_val = prices.rolling(sma_short).mean().iloc[-1]
        sma_long_val = prices.rolling(sma_long).mean().iloc[-1]

        if sma_short_val > sma_long_val * 1.02:  # 2% threshold
            return "uptrend"
        elif sma_short_val < sma_long_val * 0.98:
            return "downtrend"
        else:
            return "sideways"

    @staticmethod
    def calculate_support_resistance(
        df: pd.DataFrame,
        window: int = 20
    ) -> Dict[str, float]:
        """
        Calculate support and resistance levels.

        Args:
            df: DataFrame with OHLC data
            window: Window for calculation

        Returns:
            Dict with support and resistance levels
        """
        recent_data = df.tail(window)

        support = float(recent_data['Low'].min())
        resistance = float(recent_data['High'].max())
        current = float(df['Close'].iloc[-1])

        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "current": round(current, 2),
            "distance_to_support": round((current - support) / current * 100, 2),
            "distance_to_resistance": round((resistance - current) / current * 100, 2)
        }

    @staticmethod
    def filter_signals_by_confidence(
        signals: List[Dict[str, Any]],
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Filter signals by minimum confidence threshold.

        Args:
            signals: List of signal dictionaries
            min_confidence: Minimum confidence threshold

        Returns:
            Filtered list of signals
        """
        return [
            signal for signal in signals
            if signal.get('confidence', 0) >= min_confidence
        ]

    @staticmethod
    def aggregate_signals(
        signals: Dict[str, str],
        weights: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Aggregate multiple signals into overall recommendation.

        Args:
            signals: Dict of {strategy_name: signal}
            weights: Optional weights for each strategy

        Returns:
            Overall signal: "BUY", "SELL", or "HOLD"
        """
        if not signals:
            return "HOLD"

        # Default equal weights
        if not weights:
            weights = {k: 1.0 for k in signals.keys()}

        # Count weighted votes
        buy_score = sum(
            weights.get(k, 1.0) for k, v in signals.items()
            if v == "BUY"
        )
        sell_score = sum(
            weights.get(k, 1.0) for k, v in signals.items()
            if v == "SELL"
        )

        total_weight = sum(weights.values())

        # Determine overall signal
        if buy_score / total_weight > 0.5:
            return "BUY"
        elif sell_score / total_weight > 0.5:
            return "SELL"
        else:
            return "HOLD"

    @staticmethod
    def calculate_position_size(
        portfolio_value: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss_price: float
    ) -> Dict[str, Any]:
        """
        Calculate position size based on risk management.

        Args:
            portfolio_value: Total portfolio value
            risk_per_trade: Risk percentage per trade (e.g., 0.02 for 2%)
            entry_price: Entry price
            stop_loss_price: Stop loss price

        Returns:
            Dict with position size, shares, risk amount
        """
        risk_amount = portfolio_value * risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == 0:
            return {
                "shares": 0,
                "position_value": 0,
                "risk_amount": 0,
                "error": "Invalid stop loss (same as entry)"
            }

        shares = int(risk_amount / risk_per_share)
        position_value = shares * entry_price

        return {
            "shares": shares,
            "position_value": round(position_value, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_per_share": round(risk_per_share, 2),
            "percentage_of_portfolio": round(position_value / portfolio_value * 100, 2)
        }

    @staticmethod
    def format_prediction_result(
        symbol: str,
        current_price: float,
        predicted_price: float,
        confidence: float,
        signals: Dict[str, str],
        horizon_days: int = 5
    ) -> Dict[str, Any]:
        """
        Format prediction result for API response.

        Args:
            symbol: Stock symbol
            current_price: Current price
            predicted_price: Predicted price
            confidence: Confidence score
            signals: Technical signals
            horizon_days: Prediction horizon

        Returns:
            Formatted prediction dictionary
        """
        price_change = PredictionHelpers.calculate_price_change(
            predicted_price,
            current_price
        )

        return {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "horizon_days": horizon_days,
            "predicted_change": price_change["change"],
            "predicted_change_percent": price_change["change_percent"],
            "predicted_direction": price_change["direction"],
            "confidence": round(confidence, 4),
            "confidence_tier": PredictionHelpers.calculate_confidence_tier(confidence),
            "technical_signals": signals,
            "recommendation": PredictionHelpers.aggregate_signals(signals)
        }

    @staticmethod
    def validate_timeframe(
        period: str,
        interval: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate period and interval combination.

        Args:
            period: Time period (e.g., "1d", "1mo", "1y")
            interval: Data interval (e.g., "1m", "1h", "1d")

        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"]
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

        if period not in valid_periods:
            return False, f"Invalid period. Must be one of: {', '.join(valid_periods)}"

        if interval not in valid_intervals:
            return False, f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"

        # Validate interval vs period combination
        intraday_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]
        if interval in intraday_intervals and period in ["1y", "2y", "5y", "10y", "max"]:
            return False, "Intraday intervals not available for periods longer than 60 days"

        return True, None

    @staticmethod
    def batch_process(
        items: List[Any],
        batch_size: int = 10
    ) -> List[List[Any]]:
        """
        Split items into batches.

        Args:
            items: List of items to batch
            batch_size: Size of each batch

        Returns:
            List of batches
        """
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
