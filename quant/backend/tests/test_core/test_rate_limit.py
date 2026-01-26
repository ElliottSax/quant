"""
Tests for rate limiting module.

Tests rate limiting middleware functionality including per-minute and per-hour limits.
"""

import time
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi import Request, Response
from starlette.datastructures import Headers

from app.core.rate_limit import RateLimitMiddleware


class TestRateLimitMiddleware:
    """Test RateLimitMiddleware functionality."""

    def test_init_default_limits(self):
        """Test middleware initialization with default limits."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        assert middleware.requests_per_minute == 60
        assert middleware.requests_per_hour == 1000

    def test_init_custom_limits(self):
        """Test middleware initialization with custom limits."""
        app = Mock()
        middleware = RateLimitMiddleware(
            app,
            requests_per_minute=10,
            requests_per_hour=100
        )

        assert middleware.requests_per_minute == 10
        assert middleware.requests_per_hour == 100

    def test_get_client_ip_from_x_forwarded_for(self):
        """Test extracting client IP from X-Forwarded-For header."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.headers = {"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        request.client = None

        ip = middleware._get_client_ip(request)
        assert ip == "1.2.3.4"

    def test_get_client_ip_from_x_real_ip(self):
        """Test extracting client IP from X-Real-IP header."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.headers = {"X-Real-IP": "1.2.3.4"}
        request.client = None

        ip = middleware._get_client_ip(request)
        assert ip == "1.2.3.4"

    def test_get_client_ip_from_client_host(self):
        """Test extracting client IP from request.client.host."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.headers = {}
        request.client = Mock()
        request.client.host = "1.2.3.4"

        ip = middleware._get_client_ip(request)
        assert ip == "1.2.3.4"

    def test_get_client_ip_unknown(self):
        """Test that unknown is returned when IP cannot be determined."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.headers = {}
        request.client = None

        ip = middleware._get_client_ip(request)
        assert ip == "unknown"

    def test_cleanup_old_requests_removes_old_entries(self):
        """Test that cleanup removes requests older than 1 hour."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        current_time = time.time()

        # Add old and recent requests
        middleware.request_log["1.2.3.4"] = [
            (current_time - 7200, "/api/old"),  # 2 hours ago (should be removed)
            (current_time - 1800, "/api/old2"),  # 30 min ago (should be kept)
            (current_time - 30, "/api/recent"),  # 30 sec ago (should be kept)
        ]

        # Force cleanup by setting last_cleanup to old time
        middleware.last_cleanup = 0

        middleware._cleanup_old_requests()

        # Should only have 2 requests left
        assert len(middleware.request_log["1.2.3.4"]) == 2
        # Check that old request was removed
        timestamps = [t for t, _ in middleware.request_log["1.2.3.4"]]
        assert current_time - 7200 not in timestamps

    def test_cleanup_removes_empty_client_entries(self):
        """Test that cleanup removes empty client entries."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        current_time = time.time()

        # Add only old requests for a client
        middleware.request_log["1.2.3.4"] = [
            (current_time - 7200, "/api/old"),  # 2 hours ago
        ]

        # Force cleanup
        middleware.last_cleanup = 0

        middleware._cleanup_old_requests()

        # Client should be removed completely
        assert "1.2.3.4" not in middleware.request_log

    def test_cleanup_respects_interval(self):
        """Test that cleanup only runs after cleanup_interval."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        current_time = time.time()

        # Add old request
        middleware.request_log["1.2.3.4"] = [
            (current_time - 7200, "/api/old"),
        ]

        # Set last_cleanup to recent time
        middleware.last_cleanup = current_time

        middleware._cleanup_old_requests()

        # Cleanup should not have run (old request still there)
        assert len(middleware.request_log["1.2.3.4"]) == 1

    def test_is_rate_limited_per_minute_limit(self):
        """Test per-minute rate limit detection."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=5)

        current_time = time.time()
        client_ip = "1.2.3.4"
        endpoint = "/api/test"

        # Add 5 requests in last minute
        middleware.request_log[client_ip] = [
            (current_time - 10, endpoint),
            (current_time - 20, endpoint),
            (current_time - 30, endpoint),
            (current_time - 40, endpoint),
            (current_time - 50, endpoint),
        ]

        is_limited, reason = middleware._is_rate_limited(client_ip, endpoint)

        assert is_limited is True
        assert "per minute" in reason.lower()

    def test_is_rate_limited_per_hour_limit(self):
        """Test per-hour rate limit detection."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_hour=10)

        current_time = time.time()
        client_ip = "1.2.3.4"

        # Add 10 requests in last hour (to different endpoints)
        middleware.request_log[client_ip] = [
            (current_time - i * 300, f"/api/endpoint{i}")
            for i in range(10)
        ]

        is_limited, reason = middleware._is_rate_limited(client_ip, "/api/test")

        assert is_limited is True
        assert "per hour" in reason.lower()

    def test_is_rate_limited_not_limited(self):
        """Test that client is not rate limited when under limits."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=10)

        current_time = time.time()
        client_ip = "1.2.3.4"
        endpoint = "/api/test"

        # Add only 3 requests
        middleware.request_log[client_ip] = [
            (current_time - 10, endpoint),
            (current_time - 20, endpoint),
            (current_time - 30, endpoint),
        ]

        is_limited, reason = middleware._is_rate_limited(client_ip, endpoint)

        assert is_limited is False
        assert reason == ""

    def test_is_rate_limited_endpoint_specific(self):
        """Test that per-minute rate limit is endpoint-specific."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=5)

        current_time = time.time()
        client_ip = "1.2.3.4"

        # Add 5 requests to different endpoints
        middleware.request_log[client_ip] = [
            (current_time - 10, "/api/endpoint1"),
            (current_time - 20, "/api/endpoint2"),
            (current_time - 30, "/api/endpoint3"),
            (current_time - 40, "/api/endpoint4"),
            (current_time - 50, "/api/endpoint5"),
        ]

        # Should not be rate limited on a new endpoint
        is_limited, reason = middleware._is_rate_limited(client_ip, "/api/endpoint6")

        assert is_limited is False

    @pytest.mark.asyncio
    async def test_dispatch_skips_health_check(self):
        """Test that health check endpoints skip rate limiting."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        # Mock request for health check
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/health"

        # Mock call_next
        mock_response = Response(content="OK")
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        assert response == mock_response
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_skips_root(self):
        """Test that root endpoint skips rate limiting."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/"

        mock_response = Response(content="OK")
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        assert response == mock_response

    @pytest.mark.asyncio
    async def test_dispatch_returns_429_when_rate_limited(self):
        """Test that dispatch returns 429 when rate limit is exceeded."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=2)

        # Mock request
        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = Mock()
        request.client.host = "1.2.3.4"

        # Add requests to exceed limit
        current_time = time.time()
        middleware.request_log["1.2.3.4"] = [
            (current_time - 10, "/api/test"),
            (current_time - 20, "/api/test"),
        ]

        call_next = AsyncMock()

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert "X-RateLimit-Limit" in response.headers

    @pytest.mark.asyncio
    async def test_dispatch_records_request(self):
        """Test that dispatch records successful requests."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = Mock()
        request.client.host = "1.2.3.4"

        mock_response = Response(content="OK")
        call_next = AsyncMock(return_value=mock_response)

        # Initially no requests
        assert "1.2.3.4" not in middleware.request_log

        await middleware.dispatch(request, call_next)

        # Request should be recorded
        assert "1.2.3.4" in middleware.request_log
        assert len(middleware.request_log["1.2.3.4"]) == 1

        timestamp, endpoint = middleware.request_log["1.2.3.4"][0]
        assert endpoint == "/api/test"
        assert isinstance(timestamp, float)

    @pytest.mark.asyncio
    async def test_dispatch_adds_rate_limit_headers(self):
        """Test that dispatch adds rate limit headers to successful responses."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=10)

        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = Mock()
        request.client.host = "1.2.3.4"

        # Add some existing requests
        current_time = time.time()
        middleware.request_log["1.2.3.4"] = [
            (current_time - 10, "/api/test"),
            (current_time - 20, "/api/test"),
        ]

        mock_response = Response(content="OK")
        call_next = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next)

        # Should have rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

        # Should have 7 remaining (10 limit - 3 requests including this one)
        assert response.headers["X-RateLimit-Remaining"] == "7"

    @pytest.mark.asyncio
    async def test_dispatch_cleanup_periodically(self):
        """Test that cleanup is called periodically during dispatch."""
        app = Mock()
        middleware = RateLimitMiddleware(app)

        request = Mock(spec=Request)
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = Mock()
        request.client.host = "1.2.3.4"

        # Set last_cleanup to old time to trigger cleanup
        middleware.last_cleanup = time.time() - 400

        # Add old request that should be cleaned up
        middleware.request_log["5.6.7.8"] = [
            (time.time() - 7200, "/api/old"),
        ]

        call_next = AsyncMock(return_value=Response(content="OK"))

        await middleware.dispatch(request, call_next)

        # Cleanup should have removed the old client
        assert "5.6.7.8" not in middleware.request_log

    def test_rate_limit_tracks_separate_clients(self):
        """Test that rate limiting tracks different clients separately."""
        app = Mock()
        middleware = RateLimitMiddleware(app, requests_per_minute=5)

        current_time = time.time()

        # Client 1 has 5 requests
        middleware.request_log["1.2.3.4"] = [
            (current_time - i * 10, "/api/test")
            for i in range(5)
        ]

        # Client 2 has 2 requests
        middleware.request_log["5.6.7.8"] = [
            (current_time - i * 10, "/api/test")
            for i in range(2)
        ]

        # Client 1 should be rate limited
        is_limited_1, _ = middleware._is_rate_limited("1.2.3.4", "/api/test")
        assert is_limited_1 is True

        # Client 2 should not be rate limited
        is_limited_2, _ = middleware._is_rate_limited("5.6.7.8", "/api/test")
        assert is_limited_2 is False
