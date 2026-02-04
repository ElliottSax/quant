#!/usr/bin/env python3
"""Quick verification that tests can be imported and run."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("✓ Python path configured")

# Test imports
try:
    from app.schemas import TradeFieldSelection, TradeListResponse, TradeResponse, TradeWithPolitician
    print("✓ Schema imports successful")
except ImportError as e:
    print(f"✗ Schema import failed: {e}")
    sys.exit(1)

try:
    from app.models.user import User
    from app.models.trade import Trade
    from app.models.politician import Politician
    print("✓ Model imports successful")
except ImportError as e:
    print(f"✗ Model import failed: {e}")
    sys.exit(1)

try:
    from app.services.api_key_manager import APIKeyManager
    from app.services.database_optimizer import QueryAnalyzer
    print("✓ Service imports successful")
except ImportError as e:
    print(f"✗ Service import failed: {e}")
    sys.exit(1)

# Count test files
import glob
test_files = glob.glob("tests/test_models/*.py") + glob.glob("tests/test_services/*.py")
test_files = [f for f in test_files if not f.endswith("__init__.py")]
print(f"✓ Found {len(test_files)} test files")

# Count test functions
test_count = 0
for test_file in test_files:
    with open(test_file, 'r') as f:
        content = f.read()
        test_count += content.count("def test_")

print(f"✓ Found {test_count} test functions")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print(f"Test files: {len(test_files)}")
print(f"Test functions: {test_count}")
print("All imports working correctly!")
print("\nReady to run: python3 -m pytest tests/test_models tests/test_services -v")
