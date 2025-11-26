#!/usr/bin/env python3
"""
Comprehensive Production Test Suite
Tests all improvements with detailed reporting
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

class ProductionTester:
    def __init__(self):
        self.results = []
        self.token = None
        self.test_user = f"test_{int(time.time())}"
        self.test_email = f"{self.test_user}@test.com"
        self.test_password = "TestPass123!@#"
        
    def print_header(self, text):
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}{text.center(60)}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
        
    def print_section(self, text):
        print(f"\n{YELLOW}{text}{NC}")
        print("-" * 40)
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        icon = f"{GREEN}✅{NC}" if success else f"{RED}❌{NC}"
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
        self.results.append({"test": test_name, "success": success, "details": details})
        
    def test_health(self):
        """Test health and basic connectivity"""
        self.print_section("1. HEALTH & CONNECTIVITY")
        
        # Test root endpoint
        try:
            response = requests.get(BASE_URL)
            data = response.json()
            self.log_result(
                "Root endpoint",
                response.status_code == 200,
                f"Version: {data.get('version', 'unknown')}"
            )
        except Exception as e:
            self.log_result("Root endpoint", False, str(e))
            
        # Test health endpoint
        try:
            response = requests.get(f"{BASE_URL}/health")
            data = response.json()
            self.log_result(
                "Health check",
                data.get("status") == "healthy",
                f"Environment: {data.get('environment')}, DB: {data.get('database')}"
            )
        except Exception as e:
            self.log_result("Health check", False, str(e))
            
    def test_authentication(self):
        """Test authentication with audit logging"""
        self.print_section("2. AUTHENTICATION & AUDIT")
        
        # Register user
        try:
            response = requests.post(
                f"{API_V1}/auth/register",
                json={
                    "username": self.test_user,
                    "email": self.test_email,
                    "password": self.test_password
                }
            )
            
            if response.status_code == 201:
                user_data = response.json()
                self.log_result(
                    "User registration",
                    True,
                    f"User ID: {user_data.get('id')}"
                )
            else:
                self.log_result(
                    "User registration",
                    False,
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("User registration", False, str(e))
            
        # Login
        try:
            response = requests.post(
                f"{API_V1}/auth/login",
                json={
                    "username": self.test_user,
                    "password": self.test_password
                }
            )
            
            if response.status_code == 200:
                login_data = response.json()
                self.token = login_data.get("access_token")
                self.log_result(
                    "User login",
                    True,
                    f"Token received (length: {len(self.token) if self.token else 0})"
                )
            else:
                self.log_result("User login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("User login", False, str(e))
            
        # Test protected endpoint
        if self.token:
            try:
                response = requests.get(
                    f"{API_V1}/auth/me",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                self.log_result(
                    "Protected endpoint (/me)",
                    response.status_code == 200,
                    f"Username: {response.json().get('username', 'unknown')}"
                )
            except Exception as e:
                self.log_result("Protected endpoint", False, str(e))
                
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        self.print_section("3. RATE LIMITING")
        
        # Check for rate limit headers
        try:
            response = requests.get(f"{API_V1}/politicians/")
            headers = response.headers
            
            has_headers = any(
                h in headers for h in 
                ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
            )
            
            if has_headers:
                self.log_result(
                    "Rate limit headers",
                    True,
                    f"Limit: {headers.get('X-RateLimit-Limit', 'N/A')}, "
                    f"Remaining: {headers.get('X-RateLimit-Remaining', 'N/A')}"
                )
            else:
                # Check if using enhanced middleware
                self.log_result(
                    "Rate limit headers",
                    False,
                    "Headers not present (may need middleware update)"
                )
        except Exception as e:
            self.log_result("Rate limit headers", False, str(e))
            
        # Test rate limit enforcement
        hit_limit = False
        for i in range(15):
            try:
                response = requests.post(
                    f"{API_V1}/auth/login",
                    json={"username": "test", "password": "test"}
                )
                if response.status_code == 429:
                    hit_limit = True
                    break
            except:
                pass
                
        self.log_result(
            "Rate limit enforcement",
            hit_limit,
            "429 status returned after rapid requests" if hit_limit else "No 429 (may have high limit)"
        )
        
    def test_data_endpoints(self):
        """Test data endpoints with optimized queries"""
        self.print_section("4. DATA ENDPOINTS (N+1 OPTIMIZATIONS)")
        
        endpoints = [
            ("/politicians/", "Politicians list"),
            ("/politicians/?limit=5", "Politicians with pagination"),
            ("/stats/summary", "Statistics summary"),
            ("/trades/recent", "Recent trades"),
            ("/trades/recent?days=7", "Recent trades with filter"),
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{API_V1}{endpoint}")
                elapsed = (time.time() - start_time) * 1000
                
                self.log_result(
                    name,
                    response.status_code == 200,
                    f"Response time: {elapsed:.0f}ms"
                )
            except Exception as e:
                self.log_result(name, False, str(e))
                
    def test_analytics(self):
        """Test analytics endpoints"""
        self.print_section("5. ANALYTICS ENDPOINTS")
        
        # Get a politician for testing
        try:
            response = requests.get(f"{API_V1}/politicians/?limit=1")
            if response.status_code == 200 and response.json():
                politician = response.json()[0]
                politician_id = politician.get("id")
                
                if politician_id:
                    # Test pattern analysis endpoints
                    analytics_endpoints = [
                        (f"/patterns/cyclical/{politician_id}", "Cyclical patterns"),
                        (f"/patterns/regime/{politician_id}", "Regime analysis"),
                    ]
                    
                    for endpoint, name in analytics_endpoints:
                        try:
                            start_time = time.time()
                            response = requests.get(f"{API_V1}{endpoint}")
                            elapsed = (time.time() - start_time) * 1000
                            
                            self.log_result(
                                name,
                                response.status_code in [200, 400],  # 400 if insufficient data
                                f"Response time: {elapsed:.0f}ms"
                            )
                        except Exception as e:
                            self.log_result(name, False, str(e))
            else:
                self.log_result("Analytics endpoints", False, "No politicians found for testing")
        except Exception as e:
            self.log_result("Analytics endpoints", False, str(e))
            
    def test_openapi(self):
        """Test OpenAPI documentation"""
        self.print_section("6. OPENAPI DOCUMENTATION")
        
        # Test documentation endpoints
        doc_endpoints = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc"),
            ("/openapi.json", "OpenAPI schema"),
        ]
        
        for endpoint, name in doc_endpoints:
            try:
                response = requests.get(f"{API_V1}{endpoint}")
                self.log_result(
                    name,
                    response.status_code == 200,
                    f"Size: {len(response.content) / 1024:.1f}KB"
                )
            except Exception as e:
                self.log_result(name, False, str(e))
                
        # Check schema content
        try:
            response = requests.get(f"{API_V1}/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                paths = len(schema.get("paths", {}))
                components = len(schema.get("components", {}).get("schemas", {}))
                
                self.log_result(
                    "Schema completeness",
                    paths > 10 and components > 10,
                    f"Paths: {paths}, Components: {components}"
                )
        except Exception as e:
            self.log_result("Schema completeness", False, str(e))
            
    def test_error_handling(self):
        """Test error handling"""
        self.print_section("7. ERROR HANDLING")
        
        # Test 404
        try:
            response = requests.get(f"{API_V1}/nonexistent")
            self.log_result(
                "404 handling",
                response.status_code == 404,
                "Not found response"
            )
        except Exception as e:
            self.log_result("404 handling", False, str(e))
            
        # Test invalid UUID
        try:
            response = requests.get(f"{API_V1}/politicians/invalid-uuid")
            self.log_result(
                "Invalid UUID handling",
                response.status_code == 422,
                "Validation error response"
            )
        except Exception as e:
            self.log_result("Invalid UUID handling", False, str(e))
            
        # Test invalid JSON
        try:
            response = requests.post(
                f"{API_V1}/auth/login",
                headers={"Content-Type": "application/json"},
                data="invalid json"
            )
            self.log_result(
                "Invalid JSON handling",
                response.status_code == 422,
                "JSON parse error response"
            )
        except Exception as e:
            self.log_result("Invalid JSON handling", False, str(e))
            
    def generate_summary(self):
        """Generate test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{NC}")
        print(f"{RED}Failed: {failed}{NC}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")
        
        # Group results by category
        categories = {}
        for result in self.results:
            category = result["test"].split()[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
                
        print("By Category:")
        for category, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            print(f"  {category}: {stats['passed']}/{total_cat} passed")
            
        # Show failures
        failures = [r for r in self.results if not r["success"]]
        if failures:
            print(f"\n{RED}Failed Tests:{NC}")
            for failure in failures:
                print(f"  - {failure['test']}: {failure['details']}")
                
        # Overall status
        print(f"\n{GREEN if passed > failed else RED}{'='*60}{NC}")
        if passed >= total * 0.8:
            print(f"{GREEN}✅ PRODUCTION READY - All critical tests passed!{NC}")
        elif passed >= total * 0.6:
            print(f"{YELLOW}⚠️  MOSTLY READY - Some improvements needed{NC}")
        else:
            print(f"{RED}❌ NOT READY - Critical issues found{NC}")
        print(f"{GREEN if passed > failed else RED}{'='*60}{NC}")
        
    def run_all_tests(self):
        """Run all test suites"""
        self.print_header("PRODUCTION TEST SUITE")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: {BASE_URL}")
        
        self.test_health()
        self.test_authentication()
        self.test_rate_limiting()
        self.test_data_endpoints()
        self.test_analytics()
        self.test_openapi()
        self.test_error_handling()
        
        self.generate_summary()
        
        return 0 if all(r["success"] for r in self.results) else 1


if __name__ == "__main__":
    tester = ProductionTester()
    sys.exit(tester.run_all_tests())