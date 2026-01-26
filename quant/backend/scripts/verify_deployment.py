#!/usr/bin/env python3
"""
Post-Deployment Verification Script
Tests deployed application endpoints to ensure everything works
"""

import sys
import time
import requests
from typing import Dict, List, Tuple
from urllib.parse import urljoin

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class DeploymentVerifier:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Quant-Deployment-Verifier/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0

    def print_header(self, text: str):
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{text:^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")

    def print_success(self, text: str):
        print(f"{GREEN}✅ {text}{RESET}")
        self.tests_passed += 1

    def print_failure(self, text: str):
        print(f"{RED}❌ {text}{RESET}")
        self.tests_failed += 1

    def print_info(self, text: str):
        print(f"   {text}")

    def test_endpoint(self, path: str, method: str = 'GET', expected_status: int = 200,
                     data: Dict = None, headers: Dict = None) -> Tuple[bool, requests.Response]:
        """Test a single endpoint"""
        url = urljoin(self.base_url, path)
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == expected_status:
                return True, response
            else:
                return False, response
        except Exception as e:
            print(f"   Error: {e}")
            return False, None

    def test_health_endpoint(self):
        """Test health check endpoint"""
        self.print_header("Testing Health Endpoint")

        success, response = self.test_endpoint('/health')
        if success:
            self.print_success("Health endpoint responding")
            try:
                data = response.json()
                self.print_info(f"Status: {data.get('status', 'unknown')}")
            except:
                pass
        else:
            self.print_failure("Health endpoint not responding")

    def test_api_docs(self):
        """Test API documentation endpoints"""
        self.print_header("Testing API Documentation")

        # Test Swagger UI
        success, response = self.test_endpoint('/api/v1/docs')
        if success:
            self.print_success("Swagger UI accessible")
        else:
            self.print_failure("Swagger UI not accessible")

        # Test ReDoc
        success, response = self.test_endpoint('/api/v1/redoc')
        if success:
            self.print_success("ReDoc accessible")
        else:
            self.print_failure("ReDoc not accessible")

        # Test OpenAPI schema
        success, response = self.test_endpoint('/api/v1/openapi.json')
        if success:
            self.print_success("OpenAPI schema accessible")
        else:
            self.print_failure("OpenAPI schema not accessible")

    def test_public_endpoints(self):
        """Test public API endpoints (no auth required)"""
        self.print_header("Testing Public Endpoints")

        # Test public quote endpoint
        success, response = self.test_endpoint('/api/v1/market-data/public/quote/AAPL')
        if success:
            self.print_success("Public quote endpoint working")
            try:
                data = response.json()
                if 'symbol' in data or 'AAPL' in str(data):
                    self.print_info(f"Response contains expected data")
            except:
                pass
        else:
            self.print_failure("Public quote endpoint failed")

        # Test stats overview
        success, response = self.test_endpoint('/api/v1/stats/overview')
        if success:
            self.print_success("Stats overview endpoint working")
        else:
            self.print_failure("Stats overview endpoint failed")

    def test_cors(self):
        """Test CORS configuration"""
        self.print_header("Testing CORS Configuration")

        headers = {
            'Origin': 'https://example.com',
            'Access-Control-Request-Method': 'GET',
        }

        success, response = self.test_endpoint('/health', headers=headers)
        if success and 'Access-Control-Allow-Origin' in response.headers:
            self.print_success("CORS headers present")
            self.print_info(f"Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        else:
            self.print_failure("CORS headers missing or incorrect")

    def test_security_headers(self):
        """Test security headers"""
        self.print_header("Testing Security Headers")

        success, response = self.test_endpoint('/health')
        if success:
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'Strict-Transport-Security': 'HSTS',
            }

            for header, friendly_name in security_headers.items():
                if header in response.headers:
                    self.print_success(f"{friendly_name} header present")
                else:
                    self.print_info(f"Optional: {friendly_name} header not set")

    def test_rate_limiting(self):
        """Test rate limiting"""
        self.print_header("Testing Rate Limiting")

        # Make multiple requests quickly
        self.print_info("Making rapid requests to test rate limiting...")
        rate_limited = False

        for i in range(10):
            success, response = self.test_endpoint('/api/v1/market-data/public/quote/AAPL')
            if response and response.status_code == 429:
                rate_limited = True
                break

        if rate_limited:
            self.print_success("Rate limiting is active")
        else:
            self.print_info("Note: Rate limiting not triggered (may be configured for higher limits)")

    def test_database_connectivity(self):
        """Test database connectivity via API"""
        self.print_header("Testing Database Connectivity")

        # Stats endpoint requires DB
        success, response = self.test_endpoint('/api/v1/stats/overview')
        if success:
            self.print_success("Database connectivity working (stats endpoint)")
        else:
            self.print_failure("Database connectivity may have issues")

    def print_summary(self):
        """Print test summary"""
        self.print_header("Verification Summary")

        total = self.tests_passed + self.tests_failed
        passed_pct = (self.tests_passed / total * 100) if total > 0 else 0

        print(f"\n{GREEN}✅ Passed:{RESET} {self.tests_passed}")
        print(f"{RED}❌ Failed:{RESET} {self.tests_failed}")
        print(f"\n{BLUE}Success Rate:{RESET} {passed_pct:.1f}%")

        if self.tests_failed == 0:
            print(f"\n{GREEN}{'='*70}{RESET}")
            print(f"{GREEN}🎉 ALL TESTS PASSED! Deployment is healthy.{RESET}")
            print(f"{GREEN}{'='*70}{RESET}\n")
            return True
        else:
            print(f"\n{YELLOW}{'='*70}{RESET}")
            print(f"{YELLOW}⚠️  Some tests failed. Check the errors above.{RESET}")
            print(f"{YELLOW}{'='*70}{RESET}\n")
            return False

    def run_all_tests(self):
        """Run all verification tests"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{'Deployment Verification':^70}{RESET}")
        print(f"{BLUE}{f'Testing: {self.base_url}':^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")

        # Give the app a moment to fully start
        self.print_info("Waiting for application to be ready...")
        time.sleep(2)

        self.test_health_endpoint()
        self.test_api_docs()
        self.test_public_endpoints()
        self.test_cors()
        self.test_security_headers()
        self.test_rate_limiting()
        self.test_database_connectivity()

        is_healthy = self.print_summary()

        return is_healthy


def main():
    if len(sys.argv) < 2:
        print(f"{RED}Usage: python verify_deployment.py <base_url>{RESET}")
        print(f"Example: python verify_deployment.py https://your-app.railway.app")
        sys.exit(1)

    base_url = sys.argv[1]

    print(f"{BLUE}Starting verification for: {base_url}{RESET}")

    verifier = DeploymentVerifier(base_url)
    is_healthy = verifier.run_all_tests()

    if is_healthy:
        print(f"\n{GREEN}Your deployment is ready for production! 🚀{RESET}\n")
        print("Next steps:")
        print("  1. Set up monitoring and alerts")
        print("  2. Configure custom domain")
        print("  3. Set up automated backups")
        print("  4. Review security settings")
        sys.exit(0)
    else:
        print(f"\n{RED}Please fix the issues above before going live.{RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
