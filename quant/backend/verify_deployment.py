#!/usr/bin/env python3
"""
Deployment Verification Script

Tests all critical imports and dependencies before deployment.
Run this before starting the server to catch issues early.
"""

import sys
import importlib
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


class bcolors:
    """Terminal colors for output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def test_import(module_name: str, description: str = None, optional: bool = False) -> bool:
    """Test importing a module."""
    display_name = description or module_name
    try:
        importlib.import_module(module_name)
        print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} {display_name}")
        return True
    except ImportError as e:
        if optional:
            print(f"{bcolors.WARNING}⚠{bcolors.ENDC} {display_name} (optional, not installed)")
        else:
            print(f"{bcolors.FAIL}✗{bcolors.ENDC} {display_name}")
            print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} {display_name}")
        print(f"  Unexpected error: {e}")
        return False


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(backend_dir) / file_path
    if path.exists():
        print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} {description}")
        return True
    else:
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} {description}")
        print(f"  Missing: {path}")
        return False


def main():
    """Run all deployment verification checks."""
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}Deployment Verification Script{bcolors.ENDC}")
    print("=" * 60)

    all_passed = True

    # Check 1: Critical Files
    print(f"\n{bcolors.OKBLUE}1. Critical Files:{bcolors.ENDC}")
    all_passed &= check_file_exists("app/services/__init__.py", "app/services/__init__.py")
    all_passed &= check_file_exists(".env", ".env configuration file")
    all_passed &= check_file_exists("alembic/versions/002_add_prediction_models.py", "Prediction models migration")

    # Check 2: Core Dependencies
    print(f"\n{bcolors.OKBLUE}2. Core Dependencies:{bcolors.ENDC}")
    all_passed &= test_import("fastapi", "FastAPI")
    all_passed &= test_import("uvicorn", "Uvicorn")
    all_passed &= test_import("sqlalchemy", "SQLAlchemy")
    all_passed &= test_import("pydantic", "Pydantic")
    all_passed &= test_import("httpx", "HTTPX")
    all_passed &= test_import("redis", "Redis")

    # Check 3: Market Data Dependencies
    print(f"\n{bcolors.OKBLUE}3. Market Data Dependencies:{bcolors.ENDC}")
    all_passed &= test_import("yfinance", "yfinance")
    all_passed &= test_import("pandas", "Pandas")
    all_passed &= test_import("numpy", "NumPy")

    # Check 4: NEW Technical Analysis Dependencies
    print(f"\n{bcolors.OKBLUE}4. Technical Analysis Dependencies:{bcolors.ENDC}")
    pandas_ta_ok = test_import("pandas_ta", "pandas-ta (REQUIRED)", optional=False)
    all_passed &= pandas_ta_ok
    test_import("talib", "TA-Lib (optional)", optional=True)

    # Check 5: NEW Optional Market Data Providers
    print(f"\n{bcolors.OKBLUE}5. Optional Market Data Providers:{bcolors.ENDC}")
    test_import("alpha_vantage", "Alpha Vantage", optional=True)
    test_import("twelvedata", "Twelve Data", optional=True)
    test_import("finnhub", "Finnhub", optional=True)

    # Check 6: Core App Modules
    print(f"\n{bcolors.OKBLUE}6. Core App Modules:{bcolors.ENDC}")
    all_passed &= test_import("app.core.config", "App configuration")
    all_passed &= test_import("app.core.database", "Database setup")
    all_passed &= test_import("app.core.security", "Security module")
    all_passed &= test_import("app.core.deps", "Dependencies")

    # Check 7: NEW Rate Limiting Module
    print(f"\n{bcolors.OKBLUE}7. Security Modules:{bcolors.ENDC}")
    rate_limit_ok = test_import("app.core.rate_limiting", "Rate limiting (NEW)")
    all_passed &= rate_limit_ok

    # Check 8: Database Models
    print(f"\n{bcolors.OKBLUE}8. Database Models:{bcolors.ENDC}")
    all_passed &= test_import("app.models.user", "User model")
    all_passed &= test_import("app.models.trade", "Trade model")

    # Check 9: NEW Prediction Models
    print(f"\n{bcolors.OKBLUE}9. Prediction Models (NEW):{bcolors.ENDC}")
    prediction_models_ok = test_import("app.models.prediction", "Prediction models")
    all_passed &= prediction_models_ok

    if prediction_models_ok:
        try:
            from app.models import (
                StockPrediction, TechnicalIndicators, TradingSignal,
                PatternDetection, ModelPerformance
            )
            print(f"  {bcolors.OKGREEN}✓{bcolors.ENDC} All prediction models importable from app.models")
        except ImportError as e:
            print(f"  {bcolors.FAIL}✗{bcolors.ENDC} Prediction models not in app.models.__init__.py")
            print(f"    Error: {e}")
            all_passed = False

    # Check 10: NEW Service Modules
    print(f"\n{bcolors.OKBLUE}10. Service Modules:{bcolors.ENDC}")
    market_data_ok = test_import("app.services.market_data", "Market data service")
    all_passed &= market_data_ok

    if market_data_ok:
        try:
            from app.services.market_data import MarketDataClient
            print(f"  {bcolors.OKGREEN}✓{bcolors.ENDC} MarketDataClient importable")
        except ImportError as e:
            print(f"  {bcolors.FAIL}✗{bcolors.ENDC} MarketDataClient import failed")
            print(f"    Error: {e}")
            all_passed = False

    tech_analysis_ok = test_import("app.services.technical_analysis", "Technical analysis service")
    all_passed &= tech_analysis_ok

    if tech_analysis_ok:
        try:
            from app.services.technical_analysis import IndicatorCalculator, PatternDetector
            print(f"  {bcolors.OKGREEN}✓{bcolors.ENDC} IndicatorCalculator and PatternDetector importable")
        except ImportError as e:
            print(f"  {bcolors.FAIL}✗{bcolors.ENDC} Technical analysis classes import failed")
            print(f"    Error: {e}")
            all_passed = False

    # Check 11: API Routes
    print(f"\n{bcolors.OKBLUE}11. API Routes:{bcolors.ENDC}")
    all_passed &= test_import("app.api.v1.auth", "Auth routes")
    all_passed &= test_import("app.api.v1.trades", "Trades routes")

    # Check 12: NEW Secured Prediction Routes
    print(f"\n{bcolors.OKBLUE}12. Prediction Routes (SECURED):{bcolors.ENDC}")
    prediction_secure_ok = test_import("app.api.v1.prediction_secure", "Secured prediction routes (NEW)")
    all_passed &= prediction_secure_ok

    if prediction_secure_ok:
        try:
            from app.api.v1.prediction_secure import router
            print(f"  {bcolors.OKGREEN}✓{bcolors.ENDC} Secured prediction router available")
        except ImportError as e:
            print(f"  {bcolors.FAIL}✗{bcolors.ENDC} Prediction router import failed")
            print(f"    Error: {e}")
            all_passed = False

    # Check 13: Main App
    print(f"\n{bcolors.OKBLUE}13. Main Application:{bcolors.ENDC}")
    all_passed &= test_import("app.main", "Main FastAPI app")

    # Check 14: Environment Variables
    print(f"\n{bcolors.OKBLUE}14. Environment Variables:{bcolors.ENDC}")
    try:
        from app.core.config import settings

        # Check SECRET_KEY
        if settings.SECRET_KEY and len(settings.SECRET_KEY) >= 32:
            print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} SECRET_KEY configured (length: {len(settings.SECRET_KEY)})")
        else:
            print(f"{bcolors.FAIL}✗{bcolors.ENDC} SECRET_KEY too short or missing")
            all_passed = False

        # Check DATABASE_URL
        if settings.DATABASE_URL:
            print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} DATABASE_URL configured")
        else:
            print(f"{bcolors.WARNING}⚠{bcolors.ENDC} DATABASE_URL not set (optional for dev)")

        # Check REDIS
        if settings.REDIS_ENABLED:
            print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} Redis enabled")
        else:
            print(f"{bcolors.WARNING}⚠{bcolors.ENDC} Redis disabled (performance will be reduced)")

    except Exception as e:
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} Settings configuration error")
        print(f"  Error: {e}")
        all_passed = False

    # Check 15: Context Manager Support
    print(f"\n{bcolors.OKBLUE}15. Context Manager Support:{bcolors.ENDC}")
    try:
        from app.services.market_data import MarketDataClient

        # Check for context manager methods
        if hasattr(MarketDataClient, '__aenter__') and hasattr(MarketDataClient, '__aexit__'):
            print(f"{bcolors.OKGREEN}✓{bcolors.ENDC} MarketDataClient supports async context manager")
        else:
            print(f"{bcolors.FAIL}✗{bcolors.ENDC} MarketDataClient missing context manager support")
            all_passed = False
    except Exception as e:
        print(f"{bcolors.FAIL}✗{bcolors.ENDC} Context manager check failed")
        print(f"  Error: {e}")
        all_passed = False

    # Summary
    print(f"\n{bcolors.HEADER}{'=' * 60}{bcolors.ENDC}")
    if all_passed:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}✓ ALL CHECKS PASSED - READY FOR DEPLOYMENT{bcolors.ENDC}")
        print()
        print("Next steps:")
        print("  1. Run database migrations: alembic upgrade head")
        print("  2. Start server: uvicorn app.main:app --reload")
        print("  3. Test authentication: python examples/authenticated_prediction_demo.py")
        return 0
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}✗ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT{bcolors.ENDC}")
        print()
        print("Common fixes:")
        print("  1. Install missing dependencies: pip install -r requirements.txt")
        print("  2. Create .env file from .env.example (if exists)")
        print("  3. Run database migrations: alembic upgrade head")
        return 1


if __name__ == "__main__":
    sys.exit(main())
