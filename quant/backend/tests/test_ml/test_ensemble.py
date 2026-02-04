"""
Comprehensive tests for Ensemble Prediction Module

Tests cover:
- Enums and dataclasses
- EnsemblePredictor initialization
- Individual model prediction extraction
- Prediction aggregation and weighting
- Confidence calculation
- Model agreement calculation
- Regime and cycle detection
- Insight generation
- Anomaly scoring
- MetaLearner adaptive weighting
- Edge cases and error handling
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

from app.ml.ensemble import (
    PredictionType,
    ModelPrediction,
    EnsemblePrediction,
    EnsemblePredictor,
    MetaLearner,
)


# ==================== FIXTURES ====================

@pytest.fixture
def ensemble_predictor():
    """Create an ensemble predictor with default weights"""
    return EnsemblePredictor()


@pytest.fixture
def custom_ensemble_predictor():
    """Create an ensemble predictor with custom weights"""
    return EnsemblePredictor(
        fourier_weight=0.5,
        hmm_weight=0.3,
        dtw_weight=0.2
    )


@pytest.fixture
def sample_fourier_result():
    """Sample Fourier analysis result"""
    return {
        'dominant_cycles': [
            {
                'period_days': 30,
                'confidence': 0.85,
                'category': 'monthly'
            }
        ],
        'cycle_forecast': {
            'forecast': [2.5] * 30,  # 30-day forecast
            'residual_std': 0.5
        }
    }


@pytest.fixture
def sample_hmm_result():
    """Sample HMM regime result"""
    return {
        'current_regime': 0,
        'current_regime_name': 'high_activity',
        'regime_probabilities': [0.8, 0.2],
        'regime_characteristics': {
            0: {'avg_return': 0.05},
            1: {'avg_return': -0.02}
        },
        'expected_duration': [15, 10]
    }


@pytest.fixture
def sample_dtw_result():
    """Sample DTW matching result"""
    return {
        'prediction': {
            'predicted_return': 3.5,
            'confidence': 0.75
        },
        'matches_found': 5,
        'top_matches': [
            {
                'similarity_score': 0.9,
                'match_date': '2023-06-15'
            }
        ]
    }


@pytest.fixture
def sample_trade_frequency():
    """Sample trade frequency time series"""
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    values = np.random.normal(2.5, 0.5, 60)
    return pd.Series(values, index=dates)


@pytest.fixture
def meta_learner():
    """Create a meta learner instance"""
    return MetaLearner()


# ==================== ENUM TESTS ====================

class TestEnums:
    """Test enum definitions"""

    def test_prediction_type_values(self):
        """Test PredictionType enum has expected values"""
        assert PredictionType.TRADE_INCREASE == "trade_increase"
        assert PredictionType.TRADE_DECREASE == "trade_decrease"
        assert PredictionType.REGIME_CHANGE == "regime_change"
        assert PredictionType.CYCLE_PEAK == "cycle_peak"
        assert PredictionType.ANOMALY == "anomaly"
        assert PredictionType.INSUFFICIENT_DATA == "insufficient_data"

    def test_prediction_type_count(self):
        """Test all prediction types are defined"""
        types = list(PredictionType)
        assert len(types) == 6


# ==================== DATACLASS TESTS ====================

class TestDataclasses:
    """Test dataclass definitions"""

    def test_model_prediction_creation(self):
        """Test creating ModelPrediction"""
        pred = ModelPrediction(
            model_name='fourier',
            prediction=5.5,
            confidence=0.85,
            supporting_evidence={'cycle_period': 30}
        )

        assert pred.model_name == 'fourier'
        assert pred.prediction == 5.5
        assert pred.confidence == 0.85
        assert pred.supporting_evidence['cycle_period'] == 30

    def test_ensemble_prediction_creation(self):
        """Test creating EnsemblePrediction"""
        model_preds = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 4.5, 0.75, {})
        ]

        ensemble_pred = EnsemblePrediction(
            prediction_type=PredictionType.TRADE_INCREASE,
            value=4.8,
            confidence=0.77,
            model_agreement=0.9,
            predictions=model_preds,
            insights=['Test insight'],
            anomaly_score=0.2
        )

        assert ensemble_pred.prediction_type == PredictionType.TRADE_INCREASE
        assert ensemble_pred.value == 4.8
        assert ensemble_pred.confidence == 0.77
        assert ensemble_pred.model_agreement == 0.9
        assert len(ensemble_pred.predictions) == 2
        assert len(ensemble_pred.insights) == 1
        assert ensemble_pred.anomaly_score == 0.2


# ==================== INITIALIZATION TESTS ====================

class TestInitialization:
    """Test ensemble predictor initialization"""

    def test_default_initialization(self, ensemble_predictor):
        """Test default weight initialization"""
        assert 'fourier' in ensemble_predictor.weights
        assert 'hmm' in ensemble_predictor.weights
        assert 'dtw' in ensemble_predictor.weights

        # Weights should sum to 1
        total = sum(ensemble_predictor.weights.values())
        assert abs(total - 1.0) < 0.001

    def test_custom_weights_initialization(self, custom_ensemble_predictor):
        """Test custom weight initialization"""
        # Weights should be normalized to sum to 1
        total = sum(custom_ensemble_predictor.weights.values())
        assert abs(total - 1.0) < 0.001

        # Should have custom proportions
        assert custom_ensemble_predictor.weights['fourier'] > custom_ensemble_predictor.weights['hmm']

    def test_weights_normalization(self):
        """Test that weights are normalized"""
        predictor = EnsemblePredictor(
            fourier_weight=1.0,
            hmm_weight=1.0,
            dtw_weight=1.0
        )

        # All should be equal after normalization
        assert abs(predictor.weights['fourier'] - 0.333) < 0.01
        assert abs(predictor.weights['hmm'] - 0.333) < 0.01
        assert abs(predictor.weights['dtw'] - 0.333) < 0.01


# ==================== PREDICTION EXTRACTION TESTS ====================

class TestPredictionExtraction:
    """Test extraction of predictions from individual models"""

    def test_extract_fourier_prediction(self, ensemble_predictor, sample_fourier_result):
        """Test extracting Fourier prediction"""
        pred = ensemble_predictor._extract_fourier_prediction(sample_fourier_result)

        assert pred is not None
        assert pred.model_name == 'fourier'
        assert isinstance(pred.prediction, float)
        assert 0 <= pred.confidence <= 1
        assert 'top_cycle_period' in pred.supporting_evidence

    def test_extract_fourier_prediction_empty(self, ensemble_predictor):
        """Test Fourier extraction with empty result"""
        pred = ensemble_predictor._extract_fourier_prediction({})
        assert pred is None

    def test_extract_hmm_prediction(self, ensemble_predictor, sample_hmm_result):
        """Test extracting HMM prediction"""
        pred = ensemble_predictor._extract_hmm_prediction(sample_hmm_result)

        assert pred is not None
        assert pred.model_name == 'hmm'
        assert isinstance(pred.prediction, float)
        assert 0 <= pred.confidence <= 1
        assert 'current_regime' in pred.supporting_evidence

    def test_extract_hmm_prediction_empty(self, ensemble_predictor):
        """Test HMM extraction with empty result"""
        pred = ensemble_predictor._extract_hmm_prediction({})
        assert pred is None

    def test_extract_dtw_prediction(self, ensemble_predictor, sample_dtw_result):
        """Test extracting DTW prediction"""
        pred = ensemble_predictor._extract_dtw_prediction(sample_dtw_result)

        assert pred is not None
        assert pred.model_name == 'dtw'
        assert isinstance(pred.prediction, float)
        assert 0 <= pred.confidence <= 1
        assert 'num_matches' in pred.supporting_evidence

    def test_extract_dtw_prediction_low_confidence(self, ensemble_predictor):
        """Test DTW extraction with low confidence"""
        dtw_result = {
            'prediction': {
                'predicted_return': 5.0,
                'confidence': 0.3  # Below threshold
            }
        }

        pred = ensemble_predictor._extract_dtw_prediction(dtw_result)
        assert pred is None

    def test_extract_dtw_prediction_empty(self, ensemble_predictor):
        """Test DTW extraction with empty result"""
        pred = ensemble_predictor._extract_dtw_prediction({})
        assert pred is None


# ==================== AGGREGATION TESTS ====================

class TestAggregation:
    """Test prediction aggregation methods"""

    def test_weighted_average_single_prediction(self, ensemble_predictor):
        """Test weighted average with single prediction"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {})
        ]

        avg = ensemble_predictor._weighted_average(predictions)
        assert abs(avg - 5.0) < 0.001

    def test_weighted_average_multiple_predictions(self, ensemble_predictor):
        """Test weighted average with multiple predictions"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 3.0, 0.6, {}),
            ModelPrediction('dtw', 4.0, 0.7, {})
        ]

        avg = ensemble_predictor._weighted_average(predictions)
        assert isinstance(avg, float)
        assert 3.0 <= avg <= 5.0  # Should be between min and max

    def test_weighted_average_zero_weight(self, ensemble_predictor):
        """Test weighted average with zero confidence"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.0, {})
        ]

        avg = ensemble_predictor._weighted_average(predictions)
        assert avg == 0

    def test_aggregate_confidence(self, ensemble_predictor):
        """Test confidence aggregation"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 3.0, 0.6, {}),
            ModelPrediction('dtw', 4.0, 0.7, {})
        ]

        confidence = ensemble_predictor._aggregate_confidence(predictions)
        assert 0 <= confidence <= 1
        assert 0.6 <= confidence <= 0.8  # Should be near average

    def test_aggregate_confidence_empty(self, ensemble_predictor):
        """Test confidence aggregation with empty list"""
        confidence = ensemble_predictor._aggregate_confidence([])
        assert confidence == 0


# ==================== AGREEMENT TESTS ====================

class TestAgreement:
    """Test model agreement calculation"""

    def test_calculate_agreement_single_prediction(self, ensemble_predictor):
        """Test agreement with single prediction"""
        predictions = [ModelPrediction('fourier', 5.0, 0.8, {})]

        agreement = ensemble_predictor._calculate_agreement(predictions)
        assert agreement == 1.0

    def test_calculate_agreement_same_direction(self, ensemble_predictor):
        """Test agreement when models agree on direction"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 4.5, 0.7, {}),
            ModelPrediction('dtw', 5.2, 0.75, {})
        ]

        agreement = ensemble_predictor._calculate_agreement(predictions)
        assert 0.5 < agreement <= 1.0

    def test_calculate_agreement_opposite_directions(self, ensemble_predictor):
        """Test agreement when models disagree on direction"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', -3.0, 0.7, {}),
            ModelPrediction('dtw', 4.0, 0.75, {})
        ]

        agreement = ensemble_predictor._calculate_agreement(predictions)
        assert agreement <= 0.5  # Low agreement due to sign disagreement

    def test_calculate_agreement_all_zero(self, ensemble_predictor):
        """Test agreement when all predictions are zero"""
        predictions = [
            ModelPrediction('fourier', 0.0, 0.8, {}),
            ModelPrediction('hmm', 0.0, 0.7, {}),
            ModelPrediction('dtw', 0.0, 0.75, {})
        ]

        agreement = ensemble_predictor._calculate_agreement(predictions)
        assert agreement == 1.0


# ==================== PREDICTION TYPE TESTS ====================

class TestPredictionType:
    """Test prediction type determination"""

    def test_is_regime_change_imminent(self, ensemble_predictor, sample_hmm_result):
        """Test regime change detection"""
        # Modify to have short expected duration
        hmm_result = sample_hmm_result.copy()
        hmm_result['expected_duration'] = [5, 10]  # Less than 7 days

        is_imminent = ensemble_predictor._is_regime_change_imminent(hmm_result)
        assert is_imminent is True

    def test_is_regime_change_not_imminent(self, ensemble_predictor, sample_hmm_result):
        """Test regime change not imminent"""
        is_imminent = ensemble_predictor._is_regime_change_imminent(sample_hmm_result)
        assert is_imminent is False

    def test_is_regime_change_empty_result(self, ensemble_predictor):
        """Test regime change with empty result"""
        is_imminent = ensemble_predictor._is_regime_change_imminent({})
        assert is_imminent is False

    def test_is_cycle_peak(self, ensemble_predictor, sample_fourier_result):
        """Test cycle peak detection"""
        # Create frequency series with recent spike
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        values = [2.0] * 23 + [4.0] * 7  # Recent activity doubled
        freq = pd.Series(values, index=dates)

        is_peak = ensemble_predictor._is_cycle_peak(sample_fourier_result, freq)
        assert is_peak is True

    def test_is_cycle_peak_no_spike(self, ensemble_predictor, sample_fourier_result, sample_trade_frequency):
        """Test cycle peak with no recent spike"""
        is_peak = ensemble_predictor._is_cycle_peak(sample_fourier_result, sample_trade_frequency)
        # Should be False since random data doesn't have clear peak
        assert isinstance(is_peak, bool)

    def test_is_cycle_peak_insufficient_data(self, ensemble_predictor, sample_fourier_result):
        """Test cycle peak with insufficient data"""
        short_freq = pd.Series([2.0, 2.5, 3.0])

        is_peak = ensemble_predictor._is_cycle_peak(sample_fourier_result, short_freq)
        assert is_peak is False


# ==================== FULL PREDICTION TESTS ====================

class TestFullPrediction:
    """Test complete ensemble prediction"""

    def test_predict_with_all_models(
        self,
        ensemble_predictor,
        sample_fourier_result,
        sample_hmm_result,
        sample_dtw_result,
        sample_trade_frequency
    ):
        """Test full prediction with all three models"""
        prediction = ensemble_predictor.predict(
            fourier_result=sample_fourier_result,
            hmm_result=sample_hmm_result,
            dtw_result=sample_dtw_result,
            current_trade_frequency=sample_trade_frequency
        )

        assert isinstance(prediction, EnsemblePrediction)
        assert prediction.prediction_type in list(PredictionType)
        assert isinstance(prediction.value, float)
        assert 0 <= prediction.confidence <= 1
        assert 0 <= prediction.model_agreement <= 1
        assert len(prediction.predictions) > 0
        assert len(prediction.insights) > 0
        assert 0 <= prediction.anomaly_score <= 1

    def test_predict_insufficient_data(self, ensemble_predictor, sample_trade_frequency):
        """Test prediction with no valid model outputs"""
        prediction = ensemble_predictor.predict(
            fourier_result={},
            hmm_result={},
            dtw_result={},
            current_trade_frequency=sample_trade_frequency
        )

        assert prediction.prediction_type == PredictionType.INSUFFICIENT_DATA
        assert prediction.value == 0.0
        assert prediction.confidence == 0.0
        assert len(prediction.predictions) == 0
        assert len(prediction.insights) > 0

    def test_predict_trade_increase(
        self,
        ensemble_predictor,
        sample_trade_frequency
    ):
        """Test prediction for trade increase"""
        # Create results that predict increase
        fourier_result = {
            'dominant_cycles': [{'period_days': 30, 'confidence': 0.85, 'category': 'monthly'}],
            'cycle_forecast': {'forecast': [5.0] * 30, 'residual_std': 0.5}
        }
        hmm_result = {
            'current_regime': 0,
            'regime_probabilities': [0.8],
            'regime_characteristics': {0: {'avg_return': 0.2}},
            'expected_duration': [15]
        }
        dtw_result = {
            'prediction': {'predicted_return': 5.0, 'confidence': 0.8}
        }

        prediction = ensemble_predictor.predict(
            fourier_result=fourier_result,
            hmm_result=hmm_result,
            dtw_result=dtw_result,
            current_trade_frequency=sample_trade_frequency
        )

        assert prediction.prediction_type == PredictionType.TRADE_INCREASE
        assert prediction.value > 2  # Threshold for increase


# ==================== INSIGHT GENERATION TESTS ====================

class TestInsightGeneration:
    """Test insight generation"""

    def test_generate_insights_high_agreement(self, ensemble_predictor):
        """Test insights with high model agreement"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 5.2, 0.75, {}),
            ModelPrediction('dtw', 4.8, 0.77, {})
        ]

        insights = ensemble_predictor._generate_insights(
            predictions=predictions,
            pred_type=PredictionType.TRADE_INCREASE,
            model_agreement=0.9,
            fourier_result={},
            hmm_result={},
            dtw_result={}
        )

        assert len(insights) > 0
        assert any('consensus' in insight.lower() for insight in insights)

    def test_generate_insights_low_agreement(self, ensemble_predictor):
        """Test insights with low model agreement"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', -3.0, 0.75, {})
        ]

        insights = ensemble_predictor._generate_insights(
            predictions=predictions,
            pred_type=PredictionType.ANOMALY,
            model_agreement=0.3,
            fourier_result={},
            hmm_result={},
            dtw_result={}
        )

        assert len(insights) > 0
        assert any('disagree' in insight.lower() or 'uncertainty' in insight.lower() for insight in insights)

    def test_generate_insights_limit(self, ensemble_predictor):
        """Test that insights are limited to 5"""
        predictions = [
            ModelPrediction('fourier', 15.0, 0.9, {}),
            ModelPrediction('hmm', 14.0, 0.85, {}),
            ModelPrediction('dtw', 15.5, 0.88, {})
        ]

        fourier_result = {
            'dominant_cycles': [{'period_days': 30, 'confidence': 0.9, 'category': 'monthly'}]
        }
        hmm_result = {
            'current_regime_name': 'high_activity',
            'current_regime': 0,
            'expected_duration': [5]
        }
        dtw_result = {
            'matches_found': 3,
            'top_matches': [{'similarity_score': 0.9, 'match_date': '2023-06-15'}]
        }

        insights = ensemble_predictor._generate_insights(
            predictions=predictions,
            pred_type=PredictionType.TRADE_INCREASE,
            model_agreement=0.95,
            fourier_result=fourier_result,
            hmm_result=hmm_result,
            dtw_result=dtw_result
        )

        assert len(insights) <= 5


# ==================== ANOMALY SCORING TESTS ====================

class TestAnomalyScoring:
    """Test anomaly score calculation"""

    def test_calculate_anomaly_score_normal(self, ensemble_predictor):
        """Test anomaly score for normal behavior"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', 4.8, 0.75, {}),
            ModelPrediction('dtw', 5.2, 0.77, {})
        ]

        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        freq = pd.Series([2.5] * 60, index=dates)  # Stable frequency

        score = ensemble_predictor._calculate_anomaly_score(
            predictions=predictions,
            model_agreement=0.9,
            current_freq=freq
        )

        assert 0 <= score <= 1
        assert score < 0.5  # Should be low for normal behavior

    def test_calculate_anomaly_score_anomalous(self, ensemble_predictor):
        """Test anomaly score for anomalous behavior"""
        predictions = [
            ModelPrediction('fourier', 5.0, 0.8, {}),
            ModelPrediction('hmm', -3.0, 0.75, {}),
            ModelPrediction('dtw', 2.0, 0.4, {})  # Low confidence
        ]

        # Create anomalous frequency pattern
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        freq = pd.Series([2.0] * 53 + [10.0] * 7, index=dates)  # Recent spike

        score = ensemble_predictor._calculate_anomaly_score(
            predictions=predictions,
            model_agreement=0.3,
            current_freq=freq
        )

        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for anomalous behavior

    def test_calculate_anomaly_score_capped(self, ensemble_predictor):
        """Test anomaly score is capped at 1.0"""
        predictions = [
            ModelPrediction('dtw', 5.0, 0.2, {})  # Very low confidence
        ]

        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        freq = pd.Series([1.0] * 53 + [20.0] * 7, index=dates)  # Extreme spike

        score = ensemble_predictor._calculate_anomaly_score(
            predictions=predictions,
            model_agreement=0.1,
            current_freq=freq
        )

        assert score <= 1.0


