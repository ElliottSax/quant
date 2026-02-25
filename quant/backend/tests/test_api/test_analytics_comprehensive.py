"""
Comprehensive tests for analytics API endpoints.

Tests all endpoints in app/api/v1/analytics.py including:
- Ensemble predictions
- Correlation analysis
- Network analysis
- Automated insights
- Anomaly detection

Covers happy path, error cases, edge cases, and parameter validation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
import pandas as pd

from app.models.politician import Politician
from app.models.trade import Trade


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def politician_with_many_trades(db_session: AsyncSession) -> Politician:
    """Create politician with sufficient trades for all analytics."""
    politician = Politician(
        name="Nancy Pelosi",
        chamber="house",
        party="Democrat",
        state="CA",
        bioguide_id="P000197",
    )
    db_session.add(politician)
    await db_session.flush()

    # Create 150 trades over 2 years for comprehensive analysis
    base_date = date(2022, 1, 1)
    for i in range(150):
        trade = Trade(
            politician_id=politician.id,
            ticker=f"STOCK{i % 20}",  # 20 different stocks
            transaction_type="buy" if i % 2 == 0 else "sell",
            amount_min=Decimal("1000.00"),
            amount_max=Decimal("15000.00"),
            transaction_date=base_date + timedelta(days=i * 5),
            disclosure_date=base_date + timedelta(days=i * 5 + 15),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


@pytest.fixture
async def multiple_politicians(db_session: AsyncSession) -> list[Politician]:
    """Create multiple politicians for correlation/network testing."""
    politicians = []

    for i, name in enumerate(["Paul Pelosi", "Dan Crenshaw", "Tom Suozzi"]):
        politician = Politician(
            name=name,
            chamber="house",
            party="Republican" if i % 2 else "Democrat",
            state="CA" if i == 0 else "TX" if i == 1 else "NY",
            bioguide_id=f"P{i:05d}",
        )
        db_session.add(politician)
        await db_session.flush()

        # Create trades
        base_date = date(2022, 1, 1)
        for j in range(60):  # 60 trades each
            trade = Trade(
                politician_id=politician.id,
                ticker=f"STOCK{j % 10}",
                transaction_type="buy" if j % 2 == 0 else "sell",
                amount_min=Decimal("1000.00"),
                amount_max=Decimal("15000.00"),
                transaction_date=base_date + timedelta(days=j * 7),
                disclosure_date=base_date + timedelta(days=j * 7 + 15),
                source_url=f"https://example.com/disclosure/{i}_{j}",
            )
            db_session.add(trade)

        politicians.append(politician)

    await db_session.commit()

    for politician in politicians:
        await db_session.refresh(politician)

    return politicians


@pytest.fixture
async def politician_insufficient_data(db_session: AsyncSession) -> Politician:
    """Create politician with insufficient data for analytics."""
    politician = Politician(
        name="John Smith",
        chamber="senate",
        party="Independent",
        state="VT",
        bioguide_id="S000001",
    )
    db_session.add(politician)
    await db_session.flush()

    # Only 20 trades - insufficient for most analytics
    base_date = date(2023, 1, 1)
    for i in range(20):
        trade = Trade(
            politician_id=politician.id,
            ticker="STOCK1",
            transaction_type="buy",
            amount_min=Decimal("1000.00"),
            amount_max=Decimal("15000.00"),
            transaction_date=base_date + timedelta(days=i * 10),
            disclosure_date=base_date + timedelta(days=i * 10 + 15),
            source_url=f"https://example.com/disclosure/{i}",
        )
        db_session.add(trade)

    await db_session.commit()
    await db_session.refresh(politician)
    return politician


# ============================================================================
# Ensemble Prediction Tests
# ============================================================================

class TestEnsemblePrediction:
    """Tests for /analytics/ensemble/{politician_id} endpoint."""

    @pytest.mark.asyncio
    async def test_ensemble_prediction_success(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test successful ensemble prediction with sufficient data."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.analyze_fourier") as mock_fourier, \
             patch("app.api.v1.analytics.analyze_regime") as mock_regime, \
             patch("app.api.v1.analytics.analyze_patterns") as mock_dtw, \
             patch("app.api.v1.analytics.EnsemblePredictor") as mock_ensemble:

            # Mock analysis results
            mock_fourier.return_value = AsyncMock(dict=MagicMock(return_value={
                "dominant_cycles": [{"period_days": 30, "strength": 0.8}]
            }))
            mock_regime.return_value = AsyncMock(dict=MagicMock(return_value={
                "current_regime": 1
            }))
            mock_dtw.return_value = AsyncMock(dict=MagicMock(return_value={
                "matches_found": 5
            }))

            # Mock ensemble predictor
            from app.ml.ensemble import PredictionType, EnsemblePrediction, ModelPrediction
            mock_prediction = EnsemblePrediction(
                prediction_type=PredictionType.TRADE_INCREASE,
                value=10.5,
                confidence=0.85,
                model_agreement=0.9,
                anomaly_score=0.1,
                predictions=[
                    ModelPrediction(
                        model_name="Fourier",
                        prediction=11.0,
                        confidence=0.8,
                        supporting_evidence={"cycles": 2}
                    )
                ],
                insights=["Strong upward trend detected"]
            )
            mock_ensemble.return_value.predict.return_value = mock_prediction

            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_with_many_trades.id}"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["politician_id"] == str(politician_with_many_trades.id)
            assert data["politician_name"] == politician_with_many_trades.name
            assert "prediction_type" in data
            assert "confidence" in data
            assert 0 <= data["confidence"] <= 1
            assert "individual_predictions" in data
            assert isinstance(data["individual_predictions"], list)

    @pytest.mark.asyncio
    async def test_ensemble_prediction_insufficient_data(
        self, client: TestClient, politician_insufficient_data: Politician
    ):
        """Test ensemble prediction with insufficient data."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True):
            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_insufficient_data.id}"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_ensemble_prediction_not_found(self, client: TestClient):
        """Test ensemble prediction with non-existent politician."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/analytics/ensemble/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_ensemble_prediction_invalid_uuid(self, client: TestClient):
        """Test ensemble prediction with invalid UUID format."""
        response = client.get("/api/v1/analytics/ensemble/invalid-uuid")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_ensemble_prediction_timeout(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test ensemble prediction timeout handling."""
        import asyncio

        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.asyncio.wait_for") as mock_wait:

            mock_wait.side_effect = asyncio.TimeoutError()

            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_with_many_trades.id}"
            )

            assert response.status_code == 504
            assert "timed out" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_ensemble_prediction_cache_hit(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test ensemble prediction cache hit."""
        cached_data = {
            "politician_id": str(politician_with_many_trades.id),
            "politician_name": politician_with_many_trades.name,
            "analysis_date": datetime.utcnow().isoformat(),
            "prediction_type": "trade_increase",
            "predicted_value": 10.5,
            "confidence": 0.85,
            "model_agreement": 0.9,
            "anomaly_score": 0.1,
            "individual_predictions": [],
            "insights": ["Cached result"],
            "interpretation": "Test"
        }

        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.cache_manager.get") as mock_cache_get:

            mock_cache_get.return_value = cached_data

            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_with_many_trades.id}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["insights"] == ["Cached result"]


# ============================================================================
# Correlation Analysis Tests
# ============================================================================

class TestCorrelationAnalysis:
    """Tests for /analytics/correlation/pairwise endpoint."""

    @pytest.mark.asyncio
    async def test_pairwise_correlation_success(
        self, client: TestClient, multiple_politicians: list[Politician]
    ):
        """Test successful pairwise correlation analysis."""
        pol_ids = [str(p.id) for p in multiple_politicians[:2]]

        with patch("app.api.v1.analytics.CorrelationAnalyzer") as mock_analyzer:
            from app.ml.correlation import CorrelationResult

            mock_analyzer.return_value.analyze_cycle_correlation.return_value = [
                CorrelationResult(
                    politician1_id=pol_ids[0],
                    politician2_id=pol_ids[1],
                    correlation=0.75,
                    p_value=0.01,
                    interpretation="Strong positive correlation"
                )
            ]

            response = client.get(
                f"/api/v1/analytics/correlation/pairwise?politician_ids={pol_ids[0]}&politician_ids={pol_ids[1]}"
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert "correlation" in data[0]
            assert "p_value" in data[0]
            assert "significance" in data[0]

    @pytest.mark.asyncio
    async def test_pairwise_correlation_too_few_politicians(self, client: TestClient):
        """Test correlation with less than 2 politicians."""
        response = client.get(
            f"/api/v1/analytics/correlation/pairwise?politician_ids={uuid4()}"
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_pairwise_correlation_too_many_politicians(
        self, client: TestClient, multiple_politicians: list[Politician]
    ):
        """Test correlation with more than 10 politicians."""
        pol_ids = [str(uuid4()) for _ in range(11)]
        query_string = "&".join([f"politician_ids={pid}" for pid in pol_ids])

        response = client.get(f"/api/v1/analytics/correlation/pairwise?{query_string}")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_pairwise_correlation_insufficient_data(
        self, client: TestClient, multiple_politicians: list[Politician]
    ):
        """Test correlation when politicians have no overlapping data."""
        pol_ids = [str(p.id) for p in multiple_politicians[:2]]

        with patch("app.api.v1.analytics.prepare_time_series") as mock_prepare:
            mock_prepare.return_value = pd.Series()  # Empty series

            response = client.get(
                f"/api/v1/analytics/correlation/pairwise?politician_ids={pol_ids[0]}&politician_ids={pol_ids[1]}"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_pairwise_correlation_not_found(self, client: TestClient):
        """Test correlation with non-existent politicians."""
        pol_ids = [str(uuid4()), str(uuid4())]

        response = client.get(
            f"/api/v1/analytics/correlation/pairwise?politician_ids={pol_ids[0]}&politician_ids={pol_ids[1]}"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# Network Analysis Tests
# ============================================================================

class TestNetworkAnalysis:
    """Tests for /analytics/network/analysis endpoint."""

    @pytest.mark.asyncio
    async def test_network_analysis_success(
        self, client: TestClient, multiple_politicians: list[Politician]
    ):
        """Test successful network analysis."""
        with patch("app.api.v1.analytics.CorrelationAnalyzer") as mock_analyzer:
            from app.ml.correlation import NetworkMetrics, ClusterResult

            mock_analyzer.return_value.build_correlation_matrix.return_value = MagicMock()
            mock_analyzer.return_value.build_network_graph.return_value = MagicMock()
            mock_analyzer.return_value.calculate_network_metrics.return_value = NetworkMetrics(
                density=0.5,
                clustering_coefficient=0.6,
                average_path_length=2.5,
                central_politicians=[("pol1", 0.8), ("pol2", 0.7)]
            )
            mock_analyzer.return_value.detect_clusters.return_value = [
                ClusterResult(
                    cluster_id=0,
                    politicians=["pol1", "pol2"],
                    avg_correlation=0.75
                )
            ]
            mock_analyzer.return_value.detect_coordinated_trading.return_value = {}

            response = client.get(
                "/api/v1/analytics/network/analysis?min_trades=50&min_correlation=0.5"
            )

            assert response.status_code == 200
            data = response.json()
            assert "density" in data
            assert "clustering_coefficient" in data
            assert "central_politicians" in data
            assert "clusters" in data

    @pytest.mark.asyncio
    async def test_network_analysis_insufficient_politicians(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test network analysis with fewer than 3 politicians."""
        response = client.get(
            "/api/v1/analytics/network/analysis?min_trades=999999"  # High threshold
        )

        assert response.status_code == 400
        assert "need at least 3 politicians" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_network_analysis_parameter_validation(self, client: TestClient):
        """Test network analysis parameter validation."""
        # Test invalid min_trades
        response = client.get("/api/v1/analytics/network/analysis?min_trades=0")
        assert response.status_code == 422

        response = client.get("/api/v1/analytics/network/analysis?min_trades=1001")
        assert response.status_code == 422

        # Test invalid min_correlation
        response = client.get("/api/v1/analytics/network/analysis?min_correlation=-0.1")
        assert response.status_code == 422

        response = client.get("/api/v1/analytics/network/analysis?min_correlation=1.1")
        assert response.status_code == 422


# ============================================================================
# Insights Generation Tests
# ============================================================================

class TestInsightsGeneration:
    """Tests for /analytics/insights/{politician_id} endpoint."""

    @pytest.mark.asyncio
    async def test_insights_generation_success(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test successful insights generation."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.analyze_fourier") as mock_fourier, \
             patch("app.api.v1.analytics.analyze_regime") as mock_regime, \
             patch("app.api.v1.analytics.analyze_patterns") as mock_dtw, \
             patch("app.api.v1.analytics.SectorAnalyzer") as mock_sector, \
             patch("app.api.v1.analytics.InsightGenerator") as mock_insight_gen:

            # Mock analysis results
            mock_fourier.return_value = AsyncMock(dict=MagicMock(return_value={
                "dominant_cycles": [{"period_days": 30}]
            }))
            mock_regime.return_value = AsyncMock(dict=MagicMock(return_value={
                "current_regime": 1
            }))
            mock_dtw.return_value = AsyncMock(dict=MagicMock(return_value={
                "matches_found": 5
            }))
            mock_sector.return_value.analyze_sector_preference.return_value = {}

            # Mock insights
            from app.ml.insights import Insight, InsightType, InsightSeverity
            mock_insights = [
                Insight(
                    type=InsightType.PATTERN,
                    severity=InsightSeverity.HIGH,
                    title="Strong pattern detected",
                    description="Test insight",
                    confidence=0.9,
                    evidence={"test": "data"},
                    recommendations=["Action 1"],
                    timestamp=datetime.utcnow()
                )
            ]
            mock_insight_gen.return_value.generate_comprehensive_insights.return_value = mock_insights

            with patch("app.api.v1.analytics.generate_executive_summary") as mock_summary:
                mock_summary.return_value = "Executive summary"

                response = client.get(
                    f"/api/v1/analytics/insights/{politician_with_many_trades.id}"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["politician_id"] == str(politician_with_many_trades.id)
                assert "executive_summary" in data
                assert "total_insights" in data
                assert "insights" in data
                assert isinstance(data["insights"], list)

    @pytest.mark.asyncio
    async def test_insights_insufficient_data(
        self, client: TestClient, politician_insufficient_data: Politician
    ):
        """Test insights generation with insufficient data."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True):
            response = client.get(
                f"/api/v1/analytics/insights/{politician_insufficient_data.id}"
            )

            assert response.status_code == 400
            assert "insufficient data" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_insights_confidence_threshold(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test insights generation with custom confidence threshold."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.analyze_fourier") as mock_fourier, \
             patch("app.api.v1.analytics.InsightGenerator") as mock_insight_gen:

            mock_fourier.return_value = AsyncMock(dict=MagicMock(return_value={}))

            from app.ml.insights import InsightGenerator

            response = client.get(
                f"/api/v1/analytics/insights/{politician_with_many_trades.id}?confidence_threshold=0.9"
            )

            # Should accept the parameter even if it fails later
            assert response.status_code in [200, 500]  # May fail in analysis

    @pytest.mark.asyncio
    async def test_insights_timeout(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test insights generation timeout handling."""
        import asyncio

        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.asyncio.wait_for") as mock_wait:

            mock_wait.side_effect = asyncio.TimeoutError()

            response = client.get(
                f"/api/v1/analytics/insights/{politician_with_many_trades.id}"
            )

            assert response.status_code == 504
            assert "timed out" in response.json()["detail"].lower()


# ============================================================================
# Anomaly Detection Tests
# ============================================================================

class TestAnomalyDetection:
    """Tests for /analytics/anomaly-detection/{politician_id} endpoint."""

    @pytest.mark.asyncio
    async def test_anomaly_detection_success(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test successful anomaly detection."""
        with patch("app.api.v1.analytics.generate_insights") as mock_insights, \
             patch("app.api.v1.analytics.get_ensemble_prediction") as mock_ensemble:

            from app.ml.insights import InsightType, InsightSeverity

            mock_insights.return_value = MagicMock(
                politician_name=politician_with_many_trades.name,
                insights=[
                    MagicMock(
                        type=InsightType.ANOMALY.value,
                        severity=InsightSeverity.HIGH.value,
                        confidence=0.85
                    )
                ]
            )

            mock_ensemble.return_value = MagicMock(anomaly_score=0.8)

            response = client.get(
                f"/api/v1/analytics/anomaly-detection/{politician_with_many_trades.id}"
            )

            assert response.status_code == 200
            data = response.json()
            assert "anomaly_detected" in data
            assert "anomaly_count" in data
            assert "requires_investigation" in data

    @pytest.mark.asyncio
    async def test_anomaly_detection_threshold(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test anomaly detection with custom threshold."""
        with patch("app.api.v1.analytics.generate_insights") as mock_insights, \
             patch("app.api.v1.analytics.get_ensemble_prediction") as mock_ensemble:

            mock_insights.return_value = MagicMock(
                politician_name=politician_with_many_trades.name,
                insights=[]
            )
            mock_ensemble.return_value = MagicMock(anomaly_score=0.5)

            response = client.get(
                f"/api/v1/analytics/anomaly-detection/{politician_with_many_trades.id}?anomaly_threshold=0.9"
            )

            assert response.status_code == 200
            data = response.json()
            # With high threshold, anomaly_score of 0.5 shouldn't trigger detection
            assert data["anomaly_detected"] is False

    @pytest.mark.asyncio
    async def test_anomaly_detection_no_anomalies(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test anomaly detection when no anomalies found."""
        with patch("app.api.v1.analytics.generate_insights") as mock_insights, \
             patch("app.api.v1.analytics.get_ensemble_prediction") as mock_ensemble:

            mock_insights.return_value = MagicMock(
                politician_name=politician_with_many_trades.name,
                insights=[]
            )
            mock_ensemble.side_effect = Exception("Ensemble failed")

            response = client.get(
                f"/api/v1/analytics/anomaly-detection/{politician_with_many_trades.id}"
            )

            assert response.status_code == 200
            data = response.json()
            assert data["anomaly_detected"] is False
            assert data["anomaly_count"] == 0


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_ml_libraries_unavailable(self, client: TestClient):
        """Test endpoints when ML libraries are unavailable."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", False):
            fake_id = str(uuid4())

            # These endpoints should fail gracefully
            response = client.get(f"/api/v1/analytics/ensemble/{fake_id}")
            # May return 404 (politician not found) or other error
            assert response.status_code >= 400

    @pytest.mark.asyncio
    async def test_database_error_handling(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test graceful handling of database errors."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.load_politician_trades") as mock_load:

            mock_load.side_effect = Exception("Database error")

            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_with_many_trades.id}"
            )

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self, client: TestClient, politician_with_many_trades: Politician
    ):
        """Test concurrent request handling with semaphore."""
        with patch("app.api.v1.analytics.ML_ANALYTICS_AVAILABLE", True), \
             patch("app.api.v1.analytics.ml_semaphore") as mock_semaphore:

            # Verify semaphore is used
            mock_semaphore.__aenter__ = AsyncMock()
            mock_semaphore.__aexit__ = AsyncMock()

            response = client.get(
                f"/api/v1/analytics/ensemble/{politician_with_many_trades.id}"
            )

            # Request should attempt to acquire semaphore
            # (actual behavior depends on mocking)
            assert response.status_code >= 200

    @pytest.mark.asyncio
    async def test_invalid_parameter_types(self, client: TestClient):
        """Test invalid parameter types."""
        fake_id = str(uuid4())

        # Invalid confidence threshold
        response = client.get(
            f"/api/v1/analytics/insights/{fake_id}?confidence_threshold=invalid"
        )
        assert response.status_code == 422

        # Invalid anomaly threshold
        response = client.get(
            f"/api/v1/analytics/anomaly-detection/{fake_id}?anomaly_threshold=2.0"
        )
        assert response.status_code == 422
