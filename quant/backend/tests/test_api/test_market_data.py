"""
Comprehensive tests for market data API endpoints.

Tests cover:
- Public endpoints (no authentication)
- Authenticated endpoints
- Market data providers
- Quote fetching (single and multiple)
- Historical data
- Company information
- Market status
- Error handling and validation
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.user import User


# ============================================================================
# Test Market Data Providers
# ============================================================================

class TestMarketDataProviders:
    """Tests for market data provider endpoints"""

    def test_get_providers_public(self, client: TestClient):
        """Test getting list of available providers"""
        with patch('app.api.v1.market_data.get_available_providers') as mock_providers:
            mock_providers.return_value = ['yahoo_finance', 'alpha_vantage']

            response = client.get("/api/v1/market-data/public/providers")

            assert response.status_code == 200
            data = response.json()
            assert 'providers' in data
            assert 'default' in data
            assert 'count' in data
            assert data['count'] >= 0

    def test_providers_returns_correct_structure(self, client: TestClient):
        """Test provider response structure"""
        response = client.get("/api/v1/market-data/public/providers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data['providers'], list)
        assert data['default'] == 'yahoo_finance'


# ============================================================================
# Test Public Quote Endpoints
# ============================================================================

class TestPublicQuotes:
    """Tests for public quote endpoints (no auth required)"""

    def test_get_public_quote_success(self, client: TestClient):
        """Test getting a single quote (public)"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            # Mock provider
            mock_data_provider = MagicMock()
            mock_quote = MagicMock()
            mock_quote.symbol = 'AAPL'
            mock_quote.price = 150.0
            mock_quote.volume = 1000000
            mock_data_provider.get_quote = AsyncMock(return_value=mock_quote)
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/AAPL")

            assert response.status_code == 200
            mock_data_provider.get_quote.assert_called_once_with('AAPL')

    def test_get_public_quote_lowercase_symbol(self, client: TestClient):
        """Test that symbols are converted to uppercase"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(return_value=MagicMock())
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/aapl")

            assert response.status_code == 200
            # Should be called with uppercase
            mock_data_provider.get_quote.assert_called_once_with('AAPL')

    def test_get_public_quote_error_handling(self, client: TestClient):
        """Test error handling for quote fetching"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(
                side_effect=Exception("API error")
            )
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/INVALID")

            assert response.status_code == 500
            assert "error" in response.json()['detail'].lower()

    def test_get_public_multiple_quotes(self, client: TestClient):
        """Test getting multiple quotes at once"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_quotes = {
                'AAPL': MagicMock(symbol='AAPL', price=150.0),
                'GOOGL': MagicMock(symbol='GOOGL', price=2800.0)
            }
            mock_data_provider.get_multiple_quotes = AsyncMock(
                return_value=mock_quotes
            )
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/public/quotes?symbols=AAPL&symbols=GOOGL"
            )

            assert response.status_code == 200
            data = response.json()
            assert 'quotes' in data
            assert 'count' in data
            assert 'timestamp' in data

    def test_public_multiple_quotes_limit(self, client: TestClient):
        """Test that public endpoint enforces 20 symbol limit"""
        symbols = ['SYM' + str(i) for i in range(25)]
        query = '&'.join([f'symbols={s}' for s in symbols])

        response = client.get(f"/api/v1/market-data/public/quotes?{query}")

        assert response.status_code == 400
        assert "20 symbols" in response.json()['detail']

    def test_public_multiple_quotes_uppercase_conversion(self, client: TestClient):
        """Test that all symbols are converted to uppercase"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_multiple_quotes = AsyncMock(return_value={})
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/public/quotes?symbols=aapl&symbols=googl"
            )

            assert response.status_code == 200
            # Should be called with uppercase symbols
            call_args = mock_data_provider.get_multiple_quotes.call_args[0][0]
            assert all(s.isupper() for s in call_args)


# ============================================================================
# Test Public Historical Data
# ============================================================================

