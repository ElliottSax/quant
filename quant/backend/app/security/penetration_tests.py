"""
Automated Penetration Testing Suite

Runs security tests against the application.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class VulnerabilityType(str, Enum):
    """Types of vulnerabilities"""
    XSS = "xss"
    SQL_INJECTION = "sql_injection"
    CSRF = "csrf"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SENSITIVE_DATA = "sensitive_data"
    SECURITY_HEADERS = "security_headers"
    RATE_LIMITING = "rate_limiting"


class Severity(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Detected vulnerability"""
    type: VulnerabilityType
    severity: Severity
    endpoint: str
    description: str
    evidence: Optional[str] = None
    remediation: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class PenetrationTester:
    """
    Automated penetration testing suite.

    IMPORTANT: Only run against test environments!
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.vulnerabilities: List[Vulnerability] = []

    async def run_all_tests(self) -> List[Vulnerability]:
        """
        Run all penetration tests.

        Returns:
            List of vulnerabilities found
        """
        self.vulnerabilities = []

        tests = [
            self.test_xss(),
            self.test_security_headers(),
            self.test_authentication(),
            self.test_authorization(),
            self.test_rate_limiting(),
            self.test_sensitive_data_exposure(),
        ]

        await asyncio.gather(*tests, return_exceptions=True)

        return self.vulnerabilities

    async def test_xss(self):
        """Test for XSS vulnerabilities"""
        logger.info("Testing for XSS vulnerabilities...")

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
        ]

        # Test common endpoints
        endpoints = [
            "/api/v1/politicians?search={payload}",
            "/api/v1/trades?symbol={payload}",
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                for payload in xss_payloads:
                    url = f"{self.base_url}{endpoint.format(payload=payload)}"

                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            text = await response.text()

                            # Check if payload is reflected unescaped
                            if payload in text and "<" in text:
                                self.vulnerabilities.append(Vulnerability(
                                    type=VulnerabilityType.XSS,
                                    severity=Severity.HIGH,
                                    endpoint=endpoint,
                                    description=f"XSS vulnerability detected: payload reflected unescaped",
                                    evidence=f"Payload: {payload}",
                                    remediation="Implement proper output encoding and Content Security Policy"
                                ))

                    except Exception as e:
                        logger.debug(f"XSS test error: {e}")

    async def test_security_headers(self):
        """Test for missing security headers"""
        logger.info("Testing security headers...")

        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age",
            "Content-Security-Policy": None,  # Just check presence
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    headers = response.headers

                    for header, expected_value in required_headers.items():
                        if header not in headers:
                            self.vulnerabilities.append(Vulnerability(
                                type=VulnerabilityType.SECURITY_HEADERS,
                                severity=Severity.MEDIUM,
                                endpoint="/",
                                description=f"Missing security header: {header}",
                                remediation=f"Add {header} header to responses"
                            ))
                        elif expected_value:
                            actual_value = headers[header]
                            if isinstance(expected_value, list):
                                if not any(exp in actual_value for exp in expected_value):
                                    self.vulnerabilities.append(Vulnerability(
                                        type=VulnerabilityType.SECURITY_HEADERS,
                                        severity=Severity.MEDIUM,
                                        endpoint="/",
                                        description=f"Incorrect {header} header",
                                        evidence=f"Expected: {expected_value}, Got: {actual_value}",
                                        remediation=f"Set {header} to one of: {expected_value}"
                                    ))
                            elif expected_value not in actual_value:
                                self.vulnerabilities.append(Vulnerability(
                                    type=VulnerabilityType.SECURITY_HEADERS,
                                    severity=Severity.MEDIUM,
                                    endpoint="/",
                                    description=f"Incorrect {header} header",
                                    evidence=f"Expected: {expected_value}, Got: {actual_value}",
                                    remediation=f"Update {header} header value"
                                ))

            except Exception as e:
                logger.error(f"Security headers test error: {e}")

    async def test_authentication(self):
        """Test authentication mechanisms"""
        logger.info("Testing authentication...")

        # Test for weak password requirements
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "test",
        ]

        async with aiohttp.ClientSession() as session:
            for password in weak_passwords:
                try:
                    async with session.post(
                        f"{self.base_url}/api/v1/auth/register",
                        json={
                            "email": "test@example.com",
                            "password": password,
                            "name": "Test User"
                        },
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            self.vulnerabilities.append(Vulnerability(
                                type=VulnerabilityType.AUTHENTICATION,
                                severity=Severity.HIGH,
                                endpoint="/api/v1/auth/register",
                                description="Weak password accepted",
                                evidence=f"Password: {password}",
                                remediation="Implement strong password requirements"
                            ))

                except Exception as e:
                    logger.debug(f"Authentication test error: {e}")

    async def test_authorization(self):
        """Test authorization controls"""
        logger.info("Testing authorization...")

        # Test for broken access control
        sensitive_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/database/optimization-report",
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in sensitive_endpoints:
                try:
                    # Try accessing without authentication
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            self.vulnerabilities.append(Vulnerability(
                                type=VulnerabilityType.AUTHORIZATION,
                                severity=Severity.CRITICAL,
                                endpoint=endpoint,
                                description="Sensitive endpoint accessible without authentication",
                                remediation="Implement proper authentication and authorization"
                            ))

                except Exception as e:
                    logger.debug(f"Authorization test error: {e}")

    async def test_rate_limiting(self):
        """Test rate limiting"""
        logger.info("Testing rate limiting...")

        async with aiohttp.ClientSession() as session:
            # Make many requests quickly
            tasks = []
            for _ in range(150):  # Exceed typical rate limit
                tasks.append(
                    session.get(
                        f"{self.base_url}/api/v1/stats/overview",
                        timeout=aiohttp.ClientTimeout(total=5)
                    )
                )

            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                # Check if any were rate limited
                rate_limited = sum(
                    1 for r in responses
                    if not isinstance(r, Exception) and r.status == 429
                )

                if rate_limited == 0:
                    self.vulnerabilities.append(Vulnerability(
                        type=VulnerabilityType.RATE_LIMITING,
                        severity=Severity.MEDIUM,
                        endpoint="/api/v1/stats/overview",
                        description="No rate limiting detected",
                        evidence="150 requests succeeded without 429 response",
                        remediation="Implement rate limiting to prevent abuse"
                    ))

            except Exception as e:
                logger.error(f"Rate limiting test error: {e}")

    async def test_sensitive_data_exposure(self):
        """Test for sensitive data exposure"""
        logger.info("Testing for sensitive data exposure...")

        sensitive_patterns = [
            ("password", "Password field in response"),
            ("secret", "Secret key in response"),
            ("api_key", "API key in response"),
            ("token", "Token in response"),
            ("credit_card", "Credit card number in response"),
        ]

        async with aiohttp.ClientSession() as session:
            try:
                # Check error responses for sensitive data
                async with session.get(
                    f"{self.base_url}/api/v1/nonexistent",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    text = await response.text()

                    for pattern, description in sensitive_patterns:
                        if pattern in text.lower():
                            self.vulnerabilities.append(Vulnerability(
                                type=VulnerabilityType.SENSITIVE_DATA,
                                severity=Severity.HIGH,
                                endpoint="/api/v1/*",
                                description=description,
                                remediation="Remove sensitive data from responses"
                            ))

            except Exception as e:
                logger.debug(f"Sensitive data test error: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate penetration test report.

        Returns:
            Report dictionary
        """
        by_severity = {}
        for severity in Severity:
            by_severity[severity.value] = [
                v for v in self.vulnerabilities
                if v.severity == severity
            ]

        by_type = {}
        for vuln_type in VulnerabilityType:
            by_type[vuln_type.value] = [
                v for v in self.vulnerabilities
                if v.type == vuln_type
            ]

        return {
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": len(by_severity[Severity.CRITICAL.value]),
                "high": len(by_severity[Severity.HIGH.value]),
                "medium": len(by_severity[Severity.MEDIUM.value]),
                "low": len(by_severity[Severity.LOW.value]),
                "info": len(by_severity[Severity.INFO.value]),
            },
            "by_severity": {
                k: [v.to_dict() for v in v_list]
                for k, v_list in by_severity.items()
            },
            "by_type": {
                k: [v.to_dict() for v in v_list]
                for k, v_list in by_type.items()
            },
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities]
        }
