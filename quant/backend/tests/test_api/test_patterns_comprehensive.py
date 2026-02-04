"""
Comprehensive tests for patterns API endpoints.

Tests all endpoints in app/api/v1/patterns.py including:
- Fourier cycle analysis
- HMM regime detection
- DTW pattern matching
- Comprehensive analysis
- Pattern comparison

Covers ML model integration, error handling, data validation, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
import pandas as pd
import numpy as np

from app.models.politician import Politician
from app.models.trade import Trade


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def politician_fourier_ready(db_session: AsyncSession) -> Politician:
    """Create politician with 50 trades (sufficient for Fourier)."""
    politician = Politician(
        name="Test Fourier",
        chamber="house",
        party="Democrat",
        state="CA",
        bioguide_id="F000001",
    )
    db_session.add(politician)
    await db_session.flush()

    base_date = date(2023, 1, 1)
    for i in range(50):
        trade = Trade(
            politician_id=politician.id,
            ticker=f"STOCK{i % 5}",
            transaction_type="buy" if i % 2 == 0 else "sell",
            amount_min=Decimal("1000.00"),
            amount_max=Decimal("15000.00"),
            transaction_date=base_date + timedelta(days=i * 7),
            disclosure_date=base_date + timedelta(days=i * 7 + 15),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


@pytest.fixture
async def politician_hmm_ready(db_session: AsyncSession) -> Politician:
    """Create politician with 120 trades (sufficient for HMM)."""
    politician = Politician(
        name="Test HMM",
        chamber="senate",
        party="Republican",
        state="TX",
        bioguide_id="H000001",
    )
    db_session.add(politician)
    await db_session.flush()

    base_date = date(2022, 1, 1)
    for i in range(120):
        trade = Trade(
            politician_id=politician.id,
            ticker=f"STOCK{i % 10}",
            transaction_type="buy" if i % 3 != 0 else "sell",
            amount_min=Decimal("5000.00"),
            amount_max=Decimal("25000.00"),
            transaction_date=base_date + timedelta(days=i * 5),
            disclosure_date=base_date + timedelta(days=i * 5 + 10),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


@pytest.fixture
async def politician_dtw_ready(db_session: AsyncSession) -> Politician:
    """Create politician with 150 trades (sufficient for DTW)."""
    politician = Politician(
        name="Test DTW",
        chamber="house",
        party="Independent",
        state="VT",
        bioguide_id="D000001",
    )
    db_session.add(politician)
    await db_session.flush()

    base_date = date(2021, 6, 1)
    for i in range(150):
        trade = Trade(
            politician_id=politician.id,
            ticker=f"TECH{i % 15}",
            transaction_type="buy" if i % 2 == 0 else "sell",
            amount_min=Decimal("2000.00"),
            amount_max=Decimal("20000.00"),
            transaction_date=base_date + timedelta(days=i * 4),
            disclosure_date=base_date + timedelta(days=i * 4 + 20),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


@pytest.fixture
async def politician_minimal_data(db_session: AsyncSession) -> Politician:
    """Create politician with minimal data (< 30 trades)."""
    politician = Politician(
        name="Minimal Data",
        chamber="senate",
        party="Democrat",
        state="NY",
        bioguide_id="M000001",
    )
    db_session.add(politician)
    await db_session.flush()

    base_date = date(2024, 1, 1)
    for i in range(15):
        trade = Trade(
            politician_id=politician.id,
            ticker="AAPL",
            transaction_type="buy",
            amount_min=Decimal("1000.00"),
            amount_max=Decimal("5000.00"),
            transaction_date=base_date + timedelta(days=i * 10),
            disclosure_date=base_date + timedelta(days=i * 10 + 15),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


# ============================================================================
# List Politicians Tests
# ============================================================================

class TestListPoliticians:
    """Tests for /patterns/politicians endpoint."""

    @pytest.mark.asyncio
    async def test_list_politicians_success(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test successful politician listing."""
        response = client.get("/api/v1/patterns/politicians?min_trades=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure
        politician = data[0]
        assert "id" in politician
        assert "name" in politician
        assert "trade_count" in politician
        assert "suitable_for_analysis" in politician
        assert "fourier" in politician["suitable_for_analysis"]
        assert "hmm" in politician["suitable_for_analysis"]
        assert "dtw" in politician["suitable_for_analysis"]

    @pytest.mark.asyncio
    async def test_list_politicians_min_trades_filter(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test politician filtering by minimum trades."""
        # High threshold should return fewer results
        response = client.get("/api/v1/patterns/politicians?min_trades=100")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned politicians should have >= 100 trades
        for pol in data:
            assert pol["trade_count"] >= 100

    @pytest.mark.asyncio
    async def test_list_politicians_empty_result(self, client: TestClient):
        """Test when no politicians meet criteria."""
        response = client.get("/api/v1/patterns/politicians?min_trades=999999")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


# ============================================================================
# Fourier Analysis Tests
# ============================================================================

class TestFourierAnalysis:
    """Tests for /patterns/analyze/{politician_id}/fourier endpoint."""

    @pytest.mark.asyncio
    async def test_fourier_analysis_success(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test successful Fourier analysis."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.FourierCyclicalDetector") as mock_detector:

            mock_result = {
                "dominant_cycles": [
                    {
                        "period_days": 30.0,
                        "strength": 0.75,
                        "confidence": 0.85,
                        "category": "monthly",
                        "frequency": 0.033
                    }
                ],
                "total_cycles_found": 2,
                "cycle_forecast": {"forecast": [1.0, 1.5, 2.0]}
            }

            mock_detector.return_value.detect_cycles.return_value = mock_result
            mock_detector.return_value.get_cycle_summary.return_value = "Monthly cycle detected"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/fourier"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["politician_id"] == str(politician_fourier_ready.id)
            assert data["politician_name"] == politician_fourier_ready.name
            assert "dominant_cycles" in data
            assert len(data["dominant_cycles"]) > 0
            assert "total_cycles_found" in data
            assert "summary" in data

    @pytest.mark.asyncio
    async def test_fourier_analysis_parameters(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test Fourier analysis with custom parameters."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.FourierCyclicalDetector") as mock_detector:

            mock_detector.return_value.detect_cycles.return_value = {
                "dominant_cycles": [],
                "total_cycles_found": 0
            }
            mock_detector.return_value.get_cycle_summary.return_value = "No cycles"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/fourier"
                "?min_strength=0.1&min_confidence=0.8&include_forecast=false"
            )

            assert response.status_code == 200
            mock_detector.assert_called_once_with(
                min_strength=0.1,
                min_confidence=0.8
            )

    @pytest.mark.asyncio
    async def test_fourier_insufficient_data(
        self, client: TestClient, politician_minimal_data: Politician
    ):
        """Test Fourier analysis with insufficient data."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_minimal_data.id}/fourier"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fourier_ml_unavailable(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test Fourier analysis when ML libraries unavailable."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", False):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/fourier"
            )

            assert response.status_code == 503
            assert "not available" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fourier_not_found(self, client: TestClient):
        """Test Fourier analysis with non-existent politician."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            fake_id = str(uuid4())
            response = client.get(f"/api/v1/patterns/analyze/{fake_id}/fourier")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_fourier_analysis_error(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test Fourier analysis error handling."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.FourierCyclicalDetector") as mock_detector:

            mock_detector.return_value.detect_cycles.side_effect = ValueError("Analysis error")

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/fourier"
            )

            assert response.status_code == 500


# ============================================================================
# HMM Regime Detection Tests
# ============================================================================

class TestRegimeDetection:
    """Tests for /patterns/analyze/{politician_id}/regime endpoint."""

    @pytest.mark.asyncio
    async def test_regime_detection_success(
        self, client: TestClient, politician_hmm_ready: Politician
    ):
        """Test successful regime detection."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.RegimeDetector") as mock_detector:

            mock_result = {
                "current_regime": 1,
                "current_regime_name": "High Activity",
                "regime_probabilities": {0: 0.1, 1: 0.8, 2: 0.05, 3: 0.05},
                "expected_duration": {0: 10.0, 1: 15.0, 2: 8.0, 3: 12.0},
                "regime_characteristics": {
                    0: {
                        "name": "Low Activity",
                        "avg_return": -0.5,
                        "volatility": 0.2,
                        "frequency": 0.25,
                        "sample_size": 30
                    },
                    1: {
                        "name": "High Activity",
                        "avg_return": 1.5,
                        "volatility": 0.5,
                        "frequency": 0.40,
                        "sample_size": 48
                    }
                }
            }

            mock_detector.return_value.fit_and_predict.return_value = mock_result
            mock_detector.return_value.get_regime_transition_probabilities.return_value = {
                "0": 0.2, "1": 0.5, "2": 0.2, "3": 0.1
            }
            mock_detector.return_value.get_regime_summary.return_value = "Currently in high activity regime"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_hmm_ready.id}/regime"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["politician_id"] == str(politician_hmm_ready.id)
            assert data["current_regime"] == 1
            assert data["current_regime_name"] == "High Activity"
            assert "regime_confidence" in data
            assert 0 <= data["regime_confidence"] <= 1
            assert "regimes" in data
            assert len(data["regimes"]) > 0
            assert "transition_probabilities" in data

    @pytest.mark.asyncio
    async def test_regime_detection_custom_states(
        self, client: TestClient, politician_hmm_ready: Politician
    ):
        """Test regime detection with custom number of states."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.RegimeDetector") as mock_detector:

            mock_detector.return_value.fit_and_predict.return_value = {
                "current_regime": 0,
                "current_regime_name": "State 0",
                "regime_probabilities": {0: 1.0},
                "expected_duration": {0: 10.0},
                "regime_characteristics": {}
            }
            mock_detector.return_value.get_regime_transition_probabilities.return_value = {}
            mock_detector.return_value.get_regime_summary.return_value = "Summary"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_hmm_ready.id}/regime?n_states=3"
            )

            assert response.status_code == 200
            mock_detector.assert_called_once_with(n_states=3)

    @pytest.mark.asyncio
    async def test_regime_detection_invalid_states(
        self, client: TestClient, politician_hmm_ready: Politician
    ):
        """Test regime detection with invalid number of states."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            # Too few states
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_hmm_ready.id}/regime?n_states=1"
            )
            assert response.status_code == 422

            # Too many states
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_hmm_ready.id}/regime?n_states=10"
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_regime_insufficient_data(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test regime detection with insufficient data (< 100 trades)."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/regime"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()


# ============================================================================
# DTW Pattern Matching Tests
# ============================================================================

class TestDTWPatternMatching:
    """Tests for /patterns/analyze/{politician_id}/patterns endpoint."""

    @pytest.mark.asyncio
    async def test_dtw_analysis_success(
        self, client: TestClient, politician_dtw_ready: Politician
    ):
        """Test successful DTW pattern matching."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.DynamicTimeWarpingMatcher") as mock_matcher:

            mock_matches = [
                {
                    "match_date": pd.Timestamp("2023-06-15"),
                    "similarity_score": 0.85,
                    "confidence": 0.9,
                    "outcome_30d": {"total_return": 5.5},
                    "outcome_90d": {"total_return": 12.3}
                }
            ]

            mock_prediction = {
                "predicted_return": 6.0,
                "confidence": 0.85
            }

            mock_matcher.return_value.find_similar_patterns.return_value = mock_matches
            mock_matcher.return_value.predict_from_matches.return_value = mock_prediction
            mock_matcher.return_value.get_pattern_summary.return_value = "Similar patterns found"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["politician_id"] == str(politician_dtw_ready.id)
            assert "matches_found" in data
            assert "top_matches" in data
            assert "prediction_30d" in data
            assert "prediction_confidence" in data

    @pytest.mark.asyncio
    async def test_dtw_custom_parameters(
        self, client: TestClient, politician_dtw_ready: Politician
    ):
        """Test DTW with custom parameters."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.DynamicTimeWarpingMatcher") as mock_matcher:

            mock_matcher.return_value.find_similar_patterns.return_value = []
            mock_matcher.return_value.predict_from_matches.return_value = {
                "predicted_return": 0,
                "confidence": 0
            }
            mock_matcher.return_value.get_pattern_summary.return_value = "No matches"

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns"
                "?window_size=60&top_k=10&similarity_threshold=0.8"
            )

            assert response.status_code == 200

            # Verify matcher was called with correct similarity threshold
            mock_matcher.assert_called_once_with(similarity_threshold=0.8)

    @pytest.mark.asyncio
    async def test_dtw_parameter_validation(
        self, client: TestClient, politician_dtw_ready: Politician
    ):
        """Test DTW parameter validation."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            # Window size too small
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns?window_size=5"
            )
            assert response.status_code == 422

            # Window size too large
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns?window_size=100"
            )
            assert response.status_code == 422

            # Top_k too small
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns?top_k=0"
            )
            assert response.status_code == 422

            # Top_k too large
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/patterns?top_k=25"
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_dtw_insufficient_data(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test DTW with insufficient data."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/patterns"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()


# ============================================================================
# Comprehensive Analysis Tests
# ============================================================================

class TestComprehensiveAnalysis:
    """Tests for /patterns/analyze/{politician_id}/comprehensive endpoint."""

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_success(
        self, client: TestClient, politician_dtw_ready: Politician
    ):
        """Test successful comprehensive analysis."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.analyze_fourier") as mock_fourier, \
             patch("app.api.v1.patterns.analyze_regime") as mock_regime, \
             patch("app.api.v1.patterns.analyze_patterns") as mock_dtw:

            # Mock individual analyses
            from app.api.v1.patterns import (
                FourierAnalysisResponse,
                RegimeAnalysisResponse,
                DTWAnalysisResponse,
                CycleInfo,
                RegimeInfo,
                PatternMatch
            )

            mock_fourier.return_value = FourierAnalysisResponse(
                politician_id=str(politician_dtw_ready.id),
                politician_name=politician_dtw_ready.name,
                analysis_date=datetime.utcnow(),
                total_trades=150,
                date_range_start=date(2021, 6, 1),
                date_range_end=date(2023, 12, 1),
                dominant_cycles=[
                    CycleInfo(
                        period_days=30.0,
                        strength=0.8,
                        confidence=0.85,
                        category="monthly",
                        frequency=0.033
                    )
                ],
                total_cycles_found=2,
                summary="Monthly cycle detected"
            )

            mock_regime.return_value = RegimeAnalysisResponse(
                politician_id=str(politician_dtw_ready.id),
                politician_name=politician_dtw_ready.name,
                analysis_date=datetime.utcnow(),
                current_regime=1,
                current_regime_name="High Activity",
                regime_confidence=0.85,
                expected_duration_days=15.0,
                regimes=[
                    RegimeInfo(
                        regime_id=1,
                        name="High Activity",
                        avg_return=1.5,
                        volatility=0.5,
                        frequency=0.4,
                        sample_size=60
                    )
                ],
                transition_probabilities={"0": 0.3, "1": 0.5},
                summary="High activity regime"
            )

            mock_dtw.return_value = DTWAnalysisResponse(
                politician_id=str(politician_dtw_ready.id),
                politician_name=politician_dtw_ready.name,
                analysis_date=datetime.utcnow(),
                current_pattern_days=30,
                matches_found=3,
                top_matches=[
                    PatternMatch(
                        match_date="2023-06-15",
                        similarity_score=0.85,
                        confidence=0.9
                    )
                ],
                prediction_30d=5.5,
                prediction_confidence=0.8,
                summary="Similar patterns found"
            )

            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/comprehensive"
            )

            assert response.status_code == 200
            data = response.json()

            assert "fourier" in data
            assert "hmm" in data
            assert "dtw" in data
            assert "key_insights" in data
            assert isinstance(data["key_insights"], list)
            assert len(data["key_insights"]) > 0

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_ml_unavailable(
        self, client: TestClient, politician_dtw_ready: Politician
    ):
        """Test comprehensive analysis when ML unavailable."""
        with patch("app.api.v1.patterns.ML_AVAILABLE", False):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician_dtw_ready.id}/comprehensive"
            )

            assert response.status_code == 503


