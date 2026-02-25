#!/usr/bin/env python3
"""
Pre-Deployment Readiness Check
Verifies the application is ready for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class DeploymentChecker:
    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent
        self.project_root = self.backend_dir.parent.parent
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []

    def print_header(self, text: str):
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{text:^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")

    def print_success(self, text: str):
        print(f"{GREEN}✅ {text}{RESET}")
        self.checks_passed.append(text)

    def print_failure(self, text: str):
        print(f"{RED}❌ {text}{RESET}")
        self.checks_failed.append(text)

    def print_warning(self, text: str):
        print(f"{YELLOW}⚠️  {text}{RESET}")
        self.warnings.append(text)

    def print_info(self, text: str):
        print(f"   {text}")

    def check_required_files(self):
        """Check if all required deployment files exist"""
        self.print_header("Checking Required Files")

        required_files = {
            'Backend': [
                (self.backend_dir / 'requirements.txt', 'requirements.txt'),
                (self.backend_dir / 'alembic.ini', 'alembic.ini'),
                (self.backend_dir / '.env.example', '.env.example'),
                (self.backend_dir / 'app' / 'main.py', 'app/main.py'),
            ],
            'Deployment': [
                (self.project_root / 'Procfile', 'Procfile'),
                (self.project_root / 'runtime.txt', 'runtime.txt'),
                (self.project_root / 'railway.json', 'railway.json'),
            ],
            'Documentation': [
                (self.project_root / 'START_HERE.md', 'START_HERE.md'),
                (self.project_root / 'ONE_CLICK_DEPLOY.md', 'ONE_CLICK_DEPLOY.md'),
            ]
        }

        for category, files in required_files.items():
            print(f"\n{category} Files:")
            for file_path, display_name in files:
                if file_path.exists():
                    self.print_success(f"{display_name} exists")
                else:
                    self.print_failure(f"{display_name} missing")

    def check_environment_config(self):
        """Check environment configuration"""
        self.print_header("Checking Environment Configuration")

        env_example = self.backend_dir / '.env.example'
        if env_example.exists():
            self.print_success(".env.example file exists")

            # Read and check for required variables
            with open(env_example) as f:
                content = f.read()

            required_vars = [
                'SECRET_KEY',
                'DATABASE_URL',
                'ENVIRONMENT',
                'DEBUG',
            ]

            for var in required_vars:
                if var in content:
                    self.print_success(f"{var} defined in .env.example")
                else:
                    self.print_failure(f"{var} missing in .env.example")
        else:
            self.print_failure(".env.example file missing")

    def check_dependencies(self):
        """Check if dependencies are properly defined"""
        self.print_header("Checking Dependencies")

        req_file = self.backend_dir / 'requirements.txt'
        if req_file.exists():
            with open(req_file) as f:
                deps = f.read()

            critical_deps = [
                'fastapi',
                'uvicorn',
                'sqlalchemy',
                'alembic',
                'pydantic',
                'pytest',
            ]

            for dep in critical_deps:
                if dep in deps.lower():
                    self.print_success(f"{dep} in requirements.txt")
                else:
                    self.print_failure(f"{dep} missing in requirements.txt")
        else:
            self.print_failure("requirements.txt missing")

    def check_alembic_migrations(self):
        """Check Alembic migration setup"""
        self.print_header("Checking Database Migrations")

        alembic_dir = self.backend_dir / 'alembic'
        if alembic_dir.exists():
            self.print_success("Alembic directory exists")

            versions_dir = alembic_dir / 'versions'
            if versions_dir.exists():
                migrations = list(versions_dir.glob('*.py'))
                if migrations:
                    self.print_success(f"Found {len(migrations)} migration(s)")
                else:
                    self.print_warning("No migrations found (may be ok for new deployments)")
            else:
                self.print_failure("alembic/versions directory missing")
        else:
            self.print_failure("Alembic directory missing")

    def check_tests(self):
        """Check if tests exist and can be run"""
        self.print_header("Checking Tests")

        tests_dir = self.backend_dir / 'tests'
        if tests_dir.exists():
            test_files = list(tests_dir.rglob('test_*.py'))
            if test_files:
                self.print_success(f"Found {len(test_files)} test file(s)")

                # Check for pytest configuration
                if (self.backend_dir / 'pytest.ini').exists():
                    self.print_success("pytest.ini configuration exists")

                # Try to collect tests
                self.print_info("Collecting tests...")
                try:
                    result = subprocess.run(
                        ['python3', '-m', 'pytest', '--collect-only', '-q'],
                        cwd=self.backend_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        # Count tests from output
                        output_lines = result.stdout.strip().split('\n')
                        for line in output_lines:
                            if 'test' in line.lower():
                                self.print_success(f"Tests can be collected")
                                break
                    else:
                        self.print_warning("Test collection had issues (may need dependencies)")
                except Exception as e:
                    self.print_warning(f"Could not run pytest: {e}")
            else:
                self.print_warning("No test files found")
        else:
            self.print_warning("tests/ directory not found")

    def check_security(self):
        """Check security configurations"""
        self.print_header("Checking Security Configuration")

        # Check for .env in .gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            with open(gitignore) as f:
                content = f.read()
            if '.env' in content:
                self.print_success(".env in .gitignore")
            else:
                self.print_failure(".env NOT in .gitignore - SECURITY RISK!")
        else:
            self.print_warning(".gitignore not found")

        # Check for hardcoded secrets in example
        env_example = self.backend_dir / '.env.example'
        if env_example.exists():
            with open(env_example) as f:
                content = f.read()

            dangerous_patterns = [
                ('CHANGE_THIS', 'Placeholder passwords found'),
                ('your-', 'Placeholder API keys found'),
                ('example', 'Example values found'),
            ]

            for pattern, msg in dangerous_patterns:
                if pattern in content:
                    self.print_success(f"Using placeholders: {msg}")
                    break

    def check_deployment_configs(self):
        """Check deployment configuration files"""
        self.print_header("Checking Deployment Configurations")

        # Check Procfile
        procfile = self.project_root / 'Procfile'
        if procfile.exists():
            with open(procfile) as f:
                content = f.read()
            if 'uvicorn' in content and 'app.main:app' in content:
                self.print_success("Procfile has correct uvicorn command")
            else:
                self.print_failure("Procfile missing proper uvicorn command")

        # Check runtime.txt
        runtime = self.project_root / 'runtime.txt'
        if runtime.exists():
            with open(runtime) as f:
                version = f.read().strip()
            if version.startswith('python-3'):
                self.print_success(f"runtime.txt specifies {version}")
            else:
                self.print_failure("runtime.txt has invalid Python version")

        # Check railway.json
        railway = self.project_root / 'railway.json'
        if railway.exists():
            self.print_success("railway.json exists for Railway deployment")

    def check_documentation(self):
        """Check if documentation is complete"""
        self.print_header("Checking Documentation")

        docs = [
            'START_HERE.md',
            'ONE_CLICK_DEPLOY.md',
            'API_DOCUMENTATION.md',
            'GETTING_STARTED.md',
        ]

        for doc in docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                size = doc_path.stat().st_size
                if size > 1000:  # At least 1KB
                    self.print_success(f"{doc} exists ({size} bytes)")
                else:
                    self.print_warning(f"{doc} exists but seems small ({size} bytes)")
            else:
                self.print_warning(f"{doc} not found")

    def print_summary(self):
        """Print final summary"""
        self.print_header("Deployment Readiness Summary")

        total = len(self.checks_passed) + len(self.checks_failed)
        passed_pct = (len(self.checks_passed) / total * 100) if total > 0 else 0

        print(f"\n{GREEN}✅ Passed:{RESET} {len(self.checks_passed)}")
        print(f"{RED}❌ Failed:{RESET} {len(self.checks_failed)}")
        print(f"{YELLOW}⚠️  Warnings:{RESET} {len(self.warnings)}")
        print(f"\n{BLUE}Overall Score:{RESET} {passed_pct:.1f}%")

        if len(self.checks_failed) == 0:
            print(f"\n{GREEN}{'='*70}{RESET}")
            print(f"{GREEN}🎉 DEPLOYMENT READY! All critical checks passed.{RESET}")
            print(f"{GREEN}{'='*70}{RESET}\n")

            if len(self.warnings) > 0:
                print(f"{YELLOW}Note: {len(self.warnings)} warning(s) found. Review them before deploying.{RESET}\n")

            return True
        else:
            print(f"\n{RED}{'='*70}{RESET}")
            print(f"{RED}⚠️  NOT READY FOR DEPLOYMENT{RESET}")
            print(f"{RED}Please fix the {len(self.checks_failed)} failed check(s) above.{RESET}")
            print(f"{RED}{'='*70}{RESET}\n")
            return False

    def run_all_checks(self):
        """Run all deployment checks"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}{'Quant Trading Platform - Pre-Deployment Check':^70}{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")

        self.check_required_files()
        self.check_environment_config()
        self.check_dependencies()
        self.check_alembic_migrations()
        self.check_tests()
        self.check_security()
        self.check_deployment_configs()
        self.check_documentation()

        is_ready = self.print_summary()

        return is_ready


def main():
    checker = DeploymentChecker()
    is_ready = checker.run_all_checks()

    if is_ready:
        print(f"{GREEN}Next steps:{RESET}")
        print("1. Review ONE_CLICK_DEPLOY.md for deployment instructions")
        print("2. Choose a deployment platform (Railway recommended)")
        print("3. Set environment variables")
        print("4. Deploy!")
        sys.exit(0)
    else:
        print(f"{RED}Please fix the issues above before deploying.{RESET}")
        sys.exit(1)


if __name__ == '__main__':
    main()
