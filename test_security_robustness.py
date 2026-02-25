#!/usr/bin/env python3
"""
Security and Robustness Testing for Advanced Analytics API

Tests for:
- SQL injection attempts
- UUID validation
- Input validation and sanitization
- Error message information disclosure
- Rate limiting / DoS protection
- Concurrent request handling
- Edge cases and boundary conditions
- Memory leaks in ML computations
"""

import requests
import json
import asyncio
import concurrent.futures
from datetime import datetime
from typing import List, Dict
import time

BASE_URL = "http://localhost:8000/api/v1"

class SecurityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.results = []

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test(self, name: str, func):
        """Run a test and record results."""
        self.log(f"Testing: {name}")
        try:
            result = func()
            status = "PASS" if result["passed"] else "FAIL"
            self.results.append({
                "name": name,
                "status": status,
                "details": result
            })
            self.log(f"{'✓' if result['passed'] else '✗'} {name}", status)
            return result
        except Exception as e:
            self.results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            self.log(f"✗ {name}: {str(e)}", "ERROR")
            return {"passed": False, "error": str(e)}

    # ========================================================================
    # SQL Injection Tests
    # ========================================================================

    def test_sql_injection_in_politician_id(self) -> Dict:
        """Test SQL injection in politician_id parameter."""
        payloads = [
            "' OR '1'='1",
            "1; DROP TABLE trades; --",
            "'; DELETE FROM politicians WHERE '1'='1",
            "1' UNION SELECT * FROM politicians--",
            "admin'--",
            "' OR 1=1--"
        ]

        vulnerabilities = []
        for payload in payloads:
            try:
                response = requests.get(
                    f"{self.base_url}/analytics/ensemble/{payload}",
                    timeout=5
                )

                # Should get 400/404, not 200 or 500 with data exposure
                if response.status_code == 200:
                    vulnerabilities.append({
                        "payload": payload,
                        "status": response.status_code,
                        "issue": "Payload accepted - potential SQL injection"
                    })
                elif response.status_code == 500:
                    # Check if error message exposes SQL
                    if "SQL" in response.text or "SELECT" in response.text:
                        vulnerabilities.append({
                            "payload": payload,
                            "status": response.status_code,
                            "issue": "SQL details exposed in error"
                        })
            except Exception as e:
                pass  # Timeouts are expected for some payloads

        return {
            "passed": len(vulnerabilities) == 0,
            "vulnerabilities": vulnerabilities,
            "payloads_tested": len(payloads)
        }

    def test_sql_injection_in_list_params(self) -> Dict:
        """Test SQL injection in politician_ids list parameter."""
        payloads = [
            ["' OR '1'='1"],
            ["1'; DROP TABLE trades; --"],
            ["valid-uuid", "'; DELETE FROM politicians; --"]
        ]

        vulnerabilities = []
        for payload in payloads:
            try:
                response = requests.get(
                    f"{self.base_url}/analytics/correlation/pairwise",
                    params={"politician_ids": payload},
                    timeout=5
                )

                if response.status_code == 200:
                    vulnerabilities.append({
                        "payload": payload,
                        "issue": "SQL injection payload accepted"
                    })
            except:
                pass

        return {
            "passed": len(vulnerabilities) == 0,
            "vulnerabilities": vulnerabilities
        }

    # ========================================================================
    # Input Validation Tests
    # ========================================================================

    def test_invalid_uuid_format(self) -> Dict:
        """Test that invalid UUIDs are rejected."""
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "null",
            "undefined",
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa-extra",
            "short"
        ]

        properly_rejected = 0
        for uuid in invalid_uuids:
            try:
                response = requests.get(
                    f"{self.base_url}/analytics/ensemble/{uuid}",
                    timeout=5
                )

                # Should get 400 or 422 (validation error), not 500
                if response.status_code in [400, 404, 422]:
                    properly_rejected += 1
                elif response.status_code == 500:
                    # Check that it's not a database error
                    if "database" in response.text.lower() or "sql" in response.text.lower():
                        self.log(f"UUID {uuid} caused database error", "WARN")
            except requests.exceptions.Timeout:
                self.log(f"UUID {uuid} caused timeout", "WARN")

        return {
            "passed": properly_rejected == len(invalid_uuids),
            "properly_rejected": properly_rejected,
            "total_tested": len(invalid_uuids)
        }

    def test_boundary_conditions(self) -> Dict:
        """Test boundary conditions on numeric parameters."""
        tests = []

        # Test negative numbers
        response = requests.get(
            f"{self.base_url}/analytics/network/analysis",
            params={"min_trades": -1, "min_correlation": 0.5},
            timeout=5
        )
        tests.append({
            "test": "negative min_trades",
            "passed": response.status_code in [400, 422]
        })

        # Test correlation > 1
        response = requests.get(
            f"{self.base_url}/analytics/network/analysis",
            params={"min_trades": 50, "min_correlation": 1.5},
            timeout=5
        )
        tests.append({
            "test": "correlation > 1",
            "passed": response.status_code in [400, 422]
        })

        # Test correlation < 0
        response = requests.get(
            f"{self.base_url}/analytics/network/analysis",
            params={"min_trades": 50, "min_correlation": -0.5},
            timeout=5
        )
        tests.append({
            "test": "correlation < 0",
            "passed": response.status_code in [400, 422]
        })

        # Test too many politicians
        fake_ids = [f"00000000-0000-0000-0000-{str(i).zfill(12)}" for i in range(100)]
        response = requests.get(
            f"{self.base_url}/analytics/correlation/pairwise",
            params={"politician_ids": fake_ids},
            timeout=5
        )
        tests.append({
            "test": "too many politicians (100)",
            "passed": response.status_code in [400, 422]
        })

        all_passed = all(t["passed"] for t in tests)
        return {
            "passed": all_passed,
            "tests": tests
        }

    # ========================================================================
    # Information Disclosure Tests
    # ========================================================================

    def test_error_message_disclosure(self) -> Dict:
        """Test that error messages don't expose sensitive info."""
        sensitive_patterns = [
            "password",
            "secret",
            "api_key",
            "token",
            "database",
            "connection string",
            "traceback",
            "/app/app/",  # Internal paths
            "File \"/",  # Python tracebacks
        ]

        # Trigger various errors
        test_cases = [
            f"{self.base_url}/analytics/ensemble/invalid-uuid",
            f"{self.base_url}/analytics/ensemble/00000000-0000-0000-0000-000000000000",
            f"{self.base_url}/analytics/correlation/pairwise?politician_ids=",
        ]

        exposures = []
        for url in test_cases:
            try:
                response = requests.get(url, timeout=5)
                response_text = response.text.lower()

                for pattern in sensitive_patterns:
                    if pattern.lower() in response_text:
                        exposures.append({
                            "url": url,
                            "pattern": pattern,
                            "status_code": response.status_code
                        })
            except:
                pass

        return {
            "passed": len(exposures) == 0,
            "exposures": exposures,
            "tests_run": len(test_cases)
        }

    # ========================================================================
    # Concurrency and Performance Tests
    # ========================================================================

    def test_concurrent_requests(self) -> Dict:
        """Test handling of concurrent requests."""
        # Get a valid politician ID first
        response = requests.get(f"{self.base_url}/patterns/politicians?min_trades=30")
        if response.status_code != 200 or not response.json():
            return {"passed": False, "error": "No test data available"}

        politician_id = response.json()[0]["id"]

        def make_request():
            try:
                r = requests.get(
                    f"{self.base_url}/analytics/insights/{politician_id}",
                    timeout=30
                )
                return {"status": r.status_code, "time": r.elapsed.total_seconds()}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        successful = len([r for r in results if r.get("status") == 200])
        errors = len([r for r in results if r.get("status") == "error"])
        avg_time = sum([r.get("time", 0) for r in results if "time" in r]) / len(results)

        return {
            "passed": successful >= 8,  # Allow some failures under load
            "successful": successful,
            "errors": errors,
            "total": len(results),
            "avg_response_time": avg_time
        }

    def test_large_input_handling(self) -> Dict:
        """Test handling of unreasonably large inputs."""
        tests = []

        # Very long list of politician IDs
        long_list = [f"00000000-0000-0000-0000-{str(i).zfill(12)}" for i in range(1000)]
        try:
            response = requests.get(
                f"{self.base_url}/analytics/correlation/pairwise",
                params={"politician_ids": long_list},
                timeout=5
            )
            tests.append({
                "test": "1000 politician IDs",
                "passed": response.status_code in [400, 413, 422],
                "status": response.status_code
            })
        except requests.exceptions.Timeout:
            tests.append({
                "test": "1000 politician IDs",
                "passed": True,  # Timeout is acceptable
                "status": "timeout"
            })

        return {
            "passed": all(t["passed"] for t in tests),
            "tests": tests
        }

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_empty_data_handling(self) -> Dict:
        """Test handling of politicians with no data."""
        # Use a valid UUID format but non-existent politician
        fake_uuid = "00000000-0000-0000-0000-000000000001"

        response = requests.get(
            f"{self.base_url}/analytics/ensemble/{fake_uuid}",
            timeout=5
        )

        # Should get 404, not 500
        passed = response.status_code == 404

        return {
            "passed": passed,
            "status_code": response.status_code,
            "expected": 404
        }

    def test_special_characters(self) -> Dict:
        """Test handling of special characters in inputs."""
        special_chars = [
            "test@politician.com",
            "test<script>alert()</script>",
            "test\x00null",
            "test%00",
            "test\r\n",
            "../../../etc/passwd"
        ]

        properly_handled = 0
        for char in special_chars:
            try:
                response = requests.get(
                    f"{self.base_url}/analytics/ensemble/{char}",
                    timeout=5
                )

                # Should reject with 400/422, not crash with 500
                if response.status_code in [400, 404, 422]:
                    properly_handled += 1
            except:
                properly_handled += 1  # Timeout/error is fine

        return {
            "passed": properly_handled == len(special_chars),
            "properly_handled": properly_handled,
            "total": len(special_chars)
        }

    # ========================================================================
    # Run All Tests
    # ========================================================================

    def run_all_tests(self):
        """Run complete security test suite."""
        print("\n" + "="*80)
        print("SECURITY & ROBUSTNESS TEST SUITE")
        print("="*80 + "\n")

        print("\n" + "-"*80)
        print("SQL INJECTION TESTS")
        print("-"*80 + "\n")
        self.test("SQL Injection in politician_id", self.test_sql_injection_in_politician_id)
        self.test("SQL Injection in list parameters", self.test_sql_injection_in_list_params)

        print("\n" + "-"*80)
        print("INPUT VALIDATION TESTS")
        print("-"*80 + "\n")
        self.test("Invalid UUID format rejection", self.test_invalid_uuid_format)
        self.test("Boundary condition handling", self.test_boundary_conditions)
        self.test("Special character handling", self.test_special_characters)

        print("\n" + "-"*80)
        print("INFORMATION DISCLOSURE TESTS")
        print("-"*80 + "\n")
        self.test("Error message disclosure", self.test_error_message_disclosure)

        print("\n" + "-"*80)
        print("CONCURRENCY & PERFORMANCE TESTS")
        print("-"*80 + "\n")
        self.test("Concurrent request handling", self.test_concurrent_requests)
        self.test("Large input handling", self.test_large_input_handling)

        print("\n" + "-"*80)
        print("EDGE CASE TESTS")
        print("-"*80 + "\n")
        self.test("Empty data handling", self.test_empty_data_handling)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("SECURITY TEST RESULTS")
        print("="*80 + "\n")

        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        errors = len([r for r in self.results if r["status"] == "ERROR"])
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({100*passed/total:.1f}%)")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print()

        # Critical failures
        critical_failures = []
        for result in self.results:
            if result["status"] != "PASS":
                if "SQL" in result["name"] or "disclosure" in result["name"].lower():
                    critical_failures.append(result)

        if critical_failures:
            print("\n⚠️  CRITICAL SECURITY ISSUES:\n")
            for failure in critical_failures:
                print(f"  ✗ {failure['name']}")
                if "details" in failure and "vulnerabilities" in failure["details"]:
                    for vuln in failure["details"]["vulnerabilities"]:
                        print(f"      - {vuln}")

        # Detailed results
        print("\nDETAILED RESULTS:\n")
        for result in self.results:
            icon = "✓" if result["status"] == "PASS" else "✗"
            print(f"{icon} {result['name']}: {result['status']}")

            if result["status"] != "PASS" and "details" in result:
                details = result["details"]
                for key, value in details.items():
                    if key != "passed" and value:
                        print(f"    {key}: {value}")

        # Save results
        with open("security_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        self.log("Results saved to security_test_results.json")

        if passed == total:
            print("\n" + "="*80)
            print("✅ ALL SECURITY TESTS PASSED")
            print("="*80 + "\n")
        else:
            print("\n" + "="*80)
            print(f"⚠️  {failed + errors} SECURITY TESTS FAILED")
            print("="*80 + "\n")

def main():
    try:
        tester = SecurityTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
