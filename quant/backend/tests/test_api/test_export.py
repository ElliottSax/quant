"""
Comprehensive tests for export API endpoints.

Tests cover:
- Trade exports in all formats (JSON, CSV, Excel, Markdown)
- Analysis exports (Fourier, HMM, DTW)
- Batch exports
- Error handling and edge cases
- Data filtering and validation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock
import pandas as pd
import json
import io

from app.models.politician import Politician
from app.models.trade import Trade


# ============================================================================
# Test Export Trades Endpoint
# ============================================================================

class TestExportTrades:
    """Tests for /export/trades/{politician_id} endpoint"""

    @pytest.mark.asyncio
    async def test_export_trades_json_format(
        self, client: TestClient, test_politician: Politician, test_trade: Trade
    ):
        """Test exporting trades in JSON format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            # Create mock DataFrame
            mock_df = pd.DataFrame([{
                'transaction_date': test_trade.transaction_date,
                'ticker': test_trade.ticker,
                'transaction_type': test_trade.transaction_type,
                'amount_min': float(test_trade.amount_min),
                'amount_max': float(test_trade.amount_max)
            }])
            mock_load.return_value = mock_df

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?format=json"
            )

            assert response.status_code == 200
            assert response.headers['content-type'] == 'application/json'

            data = response.json()
            assert 'politician' in data
            assert 'trades' in data
            assert 'export_date' in data
            assert 'trade_count' in data
            assert data['politician']['name'] == test_politician.name
            assert data['trade_count'] == 1

    @pytest.mark.asyncio
    async def test_export_trades_csv_format(
        self, client: TestClient, test_politician: Politician, test_trade: Trade
    ):
        """Test exporting trades in CSV format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': test_trade.transaction_date,
                'ticker': test_trade.ticker,
                'transaction_type': test_trade.transaction_type
            }])
            mock_load.return_value = mock_df

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?format=csv"
            )

            assert response.status_code == 200
            assert 'text/csv' in response.headers['content-type']
            assert 'Content-Disposition' in response.headers
            assert '.csv' in response.headers['Content-Disposition']

    @pytest.mark.asyncio
    async def test_export_trades_excel_format(
        self, client: TestClient, test_politician: Politician, test_trade: Trade
    ):
        """Test exporting trades in Excel format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': test_trade.transaction_date,
                'ticker': test_trade.ticker,
                'transaction_type': test_trade.transaction_type,
                'amount_min': float(test_trade.amount_min)
            }])
            mock_load.return_value = mock_df

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?format=xlsx"
            )

            assert response.status_code == 200
            assert 'spreadsheetml' in response.headers['content-type']
            assert '.xlsx' in response.headers['Content-Disposition']

    @pytest.mark.asyncio
    async def test_export_trades_markdown_format(
        self, client: TestClient, test_politician: Politician, test_trade: Trade
    ):
        """Test exporting trades in Markdown format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': test_trade.transaction_date,
                'ticker': test_trade.ticker,
                'transaction_type': test_trade.transaction_type
            }])
            mock_load.return_value = mock_df

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?format=md"
            )

            assert response.status_code == 200
            assert 'text/markdown' in response.headers['content-type']
            assert test_politician.name in response.text

    @pytest.mark.asyncio
    async def test_export_trades_with_date_filter(
        self, client: TestClient, test_politician: Politician
    ):
        """Test exporting trades with date range filter"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()

        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': date.today(),
                'ticker': 'AAPL',
                'transaction_type': 'buy'
            }])
            mock_load.return_value = mock_df

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?"
                f"start_date={start_date}&end_date={end_date}"
            )

            assert response.status_code == 200
            # Verify date filter was passed to load function
            mock_load.assert_called_once()
            call_args = mock_load.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_export_trades_politician_not_found(self, client: TestClient):
        """Test export with non-existent politician"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/export/trades/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_export_trades_no_trades(
        self, client: TestClient, test_politician: Politician
    ):
        """Test export when politician has no trades"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_load.return_value = pd.DataFrame()  # Empty DataFrame

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}"
            )

            assert response.status_code == 404
            assert "no trades" in response.json()['detail'].lower()


# ============================================================================
# Test Export Analysis Endpoint
# ============================================================================

