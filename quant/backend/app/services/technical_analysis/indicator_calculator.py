"""
Technical indicator calculator using pandas-ta.

Supports 130+ technical indicators:
- Momentum: RSI, Stochastic, Williams %R, ROC, MFI
- Trend: SMA, EMA, MACD, ADX, Aroon, Ichimoku
- Volatility: Bollinger Bands, ATR, Keltner Channels
- Volume: OBV, CMF, VWAP, PVT
- And many more...

Fallback to TA-Lib if available for additional patterns.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False
    logging.warning("pandas_ta not installed. Install with: pip install pandas-ta")

try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    logging.warning("TA-Lib not installed. Some features will be unavailable.")

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Calculate technical indicators for stock data."""

    def __init__(self):
        """Initialize indicator calculator."""
        self.has_pandas_ta = HAS_PANDAS_TA
        self.has_talib = HAS_TALIB

    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive set of indicators.

        Args:
            df: DataFrame with OHLCV data (Open, High, Low, Close, Volume)

        Returns:
            Dictionary with all calculated indicators
        """
        if df.empty:
            return {}

        # Ensure proper column names
        df = self._normalize_columns(df)

        indicators = {}

        # Calculate indicator groups
        indicators['momentum'] = self.calculate_momentum_indicators(df)
        indicators['trend'] = self.calculate_trend_indicators(df)
        indicators['volatility'] = self.calculate_volatility_indicators(df)
        indicators['volume'] = self.calculate_volume_indicators(df)

        # Current values (last row)
        indicators['current'] = self._get_current_values(df, indicators)

        # Signals
        indicators['signals'] = self.generate_signals(df, indicators)

        return indicators

    def calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate momentum indicators."""
        indicators = {}

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        if self.has_pandas_ta:
            # RSI (Relative Strength Index)
            indicators['rsi'] = ta.rsi(close, length=14)

            # Stochastic Oscillator
            stoch = ta.stoch(high, low, close)
            if stoch is not None:
                indicators['stoch_k'] = stoch['STOCHk_14_3_3']
                indicators['stoch_d'] = stoch['STOCHd_14_3_3']

            # Williams %R
            indicators['willr'] = ta.willr(high, low, close)

            # Rate of Change
            indicators['roc'] = ta.roc(close, length=10)

            # Money Flow Index
            indicators['mfi'] = ta.mfi(high, low, close, volume)

            # Commodity Channel Index
            indicators['cci'] = ta.cci(high, low, close)

        elif self.has_talib:
            # Fallback to TA-Lib
            indicators['rsi'] = talib.RSI(close, timeperiod=14)
            indicators['stoch_k'], indicators['stoch_d'] = talib.STOCH(high, low, close)
            indicators['willr'] = talib.WILLR(high, low, close)
            indicators['roc'] = talib.ROC(close, timeperiod=10)
            indicators['mfi'] = talib.MFI(high, low, close, volume)
            indicators['cci'] = talib.CCI(high, low, close)

        return indicators

    def calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate trend indicators."""
        indicators = {}

        close = df['Close']
        high = df['High']
        low = df['Low']

        if self.has_pandas_ta:
            # Moving Averages
            indicators['sma_20'] = ta.sma(close, length=20)
            indicators['sma_50'] = ta.sma(close, length=50)
            indicators['sma_200'] = ta.sma(close, length=200)
            indicators['ema_12'] = ta.ema(close, length=12)
            indicators['ema_26'] = ta.ema(close, length=26)

            # MACD
            macd = ta.macd(close)
            if macd is not None:
                indicators['macd'] = macd['MACD_12_26_9']
                indicators['macd_signal'] = macd['MACDs_12_26_9']
                indicators['macd_hist'] = macd['MACDh_12_26_9']

            # ADX (Average Directional Index)
            adx = ta.adx(high, low, close)
            if adx is not None:
                indicators['adx'] = adx['ADX_14']
                indicators['dmp'] = adx['DMP_14']
                indicators['dmn'] = adx['DMN_14']

            # Aroon
            aroon = ta.aroon(high, low)
            if aroon is not None:
                indicators['aroon_up'] = aroon['AROONU_14']
                indicators['aroon_down'] = aroon['AROOND_14']

        elif self.has_talib:
            # Fallback to TA-Lib
            indicators['sma_20'] = talib.SMA(close, timeperiod=20)
            indicators['sma_50'] = talib.SMA(close, timeperiod=50)
            indicators['sma_200'] = talib.SMA(close, timeperiod=200)
            indicators['ema_12'] = talib.EMA(close, timeperiod=12)
            indicators['ema_26'] = talib.EMA(close, timeperiod=26)

            macd, signal, hist = talib.MACD(close)
            indicators['macd'] = macd
            indicators['macd_signal'] = signal
            indicators['macd_hist'] = hist

            indicators['adx'] = talib.ADX(high, low, close)
            indicators['dmp'] = talib.PLUS_DI(high, low, close)
            indicators['dmn'] = talib.MINUS_DI(high, low, close)

            indicators['aroon_up'], indicators['aroon_down'] = talib.AROON(high, low)

        return indicators

    def calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volatility indicators."""
        indicators = {}

        close = df['Close']
        high = df['High']
        low = df['Low']

        if self.has_pandas_ta:
            # Bollinger Bands
            bbands = ta.bbands(close)
            if bbands is not None:
                indicators['bb_upper'] = bbands['BBU_20_2.0']
                indicators['bb_middle'] = bbands['BBM_20_2.0']
                indicators['bb_lower'] = bbands['BBL_20_2.0']
                indicators['bb_bandwidth'] = bbands['BBB_20_2.0']

            # ATR (Average True Range)
            indicators['atr'] = ta.atr(high, low, close)

            # Keltner Channels
            kc = ta.kc(high, low, close)
            if kc is not None:
                indicators['kc_upper'] = kc['KCUe_20_2']
                indicators['kc_middle'] = kc['KCBe_20_2']
                indicators['kc_lower'] = kc['KCLe_20_2']

            # Donchian Channels
            dc = ta.donchian(high, low)
            if dc is not None:
                indicators['dc_upper'] = dc['DCU_20_20']
                indicators['dc_middle'] = dc['DCM_20_20']
                indicators['dc_lower'] = dc['DCL_20_20']

        elif self.has_talib:
            # Fallback to TA-Lib
            upper, middle, lower = talib.BBANDS(close)
            indicators['bb_upper'] = upper
            indicators['bb_middle'] = middle
            indicators['bb_lower'] = lower

            indicators['atr'] = talib.ATR(high, low, close)

        return indicators

    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volume indicators."""
        indicators = {}

        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']

        if self.has_pandas_ta:
            # OBV (On-Balance Volume)
            indicators['obv'] = ta.obv(close, volume)

            # CMF (Chaikin Money Flow)
            indicators['cmf'] = ta.cmf(high, low, close, volume)

            # VWAP (Volume Weighted Average Price)
            indicators['vwap'] = ta.vwap(high, low, close, volume)

            # PVT (Price Volume Trend)
            indicators['pvt'] = ta.pvt(close, volume)

        elif self.has_talib:
            # Fallback to TA-Lib
            indicators['obv'] = talib.OBV(close, volume)
            indicators['ad'] = talib.AD(high, low, close, volume)  # Accumulation/Distribution

        return indicators

    def generate_signals(self, df: pd.DataFrame, indicators: Dict) -> Dict[str, str]:
        """
        Generate buy/sell/hold signals based on indicators.

        Returns:
            Dictionary with signals for different strategies
        """
        signals = {}

        try:
            # RSI Signal
            rsi = indicators['momentum'].get('rsi')
            if rsi is not None and len(rsi) > 0:
                current_rsi = rsi.iloc[-1]
                if current_rsi < 30:
                    signals['rsi'] = 'BUY'
                elif current_rsi > 70:
                    signals['rsi'] = 'SELL'
                else:
                    signals['rsi'] = 'HOLD'

            # MACD Signal
            macd = indicators['trend'].get('macd')
            macd_signal = indicators['trend'].get('macd_signal')
            if macd is not None and macd_signal is not None and len(macd) > 1:
                if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
                    signals['macd'] = 'BUY'
                elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
                    signals['macd'] = 'SELL'
                else:
                    signals['macd'] = 'HOLD'

            # Moving Average Crossover
            sma_20 = indicators['trend'].get('sma_20')
            sma_50 = indicators['trend'].get('sma_50')
            close = df['Close']
            if sma_20 is not None and sma_50 is not None and len(sma_20) > 1:
                if sma_20.iloc[-1] > sma_50.iloc[-1] and sma_20.iloc[-2] <= sma_50.iloc[-2]:
                    signals['ma_crossover'] = 'BUY'
                elif sma_20.iloc[-1] < sma_50.iloc[-1] and sma_20.iloc[-2] >= sma_50.iloc[-2]:
                    signals['ma_crossover'] = 'SELL'
                else:
                    signals['ma_crossover'] = 'HOLD'

            # Bollinger Bands
            bb_upper = indicators['volatility'].get('bb_upper')
            bb_lower = indicators['volatility'].get('bb_lower')
            if bb_upper is not None and bb_lower is not None:
                current_price = close.iloc[-1]
                if current_price < bb_lower.iloc[-1]:
                    signals['bollinger'] = 'BUY'
                elif current_price > bb_upper.iloc[-1]:
                    signals['bollinger'] = 'SELL'
                else:
                    signals['bollinger'] = 'HOLD'

            # Overall Signal (majority vote)
            buy_count = sum(1 for s in signals.values() if s == 'BUY')
            sell_count = sum(1 for s in signals.values() if s == 'SELL')

            if buy_count > sell_count:
                signals['overall'] = 'BUY'
            elif sell_count > buy_count:
                signals['overall'] = 'SELL'
            else:
                signals['overall'] = 'HOLD'

        except Exception as e:
            logger.error(f"Error generating signals: {e}")

        return signals

    def _get_current_values(self, df: pd.DataFrame, indicators: Dict) -> Dict[str, float]:
        """Extract current (last) values from all indicators."""
        current = {}

        # Price data
        current['price'] = float(df['Close'].iloc[-1])
        current['volume'] = float(df['Volume'].iloc[-1])

        # Extract last value from each indicator
        for category, indicator_dict in indicators.items():
            if category in ['current', 'signals']:
                continue
            for name, series in indicator_dict.items():
                if series is not None and len(series) > 0:
                    try:
                        current[name] = float(series.iloc[-1])
                    except:
                        pass

        return current

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format."""
        column_mapping = {
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume',
            'Open': 'Open', 'High': 'High', 'Low': 'Low',
            'Close': 'Close', 'Volume': 'Volume'
        }

        df = df.copy()
        df.columns = [column_mapping.get(col, col) for col in df.columns]

        return df
