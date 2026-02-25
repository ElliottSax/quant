#!/usr/bin/env python3
"""
Comprehensive Platform Test Script
Tests all components and creates detailed report
"""

import subprocess
import requests
import json
import time
from datetime import datetime

class PlatformTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }

    def add_result(self, category, name, status, message="", details=None):
        """Add test result"""
        result = {
            "category": category,
            "name": name,
            "status": status,  # pass, fail, skip
            "message": message,
            "details": details or {}
        }
        self.results["tests"].append(result)
        self.results["summary"]["total"] += 1
        if status == "pass":
            self.results["summary"]["passed"] += 1
        elif status == "fail":
            self.results["summary"]["failed"] += 1
        else:
            self.results["summary"]["skipped"] += 1

        # Print result
        status_emoji = "✅" if status == "pass" else ("❌" if status == "fail" else "⏭️")
        print(f"{status_emoji} [{category}] {name}: {message}")

    def test_docker_services(self):
        """Test Docker infrastructure services"""
        print("\n🐳 Testing Docker Services...")

        services = [
            ("quant-postgres", 5432),
            ("quant-redis-ml", 6380),
            ("quant-mlflow", 5000),
            ("quant-minio", 9000),
        ]

        for service_name, port in services:
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={service_name}", "--format", "{{.Status}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "Up" in result.stdout:
                    self.add_result(
                        "Infrastructure",
                        f"{service_name} container",
                        "pass",
                        f"Running (port {port})"
                    )
                else:
                    self.add_result(
                        "Infrastructure",
                        f"{service_name} container",
                        "fail",
                        "Not running"
                    )
            except Exception as e:
                self.add_result(
                    "Infrastructure",
                    f"{service_name} container",
                    "fail",
                    str(e)
                )

    def test_backend_api(self, base_url="http://localhost:8000"):
        """Test backend API endpoints"""
        print("\n🚀 Testing Backend API...")

        # Test basic endpoints
        endpoints = [
            ("/health", "GET", "Health check"),
            ("/docs", "GET", "API documentation"),
            ("/api/v1/auth/me", "GET", "Auth endpoint (should fail without token)"),
        ]

        for path, method, description in endpoints:
            try:
                response = requests.request(
                    method,
                    f"{base_url}{path}",
                    timeout=5
                )
                if response.status_code < 500:  # Accept 4xx but not 5xx
                    self.add_result(
                        "Backend API",
                        description,
                        "pass",
                        f"Status {response.status_code}",
                        {"status_code": response.status_code}
                    )
                else:
                    self.add_result(
                        "Backend API",
                        description,
                        "fail",
                        f"Server error {response.status_code}"
                    )
            except requests.exceptions.ConnectionError:
                self.add_result(
                    "Backend API",
                    description,
                    "skip",
                    "Backend not running"
                )
            except Exception as e:
                self.add_result(
                    "Backend API",
                    description,
                    "fail",
                    str(e)
                )

    def test_frontend(self, base_url="http://localhost:3000"):
        """Test frontend server"""
        print("\n🎨 Testing Frontend...")

        pages = [
            ("/", "Home page"),
            ("/dashboard", "Dashboard page"),
            ("/signals", "Signals page"),
            ("/backtesting", "Backtesting page"),
            ("/discoveries", "Discoveries page"),
        ]

        for path, description in pages:
            try:
                response = requests.get(
                    f"{base_url}{path}",
                    timeout=10
                )
                if response.status_code == 200:
                    self.add_result(
                        "Frontend",
                        description,
                        "pass",
                        f"Loaded successfully ({len(response.content)} bytes)"
                    )
                else:
                    self.add_result(
                        "Frontend",
                        description,
                        "fail",
                        f"Status {response.status_code}"
                    )
            except requests.exceptions.ConnectionError:
                self.add_result(
                    "Frontend",
                    description,
                    "skip",
                    "Frontend not running"
                )
            except Exception as e:
                self.add_result(
                    "Frontend",
                    description,
                    "fail",
                    str(e)
                )

    def test_python_dependencies(self):
        """Test Python dependencies"""
        print("\n📦 Testing Python Dependencies...")

        packages = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlalchemy", "ORM"),
            ("redis", "Redis client"),
            ("pandas", "Data analysis"),
            ("numpy", "Numerical computing"),
            ("yfinance", "Market data"),
            ("scipy", "Scientific computing"),
            ("celery", "Task queue"),
            ("httpx", "HTTP client"),
            ("pydantic", "Data validation"),
        ]

        for package, description in packages:
            try:
                __import__(package)
                self.add_result(
                    "Dependencies",
                    f"{package} package",
                    "pass",
                    description
                )
            except ImportError:
                self.add_result(
                    "Dependencies",
                    f"{package} package",
                    "fail",
                    f"Not installed: {description}"
                )

    def test_file_structure(self):
        """Test critical files exist"""
        print("\n📁 Testing File Structure...")

        import os

        critical_files = [
            "/mnt/e/projects/quant/quant/backend/app/main.py",
            "/mnt/e/projects/quant/quant/backend/app/api/v1/__init__.py",
            "/mnt/e/projects/quant/quant/backend/app/services/signal_generator.py",
            "/mnt/e/projects/quant/quant/backend/app/services/backtesting.py",
            "/mnt/e/projects/quant/quant/backend/app/services/email_service.py",
            "/mnt/e/projects/quant/quant/frontend/src/app/page.tsx",
            "/mnt/e/projects/quant/quant/frontend/src/components/charts/PriceChart.tsx",
        ]

        for file_path in critical_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.add_result(
                    "File Structure",
                    os.path.basename(file_path),
                    "pass",
                    f"Exists ({size} bytes)"
                )
            else:
                self.add_result(
                    "File Structure",
                    os.path.basename(file_path),
                    "fail",
                    "File not found"
                )

    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        print(f"⏭️  Skipped: {self.results['summary']['skipped']}")

        pass_rate = (self.results['summary']['passed'] / self.results['summary']['total'] * 100) if self.results['summary']['total'] > 0 else 0
        print(f"\n📈 Pass Rate: {pass_rate:.1f}%")

        # Save detailed report
        with open("test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed report saved to: test_report.json")

        # Generate markdown report
        self.generate_markdown_report()

    def generate_markdown_report(self):
        """Generate markdown test report"""
        md = ["# Platform Test Report\n"]
        md.append(f"**Date:** {self.results['timestamp']}\n")
        md.append(f"**Total Tests:** {self.results['summary']['total']}\n")
        md.append(f"**Pass Rate:** {self.results['summary']['passed']}/{self.results['summary']['total']} ({self.results['summary']['passed']/self.results['summary']['total']*100:.1f}%)\n\n")

        # Group by category
        categories = {}
        for test in self.results['tests']:
            cat = test['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test)

        for category, tests in categories.items():
            md.append(f"## {category}\n\n")
            md.append("| Test | Status | Message |\n")
            md.append("|------|--------|----------|\n")
            for test in tests:
                status_icon = "✅" if test['status'] == "pass" else ("❌" if test['status'] == "fail" else "⏭️")
                md.append(f"| {test['name']} | {status_icon} {test['status']} | {test['message']} |\n")
            md.append("\n")

        with open("TEST_REPORT.md", "w") as f:
            f.writelines(md)
        print(f"📄 Markdown report saved to: TEST_REPORT.md")

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive Platform Tests\n")
        print("="*60)

        self.test_file_structure()
        self.test_python_dependencies()
        self.test_docker_services()
        self.test_backend_api()
        self.test_frontend()

        self.generate_report()


if __name__ == "__main__":
    tester = PlatformTester()
    tester.run_all_tests()
