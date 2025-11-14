#!/usr/bin/env python3
"""
Quick Analytics Endpoint Validation
Tests that all advanced analytics endpoints are accessible and responding.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_endpoint(name: str, url: str, params: dict = None):
    """Test if an endpoint is accessible."""
    log(f"Testing: {name}")
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            log(f"✓ {name} - Status 200 OK", "PASS")
            return True, response.json()
        else:
            log(f"✗ {name} - Status {response.status_code}", "WARN")
            log(f"  Response: {response.text[:200]}", "WARN")
            return False, None
    except Exception as e:
        log(f"✗ {name} - Error: {str(e)}", "ERROR")
        return False, None

def main():
    print("\n" + "="*80)
    print("ADVANCED ANALYTICS API ENDPOINT VALIDATION")
    print("="*80 + "\n")

    results = []

    # Get politicians first
    log("Step 1: Getting available politicians...")
    success, politicians = test_endpoint(
        "Get Politicians",
        f"{BASE_URL}/patterns/politicians",
        {"min_trades": 1}
    )

    if not success or not politicians or len(politicians) == 0:
        log("No politicians found in database", "ERROR")
        return

    log(f"Found {len(politicians)} politicians")
    politician_id = politicians[0]["id"]
    politician_name = politicians[0]["name"]
    politician_ids = [p["id"] for p in politicians[:3]]

    log(f"Using test politician: {politician_name} (ID: {politician_id})")

    print("\n" + "-"*80)
    print("TESTING ANALYTICS ENDPOINTS")
    print("-"*80 + "\n")

    # Test 1: Ensemble Prediction
    success, data = test_endpoint(
        "Ensemble Prediction",
        f"{BASE_URL}/analytics/ensemble/{politician_id}",
        {"prediction_horizon": 30}
    )
    results.append(("Ensemble Prediction", success))
    if success and data:
        log(f"  Response contains: {', '.join(data.keys())}", "INFO")

    # Test 2: Correlation Analysis
    success, data = test_endpoint(
        "Correlation Analysis",
        f"{BASE_URL}/analytics/correlation/pairwise",
        {"politician_ids": politician_ids, "correlation_threshold": 0.3}
    )
    results.append(("Correlation Analysis", success))
    if success and data:
        log(f"  Found {len(data)} correlation pairs", "INFO")

    # Test 3: Network Analysis
    success, data = test_endpoint(
        "Network Analysis",
        f"{BASE_URL}/analytics/network/analysis",
        {"politician_ids": politician_ids, "min_correlation": 0.3}
    )
    results.append(("Network Analysis", success))
    if success and data:
        metrics = data.get("network_metrics", {})
        log(f"  Nodes: {metrics.get('total_nodes')}, Edges: {metrics.get('total_edges')}", "INFO")

    # Test 4: Automated Insights
    success, data = test_endpoint(
        "Automated Insights",
        f"{BASE_URL}/analytics/insights/{politician_id}",
        {"min_confidence": 0.5, "min_severity": "LOW"}
    )
    results.append(("Automated Insights", success))
    if success and data:
        insights = data.get("insights", [])
        log(f"  Generated {len(insights)} insights", "INFO")

    # Test 5: Anomaly Detection
    success, data = test_endpoint(
        "Anomaly Detection",
        f"{BASE_URL}/analytics/anomaly-detection/{politician_id}",
        {"sensitivity": 0.7}
    )
    results.append(("Anomaly Detection", success))
    if success and data:
        log(f"  Anomaly score: {data.get('anomaly_score')}, Level: {data.get('anomaly_level')}", "INFO")

    # Print Summary
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status_icon = "✓" if success else "✗"
        status_text = "PASS" if success else "FAIL"
        print(f"{status_icon} {name}: {status_text}")

    print(f"\nTotal: {passed}/{total} endpoints working ({100*passed/total:.0f}%)")

    if passed == total:
        print("\n✓ ALL ANALYTICS ENDPOINTS ARE ACCESSIBLE AND RESPONDING")
        print("\nNote: Limited trade data available. For full testing with predictions,")
        print("more historical trade data is needed (min 30 trades per politician).")
    else:
        print(f"\n⚠️  {total - passed} endpoints failed")

    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
