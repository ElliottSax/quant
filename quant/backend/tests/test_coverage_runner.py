"""
Comprehensive test coverage runner and analyzer.
Identifies untested code and generates coverage reports.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class CoverageAnalyzer:
    """Analyzes test coverage and identifies gaps."""

    def __init__(self, backend_path: Path):
        self.backend_path = backend_path
        self.coverage_data = {}
        self.untested_files = []
        self.partially_tested = []

    def run_tests_with_coverage(self) -> bool:
        """Run all tests with coverage enabled."""
        print("Running tests with coverage...")
        cmd = [
            "python3", "-m", "pytest",
            "--cov=app",
            "--cov-report=json",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v",
            "--tb=short"
        ]

        result = subprocess.run(
            cmd,
            cwd=self.backend_path,
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0

    def load_coverage_data(self) -> bool:
        """Load coverage data from JSON report."""
        coverage_file = self.backend_path / "coverage.json"
        if not coverage_file.exists():
            print(f"Coverage file not found: {coverage_file}")
            return False

        with open(coverage_file) as f:
            data = json.load(f)
            self.coverage_data = data.get("files", {})

        return True

    def analyze_coverage(self) -> Tuple[float, List[str], List[str]]:
        """
        Analyze coverage data and identify gaps.

        Returns:
            Tuple of (overall_coverage, untested_files, partially_tested_files)
        """
        if not self.coverage_data:
            return 0.0, [], []

        total_statements = 0
        covered_statements = 0
        untested = []
        partial = []

        for file_path, file_data in self.coverage_data.items():
            # Skip test files and migrations
            if "test_" in file_path or "migrations" in file_path:
                continue

            summary = file_data.get("summary", {})
            statements = summary.get("num_statements", 0)
            covered = summary.get("covered_lines", 0)
            missing = summary.get("missing_lines", 0)

            total_statements += statements
            covered_statements += covered

            if statements > 0:
                coverage_pct = (covered / statements) * 100

                if coverage_pct == 0:
                    untested.append(f"{file_path} (0% coverage)")
                elif coverage_pct < 90:
                    partial.append(f"{file_path} ({coverage_pct:.1f}% coverage)")

        overall_coverage = (covered_statements / total_statements * 100) if total_statements > 0 else 0

        return overall_coverage, untested, partial

    def identify_critical_gaps(self) -> Dict[str, List[str]]:
        """Identify critical areas lacking tests."""
        gaps = {
            "api_endpoints": [],
            "models": [],
            "services": [],
            "core_utilities": [],
            "security": []
        }

        for file_path, file_data in self.coverage_data.items():
            summary = file_data.get("summary", {})
            statements = summary.get("num_statements", 0)
            covered = summary.get("covered_lines", 0)

            if statements == 0:
                continue

            coverage_pct = (covered / statements) * 100

            if coverage_pct < 80:
                if "/api/v1/" in file_path:
                    gaps["api_endpoints"].append(file_path)
                elif "/models/" in file_path:
                    gaps["models"].append(file_path)
                elif "/services/" in file_path:
                    gaps["services"].append(file_path)
                elif "/security" in file_path or "auth" in file_path.lower():
                    gaps["security"].append(file_path)
                elif "/core/" in file_path:
                    gaps["core_utilities"].append(file_path)

        return gaps

    def generate_test_plan(self) -> str:
        """Generate a test plan for improving coverage."""
        overall_coverage, untested, partial = self.analyze_coverage()
        gaps = self.identify_critical_gaps()

        plan = f"""
# Test Coverage Improvement Plan

## Current Status
- Overall Coverage: {overall_coverage:.1f}%
- Target Coverage: 95%
- Gap: {95 - overall_coverage:.1f}%

## Untested Files ({len(untested)})
"""
        for file in untested[:10]:  # Show first 10
            plan += f"- {file}\n"

        if len(untested) > 10:
            plan += f"... and {len(untested) - 10} more\n"

        plan += f"""
## Partially Tested Files (<90% coverage) ({len(partial)})
"""
        for file in partial[:10]:  # Show first 10
            plan += f"- {file}\n"

        if len(partial) > 10:
            plan += f"... and {len(partial) - 10} more\n"

        plan += """
## Critical Gaps by Category

### API Endpoints
"""
        for file in gaps["api_endpoints"][:5]:
            plan += f"- {file}\n"

        plan += """
### Models
"""
        for file in gaps["models"][:5]:
            plan += f"- {file}\n"

        plan += """
### Services
"""
        for file in gaps["services"][:5]:
            plan += f"- {file}\n"

        plan += """
### Security
"""
        for file in gaps["security"][:5]:
            plan += f"- {file}\n"

        plan += """
## Recommended Actions

1. **Prioritize Security Tests**
   - Ensure all authentication/authorization code is tested
   - Add tests for all security-related endpoints
   - Test rate limiting and input validation

2. **Add API Integration Tests**
   - Test all endpoints with valid/invalid inputs
   - Test authentication requirements
   - Test error handling

3. **Model Tests**
   - Test all model methods
   - Test relationships and constraints
   - Test validation logic

4. **Service Layer Tests**
   - Test business logic
   - Test error handling
   - Test edge cases

5. **Add Performance Tests**
   - Use Locust for load testing
   - Test database query performance
   - Test caching effectiveness
"""

        return plan


def main():
    """Main execution function."""
    backend_path = Path(__file__).parent.parent

    analyzer = CoverageAnalyzer(backend_path)

    # Run tests
    success = analyzer.run_tests_with_coverage()

    if not success:
        print("\n⚠️  Some tests failed. Fix failing tests before analyzing coverage.")
        return 1

    # Load and analyze coverage
    if not analyzer.load_coverage_data():
        print("\n❌ Could not load coverage data")
        return 1

    # Generate report
    plan = analyzer.generate_test_plan()
    print(plan)

    # Save plan to file
    plan_file = backend_path / "coverage_analysis_report.md"
    with open(plan_file, "w") as f:
        f.write(plan)

    print(f"\n📊 Coverage analysis saved to: {plan_file}")

    # Check if we met the goal
    overall_coverage, _, _ = analyzer.analyze_coverage()
    if overall_coverage >= 95:
        print(f"\n✅ Coverage goal met! {overall_coverage:.1f}% >= 95%")
        return 0
    else:
        print(f"\n⚠️  Coverage goal not met: {overall_coverage:.1f}% < 95%")
        print(f"   Need to increase coverage by {95 - overall_coverage:.1f}%")
        return 1


if __name__ == "__main__":
    sys.exit(main())