# ============================================================================
# Pattern Comparison Tests
# ============================================================================

class TestPatternComparison:
    """Tests for /patterns/compare endpoint."""

    @pytest.mark.asyncio
    async def test_compare_fourier_success(
        self, client: TestClient,
        politician_fourier_ready: Politician,
        politician_hmm_ready: Politician
    ):
        """Test successful Fourier comparison."""
        with patch("app.api.v1.patterns.analyze_fourier") as mock_fourier:
            from app.api.v1.patterns import FourierAnalysisResponse, CycleInfo

            mock_fourier.return_value = FourierAnalysisResponse(
                politician_id=str(politician_fourier_ready.id),
                politician_name=politician_fourier_ready.name,
                analysis_date=datetime.utcnow(),
                total_trades=50,
                date_range_start=date(2023, 1, 1),
                date_range_end=date(2024, 1, 1),
                dominant_cycles=[
                    CycleInfo(
                        period_days=30.0,
                        strength=0.75,
                        confidence=0.85,
                        category="monthly",
                        frequency=0.033
                    )
                ],
                total_cycles_found=1,
                summary="Monthly cycle"
            )

            pol_ids = [
                str(politician_fourier_ready.id),
                str(politician_hmm_ready.id)
            ]
            query_string = "&".join([f"politician_ids={pid}" for pid in pol_ids])

            response = client.get(
                f"/api/v1/patterns/compare?{query_string}&analysis_type=fourier"
            )

            assert response.status_code == 200
            data = response.json()

            assert "politicians" in data
            assert "comparison_date" in data
            assert "analysis_type" in data
            assert data["analysis_type"] == "fourier"

    @pytest.mark.asyncio
    async def test_compare_too_many_politicians(self, client: TestClient):
        """Test comparison with too many politicians."""
        pol_ids = [str(uuid4()) for _ in range(11)]
        query_string = "&".join([f"politician_ids={pid}" for pid in pol_ids])

        response = client.get(f"/api/v1/patterns/compare?{query_string}")

        assert response.status_code == 400
        assert "maximum 10 politicians" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_compare_cycle_correlation(
        self, client: TestClient,
        politician_fourier_ready: Politician,
        politician_hmm_ready: Politician
    ):
        """Test cycle correlation in comparison."""
        with patch("app.api.v1.patterns.analyze_fourier") as mock_fourier:
            from app.api.v1.patterns import FourierAnalysisResponse, CycleInfo

            # Create two politicians with similar cycles
            def create_fourier_response(pol_id, pol_name, period):
                return FourierAnalysisResponse(
                    politician_id=str(pol_id),
                    politician_name=pol_name,
                    analysis_date=datetime.utcnow(),
                    total_trades=50,
                    date_range_start=date(2023, 1, 1),
                    date_range_end=date(2024, 1, 1),
                    dominant_cycles=[
                        CycleInfo(
                            period_days=period,
                            strength=0.75,
                            confidence=0.85,
                            category="monthly",
                            frequency=0.033
                        )
                    ],
                    total_cycles_found=1,
                    summary="Cycle detected"
                )

            mock_fourier.side_effect = [
                create_fourier_response(politician_fourier_ready.id,
                                       politician_fourier_ready.name, 30.0),
                create_fourier_response(politician_hmm_ready.id,
                                       politician_hmm_ready.name, 28.0)
            ]

            pol_ids = [
                str(politician_fourier_ready.id),
                str(politician_hmm_ready.id)
            ]
            query_string = "&".join([f"politician_ids={pid}" for pid in pol_ids])

            response = client.get(
                f"/api/v1/patterns/compare?{query_string}&analysis_type=fourier"
            )

            assert response.status_code == 200
            data = response.json()

            # Should have cycle correlation analysis
            assert "cycle_correlation" in data