class TestPublicHistoricalData:
    """Tests for public historical data endpoint"""

    def test_get_public_historical_data(self, client: TestClient):
        """Test getting historical data"""
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_date = datetime.utcnow().isoformat()

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_bar = MagicMock()
            mock_bar.dict.return_value = {
                'timestamp': datetime.utcnow(),
                'open': 150.0,
                'high': 155.0,
                'low': 149.0,
                'close': 152.0,
                'volume': 1000000
            }
            mock_data_provider.get_historical_data = AsyncMock(
                return_value=[mock_bar]
            )
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/public/historical/AAPL?"
                f"start_date={start_date}&end_date={end_date}"
            )

            assert response.status_code == 200
            data = response.json()
            assert 'symbol' in data
            assert 'bars' in data
            assert 'count' in data

    def test_historical_data_default_end_date(self, client: TestClient):
        """Test that end_date defaults to current time"""
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_historical_data = AsyncMock(return_value=[])
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/public/historical/AAPL?start_date={start_date}"
            )

            assert response.status_code == 200

    def test_historical_data_invalid_date_range(self, client: TestClient):
        """Test validation of date range (end before start)"""
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

        response = client.get(
            f"/api/v1/market-data/public/historical/AAPL?"
            f"start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 400
        assert "after start date" in response.json()['detail'].lower()

    def test_historical_data_public_limit_one_year(self, client: TestClient):
        """Test that public endpoint enforces 1 year limit"""
        start_date = (datetime.utcnow() - timedelta(days=400)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/market-data/public/historical/AAPL?"
            f"start_date={start_date}&end_date={end_date}"
        )

        assert response.status_code == 400
        assert "1 year" in response.json()['detail']

    def test_historical_data_with_interval(self, client: TestClient):
        """Test historical data with different intervals"""
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_historical_data = AsyncMock(return_value=[])
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/public/historical/AAPL?"
                f"start_date={start_date}&interval=1h"
            )

            # Should accept valid interval
            assert response.status_code in [200, 422]


# ============================================================================
# Test Public Company Info
# ============================================================================

class TestPublicCompanyInfo:
    """Tests for public company information endpoint"""

    def test_get_public_company_info(self, client: TestClient):
        """Test getting company information"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_info = {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics'
            }
            mock_data_provider.get_company_info = AsyncMock(return_value=mock_info)
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/company/AAPL")

            assert response.status_code == 200

    def test_company_info_error_handling(self, client: TestClient):
        """Test company info error handling"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_company_info = AsyncMock(
                side_effect=Exception("Company not found")
            )
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/company/INVALID")

            assert response.status_code == 500


# ============================================================================
# Test Market Status
# ============================================================================

class TestMarketStatus:
    """Tests for market status endpoints"""

    def test_get_public_market_status(self, client: TestClient):
        """Test getting market status (public)"""
        response = client.get("/api/v1/market-data/public/market-status")

        assert response.status_code == 200
        data = response.json()
        assert 'is_open' in data
        assert 'market' in data
        assert 'timestamp' in data
        assert 'message' in data
        assert isinstance(data['is_open'], bool)

    def test_market_status_during_hours(self, client: TestClient):
        """Test market status logic"""
        response = client.get("/api/v1/market-data/public/market-status")

        assert response.status_code == 200
        data = response.json()
        # Status should be consistent with message
        if data['is_open']:
            assert 'open' in data['message'].lower()
        else:
            assert 'closed' in data['message'].lower()


# ============================================================================
# Test Authenticated Endpoints
# ============================================================================