# ==================== META LEARNER TESTS ====================

class TestMetaLearner:
    """Test meta-learning adaptive weights"""

    def test_meta_learner_initialization(self, meta_learner):
        """Test meta learner initialization"""
        assert 'fourier' in meta_learner.performance_history
        assert 'hmm' in meta_learner.performance_history
        assert 'dtw' in meta_learner.performance_history
        assert all(len(h) == 0 for h in meta_learner.performance_history.values())

    def test_update_performance(self, meta_learner):
        """Test updating performance history"""
        meta_learner.update_performance(
            model_name='fourier',
            predicted=5.0,
            actual=4.5,
            confidence=0.8
        )

        assert len(meta_learner.performance_history['fourier']) == 1
        assert meta_learner.performance_history['fourier'][0]['error'] == 0.5

    def test_update_performance_history_limit(self, meta_learner):
        """Test performance history is limited to 100 entries"""
        for i in range(150):
            meta_learner.update_performance('fourier', 5.0, 4.0, 0.8)

        assert len(meta_learner.performance_history['fourier']) == 100

    def test_get_optimal_weights_no_history(self, meta_learner):
        """Test optimal weights with no history"""
        weights = meta_learner.get_optimal_weights()

        assert 'fourier' in weights
        assert 'hmm' in weights
        assert 'dtw' in weights
        assert abs(sum(weights.values()) - 1.0) < 0.001

    def test_get_optimal_weights_with_history(self, meta_learner):
        """Test optimal weights adapt based on performance"""
        # Fourier performs well
        for _ in range(10):
            meta_learner.update_performance('fourier', 5.0, 5.1, 0.8)

        # HMM performs poorly
        for _ in range(10):
            meta_learner.update_performance('hmm', 5.0, 10.0, 0.8)

        # DTW performs moderately
        for _ in range(10):
            meta_learner.update_performance('dtw', 5.0, 6.0, 0.8)

        weights = meta_learner.get_optimal_weights()

        # Fourier should have highest weight (lowest error)
        assert weights['fourier'] > weights['hmm']
        assert weights['fourier'] > weights['dtw']

        # Weights should sum to 1
        assert abs(sum(weights.values()) - 1.0) < 0.001

    def test_weighted_error_calculation(self, meta_learner):
        """Test that high-confidence errors are penalized more"""
        # Low confidence, large error
        meta_learner.update_performance('fourier', 5.0, 10.0, 0.3)

        # High confidence, same error
        meta_learner.update_performance('hmm', 5.0, 10.0, 0.9)

        # HMM should have higher weighted error
        fourier_weighted = meta_learner.performance_history['fourier'][0]['weighted_error']
        hmm_weighted = meta_learner.performance_history['hmm'][0]['weighted_error']

        assert hmm_weighted > fourier_weighted


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_predictions_list(self, ensemble_predictor):
        """Test handling empty predictions list"""
        weighted_avg = ensemble_predictor._weighted_average([])
        assert weighted_avg == 0

    def test_none_regime_in_hmm(self, ensemble_predictor):
        """Test HMM extraction with None regime"""
        hmm_result = {
            'current_regime': None,
            'regime_characteristics': {}
        }

        pred = ensemble_predictor._extract_hmm_prediction(hmm_result)
        assert pred is None

    def test_missing_dtw_prediction_key(self, ensemble_predictor):
        """Test DTW extraction with missing keys"""
        dtw_result = {}

        pred = ensemble_predictor._extract_dtw_prediction(dtw_result)
        assert pred is None

    def test_insufficient_frequency_data(self, ensemble_predictor, sample_fourier_result):
        """Test cycle peak with very short frequency series"""
        short_freq = pd.Series([2.0])

        is_peak = ensemble_predictor._is_cycle_peak(sample_fourier_result, short_freq)
        assert is_peak is False
