#!/usr/bin/env python3
"""
Comprehensive Advanced Analytics API Testing Script

Tests all advanced analytics endpoints with real data:
- Ensemble predictions
- Correlation analysis
- Network analysis
- Automated insights
- Anomaly detection
"""

import requests
import json
from typing import List, Dict
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class AdvancedAnalyticsTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.politicians = []

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test(self, name: str, func):
        """Run a test and record results."""
        self.log(f"Running: {name}")
        try:
            result = func()
            self.test_results.append({
                "name": name,
                "status": "PASS" if result else "FAIL",
                "details": result
            })
            self.log(f"✓ {name}", "PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            self.log(f"✗ {name}: {str(e)}", "ERROR")
            return None

    def get_politicians(self) -> List[Dict]:
        """Get politicians with sufficient data for analysis."""
        response = requests.get(
            f"{self.base_url}/patterns/politicians",
            params={"min_trades": 30}
        )
        response.raise_for_status()
        return response.json()

    def test_ensemble_prediction(self, politician_id: str) -> Dict:
        """Test ensemble prediction endpoint."""
        response = requests.get(
            f"{self.base_url}/analytics/ensemble/{politician_id}",
            params={"prediction_horizon": 30}
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        assert "ensemble_prediction" in data
        assert "individual_predictions" in data
        assert "interpretation" in data

        ensemble = data["ensemble_prediction"]
        assert "predicted_value" in ensemble
        assert "confidence" in ensemble
        assert "model_agreement" in ensemble
        assert "anomaly_score" in ensemble

        # Validate individual predictions
        assert len(data["individual_predictions"]) >= 1
        for pred in data["individual_predictions"]:
            assert "model_name" in pred
            assert "prediction" in pred
            assert "confidence" in pred

        return {
            "politician": data.get("politician_name"),
            "prediction": ensemble["predicted_value"],
            "confidence": ensemble["confidence"],
            "agreement": ensemble["model_agreement"],
            "models_used": len(data["individual_predictions"])
        }

    def test_correlation_analysis(self, politician_ids: List[str]) -> Dict:
        """Test pairwise correlation analysis."""
        response = requests.get(
            f"{self.base_url}/analytics/correlation/pairwise",
            params={
                "politician_ids": politician_ids,
                "correlation_threshold": 0.5,
                "max_lag_days": 30
            }
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        assert isinstance(data, list)

        if len(data) > 0:
            corr = data[0]
            assert "politician1" in corr
            assert "politician2" in corr
            assert "correlation" in corr
            assert "potential_explanation" in corr

            # Validate correlation details
            corr_detail = corr["correlation"]
            assert "coefficient" in corr_detail
            assert "p_value" in corr_detail
            assert "significance" in corr_detail
            assert "shared_trading_days" in corr_detail

        return {
            "pairs_analyzed": len(data),
            "significant_correlations": len([c for c in data if c["correlation"]["significance"] != "not_significant"]),
            "unexplained": len([c for c in data if c.get("potential_explanation", {}).get("type") == "unexplained"])
        }

    def test_network_analysis(self, politician_ids: List[str]) -> Dict:
        """Test network analysis endpoint."""
        response = requests.get(
            f"{self.base_url}/analytics/network/analysis",
            params={
                "politician_ids": politician_ids,
                "min_correlation": 0.5,
                "cluster_threshold": 0.6
            }
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        assert "network_metrics" in data
        assert "central_politicians" in data
        assert "clusters" in data

        metrics = data["network_metrics"]
        assert "total_nodes" in metrics
        assert "total_edges" in metrics
        assert "density" in metrics
        assert "clustering_coefficient" in metrics

        return {
            "nodes": metrics["total_nodes"],
            "edges": metrics["total_edges"],
            "density": metrics["density"],
            "clusters": len(data["clusters"]),
            "central_politicians": len(data["central_politicians"])
        }

    def test_automated_insights(self, politician_id: str) -> Dict:
        """Test automated insights generation."""
        response = requests.get(
            f"{self.base_url}/analytics/insights/{politician_id}",
            params={
                "min_confidence": 0.6,
                "min_severity": "LOW"
            }
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        assert "insights" in data
        assert "summary" in data
        assert "recommended_actions" in data

        insights = data["insights"]
        if len(insights) > 0:
            insight = insights[0]
            assert "type" in insight
            assert "severity" in insight
            assert "confidence" in insight
            assert "title" in insight
            assert "description" in insight
            assert "evidence" in insight
            assert "recommendations" in insight

        summary = data["summary"]
        assert "overall_risk_score" in summary
        assert "requires_investigation" in summary

        # Count by severity
        severity_counts = {}
        for insight in insights:
            sev = insight["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "total_insights": len(insights),
            "severity_breakdown": severity_counts,
            "risk_score": summary["overall_risk_score"],
            "requires_investigation": summary["requires_investigation"],
            "recommended_actions": len(data["recommended_actions"])
        }

    def test_anomaly_detection(self, politician_id: str) -> Dict:
        """Test anomaly detection endpoint."""
        response = requests.get(
            f"{self.base_url}/analytics/anomaly-detection/{politician_id}",
            params={"sensitivity": 0.7}
        )
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        assert "anomaly_score" in data
        assert "anomaly_level" in data
        assert "detected_anomalies" in data
        assert "contributing_factors" in data
        assert "comparison" in data
        assert "recommendations" in data

        return {
            "anomaly_score": data["anomaly_score"],
            "anomaly_level": data["anomaly_level"],
            "detected_count": len(data["detected_anomalies"]),
            "investigation_priority": data.get("investigation_priority", "N/A")
        }

    def run_comprehensive_tests(self):
        """Run all tests in sequence."""
        print("\n" + "="*80)
        print("ADVANCED ANALYTICS API COMPREHENSIVE TEST SUITE")
        print("="*80 + "\n")

        # Step 1: Get politicians
        self.log("Step 1: Fetching politicians with sufficient data...")
        self.politicians = self.test(
            "Get Politicians",
            self.get_politicians
        )

        if not self.politicians or len(self.politicians) < 2:
            self.log("Insufficient politicians found for testing", "ERROR")
            return

        self.log(f"Found {len(self.politicians)} politicians suitable for analysis")

        # Get IDs for testing
        politician_ids = [p["id"] for p in self.politicians[:5]]  # Use top 5
        test_politician_id = politician_ids[0]

        self.log(f"Using politician: {self.politicians[0].get('name', 'Unknown')}")

        print("\n" + "-"*80)
        print("ENSEMBLE PREDICTION TESTS")
        print("-"*80 + "\n")

        # Step 2: Test ensemble prediction
        self.test(
            "Ensemble Prediction",
            lambda: self.test_ensemble_prediction(test_politician_id)
        )

        print("\n" + "-"*80)
        print("CORRELATION ANALYSIS TESTS")
        print("-"*80 + "\n")

        # Step 3: Test correlation analysis
        self.test(
            "Pairwise Correlation Analysis",
            lambda: self.test_correlation_analysis(politician_ids)
        )

        print("\n" + "-"*80)
        print("NETWORK ANALYSIS TESTS")
        print("-"*80 + "\n")

        # Step 4: Test network analysis
        self.test(
            "Network Analysis",
            lambda: self.test_network_analysis(politician_ids)
        )

        print("\n" + "-"*80)
        print("AUTOMATED INSIGHTS TESTS")
        print("-"*80 + "\n")

        # Step 5: Test automated insights
        self.test(
            "Automated Insights Generation",
            lambda: self.test_automated_insights(test_politician_id)
        )

        print("\n" + "-"*80)
        print("ANOMALY DETECTION TESTS")
        print("-"*80 + "\n")

        # Step 6: Test anomaly detection
        self.test(
            "Anomaly Detection",
            lambda: self.test_anomaly_detection(test_politician_id)
        )

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80 + "\n")

        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({100*passed/total:.1f}%)")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print()

        # Print detailed results
        for result in self.test_results:
            status_icon = "✓" if result["status"] == "PASS" else "✗"
            print(f"{status_icon} {result['name']}: {result['status']}")

            if result["status"] == "PASS" and "details" in result:
                details = result["details"]
                if details:
                    for key, value in details.items():
                        print(f"    {key}: {value}")

            if result["status"] == "ERROR":
                print(f"    Error: {result.get('error', 'Unknown error')}")
            print()

        # Save results to file
        with open("advanced_analytics_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

        self.log("Test results saved to advanced_analytics_test_results.json")

        if passed == total:
            print("\n" + "="*80)
            print("🎉 ALL TESTS PASSED! Advanced Analytics API is fully functional.")
            print("="*80 + "\n")
        else:
            print("\n" + "="*80)
            print(f"⚠️  {failed + errors} tests failed. Review errors above.")
            print("="*80 + "\n")

def main():
    """Main entry point."""
    try:
        tester = AdvancedAnalyticsTest()
        tester.run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