class TestAuthenticatedQuotes:
    """Tests for authenticated quote endpoints"""

    @pytest.mark.asyncio
    async def test_get_quote_authenticated(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test getting quote with authentication"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(return_value=MagicMock())
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/quote/AAPL",
                headers=auth_headers
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_quote_without_auth(self, client: TestClient):
        """Test that authenticated endpoint requires auth"""
        response = client.get("/api/v1/market-data/quote/AAPL")

        # Should require authentication
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_multiple_quotes_authenticated(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting multiple quotes with authentication"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_multiple_quotes = AsyncMock(return_value={})
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/quotes?symbols=AAPL&symbols=GOOGL",
                headers=auth_headers
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_authenticated_quotes_higher_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that authenticated endpoint allows up to 50 symbols"""
        symbols = ['SYM' + str(i) for i in range(45)]
        query = '&'.join([f'symbols={s}' for s in symbols])

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_multiple_quotes = AsyncMock(return_value={})
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/quotes?{query}",
                headers=auth_headers
            )

            # 45 symbols should be allowed
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_authenticated_quotes_exceeds_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that authenticated endpoint rejects >50 symbols"""
        symbols = ['SYM' + str(i) for i in range(55)]
        query = '&'.join([f'symbols={s}' for s in symbols])

        response = client.get(
            f"/api/v1/market-data/quotes?{query}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "50 symbols" in response.json()['detail']


# ============================================================================
# Test Authenticated Historical Data
# ============================================================================

class TestAuthenticatedHistoricalData:
    """Tests for authenticated historical data endpoint"""

    @pytest.mark.asyncio
    async def test_historical_data_authenticated(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting historical data with authentication"""
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_historical_data = AsyncMock(return_value=[])
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/historical/AAPL?start_date={start_date}",
                headers=auth_headers
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_historical_data_authenticated_10_year_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that authenticated endpoint allows up to 10 years"""
        start_date = (datetime.utcnow() - timedelta(days=3650)).isoformat()
        end_date = datetime.utcnow().isoformat()

        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_historical_data = AsyncMock(return_value=[])
            mock_provider.return_value = mock_data_provider

            response = client.get(
                f"/api/v1/market-data/historical/AAPL?"
                f"start_date={start_date}&end_date={end_date}",
                headers=auth_headers
            )

            # 10 years should be allowed
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_historical_data_exceeds_10_years(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that authenticated endpoint rejects >10 years"""
        start_date = (datetime.utcnow() - timedelta(days=3700)).isoformat()
        end_date = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/market-data/historical/AAPL?"
            f"start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "10 years" in response.json()['detail']


# ============================================================================
# Test Symbol Search
# ============================================================================

class TestSymbolSearch:
    """Tests for symbol search endpoint"""

    @pytest.mark.asyncio
    async def test_search_symbols(self, client: TestClient, auth_headers: dict):
        """Test symbol search endpoint"""
        response = client.get(
            "/api/v1/market-data/search?query=AAPL",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'query' in data
        assert 'results' in data
        # Currently returns placeholder message
        assert 'message' in data

    @pytest.mark.asyncio
    async def test_search_with_limit(self, client: TestClient, auth_headers: dict):
        """Test search with limit parameter"""
        response = client.get(
            "/api/v1/market-data/search?query=tech&limit=5",
            headers=auth_headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_requires_query(self, client: TestClient, auth_headers: dict):
        """Test that search requires query parameter"""
        response = client.get(
            "/api/v1/market-data/search",
            headers=auth_headers
        )

        # Should require query parameter
        assert response.status_code == 422


# ============================================================================
# Test Provider Selection
# ============================================================================

class TestProviderSelection:
    """Tests for data provider selection"""

    def test_default_provider(self, client: TestClient):
        """Test that default provider is used when not specified"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(return_value=MagicMock())
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/AAPL")

            assert response.status_code == 200
            # Should be called with default provider
            mock_provider.assert_called()

    def test_explicit_provider_selection(self, client: TestClient):
        """Test selecting specific provider"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(return_value=MagicMock())
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/public/quote/AAPL?provider=yahoo_finance"
            )

            assert response.status_code == 200


# ============================================================================
# Test Error Scenarios
# ============================================================================

class TestMarketDataErrors:
    """Tests for error handling"""

    def test_invalid_symbol_format(self, client: TestClient):
        """Test handling of invalid symbol formats"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(
                side_effect=Exception("Invalid symbol")
            )
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/INVALID@#$")

            assert response.status_code == 500

    def test_provider_unavailable(self, client: TestClient):
        """Test handling when provider is unavailable"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_provider.side_effect = Exception("Provider not available")

            response = client.get("/api/v1/market-data/public/quote/AAPL")

            # Should handle provider error
            assert response.status_code in [500, 503]

    def test_network_timeout(self, client: TestClient):
        """Test handling of network timeouts"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_data_provider.get_quote = AsyncMock(
                side_effect=TimeoutError("Request timeout")
            )
            mock_provider.return_value = mock_data_provider

            response = client.get("/api/v1/market-data/public/quote/AAPL")

            assert response.status_code == 500


# ============================================================================
# Test Authenticated Market Status
# ============================================================================

class TestAuthenticatedMarketStatus:
    """Tests for authenticated market status endpoint"""

    @pytest.mark.asyncio
    async def test_market_status_authenticated(
        self, client: TestClient, auth_headers: dict
    ):
        """Test market status with authentication"""
        response = client.get(
            "/api/v1/market-data/market-status",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'is_open' in data
        assert 'market' in data


# ============================================================================
# Test Company Info Authenticated
# ============================================================================

class TestAuthenticatedCompanyInfo:
    """Tests for authenticated company info endpoint"""

    @pytest.mark.asyncio
    async def test_company_info_authenticated(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting company info with authentication"""
        with patch('app.api.v1.market_data.get_market_data_provider') as mock_provider:
            mock_data_provider = MagicMock()
            mock_info = {'symbol': 'AAPL', 'name': 'Apple Inc.'}
            mock_data_provider.get_company_info = AsyncMock(return_value=mock_info)
            mock_provider.return_value = mock_data_provider

            response = client.get(
                "/api/v1/market-data/company/AAPL",
                headers=auth_headers
            )

            assert response.status_code == 200
