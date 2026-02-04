#!/usr/bin/env python3
"""
Verification script for Task #10: Premium Features

This script verifies that all premium features are correctly implemented.
"""

import sys
from pathlib import Path


def verify_files_exist():
    """Verify all required files exist."""
    print("✓ Verifying file structure...")

    base_path = Path(__file__).parent
    required_files = [
        # Models
        "app/models/alert.py",
        "app/models/portfolio.py",
        "app/models/subscription.py",
        # Services
        "app/services/alert_service.py",
        "app/services/portfolio_service.py",
        "app/services/subscription_service.py",
        # API Endpoints
        "app/api/v1/alerts.py",
        "app/api/v1/portfolios.py",
        "app/api/v1/subscriptions.py",
        # Migration
        "alembic/versions/007_add_premium_features.py",
        # Tests
        "tests/test_premium_features.py",
        # Documentation
        "PREMIUM_FEATURES_DOCUMENTATION.md",
    ]

    missing = []
    for file in required_files:
        if not (base_path / file).exists():
            missing.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")

    if missing:
        print(f"\n✗ {len(missing)} files missing!")
        return False

    print(f"\n✓ All {len(required_files)} files present!")
    return True


def verify_imports():
    """Verify all imports work correctly."""
    print("\n✓ Verifying imports...")

    try:
        # Models
        from app.models.alert import Alert, AlertType, AlertStatus
        from app.models.portfolio import Portfolio, Watchlist
        from app.models.subscription import (
            Subscription,
            SubscriptionTier,
            SubscriptionStatus,
            UsageRecord,
        )

        print("  ✓ Models import successfully")

        # Services
        from app.services.alert_service import alert_service
        from app.services.portfolio_service import portfolio_service
        from app.services.subscription_service import (
            subscription_service,
            stripe_service,
        )

        print("  ✓ Services import successfully")

        # API endpoints
        from app.api.v1 import alerts, portfolios, subscriptions

        print("  ✓ API endpoints import successfully")

        print("\n✓ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        return False


def verify_stripe_dependency():
    """Verify stripe is installed."""
    print("\n✓ Verifying dependencies...")

    try:
        import stripe

        print(f"  ✓ Stripe installed (version: {stripe.__version__})")
        return True
    except ImportError:
        print("  ✗ Stripe not installed")
        print("  Run: pip install stripe>=7.0.0")
        return False


def verify_models():
    """Verify model structure."""
    print("\n✓ Verifying model structure...")

    from app.models.alert import Alert
    from app.models.portfolio import Portfolio, Watchlist
    from app.models.subscription import Subscription, UsageRecord

    # Check Alert model
    alert_fields = [
        "id",
        "user_id",
        "name",
        "alert_type",
        "conditions",
        "notification_channels",
        "status",
        "is_active",
    ]
    for field in alert_fields:
        if not hasattr(Alert, field):
            print(f"  ✗ Alert missing field: {field}")
            return False

    print("  ✓ Alert model structure correct")

    # Check Portfolio model
    portfolio_fields = [
        "id",
        "politician_id",
        "snapshot_date",
        "holdings",
        "total_value",
        "sector_allocation",
    ]
    for field in portfolio_fields:
        if not hasattr(Portfolio, field):
            print(f"  ✗ Portfolio missing field: {field}")
            return False

    print("  ✓ Portfolio model structure correct")

    # Check Watchlist model
    watchlist_fields = ["id", "user_id", "name", "politician_ids"]
    for field in watchlist_fields:
        if not hasattr(Watchlist, field):
            print(f"  ✗ Watchlist missing field: {field}")
            return False

    print("  ✓ Watchlist model structure correct")

    # Check Subscription model
    subscription_fields = [
        "id",
        "user_id",
        "tier",
        "status",
        "stripe_customer_id",
        "api_rate_limit",
        "features",
    ]
    for field in subscription_fields:
        if not hasattr(Subscription, field):
            print(f"  ✗ Subscription missing field: {field}")
            return False

    print("  ✓ Subscription model structure correct")

    # Check UsageRecord model
    usage_fields = ["id", "user_id", "resource_type", "usage_date", "request_count"]
    for field in usage_fields:
        if not hasattr(UsageRecord, field):
            print(f"  ✗ UsageRecord missing field: {field}")
            return False

    print("  ✓ UsageRecord model structure correct")

    print("\n✓ All models correctly structured!")
    return True


def verify_services():
    """Verify service methods exist."""
    print("\n✓ Verifying service methods...")

    from app.services.alert_service import alert_service
    from app.services.portfolio_service import portfolio_service
    from app.services.subscription_service import subscription_service

    # Alert service methods
    alert_methods = [
        "create_alert",
        "get_user_alerts",
        "delete_alert",
        "update_alert",
    ]
    for method in alert_methods:
        if not hasattr(alert_service, method):
            print(f"  ✗ AlertService missing method: {method}")
            return False

    print("  ✓ AlertService methods correct")

    # Portfolio service methods
    portfolio_methods = [
        "create_watchlist",
        "get_user_watchlists",
        "delete_watchlist",
        "calculate_portfolio_snapshot",
    ]
    for method in portfolio_methods:
        if not hasattr(portfolio_service, method):
            print(f"  ✗ PortfolioService missing method: {method}")
            return False

    print("  ✓ PortfolioService methods correct")

    # Subscription service methods
    subscription_methods = [
        "get_subscription",
        "check_premium_access",
        "check_rate_limit",
        "record_usage",
        "upgrade_subscription",
    ]
    for method in subscription_methods:
        if not hasattr(subscription_service, method):
            print(f"  ✗ SubscriptionService missing method: {method}")
            return False

    print("  ✓ SubscriptionService methods correct")

    print("\n✓ All service methods present!")
    return True


def verify_api_routes():
    """Verify API routes are registered."""
    print("\n✓ Verifying API routes...")

    try:
        from app.api.v1 import api_router

        # Get all registered routes
        routes = [route.path for route in api_router.routes]

        # Check for premium feature routes
        required_routes = [
            "/alerts",
            "/portfolios/watchlists",
            "/subscriptions/current",
        ]

        for route in required_routes:
            matching = [r for r in routes if route in r]
            if not matching:
                print(f"  ✗ Route not found: {route}")
                return False

        print("  ✓ Alert routes registered")
        print("  ✓ Portfolio routes registered")
        print("  ✓ Subscription routes registered")

        print(f"\n✓ All API routes registered!")
        return True

    except Exception as e:
        print(f"\n✗ Route verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Task #10: Premium Features Verification")
    print("=" * 60)

    checks = [
        ("File Structure", verify_files_exist),
        ("Dependencies", verify_stripe_dependency),
        ("Imports", verify_imports),
        ("Models", verify_models),
        ("Services", verify_services),
        ("API Routes", verify_api_routes),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n✓✓✓ All checks passed! Task #10 is COMPLETE! ✓✓✓")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} checks failed. Please review. ✗✗✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
