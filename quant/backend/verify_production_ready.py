#!/usr/bin/env python3
"""
Production Readiness Verification Script

Checks if the QuantEngines platform is ready for deployment.
Run this before deploying to production or staging.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ProductionReadinessChecker:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
        self.base_path = Path(__file__).parent

    def check_required_files(self) -> bool:
        """Check if all required files exist"""
        print(f"\n{BLUE}1. Checking Required Files...{RESET}")

        required_files = [
            '.env.example',
            'requirements.txt',
            'alembic.ini',
            'app/main.py',
            'app/__init__.py',
            'README.md',
        ]

        all_exist = True
        for file in required_files:
            file_path = self.base_path / file
            if file_path.exists():
                self.successes.append(f"✓ {file} exists")
            else:
                self.errors.append(f"✗ {file} missing")
                all_exist = False

        return all_exist

    def check_environment_example(self) -> bool:
        """Check if .env.example has required variables"""
        print(f"\n{BLUE}2. Checking .env.example...{RESET}")

        required_vars = [
            'PROJECT_NAME',
            'VERSION',
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL',
            'ENVIRONMENT',
        ]

        env_example_path = self.base_path / '.env.example'
        if not env_example_path.exists():
            self.errors.append("✗ .env.example not found")
            return False

        content = env_example_path.read_text()
        all_present = True

        for var in required_vars:
            if f"{var}=" in content:
                self.successes.append(f"✓ {var} in .env.example")
            else:
                self.warnings.append(f"⚠ {var} missing from .env.example")
                all_present = False

        return all_present

    def check_debug_code(self) -> bool:
        """Check for debug code (print statements)"""
        print(f"\n{BLUE}3. Checking for Debug Code...{RESET}")

        python_files = list(self.base_path.glob("app/**/*.py"))
        print_found = []

        for file_path in python_files:
            if file_path.name.startswith('test_'):
                continue
            if 'scripts' in str(file_path):
                continue

            content = file_path.read_text()
            lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                # Skip comments
                stripped = line.strip()
                if stripped.startswith('#'):
                    continue
                # Look for print statements
                if 'print(' in line and 'logger' not in line:
                    rel_path = file_path.relative_to(self.base_path)
                    print_found.append(f"{rel_path}:{i}")

        if print_found:
            for location in print_found:
                self.warnings.append(f"⚠ print() found in {location}")
            return False
        else:
            self.successes.append("✓ No debug print statements found")
            return True

    def check_secrets_in_code(self) -> bool:
        """Check for potential secrets in code"""
        print(f"\n{BLUE}4. Checking for Hardcoded Secrets...{RESET}")

        python_files = list(self.base_path.glob("app/**/*.py"))
        secrets_found = []

        secret_patterns = [
            'sk_live_',  # Stripe live key
            'sk_test_',  # Stripe test key
            'api_key = "',  # API key
            'secret = "',  # Secret
            'password = "',  # Password
        ]

        for file_path in python_files:
            content = file_path.read_text()

            for pattern in secret_patterns:
                if pattern in content.lower():
                    rel_path = file_path.relative_to(self.base_path)
                    secrets_found.append(f"{rel_path} (pattern: {pattern})")

        if secrets_found:
            for location in secrets_found:
                self.errors.append(f"✗ Potential secret in {location}")
            return False
        else:
            self.successes.append("✓ No hardcoded secrets found")
            return True

    def check_import_health(self) -> bool:
        """Check if main app imports successfully"""
        print(f"\n{BLUE}5. Checking Import Health...{RESET}")

        try:
            # Try importing the main app
            sys.path.insert(0, str(self.base_path))
            from app.main import app  # noqa
            self.successes.append("✓ Main app imports successfully")
            return True
        except Exception as e:
            self.errors.append(f"✗ Import error: {str(e)}")
            return False

    def check_gitignore(self) -> bool:
        """Check if .gitignore exists and covers important files"""
        print(f"\n{BLUE}6. Checking .gitignore...{RESET}")

        gitignore_path = self.base_path.parent.parent / '.gitignore'

        if not gitignore_path.exists():
            self.errors.append("✗ .gitignore not found")
            return False

        content = gitignore_path.read_text()

        required_patterns = [
            '.env',
            '__pycache__',
            '*.pyc',
            'venv/',
            'node_modules/',
        ]

        all_present = True
        for pattern in required_patterns:
            if pattern in content:
                self.successes.append(f"✓ .gitignore includes {pattern}")
            else:
                self.warnings.append(f"⚠ .gitignore missing {pattern}")
                all_present = False

        return all_present

    def check_documentation(self) -> bool:
        """Check if key documentation exists"""
        print(f"\n{BLUE}7. Checking Documentation...{RESET}")

        doc_files = [
            self.base_path.parent.parent / 'README.md',
            self.base_path.parent / 'frontend' / 'README.md',
            self.base_path / 'DEPLOYMENT_GUIDE.md',
        ]

        all_exist = True
        for doc_file in doc_files:
            if doc_file.exists():
                self.successes.append(f"✓ {doc_file.name} exists")
            else:
                self.warnings.append(f"⚠ {doc_file.name} missing")
                all_exist = False

        return all_exist

    def run_all_checks(self) -> Tuple[int, int, int]:
        """Run all checks and return counts"""
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}QuantEngines Production Readiness Check{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")

        checks = [
            self.check_required_files(),
            self.check_environment_example(),
            self.check_debug_code(),
            self.check_secrets_in_code(),
            self.check_import_health(),
            self.check_gitignore(),
            self.check_documentation(),
        ]

        passed = sum(checks)
        total = len(checks)

        return len(self.errors), len(self.warnings), len(self.successes)

    def print_summary(self, errors: int, warnings: int, successes: int):
        """Print final summary"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}SUMMARY{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

        if self.successes:
            print(f"{GREEN}Successes ({len(self.successes)}):{RESET}")
            for success in self.successes[:10]:  # Show first 10
                print(f"  {success}")
            if len(self.successes) > 10:
                print(f"  ... and {len(self.successes) - 10} more")
            print()

        if self.warnings:
            print(f"{YELLOW}Warnings ({len(self.warnings)}):{RESET}")
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.errors:
            print(f"{RED}Errors ({len(self.errors)}):{RESET}")
            for error in self.errors:
                print(f"  {error}")
            print()

        print(f"{BLUE}{'='*60}{RESET}")

        if errors == 0 and warnings == 0:
            print(f"{GREEN}✓ PRODUCTION READY! All checks passed.{RESET}")
            print(f"{GREEN}  You can proceed with deployment.{RESET}")
            return 0
        elif errors == 0:
            print(f"{YELLOW}⚠ READY WITH WARNINGS ({warnings} warnings){RESET}")
            print(f"{YELLOW}  Review warnings but can deploy if acceptable.{RESET}")
            return 0
        else:
            print(f"{RED}✗ NOT READY ({errors} errors, {warnings} warnings){RESET}")
            print(f"{RED}  Fix errors before deploying to production.{RESET}")
            return 1


def main():
    """Main entry point"""
    checker = ProductionReadinessChecker()
    errors, warnings, successes = checker.run_all_checks()
    exit_code = checker.print_summary(errors, warnings, successes)

    print(f"\n{BLUE}Next Steps:{RESET}")
    if exit_code == 0:
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your environment-specific values")
        print("  3. Get API keys for external services")
        print("  4. Run: alembic upgrade head")
        print("  5. Run: uvicorn app.main:app --reload")
        print("  6. Deploy using: ./scripts/quick_deploy.sh")
    else:
        print("  1. Fix errors listed above")
        print("  2. Run this script again")
        print("  3. Proceed with deployment when all checks pass")

    print()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
