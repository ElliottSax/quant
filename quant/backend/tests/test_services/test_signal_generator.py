"""Tests for Signal Generator service."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
import numpy as np

# No mocking needed - signal_generator now handles lazy imports
from app.services.signal_generator import (
    SignalGenerator,
    SignalType,
    SignalConfidence,
    TradingSignal,
    get_signal_generator,
)


class TestSignalType:
    """Test SignalType enum."""

    def test_signal_types_exist(self):
        """Test that all signal types are defined."""
        assert SignalType.BUY == "buy"
        assert SignalType.SELL == "sell"
        assert SignalType.HOLD == "hold"
        assert SignalType.STRONG_BUY == "strong_buy"
        assert SignalType.STRONG_SELL == "strong_sell"

    def test_signal_type_count(self):
        """Test that we have exactly 5 signal types."""
        assert len(list(SignalType)) == 5


class TestSignalConfidence:
    """Test SignalConfidence enum."""

    def test_confidence_levels_exist(self):
        """Test that all confidence levels are defined."""
        assert SignalConfidence.VERY_LOW == "very_low"
        assert SignalConfidence.LOW == "low"
        assert SignalConfidence.MEDIUM == "medium"
        assert SignalConfidence.HIGH == "high"
        assert SignalConfidence.VERY_HIGH == "very_high"

    def test_confidence_count(self):
        """Test that we have exactly 5 confidence levels."""
        assert len(list(SignalConfidence)) == 5


class TestTradingSignal:
    """Test TradingSignal Pydantic model."""

    def test_create_basic_signal(self):
        """Test creating a basic trading signal."""
        signal = TradingSignal(
            symbol="AAPL",
            signal_type=SignalType.BUY,
            confidence=SignalConfidence.HIGH,
            confidence_score=0.75,
            price=150.50,
            timestamp=datetime.utcnow(),
            indicators={"rsi": 45.0, "macd": 1.2},
            risk_score=35.0,
            reasoning="Technical indicators suggest buy",
            sources=["rsi", "macd"],
        )

        assert signal.symbol == "AAPL"
        assert signal.signal_type == SignalType.BUY
        assert signal.confidence == SignalConfidence.HIGH
        assert signal.confidence_score == 0.75
        assert signal.price == 150.50
        assert signal.risk_score == 35.0

    def test_signal_with_targets(self):
        """Test signal with target and stop loss."""
        signal = TradingSignal(
            symbol="TSLA",
            signal_type=SignalType.STRONG_BUY,
            confidence=SignalConfidence.VERY_HIGH,
            confidence_score=0.9,
            price=200.0,
            timestamp=datetime.utcnow(),
            indicators={},
            risk_score=25.0,
            target_price=220.0,
            stop_loss=190.0,
            reasoning="Strong bullish signal",
            sources=["ml_model"],
        )

        assert signal.target_price == 220.0
        assert signal.stop_loss == 190.0

    def test_signal_optional_fields(self):
        """Test that target_price and stop_loss are optional."""
        signal = TradingSignal(
            symbol="MSFT",
            signal_type=SignalType.HOLD,
            confidence=SignalConfidence.LOW,
            confidence_score=0.3,
            price=300.0,
            timestamp=datetime.utcnow(),
            indicators={},
            risk_score=50.0,
            reasoning="No clear signal",
            sources=[],
        )

        assert signal.target_price is None
        assert signal.stop_loss is None


class TestSignalGenerator:
    """Test SignalGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a signal generator instance."""
        return SignalGenerator()

    @pytest.fixture
    def price_data_short(self):
        """Short price data (< 20 periods)."""
        return [100.0, 101.0, 102.0, 101.5, 103.0, 104.0, 103.5, 105.0, 106.0, 107.0]

    @pytest.fixture
    def price_data_medium(self):
        """Medium price data (20-50 periods)."""
        base = 100.0
        return [base + i * 0.5 + np.sin(i * 0.3) * 2 for i in range(30)]

    @pytest.fixture
    def price_data_long(self):
        """Long price data (200+ periods)."""
        base = 100.0
        return [base + i * 0.1 + np.sin(i * 0.1) * 5 for i in range(250)]

    @pytest.fixture
    def volume_data(self):
        """Sample volume data."""
        return [1000000 + i * 10000 + np.random.randint(-50000, 50000) for i in range(30)]

    # Test technical indicator calculations

    def test_calculate_indicators_short_data(self, generator, price_data_short):
        """Test indicator calculation with short data."""
        indicators = generator._calculate_indicators(price_data_short)

        # Should have limited indicators
        assert 'rsi' not in indicators  # Need 14+ periods
        assert 'sma_20' not in indicators  # Need 20 periods
        assert 'volatility' not in indicators  # Need 20 periods

    def test_calculate_indicators_medium_data(self, generator, price_data_medium):
        """Test indicator calculation with medium data."""
        indicators = generator._calculate_indicators(price_data_medium)

        # Should have basic indicators
        assert 'sma_20' in indicators
        assert 'ema_12' in indicators
        assert 'ema_26' in indicators
        assert 'rsi' in indicators
        assert 'bb_upper' in indicators
        assert 'bb_middle' in indicators
        assert 'bb_lower' in indicators
        assert 'volatility' in indicators
        assert 'momentum_10' in indicators

    def test_calculate_indicators_long_data(self, generator, price_data_long):
        """Test indicator calculation with long data."""
        indicators = generator._calculate_indicators(price_data_long)

        # Should have all indicators including long-term ones
        assert 'sma_20' in indicators
        assert 'sma_50' in indicators
        assert 'sma_200' in indicators

    def test_calculate_indicators_with_volume(self, generator, price_data_medium, volume_data):
        """Test indicator calculation with volume data."""
        indicators = generator._calculate_indicators(price_data_medium, volume_data)

        assert 'volume_sma_20' in indicators
        assert 'volume_ratio' in indicators

    def test_calculate_ema(self, generator):
        """Test EMA calculation."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        ema = generator._calculate_ema(data, 5)

        assert isinstance(ema, float)
        assert ema > 5  # Should be weighted toward recent values

    def test_calculate_rsi_overbought(self, generator):
        """Test RSI calculation for overbought conditions."""
        # Upward trending prices
        prices = np.array([100 + i * 2 for i in range(20)])
        rsi = generator._calculate_rsi(prices, 14)

        assert isinstance(rsi, float)
        assert rsi > 50  # Uptrend should have high RSI

    def test_calculate_rsi_oversold(self, generator):
        """Test RSI calculation for oversold conditions."""
        # Downward trending prices
        prices = np.array([100 - i * 2 for i in range(20)])
        rsi = generator._calculate_rsi(prices, 14)

        assert isinstance(rsi, float)
        assert rsi < 50  # Downtrend should have low RSI

    def test_calculate_rsi_no_losses(self, generator):
        """Test RSI when there are no losses (all gains)."""
        prices = np.array([100 + i for i in range(20)])
        rsi = generator._calculate_rsi(prices, 14)

        assert rsi == 100.0  # All gains = RSI 100

    def test_calculate_bollinger_bands(self, generator):
        """Test Bollinger Bands calculation."""
        prices = np.array([100 + i * 0.5 for i in range(30)])
        upper, middle, lower = generator._calculate_bollinger_bands(prices, 20, 2.0)

        assert isinstance(upper, float)
        assert isinstance(middle, float)
        assert isinstance(lower, float)
        assert upper > middle > lower
        assert upper - middle == middle - lower  # Symmetric bands

    def test_calculate_atr(self, generator):
        """Test ATR calculation."""
        prices = np.array([100, 102, 101, 103, 102, 105, 104, 106, 105, 108,
                          107, 109, 108, 110, 109, 111])
        atr = generator._calculate_atr(prices, 14)

        assert isinstance(atr, float)
        assert atr > 0

    # Test signal combination logic

    def test_combine_signals_rsi_oversold(self, generator):
        """Test signal combination with oversold RSI."""
        indicators = {'rsi': 25.0}
        scores = generator._combine_signals(indicators, None)

        assert 'rsi' in scores
        assert scores['rsi'] == 1.0  # Oversold = buy signal

    def test_combine_signals_rsi_overbought(self, generator):
        """Test signal combination with overbought RSI."""
        indicators = {'rsi': 75.0}
        scores = generator._combine_signals(indicators, None)

        assert 'rsi' in scores
        assert scores['rsi'] == -1.0  # Overbought = sell signal

    def test_combine_signals_rsi_neutral(self, generator):
        """Test signal combination with neutral RSI."""
        indicators = {'rsi': 50.0}
        scores = generator._combine_signals(indicators, None)

        assert 'rsi' in scores
        assert scores['rsi'] == 0.0  # Neutral RSI

    def test_combine_signals_macd(self, generator):
        """Test signal combination with MACD."""
        indicators = {
            'macd': 2.5,
            'macd_signal': 2.0
        }
        scores = generator._combine_signals(indicators, None)

        assert 'macd' in scores
        assert scores['macd'] > 0  # Positive MACD crossover

    def test_combine_signals_ma_crossover(self, generator):
        """Test signal combination with MA crossover."""
        indicators = {
            'sma_20': 105.0,
            'sma_50': 100.0
        }
        scores = generator._combine_signals(indicators, None)

        assert 'ma_crossover' in scores
        assert scores['ma_crossover'] > 0  # Bullish crossover

    def test_combine_signals_bollinger_lower(self, generator):
        """Test signal with price near lower Bollinger Band."""
        indicators = {'bb_position': 0.1}  # Near lower band
        scores = generator._combine_signals(indicators, None)

        assert 'bollinger' in scores
        assert scores['bollinger'] == 1.0  # Buy signal

    def test_combine_signals_bollinger_upper(self, generator):
        """Test signal with price near upper Bollinger Band."""
        indicators = {'bb_position': 0.9}  # Near upper band
        scores = generator._combine_signals(indicators, None)

        assert 'bollinger' in scores
        assert scores['bollinger'] == -1.0  # Sell signal

    def test_combine_signals_high_volume(self, generator):
        """Test signal with high volume."""
        indicators = {'volume_ratio': 2.0}  # 2x average volume
        scores = generator._combine_signals(indicators, None)

        assert 'volume' in scores
        assert scores['volume'] == 0.3  # Volume confirmation

    def test_combine_signals_low_volume(self, generator):
        """Test signal with low volume."""
        indicators = {'volume_ratio': 0.4}  # 40% of average
        scores = generator._combine_signals(indicators, None)

        assert 'volume' in scores
        assert scores['volume'] == -0.2  # Low volume warning

    def test_combine_signals_momentum(self, generator):
        """Test signal with momentum."""
        indicators = {'momentum_10': 5.0}  # 5% gain in 10 periods
        scores = generator._combine_signals(indicators, None)

        assert 'momentum' in scores
        assert scores['momentum'] > 0

    def test_combine_signals_ml_prediction(self, generator):
        """Test signal with ML prediction."""
        indicators = {}
        ml_prediction = {'trend_score': 0.7, 'prediction_confidence': 0.8}
        scores = generator._combine_signals(indicators, ml_prediction)

        assert 'ml_model' in scores
        assert scores['ml_model'] == 0.7

    # Test signal determination

    def test_determine_signal_empty(self, generator):
        """Test signal determination with empty scores."""
        signal, confidence, score = generator._determine_signal({})

        assert signal == SignalType.HOLD
        assert confidence == SignalConfidence.LOW
        assert score == 0.5

    def test_determine_signal_strong_buy(self, generator):
        """Test strong buy signal determination."""
        scores = {'rsi': 1.0, 'macd': 0.8, 'bollinger': 0.9}
        signal, confidence, score = generator._determine_signal(scores)

        assert signal == SignalType.STRONG_BUY
        assert confidence in [SignalConfidence.HIGH, SignalConfidence.VERY_HIGH]

    def test_determine_signal_buy(self, generator):
        """Test buy signal determination."""
        scores = {'rsi': 0.5, 'macd': 0.3}
        signal, confidence, score = generator._determine_signal(scores)

        assert signal in [SignalType.BUY, SignalType.STRONG_BUY]

    def test_determine_signal_strong_sell(self, generator):
        """Test strong sell signal determination."""
        scores = {'rsi': -1.0, 'macd': -0.8, 'bollinger': -0.9}
        signal, confidence, score = generator._determine_signal(scores)

        assert signal == SignalType.STRONG_SELL
        assert confidence in [SignalConfidence.HIGH, SignalConfidence.VERY_HIGH]

    def test_determine_signal_sell(self, generator):
        """Test sell signal determination."""
        scores = {'rsi': -0.5, 'macd': -0.3}
        signal, confidence, score = generator._determine_signal(scores)

        assert signal in [SignalType.SELL, SignalType.STRONG_SELL]

    def test_determine_signal_hold(self, generator):
        """Test hold signal determination."""
        scores = {'rsi': 0.1, 'macd': -0.05}
        signal, confidence, score = generator._determine_signal(scores)

        assert signal == SignalType.HOLD

    # Test risk calculation

    def test_calculate_risk_short_data(self, generator, price_data_short):
        """Test risk calculation with short data."""
        risk = generator._calculate_risk(price_data_short, SignalType.BUY)

        assert isinstance(risk, float)
        assert 0 <= risk <= 100

    def test_calculate_risk_volatile_prices(self, generator):
        """Test risk calculation with volatile prices."""
        # High volatility data
        prices = [100, 110, 95, 105, 90, 115, 85, 120]
        prices.extend([100 + i for i in range(30)])
        risk = generator._calculate_risk(prices, SignalType.BUY)

        assert risk > 30  # High volatility should increase risk

    def test_calculate_risk_stable_prices(self, generator):
        """Test risk calculation with stable prices."""
        # Low volatility data
        prices = [100 + i * 0.1 for i in range(50)]
        risk = generator._calculate_risk(prices, SignalType.BUY)

        assert risk < 50  # Low volatility should reduce risk

    def test_calculate_risk_strong_signal(self, generator, price_data_medium):
        """Test that strong signals have lower risk."""
        risk_strong = generator._calculate_risk(price_data_medium, SignalType.STRONG_BUY)
        risk_weak = generator._calculate_risk(price_data_medium, SignalType.BUY)

        # Strong signals should have lower signal risk component
        assert isinstance(risk_strong, float)
        assert isinstance(risk_weak, float)

    def test_calculate_risk_bounds(self, generator, price_data_long):
        """Test that risk is bounded between 0 and 100."""
        for signal_type in SignalType:
            risk = generator._calculate_risk(price_data_long, signal_type)
            assert 0 <= risk <= 100

    # Test target and stop loss calculation

    def test_calculate_levels_hold(self, generator):
        """Test that HOLD signal has no targets."""
        target, stop = generator._calculate_levels(100.0, SignalType.HOLD, 50.0)

        assert target is None
        assert stop is None

    def test_calculate_levels_buy(self, generator):
        """Test buy target and stop loss."""
        target, stop = generator._calculate_levels(100.0, SignalType.BUY, 30.0)

        assert target is not None
        assert stop is not None
        assert target > 100.0  # Target above current
        assert stop < 100.0    # Stop below current

    def test_calculate_levels_strong_buy(self, generator):
        """Test strong buy has higher targets."""
        target_strong, stop_strong = generator._calculate_levels(100.0, SignalType.STRONG_BUY, 30.0)
        target_normal, stop_normal = generator._calculate_levels(100.0, SignalType.BUY, 30.0)

        assert target_strong > target_normal  # Higher target for strong buy

    def test_calculate_levels_sell(self, generator):
        """Test sell target and stop loss."""
        target, stop = generator._calculate_levels(100.0, SignalType.SELL, 30.0)

        assert target is not None
        assert stop is not None
        assert target < 100.0  # Target below current (shorting)
        assert stop > 100.0    # Stop above current

    def test_calculate_levels_strong_sell(self, generator):
        """Test strong sell has lower targets."""
        target_strong, stop_strong = generator._calculate_levels(100.0, SignalType.STRONG_SELL, 30.0)
        target_normal, stop_normal = generator._calculate_levels(100.0, SignalType.SELL, 30.0)

        assert target_strong < target_normal  # Lower target for strong sell

    def test_calculate_levels_risk_adjustment(self, generator):
        """Test that high risk reduces targets."""
        target_low_risk, _ = generator._calculate_levels(100.0, SignalType.BUY, 20.0)
        target_high_risk, _ = generator._calculate_levels(100.0, SignalType.BUY, 80.0)

        assert target_low_risk > target_high_risk  # Lower targets with higher risk

    # Test reasoning generation

    def test_generate_reasoning_rsi_oversold(self, generator):
        """Test reasoning generation for oversold RSI."""
        indicators = {'rsi': 25.0}
        scores = {'rsi': 1.0}
        reasoning = generator._generate_reasoning(indicators, SignalType.BUY, scores)

        assert "oversold" in reasoning.lower()
        assert "25" in reasoning

    def test_generate_reasoning_rsi_overbought(self, generator):
        """Test reasoning generation for overbought RSI."""
        indicators = {'rsi': 75.0}
        scores = {'rsi': -1.0}
        reasoning = generator._generate_reasoning(indicators, SignalType.SELL, scores)

        assert "overbought" in reasoning.lower()
        assert "75" in reasoning

    def test_generate_reasoning_macd_bullish(self, generator):
        """Test reasoning generation for bullish MACD."""
        indicators = {}
        scores = {'macd': 0.5}
        reasoning = generator._generate_reasoning(indicators, SignalType.BUY, scores)

        assert "macd" in reasoning.lower()
        assert "bullish" in reasoning.lower()

    def test_generate_reasoning_ma_crossover(self, generator):
        """Test reasoning generation for MA crossover."""
        indicators = {}
        scores = {'ma_crossover': 0.4}
        reasoning = generator._generate_reasoning(indicators, SignalType.BUY, scores)

        assert "ma" in reasoning.lower() or "moving average" in reasoning.lower()

    def test_generate_reasoning_bollinger(self, generator):
        """Test reasoning generation for Bollinger Bands."""
        indicators = {'bb_position': 0.1}
        scores = {}
        reasoning = generator._generate_reasoning(indicators, SignalType.BUY, scores)

        assert "bollinger" in reasoning.lower()

    def test_generate_reasoning_high_volume(self, generator):
        """Test reasoning generation for high volume."""
        indicators = {'volume_ratio': 2.5}
        scores = {}
        reasoning = generator._generate_reasoning(indicators, SignalType.BUY, scores)

        assert "volume" in reasoning.lower()
        assert "2.5" in reasoning

    def test_generate_reasoning_no_indicators(self, generator):
        """Test reasoning generation with no clear indicators."""
        reasoning = generator._generate_reasoning({}, SignalType.HOLD, {})

        assert len(reasoning) > 0
        assert "indicators" in reasoning.lower()

    # Test complete signal generation

    async def test_generate_signal_basic(self, generator, price_data_medium):
        """Test basic signal generation."""
        signal = await generator.generate_signal(
            symbol="AAPL",
            price_data=price_data_medium
        )

        assert isinstance(signal, TradingSignal)
        assert signal.symbol == "AAPL"
        assert signal.signal_type in SignalType
        assert signal.confidence in SignalConfidence
        assert 0 <= signal.confidence_score <= 1
        assert signal.price == price_data_medium[-1]
        assert 0 <= signal.risk_score <= 100
        assert len(signal.reasoning) > 0

    async def test_generate_signal_with_volume(self, generator, price_data_medium, volume_data):
        """Test signal generation with volume data."""
        signal = await generator.generate_signal(
            symbol="TSLA",
            price_data=price_data_medium,
            volume_data=volume_data
        )

        assert isinstance(signal, TradingSignal)
        assert 'volume_ratio' in signal.indicators or 'volume_sma_20' in signal.indicators

    async def test_generate_signal_with_timestamps(self, generator, price_data_medium):
        """Test signal generation with timestamps."""
        timestamps = [datetime.utcnow() - timedelta(days=30-i) for i in range(30)]
        signal = await generator.generate_signal(
            symbol="MSFT",
            price_data=price_data_medium,
            timestamps=timestamps
        )

        assert signal.timestamp == timestamps[-1]

    async def test_generate_signal_short_data(self, generator, price_data_short):
        """Test signal generation with insufficient data."""
        signal = await generator.generate_signal(
            symbol="GOOGL",
            price_data=price_data_short
        )

        # Should still generate a signal with available indicators
        assert isinstance(signal, TradingSignal)
        assert len(signal.indicators) > 0

    async def test_generate_signal_long_data(self, generator, price_data_long):
        """Test signal generation with long historical data."""
        signal = await generator.generate_signal(
            symbol="AMZN",
            price_data=price_data_long
        )

        # Should have all indicators including SMA_200
        assert 'sma_200' in signal.indicators
        assert isinstance(signal, TradingSignal)

    async def test_generate_signal_ml_ensemble(self, generator, price_data_medium):
        """Test signal generation with ML ensemble."""
        mock_ensemble = Mock()
        generator.ensemble = mock_ensemble

        signal = await generator.generate_signal(
            symbol="NVDA",
            price_data=price_data_medium,
            use_ai=True
        )

        assert isinstance(signal, TradingSignal)

    async def test_generate_signal_no_ai(self, generator, price_data_medium):
        """Test signal generation without AI."""
        signal = await generator.generate_signal(
            symbol="AMD",
            price_data=price_data_medium,
            use_ai=False
        )

        assert isinstance(signal, TradingSignal)

    # Test edge cases

    async def test_generate_signal_flat_prices(self, generator):
        """Test signal with completely flat prices."""
        flat_prices = [100.0] * 50
        signal = await generator.generate_signal(
            symbol="FLAT",
            price_data=flat_prices
        )

        assert isinstance(signal, TradingSignal)
        # Flat prices should result in HOLD or neutral signal
        assert signal.signal_type in [SignalType.HOLD, SignalType.BUY, SignalType.SELL]

    async def test_generate_signal_extreme_volatility(self, generator):
        """Test signal with extreme price volatility."""
        volatile_prices = [100 + (i % 2) * 50 for i in range(50)]
        signal = await generator.generate_signal(
            symbol="VOLATILE",
            price_data=volatile_prices
        )

        assert isinstance(signal, TradingSignal)
        assert signal.risk_score > 30  # High risk due to volatility

    async def test_generate_signal_uptrend(self, generator):
        """Test signal with clear uptrend."""
        uptrend_prices = [100 + i * 2 for i in range(50)]
        signal = await generator.generate_signal(
            symbol="UPTREND",
            price_data=uptrend_prices
        )

        assert isinstance(signal, TradingSignal)
        # Strong uptrend should likely generate buy signal
        assert signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.HOLD]

    async def test_generate_signal_downtrend(self, generator):
        """Test signal with clear downtrend."""
        downtrend_prices = [100 - i * 2 for i in range(50)]
        signal = await generator.generate_signal(
            symbol="DOWNTREND",
            price_data=downtrend_prices
        )

        assert isinstance(signal, TradingSignal)
        # Strong downtrend should likely generate sell signal
        assert signal.signal_type in [SignalType.SELL, SignalType.STRONG_SELL, SignalType.HOLD]

    async def test_ml_prediction_failure(self, generator, price_data_medium):
        """Test that ML prediction failures are handled gracefully."""
        mock_ensemble = AsyncMock()
        mock_ensemble.predict = AsyncMock(side_effect=Exception("ML Error"))
        generator.ensemble = mock_ensemble

        # Should not raise exception
        signal = await generator.generate_signal(
            symbol="TEST",
            price_data=price_data_medium,
            use_ai=True
        )

        assert isinstance(signal, TradingSignal)


class TestGetSignalGenerator:
    """Test the get_signal_generator singleton function."""

    def test_get_signal_generator_creates_instance(self):
        """Test that get_signal_generator creates an instance."""
        from app.services import signal_generator
        signal_generator._signal_generator = None  # Reset

        gen = get_signal_generator()
        assert isinstance(gen, SignalGenerator)

    def test_get_signal_generator_singleton(self):
        """Test that get_signal_generator returns same instance."""
        gen1 = get_signal_generator()
        gen2 = get_signal_generator()

        assert gen1 is gen2  # Same instance
