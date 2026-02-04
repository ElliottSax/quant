"""
SQL Injection Testing Suite

Automated testing for SQL injection vulnerabilities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.logging import get_logger

logger = get_logger(__name__)


class InjectionType(str, Enum):
    """Types of SQL injection tests"""
    CLASSIC = "classic"
    BLIND = "blind"
    TIME_BASED = "time_based"
    UNION = "union"
    ERROR_BASED = "error_based"


@dataclass
class InjectionTestResult:
    """Result of an injection test"""
    test_name: str
    injection_type: InjectionType
    payload: str
    vulnerable: bool
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None


class SQLInjectionTester:
    """
    Tests endpoints for SQL injection vulnerabilities.

    IMPORTANT: Only use in testing environments!
    """

    def __init__(self):
        self.payloads = {
            InjectionType.CLASSIC: [
                "' OR '1'='1",
                "' OR '1'='1' --",
                "' OR '1'='1' /*",
                "admin' --",
                "admin' #",
                "' OR 1=1--",
                "') OR ('1'='1",
            ],
            InjectionType.BLIND: [
                "' AND '1'='1",
                "' AND '1'='2",
                "' AND SUBSTRING(version(),1,1)='5",
            ],
            InjectionType.TIME_BASED: [
                "' AND SLEEP(5)--",
                "'; WAITFOR DELAY '0:0:5'--",
                "' AND pg_sleep(5)--",
            ],
            InjectionType.UNION: [
                "' UNION SELECT NULL--",
                "' UNION SELECT NULL,NULL--",
                "' UNION SELECT NULL,NULL,NULL--",
                "' UNION ALL SELECT NULL--",
            ],
            InjectionType.ERROR_BASED: [
                "'",
                "''",
                "' '",
                "' ORDER BY 1--",
                "' GROUP BY 1--",
            ]
        }

    async def test_query(
        self,
        db: AsyncSession,
        query_template: str,
        test_param: str,
        injection_types: Optional[List[InjectionType]] = None
    ) -> List[InjectionTestResult]:
        """
        Test a query for SQL injection vulnerabilities.

        Args:
            db: Database session
            query_template: SQL query with placeholder
            test_param: Parameter to test
            injection_types: Types of injections to test

        Returns:
            List of test results
        """
        if injection_types is None:
            injection_types = list(InjectionType)

        results = []

        for injection_type in injection_types:
            payloads = self.payloads.get(injection_type, [])

            for payload in payloads:
                result = await self._test_payload(
                    db,
                    query_template,
                    test_param,
                    payload,
                    injection_type
                )
                results.append(result)

        return results

    async def _test_payload(
        self,
        db: AsyncSession,
        query_template: str,
        test_param: str,
        payload: str,
        injection_type: InjectionType
    ) -> InjectionTestResult:
        """
        Test a single payload.

        Args:
            db: Database session
            query_template: SQL query template
            test_param: Parameter to inject into
            payload: Injection payload
            injection_type: Type of injection

        Returns:
            Test result
        """
        import time

        test_name = f"{injection_type.value}:{payload[:20]}"

        try:
            # Inject payload
            injected_query = query_template.replace(
                f"{{{test_param}}}",
                payload
            )

            # Execute query
            start_time = time.time()
            result = await db.execute(text(injected_query))
            response_time = (time.time() - start_time) * 1000

            # Check if vulnerable
            vulnerable = False

            # For time-based injection, check response time
            if injection_type == InjectionType.TIME_BASED:
                if response_time > 4000:  # Expected 5s delay
                    vulnerable = True

            # For other types, if query succeeds with malicious input, it's vulnerable
            elif result:
                vulnerable = True

            return InjectionTestResult(
                test_name=test_name,
                injection_type=injection_type,
                payload=payload,
                vulnerable=vulnerable,
                response_time_ms=response_time
            )

        except Exception as e:
            # Error doesn't necessarily mean secure
            # Could be syntax error from our payload
            error_msg = str(e).lower()

            # Check for error-based injection success
            vulnerable = False
            if injection_type == InjectionType.ERROR_BASED:
                # If we get specific SQL errors, the input isn't sanitized
                sql_errors = [
                    "syntax error",
                    "unterminated string",
                    "unexpected end of command",
                    "pg_query"
                ]
                vulnerable = any(err in error_msg for err in sql_errors)

            return InjectionTestResult(
                test_name=test_name,
                injection_type=injection_type,
                payload=payload,
                vulnerable=vulnerable,
                error_message=str(e)
            )

    def generate_report(
        self,
        results: List[InjectionTestResult]
    ) -> Dict[str, Any]:
        """
        Generate a report from test results.

        Args:
            results: List of test results

        Returns:
            Report dictionary
        """
        total_tests = len(results)
        vulnerable_tests = sum(1 for r in results if r.vulnerable)

        vulnerable_by_type = {}
        for injection_type in InjectionType:
            type_results = [r for r in results if r.injection_type == injection_type]
            vulnerable_by_type[injection_type.value] = {
                "total": len(type_results),
                "vulnerable": sum(1 for r in type_results if r.vulnerable),
                "payloads": [
                    r.payload for r in type_results if r.vulnerable
                ]
            }

        return {
            "summary": {
                "total_tests": total_tests,
                "vulnerable_tests": vulnerable_tests,
                "vulnerability_rate": vulnerable_tests / total_tests if total_tests > 0 else 0,
                "is_secure": vulnerable_tests == 0
            },
            "by_type": vulnerable_by_type,
            "vulnerable_payloads": [
                {
                    "payload": r.payload,
                    "type": r.injection_type.value,
                    "test_name": r.test_name
                }
                for r in results if r.vulnerable
            ]
        }


class InputSanitizer:
    """
    Utility for sanitizing user input.

    Use this as a defense-in-depth measure.
    Primary protection should be parameterized queries!
    """

    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """
        Sanitize input for SQL queries.

        Note: This is NOT a substitute for parameterized queries!
        Use this only as additional defense.

        Args:
            value: Input to sanitize

        Returns:
            Sanitized input
        """
        if not isinstance(value, str):
            return value

        # Remove common SQL injection patterns
        dangerous_patterns = [
            "--",
            ";",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "exec",
            "execute",
            "select",
            "insert",
            "update",
            "delete",
            "drop",
            "create",
            "alter",
            "union",
            "waitfor",
            "sleep"
        ]

        sanitized = value
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")

        return sanitized

    @staticmethod
    def is_safe_identifier(value: str) -> bool:
        """
        Check if a value is safe to use as a SQL identifier.

        Args:
            value: Value to check

        Returns:
            True if safe
        """
        # Only allow alphanumeric and underscore
        return value.replace("_", "").isalnum()

    @staticmethod
    def escape_like_pattern(value: str) -> str:
        """
        Escape special characters in LIKE patterns.

        Args:
            value: Pattern to escape

        Returns:
            Escaped pattern
        """
        return value.replace("%", "\\%").replace("_", "\\_")
