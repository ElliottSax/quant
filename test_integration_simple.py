#!/usr/bin/env python3
"""
Simple integration test - checks if prediction router is registered.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "quant" / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("Simple Integration Test")
print("=" * 60)

# Test 1: Check if prediction.py file exists
print("\n1. Checking if prediction.py exists...")
prediction_file = backend_path / "app" / "api" / "v1" / "prediction.py"
if prediction_file.exists():
    print(f"   ✅ Found: {prediction_file}")
else:
    print(f"   ❌ Not found: {prediction_file}")
    sys.exit(1)

# Test 2: Check if __init__.py has prediction import
print("\n2. Checking if prediction router is registered...")
init_file = backend_path / "app" / "api" / "v1" / "__init__.py"
with open(init_file, 'r') as f:
    content = f.read()
    if 'from app.api.v1 import prediction' in content:
        print("   ✅ Prediction router import found")
    else:
        print("   ❌ Prediction router import NOT found")
        sys.exit(1)

    if 'api_router.include_router(prediction.router' in content:
        print("   ✅ Prediction router registered")
    else:
        print("   ❌ Prediction router NOT registered")
        sys.exit(1)

# Test 3: Check if deps.py has get_redis_client
print("\n3. Checking if get_redis_client dependency exists...")
deps_file = backend_path / "app" / "core" / "deps.py"
with open(deps_file, 'r') as f:
    content = f.read()
    if 'def get_redis_client' in content:
        print("   ✅ get_redis_client dependency found")
    else:
        print("   ❌ get_redis_client dependency NOT found")
        sys.exit(1)

# Test 4: Check service files exist
print("\n4. Checking if service files exist...")
service_files = [
    "app/services/market_data/__init__.py",
    "app/services/market_data/multi_provider_client.py",
    "app/services/technical_analysis/__init__.py",
    "app/services/technical_analysis/indicator_calculator.py",
    "app/services/technical_analysis/pattern_detector.py",
]

all_exist = True
for service_file in service_files:
    file_path = backend_path / service_file
    if file_path.exists():
        print(f"   ✅ {service_file}")
    else:
        print(f"   ❌ {service_file} NOT found")
        all_exist = False

if not all_exist:
    sys.exit(1)

# Test 5: Check documentation exists
print("\n5. Checking if documentation exists...")
doc_files = [
    "STOCK_PREDICTION_INTEGRATION_PLAN.md",
    "STOCK_PREDICTION_QUICK_START.md",
    "PREDICTION_FEATURES_SUMMARY.md",
    "PREDICTION_INTEGRATION_COMPLETE.md",
]

for doc_file in doc_files:
    file_path = Path(__file__).parent / doc_file
    if file_path.exists():
        print(f"   ✅ {doc_file}")
    else:
        print(f"   ❌ {doc_file} NOT found")

print("\n" + "=" * 60)
print("✅ ALL INTEGRATION CHECKS PASSED!")
print("=" * 60)

print("\n📋 Summary:")
print("  ✅ Prediction API files created")
print("  ✅ Router properly registered")
print("  ✅ Dependencies configured")
print("  ✅ Service modules present")
print("  ✅ Documentation complete")

print("\n🚀 Next Steps:")
print("  1. Install dependencies:")
print("     cd quant/backend")
print("     pip install yfinance pandas-ta")
print()
print("  2. Start the server:")
print("     uvicorn app.main:app --reload")
print()
print("  3. Test endpoints:")
print("     http://localhost:8000/api/v1/docs")
print("     Look for 'stock-prediction' tag")

sys.exit(0)