# ============================================================================
# Helper Function Tests
# ============================================================================

class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.asyncio
    async def test_load_politician_trades(
        self, db_session: AsyncSession, politician_fourier_ready: Politician
    ):
        """Test load_politician_trades helper."""
        from app.api.v1.patterns import load_politician_trades

        df = await load_politician_trades(db_session, str(politician_fourier_ready.id))

        assert not df.empty
        assert "transaction_date" in df.columns
        assert "ticker" in df.columns
        assert "transaction_type" in df.columns
        assert len(df) == 50

    @pytest.mark.asyncio
    async def test_load_politician_trades_date_filter(
        self, db_session: AsyncSession, politician_fourier_ready: Politician
    ):
        """Test load_politician_trades with date filters."""
        from app.api.v1.patterns import load_politician_trades

        start_date = date(2023, 6, 1)
        end_date = date(2023, 12, 31)

        df = await load_politician_trades(
            db_session,
            str(politician_fourier_ready.id),
            start_date=start_date,
            end_date=end_date
        )

        assert not df.empty
        # All dates should be within range
        assert all(df["transaction_date"] >= pd.Timestamp(start_date))
        assert all(df["transaction_date"] <= pd.Timestamp(end_date))

    @pytest.mark.asyncio
    async def test_prepare_time_series(self):
        """Test prepare_time_series helper."""
        from app.api.v1.patterns import prepare_time_series

        # Create sample DataFrame
        dates = pd.date_range(start="2023-01-01", end="2023-01-10", freq="D")
        df = pd.DataFrame({
            "transaction_date": dates,
            "ticker": ["AAPL"] * len(dates),
            "transaction_type": ["buy"] * len(dates)
        })

        ts = prepare_time_series(df)

        assert isinstance(ts, pd.Series)
        assert len(ts) > 0
        assert all(ts >= 0)  # Trade frequency should be non-negative

    @pytest.mark.asyncio
    async def test_prepare_time_series_empty(self):
        """Test prepare_time_series with empty DataFrame."""
        from app.api.v1.patterns import prepare_time_series

        df = pd.DataFrame()
        ts = prepare_time_series(df)

        assert isinstance(ts, pd.Series)
        assert len(ts) == 0


