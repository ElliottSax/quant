"""
Integration Tests for Cyclical Pattern Detection Models

Tests all three cyclical models:
- Fourier Cyclical Detector
- HMM Regime Detector
- Dynamic Time Warping Pattern Matcher

Author: Claude
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from app.ml.cyclical.fourier import FourierCyclicalDetector
from app.ml.cyclical.hmm import RegimeDetector
from app.ml.cyclical.dtw import DynamicTimeWarpingMatcher


class TestFourierCyclicalDetector:
    """Tests for Fourier analysis cyclical detection"""

    @pytest.fixture
    def synthetic_cycle_data(self):
        """Create synthetic data with known cycles"""
        np.random.seed(42)
        t = np.arange(500)

        # Create signal with known cycles
        # Weekly cycle (7 days)
        weekly = 0.5 * np.sin(2 * np.pi * t / 7)
        # Monthly cycle (21 days)
        monthly = 0.3 * np.sin(2 * np.pi * t / 21)
        # Quarterly cycle (63 days)
        quarterly = 0.2 * np.sin(2 * np.pi * t / 63)
        # Noise
        noise = 0.1 * np.random.randn(500)

        signal = weekly + monthly + quarterly + noise + 1.0  # Add baseline

        dates = pd.date_range('2023-01-01', periods=500, freq='D')
        return pd.Series(signal, index=dates)

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return FourierCyclicalDetector(min_strength=0.05, min_confidence=0.5)

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector.min_strength == 0.05
        assert detector.min_confidence == 0.5
        assert detector.cycles_detected == []

    def test_detect_cycles_basic(self, detector, synthetic_cycle_data):
        """Test basic cycle detection"""
        result = detector.detect_cycles(synthetic_cycle_data)

        assert 'dominant_cycles' in result
        assert 'total_cycles_found' in result
        assert 'cycle_forecast' in result

        # Should detect our three cycles
        assert len(result['dominant_cycles']) > 0
        assert result['total_cycles_found'] >= 3

    def test_detect_known_cycles(self, detector, synthetic_cycle_data):
        """Test that detector finds known cycles"""
        result = detector.detect_cycles(synthetic_cycle_data)

        cycles = result['dominant_cycles']
        periods = [c['period_days'] for c in cycles]

        # Should detect cycles near 7, 21, and 63 days
        # Allow some tolerance for FFT discretization
        assert any(5 <= p <= 9 for p in periods), "Should detect weekly cycle"
        assert any(18 <= p <= 24 for p in periods), "Should detect monthly cycle"
        assert any(58 <= p <= 68 for p in periods), "Should detect quarterly cycle"

    def test_cycle_categories(self, detector, synthetic_cycle_data):
        """Test cycle categorization"""
        result = detector.detect_cycles(synthetic_cycle_data)

        cycles = result['dominant_cycles']
        categories = [c['category'] for c in cycles]

        # Should have weekly, monthly, quarterly
        assert 'weekly' in categories
        assert 'monthly' in categories
        assert 'quarterly' in categories

    def test_forecast_generation(self, detector, synthetic_cycle_data):
        """Test that forecast is generated"""
        result = detector.detect_cycles(synthetic_cycle_data)

        forecast = result['cycle_forecast']

        assert 'forecast' in forecast
        assert 'lower_bound' in forecast
        assert 'upper_bound' in forecast
        assert len(forecast['forecast']) == 30  # Default forecast period

    def test_seasonal_decomposition(self, detector, synthetic_cycle_data):
        """Test seasonal decomposition"""
        result = detector.detect_cycles(synthetic_cycle_data, return_details=True)

        assert 'seasonal_decomposition' in result
        decomp = result['seasonal_decomposition']

        if decomp is not None:
            assert 'trend' in decomp
            assert 'seasonal' in decomp
            assert 'residual' in decomp

    def test_short_series_error(self, detector):
        """Test that short time series raises error"""
        short_series = pd.Series(np.random.randn(20))

        with pytest.raises(ValueError, match="Time series too short"):
            detector.detect_cycles(short_series)

    def test_nan_handling(self, detector):
        """Test NaN handling"""
        data = np.random.randn(100)
        data[20:25] = np.nan
        series = pd.Series(data)

        # Should not raise error, should interpolate
        result = detector.detect_cycles(series)
        assert 'dominant_cycles' in result

    def test_get_cycle_summary(self, detector, synthetic_cycle_data):
        """Test summary generation"""
        detector.detect_cycles(synthetic_cycle_data)
        summary = detector.get_cycle_summary()

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "cycles" in summary.lower()


class TestRegimeDetector:
    """Tests for Hidden Markov Model regime detection"""

    @pytest.fixture
    def synthetic_regime_data(self):
        """Create synthetic data with distinct regimes"""
        np.random.seed(42)

        # Bull market: high returns, low vol
        bull = np.random.normal(0.02, 0.01, 100)

        # Bear market: negative returns, high vol
        bear = np.random.normal(-0.015, 0.03, 100)

        # Sideways: low returns, moderate vol
        sideways = np.random.normal(0.001, 0.015, 100)

        # Low vol: stable
        low_vol = np.random.normal(0.005, 0.005, 100)

        returns = np.concatenate([bull, bear, sideways, low_vol])
        volumes = np.abs(returns) * 1000 + np.random.normal(500, 50, 400)

        dates = pd.date_range('2023-01-01', periods=400, freq='D')

        return pd.Series(returns, index=dates), pd.Series(volumes, index=dates)

    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return RegimeDetector(n_states=4)

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector.n_states == 4
        assert not detector.is_fitted

    def test_fit(self, detector, synthetic_regime_data):
        """Test model fitting"""
        returns, volumes = synthetic_regime_data

        detector.fit(returns, volumes)

        assert detector.is_fitted
        assert len(detector.feature_names) > 0

    def test_fit_and_predict(self, detector, synthetic_regime_data):
        """Test fit and prediction"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)

        assert 'current_regime' in result
        assert 'current_regime_name' in result
        assert 'regime_probabilities' in result
        assert 'regime_characteristics' in result
        assert 'transition_matrix' in result
        assert 'expected_duration' in result
        assert 'all_regimes' in result

    def test_regime_count(self, detector, synthetic_regime_data):
        """Test correct number of regimes detected"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)

        # Should have 4 regimes
        assert len(result['regime_characteristics']) == 4
        assert len(result['regime_probabilities']) == 4
        assert len(result['expected_duration']) == 4

    def test_transition_matrix_validity(self, detector, synthetic_regime_data):
        """Test transition matrix is valid probability matrix"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)
        trans_matrix = np.array(result['transition_matrix'])

        # Each row should sum to 1 (probability distribution)
        row_sums = np.sum(trans_matrix, axis=1)
        np.testing.assert_array_almost_equal(row_sums, np.ones(4), decimal=5)

        # All probabilities should be between 0 and 1
        assert np.all(trans_matrix >= 0)
        assert np.all(trans_matrix <= 1)

    def test_regime_characteristics(self, detector, synthetic_regime_data):
        """Test regime characteristics are calculated"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)
        chars = result['regime_characteristics']

        for state_chars in chars.values():
            assert 'name' in state_chars
            assert 'avg_return' in state_chars
            assert 'volatility' in state_chars
            assert 'frequency' in state_chars
            assert 'sample_size' in state_chars

    def test_predict_requires_fit(self, detector):
        """Test that predict requires fitting first"""
        X = np.random.randn(100, 3)

        with pytest.raises(ValueError, match="must be fitted"):
            detector.predict(X)

    def test_get_regime_summary(self, detector, synthetic_regime_data):
        """Test summary generation"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)
        summary = detector.get_regime_summary(result)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Regime" in summary

    def test_get_transition_probabilities(self, detector, synthetic_regime_data):
        """Test transition probability extraction"""
        returns, volumes = synthetic_regime_data

        result = detector.fit_and_predict(returns, volumes)
        current = result['current_regime']

        transitions = detector.get_regime_transition_probabilities(current)

        assert isinstance(transitions, dict)
        # Should sum to approximately 1
        total_prob = sum(transitions.values())
        assert abs(total_prob - 1.0) < 0.01