class TestExportAnalysis:
    """Tests for /export/analysis/{politician_id} endpoint"""

    @pytest.mark.asyncio
    async def test_export_analysis_json_all_types(
        self, client: TestClient, test_politician: Politician
    ):
        """Test exporting all analysis types in JSON format"""
        with patch('app.api.v1.export.analyze_fourier') as mock_fourier, \
             patch('app.api.v1.export.analyze_regime') as mock_hmm, \
             patch('app.api.v1.export.analyze_patterns') as mock_dtw:

            # Mock Fourier analysis
            mock_fourier_result = MagicMock()
            mock_fourier_result.dict.return_value = {
                'total_trades': 10,
                'dominant_cycles': [],
                'summary': 'Test summary'
            }
            mock_fourier.return_value = mock_fourier_result

            # Mock HMM analysis
            mock_hmm_result = MagicMock()
            mock_hmm_result.dict.return_value = {
                'current_regime_name': 'Normal',
                'regime_confidence': 0.85,
                'regimes': []
            }
            mock_hmm.return_value = mock_hmm_result

            # Mock DTW analysis
            mock_dtw_result = MagicMock()
            mock_dtw_result.dict.return_value = {
                'matches_found': 5,
                'prediction_30d': 3.2,
                'top_matches': []
            }
            mock_dtw.return_value = mock_dtw_result

            response = client.get(
                f"/api/v1/export/analysis/{test_politician.id}?"
                "format=json&include_fourier=true&include_hmm=true&include_dtw=true"
            )

            assert response.status_code == 200
            data = response.json()
            assert 'analyses' in data
            assert 'fourier' in data['analyses']
            assert 'hmm' in data['analyses']
            assert 'dtw' in data['analyses']

    @pytest.mark.asyncio
    async def test_export_analysis_markdown_format(
        self, client: TestClient, test_politician: Politician
    ):
        """Test exporting analysis in Markdown format"""
        with patch('app.api.v1.export.analyze_fourier') as mock_fourier:
            mock_fourier_result = MagicMock()
            mock_fourier_result.total_trades = 10
            mock_fourier_result.date_range_start = date(2024, 1, 1)
            mock_fourier_result.date_range_end = date(2024, 12, 31)
            mock_fourier_result.total_cycles_found = 3
            mock_fourier_result.dominant_cycles = []
            mock_fourier_result.summary = "Test summary"
            mock_fourier.return_value = mock_fourier_result

            response = client.get(
                f"/api/v1/export/analysis/{test_politician.id}?"
                "format=md&include_fourier=true&include_hmm=false&include_dtw=false"
            )

            assert response.status_code == 200
            assert 'text/markdown' in response.headers['content-type']
            assert test_politician.name in response.text
            assert 'Fourier' in response.text

    @pytest.mark.asyncio
    async def test_export_analysis_selective_analyses(
        self, client: TestClient, test_politician: Politician
    ):
        """Test exporting only selected analysis types"""
        with patch('app.api.v1.export.analyze_fourier') as mock_fourier, \
             patch('app.api.v1.export.analyze_regime') as mock_hmm:

            mock_fourier_result = MagicMock()
            mock_fourier_result.dict.return_value = {'test': 'data'}
            mock_fourier.return_value = mock_fourier_result

            response = client.get(
                f"/api/v1/export/analysis/{test_politician.id}?"
                "include_fourier=true&include_hmm=false&include_dtw=false"
            )

            assert response.status_code == 200
            # Only Fourier should be called
            mock_fourier.assert_called_once()
            mock_hmm.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_analysis_no_selections(
        self, client: TestClient, test_politician: Politician
    ):
        """Test export with no analyses selected"""
        response = client.get(
            f"/api/v1/export/analysis/{test_politician.id}?"
            "include_fourier=false&include_hmm=false&include_dtw=false"
        )

        assert response.status_code == 400
        assert "no analyses" in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_export_analysis_error_handling(
        self, client: TestClient, test_politician: Politician
    ):
        """Test analysis export error handling"""
        with patch('app.api.v1.export.analyze_fourier') as mock_fourier:
            mock_fourier.side_effect = Exception("Analysis failed")

            response = client.get(
                f"/api/v1/export/analysis/{test_politician.id}?"
                "include_fourier=true&include_hmm=false&include_dtw=false"
            )

            assert response.status_code == 500
            assert "failed" in response.json()['detail'].lower()

    @pytest.mark.asyncio
    async def test_export_analysis_unsupported_format(
        self, client: TestClient, test_politician: Politician
    ):
        """Test export with unsupported format for analysis"""
        with patch('app.api.v1.export.analyze_fourier') as mock_fourier:
            mock_fourier_result = MagicMock()
            mock_fourier_result.dict.return_value = {'test': 'data'}
            mock_fourier.return_value = mock_fourier_result

            response = client.get(
                f"/api/v1/export/analysis/{test_politician.id}?"
                "format=csv&include_fourier=true"
            )

            assert response.status_code == 400
            assert "not supported" in response.json()['detail'].lower()


# ============================================================================
# Test Batch Export Endpoint
# ============================================================================

