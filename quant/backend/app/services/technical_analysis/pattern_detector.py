"""
Candlestick pattern detection using TA-Lib.

Detects 60+ candlestick patterns including:
- Reversal patterns: Hammer, Shooting Star, Engulfing, Morning/Evening Star
- Continuation patterns: Three White Soldiers, Three Black Crows
- Doji patterns: Dragonfly, Gravestone, Long-legged
- And many more...
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    logging.warning("TA-Lib not installed. Pattern detection unavailable. Install from: https://github.com/TA-Lib/ta-lib-python")

logger = logging.getLogger(__name__)


class PatternDetector:
    """Detect candlestick patterns in stock data."""

    # Candlestick pattern functions from TA-Lib
    PATTERN_FUNCTIONS = [
        # Reversal Patterns
        'CDLHAMMER', 'CDLINVERTEDHAMMER', 'CDLSHOOTINGSTAR', 'CDLHANGINGMAN',
        'CDLENGULFING', 'CDLHARAMI', 'CDLPIERCING', 'CDLDARKCLOUDCOVER',
        'CDLMORNINGSTAR', 'CDLEVENINGSTAR', 'CDLMORNINGDOJISTAR', 'CDLEVENINGDOJISTAR',

        # Doji Patterns
        'CDLDOJI', 'CDLDRAGONFLYDOJI', 'CDLGRAVESTONEDOJI', 'CDLLONGLEGGEDDOJI',
        'CDLDOJISTAR', 'CDL4PRICE DOJI',

        # Continuation Patterns
        'CDL3WHITESOLDIERS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3OUTSIDE',
        'CDLTHRUSTING', 'CDLSEPARATINGLINES', 'CDLIDENTICAL3CROWS',

        # Other Notable Patterns
        'CDLMARUBOZU', 'CDLSPINNINGTOP', 'CDLHIGHWAVE', 'CDLKICKING',
        'CDLTAKURI', 'CDLHIKKAKE', 'CDLABANDONEDBABY', 'CDLBREAKAWAY',
        'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLGAPSIDESIDEWHITE',
        'CDLHOMINGPIGEON', 'CDLLADDERBOTTOM', 'CDLMATHOLD', 'CDLRISEFALL3METHODS',
        'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTASUKIGAP', 'CDLTRISTAR',
        'CDLUNIQUE3RIVER', 'CDLXSIDEGAP3METHODS'
    ]

    # Pattern interpretations
    PATTERN_MEANINGS = {
        'CDLHAMMER': {'name': 'Hammer', 'type': 'bullish_reversal'},
        'CDLINVERTEDHAMMER': {'name': 'Inverted Hammer', 'type': 'bullish_reversal'},
        'CDLSHOOTINGSTAR': {'name': 'Shooting Star', 'type': 'bearish_reversal'},
        'CDLHANGINGMAN': {'name': 'Hanging Man', 'type': 'bearish_reversal'},
        'CDLENGULFING': {'name': 'Engulfing', 'type': 'reversal'},
        'CDLHARAMI': {'name': 'Harami', 'type': 'reversal'},
        'CDLPIERCING': {'name': 'Piercing Pattern', 'type': 'bullish_reversal'},
        'CDLDARKCLOUDCOVER': {'name': 'Dark Cloud Cover', 'type': 'bearish_reversal'},
        'CDLMORNINGSTAR': {'name': 'Morning Star', 'type': 'bullish_reversal'},
        'CDLEVENINGSTAR': {'name': 'Evening Star', 'type': 'bearish_reversal'},
        'CDLMORNINGDOJISTAR': {'name': 'Morning Doji Star', 'type': 'bullish_reversal'},
        'CDLEVENINGDOJISTAR': {'name': 'Evening Doji Star', 'type': 'bearish_reversal'},
        'CDLDOJI': {'name': 'Doji', 'type': 'indecision'},
        'CDLDRAGONFLYDOJI': {'name': 'Dragonfly Doji', 'type': 'bullish_reversal'},
        'CDLGRAVESTONEDOJI': {'name': 'Gravestone Doji', 'type': 'bearish_reversal'},
        'CDLLONGLEGGEDDOJI': {'name': 'Long-Legged Doji', 'type': 'indecision'},
        'CDL3WHITESOLDIERS': {'name': 'Three White Soldiers', 'type': 'bullish_continuation'},
        'CDL3BLACKCROWS': {'name': 'Three Black Crows', 'type': 'bearish_continuation'},
        'CDLMARUBOZU': {'name': 'Marubozu', 'type': 'continuation'},
        'CDLSPINNINGTOP': {'name': 'Spinning Top', 'type': 'indecision'},
    }

    def __init__(self):
        """Initialize pattern detector."""
        self.has_talib = HAS_TALIB
        if not HAS_TALIB:
            logger.warning("TA-Lib not available. Pattern detection will be limited.")

    def detect_all_patterns(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Detect all candlestick patterns in the data.

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dictionary with detected patterns:
            {
                'current': [list of patterns in last candle],
                'recent': [list of patterns in last 10 candles],
                'all': {pattern_name: [indices where pattern occurred]}
            }
        """
        if not self.has_talib:
            return self._fallback_pattern_detection(df)

        df = self._normalize_columns(df)

        open_prices = df['Open'].values
        high_prices = df['High'].values
        low_prices = df['Low'].values
        close_prices = df['Close'].values

        detected_patterns = {
            'current': [],
            'recent': [],
            'all': {}
        }

        # Detect each pattern
        for pattern_func in self.PATTERN_FUNCTIONS:
            try:
                func = getattr(talib, pattern_func)
                result = func(open_prices, high_prices, low_prices, close_prices)

                # Find where pattern occurred (non-zero values)
                pattern_indices = np.where(result != 0)[0]

                if len(pattern_indices) > 0:
                    detected_patterns['all'][pattern_func] = pattern_indices.tolist()

                    # Check last candle
                    if result[-1] != 0:
                        pattern_info = self._get_pattern_info(pattern_func, result[-1], len(df) - 1)
                        detected_patterns['current'].append(pattern_info)

                    # Check last 10 candles
                    recent_indices = pattern_indices[pattern_indices >= len(df) - 10]
                    for idx in recent_indices:
                        if idx != len(df) - 1:  # Skip current (already added)
                            pattern_info = self._get_pattern_info(pattern_func, result[idx], idx)
                            detected_patterns['recent'].append(pattern_info)

            except AttributeError:
                continue
            except Exception as e:
                logger.warning(f"Error detecting pattern {pattern_func}: {e}")

        # Sort recent patterns by recency
        detected_patterns['recent'] = sorted(
            detected_patterns['recent'],
            key=lambda x: x['index'],
            reverse=True
        )

        return detected_patterns

    def detect_specific_pattern(
        self,
        df: pd.DataFrame,
        pattern_name: str
    ) -> Optional[pd.Series]:
        """
        Detect a specific pattern.

        Args:
            df: DataFrame with OHLC data
            pattern_name: Pattern function name (e.g., 'CDLHAMMER')

        Returns:
            Series with pattern values (100=strong bullish, -100=strong bearish, 0=no pattern)
        """
        if not self.has_talib:
            return None

        df = self._normalize_columns(df)

        try:
            func = getattr(talib, pattern_name)
            result = func(
                df['Open'].values,
                df['High'].values,
                df['Low'].values,
                df['Close'].values
            )
            return pd.Series(result, index=df.index)
        except Exception as e:
            logger.error(f"Error detecting pattern {pattern_name}: {e}")
            return None

    def scan_multiple_symbols(
        self,
        data_dict: Dict[str, pd.DataFrame],
        pattern_filter: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Scan multiple symbols for patterns.

        Args:
            data_dict: Dictionary of {symbol: DataFrame}
            pattern_filter: List of specific patterns to look for (optional)

        Returns:
            Dictionary of {symbol: [patterns found]}
        """
        results = {}

        for symbol, df in data_dict.items():
            detected = self.detect_all_patterns(df)

            # Apply filter if specified
            if pattern_filter:
                filtered_current = [
                    p for p in detected['current']
                    if p['pattern'] in pattern_filter
                ]
                if filtered_current:
                    results[symbol] = filtered_current
            elif detected['current']:
                results[symbol] = detected['current']

        return results

    def get_bullish_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Get only bullish patterns from current candle."""
        all_patterns = self.detect_all_patterns(df)
        return [
            p for p in all_patterns['current']
            if 'bullish' in p.get('type', '')
        ]

    def get_bearish_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Get only bearish patterns from current candle."""
        all_patterns = self.detect_all_patterns(df)
        return [
            p for p in all_patterns['current']
            if 'bearish' in p.get('type', '')
        ]

    def _get_pattern_info(self, pattern_func: str, value: int, index: int) -> Dict:
        """Get detailed information about a detected pattern."""
        meaning = self.PATTERN_MEANINGS.get(pattern_func, {
            'name': pattern_func.replace('CDL', '').title(),
            'type': 'unknown'
        })

        # Value interpretation: 100=strong bullish, -100=strong bearish
        strength = 'strong' if abs(value) == 100 else 'weak'
        direction = 'bullish' if value > 0 else 'bearish'

        return {
            'pattern': pattern_func,
            'name': meaning['name'],
            'type': meaning['type'],
            'strength': strength,
            'direction': direction,
            'value': int(value),
            'index': index
        }

    def _fallback_pattern_detection(self, df: pd.DataFrame) -> Dict:
        """
        Fallback pattern detection without TA-Lib.
        Implements basic patterns manually.
        """
        df = self._normalize_columns(df)

        detected_patterns = {
            'current': [],
            'recent': [],
            'all': {}
        }

        # Basic Doji detection
        body_size = abs(df['Close'] - df['Open'])
        range_size = df['High'] - df['Low']
        body_ratio = body_size / (range_size + 0.0001)  # Avoid division by zero

        is_doji = body_ratio < 0.1

        if is_doji.iloc[-1]:
            detected_patterns['current'].append({
                'pattern': 'CDLDOJI',
                'name': 'Doji',
                'type': 'indecision',
                'strength': 'moderate',
                'direction': 'neutral',
                'value': 100,
                'index': len(df) - 1
            })

        # Basic Hammer detection
        lower_shadow = df['Open'].where(df['Close'] > df['Open'], df['Close']) - df['Low']
        upper_shadow = df['High'] - df['Close'].where(df['Close'] > df['Open'], df['Open'])

        is_hammer = (lower_shadow > 2 * body_size) & (upper_shadow < body_size)

        if is_hammer.iloc[-1]:
            detected_patterns['current'].append({
                'pattern': 'CDLHAMMER',
                'name': 'Hammer',
                'type': 'bullish_reversal',
                'strength': 'moderate',
                'direction': 'bullish',
                'value': 100,
                'index': len(df) - 1
            })

        logger.info("Using fallback pattern detection (limited patterns)")
        return detected_patterns

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names."""
        column_mapping = {
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'
        }
        df = df.copy()
        df.columns = [column_mapping.get(col, col) for col in df.columns]
        return df