class TestDynamicTimeWarpingMatcher:
    """Tests for Dynamic Time Warping pattern matcher"""

    @pytest.fixture
    def pattern_data(self):
        """Create data with repeating pattern"""
        np.random.seed(42)

        # Create a distinctive pattern
        base_pattern = np.array([0, 1, 2, 3, 2, 1, 0, -1, -2, -1])

        # Repeat pattern 3 times with slight variations
        historical = []
        for _ in range(3):
            pattern = base_pattern + np.random.normal(0, 0.2, 10)
            # Add spacing between patterns
            spacing = np.random.normal(0, 0.1, 20)
            historical.extend(pattern)
            historical.extend(spacing)

        historical = np.array(historical)

        # Current pattern is similar to base pattern
        current = base_pattern + np.random.normal(0, 0.15, 10)

        dates = pd.date_range('2023-01-01', periods=len(historical), freq='D')
        hist_series = pd.Series(historical, index=dates)

        return current, hist_series

    @pytest.fixture
    def matcher(self):
        """Create matcher instance"""
        return DynamicTimeWarpingMatcher(similarity_threshold=0.6)

    def test_matcher_initialization(self, matcher):
        """Test matcher initializes correctly"""
        assert matcher.similarity_threshold == 0.6
        assert matcher.matches_cache == []

    def test_find_similar_patterns(self, matcher, pattern_data):
        """Test finding similar patterns"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        assert isinstance(matches, list)
        assert len(matches) > 0

    def test_match_structure(self, matcher, pattern_data):
        """Test match dictionary structure"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        if len(matches) > 0:
            match = matches[0]
            assert 'match_date' in match
            assert 'similarity_score' in match
            assert 'dtw_distance' in match
            assert 'outcome_30d' in match
            assert 'outcome_90d' in match
            assert 'pattern' in match
            assert 'confidence' in match

    def test_similarity_scores(self, matcher, pattern_data):
        """Test that similarity scores are in valid range"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        for match in matches:
            sim = match['similarity_score']
            assert 0 <= sim <= 1
            assert sim >= matcher.similarity_threshold

    def test_matches_sorted(self, matcher, pattern_data):
        """Test that matches are sorted by similarity"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        if len(matches) > 1:
            similarities = [m['similarity_score'] for m in matches]
            # Should be in descending order
            assert all(similarities[i] >= similarities[i+1] for i in range(len(similarities)-1))

    def test_predict_from_matches(self, matcher, pattern_data):
        """Test prediction from matches"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        prediction = matcher.predict_from_matches(matches, horizon=30)

        assert 'predicted_return' in prediction
        assert 'confidence' in prediction
        assert 'return_distribution' in prediction
        assert 'num_matches' in prediction

        # Confidence should be between 0 and 1
        assert 0 <= prediction['confidence'] <= 1

    def test_empty_matches_prediction(self, matcher):
        """Test prediction with no matches"""
        prediction = matcher.predict_from_matches([])

        assert prediction['predicted_return'] == 0.0
        assert prediction['confidence'] == 0.0
        assert prediction['num_matches'] == 0

    def test_short_pattern_error(self, matcher):
        """Test error on pattern too short"""
        short_pattern = np.array([1, 2, 3])
        historical = np.random.randn(200)

        with pytest.raises(ValueError, match="Current pattern length"):
            matcher.find_similar_patterns(
                short_pattern,
                historical,
                window_size=10
            )

    def test_short_historical_error(self, matcher):
        """Test error on historical data too short"""
        pattern = np.random.randn(30)
        short_historical = np.random.randn(50)

        with pytest.raises(ValueError, match="Historical data too short"):
            matcher.find_similar_patterns(
                pattern,
                short_historical,
                window_size=10
            )

    def test_get_pattern_summary(self, matcher, pattern_data):
        """Test summary generation"""
        current, historical = pattern_data

        matches = matcher.find_similar_patterns(
            current,
            historical,
            window_size=10,
            top_k=5
        )

        summary = matcher.get_pattern_summary(matches)

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "patterns" in summary.lower()


class TestCyclicalIntegration:
    """Integration tests combining all cyclical models"""

    @pytest.fixture
    def realistic_trading_data(self):
        """Create realistic synthetic trading data"""
        np.random.seed(42)
        n_days = 500

        # Base trend
        trend = np.linspace(0, 5, n_days)

        # Cyclical components
        weekly = 0.5 * np.sin(2 * np.pi * np.arange(n_days) / 7)
        monthly = 0.3 * np.sin(2 * np.pi * np.arange(n_days) / 21)

        # Regime switching (simplified)
        regime_changes = [0, 150, 300, 400]
        regimes = np.zeros(n_days)
        volatilities = [0.01, 0.03, 0.01, 0.025]  # Different volatility for each regime

        for i in range(len(regime_changes) - 1):
            start = regime_changes[i]
            end = regime_changes[i + 1]
            regimes[start:end] = np.random.normal(0, volatilities[i], end - start)

        # Combine all components
        prices = trend + weekly + monthly + regimes + 100
        returns = np.diff(prices) / prices[:-1]

        # Volumes
        volumes = np.abs(returns) * 10000 + np.random.normal(5000, 500, len(returns))

        dates = pd.date_range('2023-01-01', periods=len(returns), freq='D')

        return pd.Series(returns, index=dates), pd.Series(volumes, index=dates)

    def test_all_models_work_together(self, realistic_trading_data):
        """Test that all models can be used on the same data"""
        returns, volumes = realistic_trading_data

        # Fourier detector
        fourier = FourierCyclicalDetector()
        fourier_result = fourier.detect_cycles(returns)
        assert len(fourier_result['dominant_cycles']) > 0

        # HMM detector
        hmm = RegimeDetector(n_states=3)
        hmm_result = hmm.fit_and_predict(returns, volumes)
        assert hmm_result['current_regime'] in [0, 1, 2]

        # DTW matcher
        dtw = DynamicTimeWarpingMatcher()
        dtw_matches = dtw.find_similar_patterns(
            returns,
            returns,
            window_size=30,
            top_k=5
        )
        assert len(dtw_matches) > 0

    def test_combined_insights(self, realistic_trading_data):
        """Test extracting combined insights from all models"""
        returns, volumes = realistic_trading_data

        insights = {}

        # Cyclical patterns
        fourier = FourierCyclicalDetector()
        cycles = fourier.detect_cycles(returns)
        insights['cycles'] = cycles['dominant_cycles']

        # Current regime
        hmm = RegimeDetector(n_states=3)
        regimes = hmm.fit_and_predict(returns, volumes)
        insights['regime'] = regimes['current_regime_name']

        # Historical patterns
        dtw = DynamicTimeWarpingMatcher()
        matches = dtw.find_similar_patterns(returns, returns, window_size=30, top_k=3)
        prediction = dtw.predict_from_matches(matches)
        insights['pattern_prediction'] = prediction['predicted_return']

        # Should have all insights
        assert 'cycles' in insights
        assert 'regime' in insights
        assert 'pattern_prediction' in insights
        assert len(insights['cycles']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
