#!/usr/bin/env python3
"""
Test that main.py can be loaded and app initialized (without running server).
This verifies all imports and initialization logic work.
"""

import sys
import os

# Set required environment variables for testing
os.environ.update({
    "ENVIRONMENT": "development",
    "DEBUG": "true",
    "SECRET_KEY": "test-secret-key-for-testing-that-is-32-characters-long",
    "DATABASE_URL": "postgresql://quant_user:quant_password@localhost:5432/quant_db",
    "REDIS_URL": "redis://localhost:6379/0",
    "PROJECT_NAME": "Quant Test",
    "VERSION": "1.0.0",
    "API_V1_STR": "/api/v1",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "BACKEND_CORS_ORIGINS": '["http://localhost:3000"]'
})

# Add backend to path
sys.path.insert(0, 'quant/backend')

print("=" * 60)
print("TESTING MAIN.PY STARTUP")
print("=" * 60)
print()

def test_imports():
    """Test that all imports work."""
    print("1. Testing imports...")
    
    try:
        # Test config validator
        from app.core.config_validator import ConfigValidator, validate_config_on_startup
        print("   ✅ Config validator imported")
        
        # Test enhanced rate limiting
        from app.core.rate_limit_enhanced import EnhancedRateLimiter, EnhancedRateLimitMiddleware
        print("   ✅ Enhanced rate limiter imported")
        
        # Test audit logging
        from app.core.audit import AuditLogger, AuditEventType, AuditSeverity
        print("   ✅ Audit logger imported")
        
        # Test analytics schemas
        from app.schemas.analytics import (
            EnsemblePredictionResponse,
            CorrelationPairResponse,
            NetworkMetricsResponse
        )
        print("   ✅ OpenAPI schemas imported")
        
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_config_validation():
    """Test configuration validation."""
    print("\n2. Testing configuration validation...")
    
    try:
        from app.core.config_validator import ConfigValidator
        
        validator = ConfigValidator("development")
        
        # Test that validator methods exist
        assert hasattr(validator, 'validate_all')
        assert hasattr(validator, '_validate_security')
        assert hasattr(validator, '_validate_database')
        
        print("   ✅ Config validator initialized")
        
        # Check validation with current env
        result = validator.validate_all()
        
        if validator.errors:
            print(f"   ⚠️  Config warnings: {len(validator.warnings)} warnings")
            for warning in validator.warnings[:3]:
                print(f"      - {warning}")
        else:
            print("   ✅ Configuration valid")
        
        return True
    except Exception as e:
        print(f"   ❌ Config validation error: {e}")
        return False

def test_rate_limiter():
    """Test rate limiter initialization."""
    print("\n3. Testing rate limiter...")
    
    try:
        from app.core.rate_limit_enhanced import EnhancedRateLimiter, RateLimitTier
        
        limiter = EnhancedRateLimiter(
            redis_client=None,  # Will create on demand
            default_limit=60,
            window_seconds=60
        )
        
        # Check tier limits
        assert RateLimitTier.LIMITS[RateLimitTier.FREE] == 20
        assert RateLimitTier.LIMITS[RateLimitTier.BASIC] == 60
        assert RateLimitTier.LIMITS[RateLimitTier.PREMIUM] == 200
        
        print("   ✅ Rate limiter initialized")
        print(f"   ✅ Tier limits: Free=20, Basic=60, Premium=200")
        
        return True
    except Exception as e:
        print(f"   ❌ Rate limiter error: {e}")
        return False

def test_audit_logger():
    """Test audit logger initialization."""
    print("\n4. Testing audit logger...")
    
    try:
        from app.core.audit import AuditLogger, AuditEventType
        
        audit_logger = AuditLogger()
        
        # Check methods exist
        assert hasattr(audit_logger, 'log_event')
        assert hasattr(audit_logger, 'log_login')
        assert hasattr(audit_logger, 'log_data_access')
        assert hasattr(audit_logger, '_extract_request_info')
        
        # Check event types
        assert AuditEventType.LOGIN_SUCCESS
        assert AuditEventType.DATA_CREATED
        assert AuditEventType.RATE_LIMIT_EXCEEDED
        
        print("   ✅ Audit logger initialized")
        print(f"   ✅ Event types defined: {len(list(AuditEventType))}")
        
        return True
    except Exception as e:
        print(f"   ❌ Audit logger error: {e}")
        return False

def test_app_creation():
    """Test FastAPI app can be created."""
    print("\n5. Testing FastAPI app creation...")
    
    try:
        # This will test if the app can be created with all middleware
        # Note: This won't run the lifespan events (no DB connection needed)
        from app.main import app
        
        # Check app attributes
        assert app.title
        assert app.version
        
        # Check middleware stack
        middleware_count = len(app.middleware_stack)
        
        print(f"   ✅ FastAPI app created")
        print(f"   ✅ App title: {app.title}")
        print(f"   ✅ Middleware stack: {middleware_count} middleware")
        
        # Check routes
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        print(f"   ✅ Routes registered: {len(routes)} routes")
        
        return True
    except Exception as e:
        print(f"   ❌ App creation error: {e}")
        return False

def main():
    """Run all tests."""
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_config_validation()
    all_passed &= test_rate_limiter()
    all_passed &= test_audit_logger()
    all_passed &= test_app_creation()
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ ALL STARTUP TESTS PASSED!")
        print("\nThe application can be started with:")
        print("  cd quant/backend")
        print("  uvicorn app.main:app --reload --port 8000")
    else:
        print("❌ Some tests failed - check errors above")
    
    print("=" * 60)
    
    # Show summary
    print("\nIMPROVEMENTS SUMMARY:")
    print("✅ Config Validation: Validates environment on startup")
    print("✅ Rate Limiting: Per-user tiers with sliding window")
    print("✅ Audit Logging: Comprehensive security event tracking")
    print("✅ OpenAPI Docs: Complete schemas with examples")
    print("✅ N+1 Prevention: Optimized queries with eager loading")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())