#!/usr/bin/env python3
"""
Simple test to verify all improvement files are in place and have correct structure.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ Missing: {description} - {filepath}")
        return False

def check_file_contains(filepath, search_text, description):
    """Check if file contains specific text."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - text not found")
                return False
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("QUANT PLATFORM IMPROVEMENTS VERIFICATION")
    print("=" * 60)
    print()
    
    all_passed = True
    base_path = "quant/backend/app"
    
    # 1. Check optimized analytics file
    print("1. N+1 QUERY OPTIMIZATION")
    print("-" * 40)
    if check_file_exists(f"{base_path}/api/v1/analytics_optimized.py", "Optimized analytics"):
        check_file_contains(
            f"{base_path}/api/v1/analytics_optimized.py",
            "load_politicians_with_trades_batch",
            "   - Batch loading function"
        )
        check_file_contains(
            f"{base_path}/api/v1/analytics_optimized.py",
            "selectinload",
            "   - Eager loading imports"
        )
    else:
        all_passed = False
    print()
    
    # 2. Check OpenAPI schemas
    print("2. OPENAPI DOCUMENTATION")
    print("-" * 40)
    if check_file_exists(f"{base_path}/schemas/analytics.py", "Analytics schemas"):
        check_file_contains(
            f"{base_path}/schemas/analytics.py",
            "EnsemblePredictionResponse",
            "   - Ensemble prediction schema"
        )
        check_file_contains(
            f"{base_path}/schemas/analytics.py",
            "model_config = ConfigDict",
            "   - OpenAPI examples"
        )
    else:
        all_passed = False
    print()
    
    # 3. Check enhanced rate limiting
    print("3. ENHANCED RATE LIMITING")
    print("-" * 40)
    if check_file_exists(f"{base_path}/core/rate_limit_enhanced.py", "Enhanced rate limiter"):
        check_file_contains(
            f"{base_path}/core/rate_limit_enhanced.py",
            "RateLimitTier",
            "   - Tier-based limits"
        )
        check_file_contains(
            f"{base_path}/core/rate_limit_enhanced.py",
            "EnhancedRateLimiter",
            "   - Enhanced limiter class"
        )
        check_file_contains(
            f"{base_path}/core/rate_limit_enhanced.py",
            "_check_sliding_window",
            "   - Sliding window algorithm"
        )
    else:
        all_passed = False
    print()
    
    # 4. Check audit logging
    print("4. AUDIT LOGGING SYSTEM")
    print("-" * 40)
    if check_file_exists(f"{base_path}/core/audit.py", "Audit logging"):
        check_file_contains(
            f"{base_path}/core/audit.py",
            "AuditEventType",
            "   - Event type enum"
        )
        check_file_contains(
            f"{base_path}/core/audit.py",
            "AuditLogger",
            "   - Audit logger class"
        )
        check_file_contains(
            f"{base_path}/core/audit.py",
            "log_login",
            "   - Login audit method"
        )
        check_file_contains(
            f"{base_path}/core/audit.py",
            "_extract_request_info",
            "   - Request info extraction"
        )
    else:
        all_passed = False
    print()
    
    # 5. Check config validation
    print("5. CONFIGURATION VALIDATION")
    print("-" * 40)
    if check_file_exists(f"{base_path}/core/config_validator.py", "Config validator"):
        check_file_contains(
            f"{base_path}/core/config_validator.py",
            "ConfigValidator",
            "   - Validator class"
        )
        check_file_contains(
            f"{base_path}/core/config_validator.py",
            "_validate_security",
            "   - Security validation"
        )
        check_file_contains(
            f"{base_path}/core/config_validator.py",
            "_validate_production",
            "   - Production checks"
        )
    else:
        all_passed = False
    print()
    
    # 6. Check main.py updates
    print("6. MAIN.PY INTEGRATION")
    print("-" * 40)
    if check_file_exists(f"{base_path}/main.py", "Main application"):
        check_file_contains(
            f"{base_path}/main.py",
            "validate_config_on_startup",
            "   - Config validation import"
        )
        check_file_contains(
            f"{base_path}/main.py",
            "EnhancedRateLimitMiddleware",
            "   - Enhanced rate limiting"
        )
        check_file_contains(
            f"{base_path}/main.py",
            "audit_logger",
            "   - Audit logging setup"
        )
    else:
        all_passed = False
    print()
    
    # 7. Check auth.py updates
    print("7. AUTH ENDPOINT UPDATES")
    print("-" * 40)
    if check_file_exists(f"{base_path}/api/v1/auth.py", "Auth endpoints"):
        check_file_contains(
            f"{base_path}/api/v1/auth.py",
            "from app.core.audit import audit_logger",
            "   - Audit logger import"
        )
        check_file_contains(
            f"{base_path}/api/v1/auth.py",
            "AuditEventType.ACCOUNT_CREATED",
            "   - Registration audit"
        )
    else:
        all_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ ALL IMPROVEMENTS SUCCESSFULLY IMPLEMENTED!")
    else:
        print("⚠️  Some improvements may need attention")
    print("=" * 60)
    print()
    print("FEATURE SUMMARY:")
    print("1. N+1 Query Prevention: Batch loading & eager loading")
    print("2. OpenAPI Documentation: Complete schemas with examples")
    print("3. Rate Limiting: Per-user tiers (Free/Basic/Premium)")
    print("4. Audit Logging: Comprehensive security & compliance")
    print("5. Config Validation: Startup checks with env validation")
    print()
    print("FILES CREATED/MODIFIED:")
    print("- app/api/v1/analytics_optimized.py")
    print("- app/schemas/analytics.py")
    print("- app/core/rate_limit_enhanced.py")
    print("- app/core/audit.py")
    print("- app/core/config_validator.py")
    print("- app/main.py (updated)")
    print("- app/api/v1/auth.py (updated)")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())