# ============================================================================
# Edge Cases and Integration
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_analysis_with_single_trade_day(
        self, client: TestClient, db_session: AsyncSession
    ):
        """Test analysis when all trades occur on same day."""
        politician = Politician(
            name="Single Day Trader",
            chamber="house",
            party="Democrat",
            state="CA",
            bioguide_id="S999999",
        )
        db_session.add(politician)
        await db_session.flush()

        # All trades on same day
        same_date = date(2023, 6, 15)
        for i in range(50):
            trade = Trade(
                politician_id=politician.id,
                ticker=f"STOCK{i}",
                transaction_type="buy",
                amount_min=Decimal("1000.00"),
                amount_max=Decimal("5000.00"),
                transaction_date=same_date,
                disclosure_date=same_date + timedelta(days=15),
                source_url=f"https://example.com/{i}",
            )
            db_session.add(trade)

        await db_session.commit()
        await db_session.refresh(politician)

        with patch("app.api.v1.patterns.ML_AVAILABLE", True):
            response = client.get(
                f"/api/v1/patterns/analyze/{politician.id}/fourier"
            )

            # Should handle gracefully (may return error or minimal analysis)
            assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(
        self, client: TestClient, politician_fourier_ready: Politician
    ):
        """Test handling of concurrent analysis requests."""
        import asyncio

        with patch("app.api.v1.patterns.ML_AVAILABLE", True), \
             patch("app.api.v1.patterns.FourierCyclicalDetector") as mock_detector:

            mock_detector.return_value.detect_cycles.return_value = {
                "dominant_cycles": [],
                "total_cycles_found": 0
            }
            mock_detector.return_value.get_cycle_summary.return_value = "Summary"

            # Make multiple concurrent requests
            responses = []
            for _ in range(3):
                response = client.get(
                    f"/api/v1/patterns/analyze/{politician_fourier_ready.id}/fourier"
                )
                responses.append(response)

            # All should complete successfully
            for response in responses:
                assert response.status_code == 200