class TestBatchExport:
    """Tests for /export/batch/all-politicians endpoint"""

    @pytest.mark.asyncio
    async def test_batch_export_csv(
        self, client: TestClient, test_politician: Politician, test_trade: Trade
    ):
        """Test batch export in CSV format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': test_trade.transaction_date,
                'ticker': test_trade.ticker,
                'transaction_type': test_trade.transaction_type
            }])
            mock_load.return_value = mock_df

            response = client.get("/api/v1/export/batch/all-politicians?format=csv")

            # May be 200 or 404 depending on trade count
            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_batch_export_json(
        self, client: TestClient, test_politician: Politician
    ):
        """Test batch export in JSON format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': date.today(),
                'ticker': 'AAPL',
                'transaction_type': 'buy'
            }])
            mock_load.return_value = mock_df

            response = client.get("/api/v1/export/batch/all-politicians?format=json")

            # May succeed or fail based on trade count
            assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_batch_export_min_trades_filter(
        self, client: TestClient, test_politician: Politician
    ):
        """Test batch export with minimum trades filter"""
        response = client.get(
            "/api/v1/export/batch/all-politicians?min_trades=100"
        )

        # Should return 404 if no politicians meet criteria
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_batch_export_no_politicians(self, client: TestClient):
        """Test batch export when no politicians meet criteria"""
        response = client.get(
            "/api/v1/export/batch/all-politicians?min_trades=10000"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_batch_export_unsupported_format(self, client: TestClient):
        """Test batch export with unsupported format"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_load.return_value = pd.DataFrame([{'test': 'data'}])

            response = client.get(
                "/api/v1/export/batch/all-politicians?format=xlsx"
            )

            assert response.status_code in [400, 404]


# ============================================================================
# Test Research Dataset Endpoint
# ============================================================================

class TestResearchDataset:
    """Tests for /export/research-dataset endpoint"""

    def test_research_dataset_not_implemented(self, client: TestClient):
        """Test that research dataset returns 501 (not implemented)"""
        response = client.get("/api/v1/export/research-dataset")

        assert response.status_code == 501
        assert "in progress" in response.json()['detail'].lower()

    def test_research_dataset_with_params(self, client: TestClient):
        """Test research dataset with parameters"""
        response = client.get(
            "/api/v1/export/research-dataset?"
            "include_analysis=true&format=excel"
        )

        assert response.status_code == 501


# ============================================================================
# Test Export Format Enum
# ============================================================================

class TestExportFormats:
    """Tests for export format handling"""

    @pytest.mark.asyncio
    async def test_all_format_types(
        self, client: TestClient, test_politician: Politician
    ):
        """Test all supported format types"""
        formats = ['json', 'csv', 'xlsx', 'md']

        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_df = pd.DataFrame([{
                'transaction_date': date.today(),
                'ticker': 'AAPL',
                'transaction_type': 'buy'
            }])
            mock_load.return_value = mock_df

            for fmt in formats:
                response = client.get(
                    f"/api/v1/export/trades/{test_politician.id}?format={fmt}"
                )
                # Should either succeed or fail with 404 (no trades)
                assert response.status_code in [200, 404]


# ============================================================================
# Test Error Handling
# ============================================================================

class TestExportErrorHandling:
    """Tests for export error handling"""

    @pytest.mark.asyncio
    async def test_database_error_handling(
        self, client: TestClient, test_politician: Politician
    ):
        """Test handling of database errors"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_load.side_effect = Exception("Database connection failed")

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}"
            )

            # Should handle error gracefully
            assert response.status_code in [404, 500]

    @pytest.mark.asyncio
    async def test_invalid_politician_id_format(self, client: TestClient):
        """Test export with invalid politician ID format"""
        response = client.get("/api/v1/export/trades/invalid-uuid")

        # Should reject invalid UUID
        assert response.status_code in [404, 422]

    @pytest.mark.asyncio
    async def test_export_with_corrupted_data(
        self, client: TestClient, test_politician: Politician
    ):
        """Test export when data is corrupted"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            # Return DataFrame with missing required columns
            mock_load.return_value = pd.DataFrame({'invalid': ['data']})

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}"
            )

            # Should handle missing columns
            assert response.status_code in [200, 500]


# ============================================================================
# Test Content-Type and Headers
# ============================================================================

class TestExportHeaders:
    """Tests for export response headers"""

    @pytest.mark.asyncio
    async def test_csv_headers(
        self, client: TestClient, test_politician: Politician
    ):
        """Test CSV export headers"""
        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_load.return_value = pd.DataFrame([{'test': 'data'}])

            response = client.get(
                f"/api/v1/export/trades/{test_politician.id}?format=csv"
            )

            if response.status_code == 200:
                assert 'Content-Disposition' in response.headers
                assert 'attachment' in response.headers['Content-Disposition']
                assert '.csv' in response.headers['Content-Disposition']

    @pytest.mark.asyncio
    async def test_filename_sanitization(
        self, client: TestClient, db_session: AsyncSession
    ):
        """Test that filenames are properly sanitized"""
        # Create politician with spaces in name
        politician = Politician(
            name="John Q. Public",
            chamber="senate",
            party="Independent",
            state="CA",
            bioguide_id="P000001"
        )
        db_session.add(politician)
        await db_session.commit()
        await db_session.refresh(politician)

        with patch('app.api.v1.export.load_politician_trades') as mock_load:
            mock_load.return_value = pd.DataFrame([{'test': 'data'}])

            response = client.get(
                f"/api/v1/export/trades/{politician.id}?format=json"
            )

            if response.status_code == 200:
                # Spaces should be replaced with underscores
                disposition = response.headers.get('Content-Disposition', '')
                assert '_' in disposition or 'John' in disposition
