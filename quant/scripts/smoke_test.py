#!/usr/bin/env python3
"""
Smoke Tests for Production Deployment

Tests critical endpoints and services after deployment to ensure
the application is functioning correctly.

Usage:
    python scripts/smoke_test.py --url https://api.yourdomain.com
    python scripts/smoke_test.py --url https://api.yourdomain.com --verbose
"""

import argparse
import sys
import time
from typing import Dict, List, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Color:
    """Terminal colors for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def create_session() -> requests.Session:
    """
    Create a requests session with retry logic.

    Returns:
        Configured requests session
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{text.center(60)}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.RESET}\n")


def print_test(name: str, passed: bool, details: str = "") -> None:
    """Print test result."""
    status = f"{Color.GREEN}✓ PASS{Color.RESET}" if passed else f"{Color.RED}✗ FAIL{Color.RESET}"
    print(f"{status} {name}")
    if details and not passed:
        print(f"    {Color.YELLOW}{details}{Color.RESET}")


def test_health_check(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """
    Test the health check endpoint.

    Returns:
        Tuple of (success, message)
    """
    try:
        response = session.get(f"{base_url}/health", timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        data = response.json()

        # Check overall status
        if data.get("status") != "healthy":
            return False, f"Status: {data.get('status')}"

        # Check services
        services = data.get("services", {})
        unhealthy = [
            name for name, status in services.items()
            if status not in ["connected", "disabled"]
        ]

        if unhealthy:
            return False, f"Unhealthy services: {', '.join(unhealthy)}"

        if verbose:
            print(f"    Environment: {data.get('environment')}")
            print(f"    Version: {data.get('version')}")
            print(f"    Services: {services}")

        return True, "Health check passed"

    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except Exception as e:
        return False, str(e)


def test_root_endpoint(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test the root endpoint."""
    try:
        response = session.get(base_url, timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        data = response.json()

        if "message" not in data or "version" not in data:
            return False, "Missing required fields"

        if verbose:
            print(f"    Message: {data.get('message')}")
            print(f"    Version: {data.get('version')}")

        return True, "Root endpoint accessible"

    except Exception as e:
        return False, str(e)


def test_api_docs(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test API documentation endpoint."""
    try:
        response = session.get(f"{base_url}/api/v1/docs", timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        if "swagger" not in response.text.lower():
            return False, "Swagger UI not found"

        return True, "API docs accessible"

    except Exception as e:
        return False, str(e)


def test_database_connectivity(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test database connectivity through health endpoint."""
    try:
        response = session.get(f"{base_url}/health", timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        data = response.json()
        db_status = data.get("services", {}).get("database")

        if db_status != "connected":
            return False, f"Database status: {db_status}"

        return True, "Database connected"

    except Exception as e:
        return False, str(e)


def test_cache_connectivity(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test Redis cache connectivity."""
    try:
        response = session.get(f"{base_url}/health", timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        data = response.json()
        cache_status = data.get("services", {}).get("cache")

        if cache_status not in ["connected", "disabled"]:
            return False, f"Cache status: {cache_status}"

        return True, f"Cache {cache_status}"

    except Exception as e:
        return False, str(e)


def test_metrics_endpoint(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test Prometheus metrics endpoint."""
    try:
        response = session.get(f"{base_url}/api/v1/metrics", timeout=10)

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        # Check for Prometheus metrics format
        if "# HELP" not in response.text or "# TYPE" not in response.text:
            return False, "Invalid Prometheus format"

        if verbose:
            metrics_count = response.text.count("# TYPE")
            print(f"    Metrics exposed: {metrics_count}")

        return True, "Metrics endpoint working"

    except Exception as e:
        return False, str(e)


def test_cors_headers(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test CORS headers are present."""
    try:
        response = session.options(
            f"{base_url}/api/v1/health",
            headers={"Origin": "https://example.com"},
            timeout=10
        )

        cors_header = response.headers.get("Access-Control-Allow-Origin")

        if not cors_header:
            return False, "CORS header missing"

        if verbose:
            print(f"    CORS Origin: {cors_header}")
            print(f"    CORS Methods: {response.headers.get('Access-Control-Allow-Methods', 'N/A')}")

        return True, "CORS configured"

    except Exception as e:
        return False, str(e)


def test_security_headers(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test security headers are present."""
    try:
        response = session.get(base_url, timeout=10)

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
        ]

        missing = [h for h in required_headers if h not in response.headers]

        if missing:
            return False, f"Missing headers: {', '.join(missing)}"

        if verbose:
            for header in required_headers:
                print(f"    {header}: {response.headers.get(header)}")

        return True, "Security headers present"

    except Exception as e:
        return False, str(e)


def test_response_time(session: requests.Session, base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test API response time."""
    try:
        start_time = time.time()
        response = session.get(f"{base_url}/health", timeout=10)
        elapsed = time.time() - start_time

        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"

        # Response should be under 2 seconds
        if elapsed > 2.0:
            return False, f"Slow response: {elapsed:.2f}s"

        if verbose:
            print(f"    Response time: {elapsed*1000:.0f}ms")

        return True, f"Response time: {elapsed*1000:.0f}ms"

    except Exception as e:
        return False, str(e)


def test_ssl_certificate(base_url: str, verbose: bool) -> Tuple[bool, str]:
    """Test SSL certificate (for HTTPS URLs)."""
    if not base_url.startswith("https://"):
        return True, "Not HTTPS (skipped)"

    try:
        response = requests.get(base_url, timeout=10)

        # If we get here, SSL is valid
        if verbose:
            print(f"    SSL verified")

        return True, "SSL certificate valid"

    except requests.exceptions.SSLError as e:
        return False, f"SSL error: {str(e)}"
    except Exception as e:
        return False, str(e)


def run_all_tests(base_url: str, verbose: bool = False) -> Dict[str, Tuple[bool, str]]:
    """
    Run all smoke tests.

    Args:
        base_url: Base URL of the API
        verbose: Print verbose output

    Returns:
        Dictionary of test results
    """
    session = create_session()

    tests = [
        ("Root Endpoint", lambda: test_root_endpoint(session, base_url, verbose)),
        ("Health Check", lambda: test_health_check(session, base_url, verbose)),
        ("API Documentation", lambda: test_api_docs(session, base_url, verbose)),
        ("Database Connectivity", lambda: test_database_connectivity(session, base_url, verbose)),
        ("Cache Connectivity", lambda: test_cache_connectivity(session, base_url, verbose)),
        ("Metrics Endpoint", lambda: test_metrics_endpoint(session, base_url, verbose)),
        ("CORS Headers", lambda: test_cors_headers(session, base_url, verbose)),
        ("Security Headers", lambda: test_security_headers(session, base_url, verbose)),
        ("Response Time", lambda: test_response_time(session, base_url, verbose)),
        ("SSL Certificate", lambda: test_ssl_certificate(base_url, verbose)),
    ]

    results = {}

    for name, test_func in tests:
        try:
            passed, message = test_func()
            results[name] = (passed, message)
            print_test(name, passed, message if not passed else "")
        except Exception as e:
            results[name] = (False, str(e))
            print_test(name, False, str(e))

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run smoke tests against deployed API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smoke_test.py --url https://api.yourdomain.com
  python smoke_test.py --url https://api.yourdomain.com --verbose
  python smoke_test.py --url http://localhost:8000 --verbose
        """
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of the API (e.g., https://api.yourdomain.com)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output"
    )

    args = parser.parse_args()

    # Remove trailing slash
    base_url = args.url.rstrip("/")

    print_header("SMOKE TESTS - PRODUCTION DEPLOYMENT")
    print(f"Testing: {Color.BOLD}{base_url}{Color.RESET}\n")

    # Run tests
    results = run_all_tests(base_url, args.verbose)

    # Summary
    print_header("SUMMARY")

    total = len(results)
    passed = sum(1 for success, _ in results.values() if success)
    failed = total - passed

    print(f"Total tests:  {total}")
    print(f"{Color.GREEN}Passed:       {passed}{Color.RESET}")
    if failed > 0:
        print(f"{Color.RED}Failed:       {failed}{Color.RESET}")

    # Exit with appropriate code
    if failed > 0:
        print(f"\n{Color.RED}{Color.BOLD}❌ SMOKE TESTS FAILED{Color.RESET}")
        sys.exit(1)
    else:
        print(f"\n{Color.GREEN}{Color.BOLD}✅ ALL SMOKE TESTS PASSED{Color.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
