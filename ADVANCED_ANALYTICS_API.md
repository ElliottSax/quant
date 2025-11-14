# Advanced Analytics API Guide
## Ensemble Models, Correlation Analysis, and Automated Insights

**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api/v1/analytics`
**Purpose**: Multi-model predictions, coordinated trading detection, automated insights
**Status**: Research & Transparency Tool - NOT FOR TRADING

---

## Table of Contents

1. [Overview](#overview)
2. [Ensemble Predictions](#ensemble-predictions)
3. [Correlation Analysis](#correlation-analysis)
4. [Network Analysis](#network-analysis)
5. [Automated Insights](#automated-insights)
6. [Anomaly Detection](#anomaly-detection)
7. [Complete Examples](#complete-examples)
8. [Research Use Cases](#research-use-cases)

---

## Overview

The Advanced Analytics API combines multiple machine learning models to provide:

- **Ensemble Predictions**: Weighted combination of Fourier, HMM, and DTW models
- **Correlation Analysis**: Detect coordinated trading patterns across politicians
- **Network Analysis**: Identify trading clusters and influential actors
- **Automated Insights**: AI-generated findings with severity levels
- **Anomaly Detection**: Flag unusual patterns requiring investigation

### Why Ensemble Learning?

Single models can be fooled or biased. By combining:
- **Fourier Transform** (frequency domain patterns)
- **Hidden Markov Models** (regime detection)
- **Dynamic Time Warping** (historical similarity)

...we achieve more robust, reliable insights with confidence scoring.

---

## Ensemble Predictions

### GET /analytics/ensemble/{politician_id}

Generate combined prediction from all three models with model agreement scoring.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `prediction_horizon` (int, 1-90, default: 30): Days ahead to predict
- `min_model_confidence` (float, 0-1, default: 0.6): Filter low-confidence models

**Response Model**: `EnsemblePredictionResponse`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/analytics/ensemble/{politician_id}?prediction_horizon=30"
```

**Example Response**:
```json
{
  "politician_id": "uuid-here",
  "politician_name": "Nancy Pelosi",
  "analysis_date": "2024-11-14T10:30:00Z",
  "prediction_horizon_days": 30,

  "ensemble_prediction": {
    "prediction_type": "trade_increase",
    "predicted_value": 8.4,
    "confidence": 0.82,
    "model_agreement": 0.89,
    "anomaly_score": 0.12,

    "insights": [
      "Strong consensus: All models predict trade increase",
      "Strong monthly cycle detected (21 days, 92% confidence)",
      "Stable regime: 'Bull Market' expected to continue for 18 days",
      "Strong historical precedent: 87% similar to 2023-06-15"
    ]
  },

  "individual_predictions": [
    {
      "model_name": "fourier",
      "prediction": 9.2,
      "confidence": 0.92,
      "supporting_evidence": {
        "top_cycle_period": 21.3,
        "forecast_std": 1.2
      }
    },
    {
      "model_name": "hmm",
      "prediction": 7.8,
      "confidence": 0.87,
      "supporting_evidence": {
        "current_regime": "Bull Market",
        "expected_duration": 18.4
      }
    },
    {
      "model_name": "dtw",
      "prediction": 8.1,
      "confidence": 0.78,
      "supporting_evidence": {
        "num_matches": 3,
        "top_similarity": 0.87
      }
    }
  ],

  "interpretation": {
    "summary": "High-confidence prediction of increased trading activity",
    "agreement_level": "Strong consensus (89% agreement)",
    "uncertainty": "Low (anomaly score: 12%)",
    "reliability": "High - all models agree on direction and magnitude"
  }
}
```

**Python Example**:
```python
import requests

response = requests.get(
    f"http://localhost:8000/api/v1/analytics/ensemble/{politician_id}",
    params={"prediction_horizon": 30}
)

result = response.json()

print(f"Prediction: {result['ensemble_prediction']['predicted_value']:+.1f} trades")
print(f"Confidence: {result['ensemble_prediction']['confidence']:.1%}")
print(f"Agreement: {result['ensemble_prediction']['model_agreement']:.1%}")

if result['ensemble_prediction']['anomaly_score'] > 0.7:
    print("⚠️ WARNING: High anomaly score - unusual pattern detected")

print("\nInsights:")
for insight in result['ensemble_prediction']['insights']:
    print(f"  • {insight}")
```

**Research Questions This Answers**:
- "What do all models collectively predict?"
- "How much do the models agree?"
- "Is this prediction reliable?"
- "Are there any red flags?"

---

## Correlation Analysis

### GET /analytics/correlation/pairwise

Analyze trading correlations between multiple politicians to detect coordinated patterns.

**Query Parameters**:
- `politician_ids` (list[uuid]): Politicians to analyze (2-20)
- `correlation_threshold` (float, 0-1, default: 0.5): Minimum correlation
- `max_lag_days` (int, 0-60, default: 30): Maximum time lag to test
- `group_by` (enum, optional): party | state | family

**Response Model**: `List[CorrelationPairResponse]`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/analytics/correlation/pairwise?politician_ids=uuid1&politician_ids=uuid2&politician_ids=uuid3&correlation_threshold=0.6"
```

**Example Response**:
```json
[
  {
    "politician1": {
      "id": "uuid1",
      "name": "Nancy Pelosi",
      "party": "Democratic"
    },
    "politician2": {
      "id": "uuid2",
      "name": "Paul Pelosi Jr",
      "party": "Democratic"
    },
    "correlation": {
      "coefficient": 0.87,
      "p_value": 0.0012,
      "significance": "highly_significant",
      "shared_trading_days": 245,
      "optimal_lag_days": 2,
      "interpretation": "Strong positive correlation (politician 1 leads by 2 days)"
    },
    "potential_explanation": {
      "type": "family",
      "confidence": 0.95,
      "evidence": "Same last name: Pelosi"
    }
  },
  {
    "politician1": {
      "id": "uuid2",
      "name": "John Doe",
      "party": "Republican"
    },
    "politician2": {
      "id": "uuid3",
      "name": "Jane Smith",
      "party": "Republican"
    },
    "correlation": {
      "coefficient": 0.73,
      "p_value": 0.0089,
      "significance": "significant",
      "shared_trading_days": 180,
      "optimal_lag_days": 0,
      "interpretation": "Moderate positive correlation (synchronized)"
    },
    "potential_explanation": {
      "type": "party",
      "confidence": 0.70,
      "evidence": "Same party: Republican"
    }
  }
]
```

**Python Example**:
```python
politician_ids = ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]

response = requests.get(
    "http://localhost:8000/api/v1/analytics/correlation/pairwise",
    params={
        "politician_ids": politician_ids,
        "correlation_threshold": 0.6,
        "max_lag_days": 30
    }
)

correlations = response.json()

# Find unexplained correlations (potential coordinated trading)
unexplained = [
    c for c in correlations
    if c['potential_explanation']['type'] == 'unexplained'
    and c['correlation']['coefficient'] > 0.75
]

print(f"Found {len(unexplained)} unexplained high correlations:")
for corr in unexplained:
    print(f"\n{corr['politician1']['name']} <-> {corr['politician2']['name']}")
    print(f"  Correlation: {corr['correlation']['coefficient']:.2f}")
    print(f"  Lag: {corr['correlation']['optimal_lag_days']} days")
    print(f"  P-value: {corr['correlation']['p_value']:.4f}")
```

**Research Questions This Answers**:
- "Do these politicians trade in a coordinated manner?"
- "Who leads and who follows?"
- "Are family members trading together?"
- "Are there party-based trading patterns?"
- "Which correlations lack obvious explanations?"

---

## Network Analysis

### GET /analytics/network/analysis

Build and analyze the trading correlation network to identify clusters and central figures.

**Query Parameters**:
- `politician_ids` (list[uuid]): Politicians to include (3-100)
- `min_correlation` (float, 0-1, default: 0.5): Minimum edge weight
- `cluster_threshold` (float, 0-1, default: 0.6): Clustering threshold
- `include_visualization` (bool, default: false): Return graph data for plotting

**Response Model**: `NetworkAnalysisResponse`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/analytics/network/analysis?politician_ids=uuid1&politician_ids=uuid2&politician_ids=uuid3&min_correlation=0.6"
```

**Example Response**:
```json
{
  "network_metrics": {
    "total_nodes": 15,
    "total_edges": 42,
    "density": 0.42,
    "clustering_coefficient": 0.68,
    "average_path_length": 2.3,
    "connected_components": 2
  },

  "central_politicians": [
    {
      "politician_id": "uuid1",
      "name": "Nancy Pelosi",
      "centrality_score": 0.89,
      "connections": 12,
      "interpretation": "Highly influential - trades correlate with many others"
    },
    {
      "politician_id": "uuid2",
      "name": "Mitch McConnell",
      "centrality_score": 0.76,
      "connections": 9,
      "interpretation": "Central figure - well-connected trading patterns"
    }
  ],

  "clusters": [
    {
      "cluster_id": 1,
      "size": 7,
      "politicians": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5", "uuid6", "uuid7"],
      "avg_correlation": 0.78,
      "common_characteristics": {
        "dominant_party": "Democratic",
        "party_purity": 0.86,
        "avg_trade_count": 65,
        "common_sectors": ["Technology", "Finance"]
      },
      "interpretation": "Tight-knit group with synchronized trading patterns"
    },
    {
      "cluster_id": 2,
      "size": 5,
      "politicians": ["uuid8", "uuid9", "uuid10", "uuid11", "uuid12"],
      "avg_correlation": 0.71,
      "common_characteristics": {
        "dominant_party": "Republican",
        "party_purity": 1.0,
        "avg_trade_count": 48,
        "common_sectors": ["Energy", "Finance"]
      },
      "interpretation": "Distinct group with shared trading behavior"
    }
  ],

  "anomalous_connections": [
    {
      "politician1": "uuid3",
      "politician2": "uuid9",
      "correlation": 0.82,
      "why_anomalous": "High correlation despite different parties, states, and committees"
    }
  ],

  "summary": "Network shows clear clustering by party affiliation with two distinct groups..."
}
```

**Python Example**:
```python
response = requests.get(
    "http://localhost:8000/api/v1/analytics/network/analysis",
    params={
        "politician_ids": politician_ids,
        "min_correlation": 0.6,
        "cluster_threshold": 0.65
    }
)

network = response.json()

print(f"Network Density: {network['network_metrics']['density']:.1%}")
print(f"Found {len(network['clusters'])} distinct trading clusters")

print("\nMost Influential:")
for politician in network['central_politicians'][:3]:
    print(f"  {politician['name']}: {politician['centrality_score']:.2f}")

print("\nClusters:")
for cluster in network['clusters']:
    print(f"\n  Cluster {cluster['cluster_id']}: {cluster['size']} politicians")
    print(f"    Avg Correlation: {cluster['avg_correlation']:.1%}")
    print(f"    Party: {cluster['common_characteristics']['dominant_party']}")

if network['anomalous_connections']:
    print("\n⚠️ Anomalous Connections Found:")
    for conn in network['anomalous_connections']:
        print(f"  {conn['politician1']} <-> {conn['politician2']}")
        print(f"    {conn['why_anomalous']}")
```

**Research Questions This Answers**:
- "How connected is the trading network?"
- "Who are the most influential traders?"
- "Are there distinct trading groups?"
- "Do clusters align with party/state/committee?"
- "Are there unexpected connections?"

---

## Automated Insights

### GET /analytics/insights/{politician_id}

Generate comprehensive automated insights using all analytics tools.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `min_confidence` (float, 0-1, default: 0.6): Filter low-confidence insights
- `min_severity` (enum, default: INFO): CRITICAL | HIGH | MEDIUM | LOW | INFO
- `include_recommendations` (bool, default: true): Include action items

**Response Model**: `ComprehensiveInsightsResponse`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/analytics/insights/{politician_id}?min_severity=MEDIUM"
```

**Example Response**:
```json
{
  "politician_id": "uuid-here",
  "politician_name": "Nancy Pelosi",
  "analysis_date": "2024-11-14T10:30:00Z",
  "total_insights": 12,

  "insights": [
    {
      "type": "ANOMALY",
      "severity": "CRITICAL",
      "confidence": 0.94,
      "title": "Unusual Trading Spike Detected",
      "description": "Trading volume increased 420% in the last 7 days compared to 90-day average. This is the 99th percentile of historical activity.",
      "evidence": {
        "recent_trades": 28,
        "historical_avg": 5.2,
        "percentile": 0.99,
        "timeframe": "7_days"
      },
      "recommendations": [
        "Investigate trades for potential policy conflicts",
        "Review upcoming legislative calendar",
        "Check for recent committee assignments",
        "Verify disclosure timeline compliance"
      ],
      "context": {
        "related_events": ["Upcoming tech regulation vote"],
        "sector_focus": ["Technology"],
        "timing_notes": "Activity preceded policy announcement by 3 days"
      }
    },
    {
      "type": "PATTERN",
      "severity": "HIGH",
      "confidence": 0.89,
      "title": "Consistent 21-Day Trading Cycle",
      "description": "Strong evidence of trading on a 21-day cycle (monthly), with 89% confidence. This pattern has persisted for 580 days.",
      "evidence": {
        "cycle_period": 21.3,
        "cycle_confidence": 0.89,
        "duration_days": 580,
        "strength": 0.86
      },
      "recommendations": [
        "Compare cycle timing with earnings calendar",
        "Check alignment with committee meeting schedule",
        "Review for potential insider information timing"
      ]
    },
    {
      "type": "CORRELATION",
      "severity": "HIGH",
      "confidence": 0.87,
      "title": "Strong Correlation with Family Member",
      "description": "Trading patterns show 87% correlation with Paul Pelosi Jr (family member) with 2-day lag, suggesting coordinated activity.",
      "evidence": {
        "correlation": 0.87,
        "p_value": 0.0012,
        "lag_days": 2,
        "relationship": "family"
      },
      "recommendations": [
        "Review family trading policies",
        "Verify independent decision-making",
        "Check for shared information sources"
      ]
    },
    {
      "type": "PREDICTION",
      "severity": "MEDIUM",
      "confidence": 0.82,
      "title": "Increased Activity Predicted",
      "description": "Ensemble model predicts 8.4 additional trades in the next 30 days (82% confidence). All three models agree on direction.",
      "evidence": {
        "predicted_trades": 8.4,
        "ensemble_confidence": 0.82,
        "model_agreement": 0.89,
        "horizon_days": 30
      },
      "recommendations": [
        "Monitor for predicted activity",
        "Track disclosure timeliness",
        "Compare actual vs predicted for validation"
      ]
    },
    {
      "type": "REGIME",
      "severity": "MEDIUM",
      "confidence": 0.87,
      "title": "Currently in Bull Market Regime",
      "description": "HMM analysis indicates 'Bull Market' regime with high trading frequency. Expected to persist for 18 days.",
      "evidence": {
        "current_regime": "Bull Market",
        "regime_confidence": 0.87,
        "expected_duration": 18.4,
        "avg_return": 0.52
      },
      "recommendations": [
        "Normal behavior for this regime",
        "Monitor for regime change signals",
        "Compare with market conditions"
      ]
    }
  ],

  "summary": {
    "critical_findings": 1,
    "high_priority": 2,
    "medium_priority": 2,
    "low_priority": 4,
    "info": 3,
    "overall_risk_score": 0.68,
    "requires_investigation": true,
    "investigation_priority": "High"
  },

  "recommended_actions": [
    "Immediate investigation of 420% trading spike",
    "Review family trading coordination policies",
    "Verify timing of trades relative to policy announcements",
    "Monitor predicted activity over next 30 days"
  ]
}
```

**Python Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/analytics/insights/{politician_id}",
    params={
        "min_confidence": 0.7,
        "min_severity": "MEDIUM"
    }
)

result = response.json()

# Filter critical insights
critical = [i for i in result['insights'] if i['severity'] == 'CRITICAL']

if critical:
    print(f"⚠️ {len(critical)} CRITICAL INSIGHTS FOUND\n")
    for insight in critical:
        print(f"Title: {insight['title']}")
        print(f"Description: {insight['description']}")
        print(f"Confidence: {insight['confidence']:.1%}\n")
        print("Recommendations:")
        for rec in insight['recommendations']:
            print(f"  • {rec}")
        print()

# Overall risk assessment
if result['summary']['requires_investigation']:
    print(f"⚠️ Investigation Required: {result['summary']['investigation_priority']} Priority")
    print(f"Overall Risk Score: {result['summary']['overall_risk_score']:.1%}")
```

**Research Questions This Answers**:
- "What are the most important findings?"
- "What should investigators focus on?"
- "Are there any red flags?"
- "What patterns exist across all analyses?"
- "What actions should be taken?"

---

## Anomaly Detection

### GET /analytics/anomaly-detection/{politician_id}

Detect anomalous trading patterns that deviate significantly from historical norms.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `sensitivity` (float, 0-1, default: 0.7): Detection sensitivity
- `lookback_days` (int, 30-365, default: 90): Historical comparison window

**Response Model**: `AnomalyDetectionResponse`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/analytics/anomaly-detection/{politician_id}?sensitivity=0.8"
```

**Example Response**:
```json
{
  "politician_id": "uuid-here",
  "politician_name": "Nancy Pelosi",
  "analysis_date": "2024-11-14T10:30:00Z",
  "anomaly_score": 0.82,
  "anomaly_level": "HIGH",

  "detected_anomalies": [
    {
      "type": "volume_spike",
      "severity": "HIGH",
      "score": 0.94,
      "description": "Trading volume 420% above normal",
      "timeframe": "last_7_days",
      "statistical_significance": {
        "z_score": 3.8,
        "p_value": 0.0001,
        "percentile": 0.99
      }
    },
    {
      "type": "unusual_timing",
      "severity": "MEDIUM",
      "score": 0.71,
      "description": "Trades occurring at unusual times (outside normal patterns)",
      "timeframe": "last_14_days",
      "details": "Trades made on days with no historical precedent"
    },
    {
      "type": "model_disagreement",
      "severity": "MEDIUM",
      "score": 0.68,
      "description": "Low agreement among prediction models (38% agreement)",
      "explanation": "Models cannot converge on expected pattern - suggests unprecedented behavior"
    }
  ],

  "contributing_factors": [
    "Recent trading volume far exceeds historical norms",
    "No similar patterns found in DTW historical search",
    "Current behavior not explained by any known regime",
    "Timing does not align with any detected cycles"
  ],

  "comparison": {
    "current_period": {
      "trades": 28,
      "avg_value": 145000,
      "sectors": ["Technology", "Finance"]
    },
    "historical_baseline": {
      "avg_trades": 5.2,
      "avg_value": 82000,
      "typical_sectors": ["Technology", "Healthcare"]
    },
    "deviation": {
      "trade_count_ratio": 5.38,
      "value_ratio": 1.77,
      "sector_shift": "Increased Finance exposure"
    }
  },

  "recommendations": [
    "Investigate triggers for volume spike",
    "Review recent legislative activity",
    "Check disclosure compliance",
    "Compare with market events",
    "Monitor for continued anomalous behavior"
  ],

  "investigation_priority": "HIGH"
}
```

**Python Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/analytics/anomaly-detection/{politician_id}",
    params={"sensitivity": 0.75}
)

result = response.json()

if result['anomaly_level'] in ['HIGH', 'CRITICAL']:
    print(f"⚠️ {result['anomaly_level']} ANOMALY DETECTED")
    print(f"Anomaly Score: {result['anomaly_score']:.1%}\n")

    print("Detected Anomalies:")
    for anomaly in result['detected_anomalies']:
        print(f"\n  • {anomaly['type'].upper()}")
        print(f"    {anomaly['description']}")
        print(f"    Severity: {anomaly['severity']} (Score: {anomaly['score']:.1%})")

    print(f"\nInvestigation Priority: {result['investigation_priority']}")
```

**Research Questions This Answers**:
- "Is this behavior unusual?"
- "How unusual is it statistically?"
- "What specifically is anomalous?"
- "How urgent is investigation?"
- "What should investigators examine?"

---

## Complete Examples

### Example 1: Full Research Pipeline

```python
import requests
import pandas as pd
from typing import List, Dict

BASE_URL = "http://localhost:8000/api/v1"

class ResearchPipeline:
    def __init__(self):
        self.base_url = BASE_URL

    def get_politicians(self, min_trades: int = 50) -> List[Dict]:
        """Get politicians with sufficient data."""
        response = requests.get(
            f"{self.base_url}/patterns/politicians",
            params={"min_trades": min_trades}
        )
        return response.json()

    def analyze_politician(self, politician_id: str) -> Dict:
        """Run complete analysis on one politician."""
        results = {}

        # 1. Ensemble prediction
        response = requests.get(f"{self.base_url}/analytics/ensemble/{politician_id}")
        results['ensemble'] = response.json()

        # 2. Automated insights
        response = requests.get(
            f"{self.base_url}/analytics/insights/{politician_id}",
            params={"min_severity": "MEDIUM"}
        )
        results['insights'] = response.json()

        # 3. Anomaly detection
        response = requests.get(f"{self.base_url}/analytics/anomaly-detection/{politician_id}")
        results['anomalies'] = response.json()

        return results

    def compare_politicians(self, politician_ids: List[str]) -> Dict:
        """Compare multiple politicians."""
        results = {}

        # Correlation analysis
        response = requests.get(
            f"{self.base_url}/analytics/correlation/pairwise",
            params={"politician_ids": politician_ids, "correlation_threshold": 0.6}
        )
        results['correlations'] = response.json()

        # Network analysis
        response = requests.get(
            f"{self.base_url}/analytics/network/analysis",
            params={"politician_ids": politician_ids, "min_correlation": 0.6}
        )
        results['network'] = response.json()

        return results

    def generate_report(self, politician_id: str) -> str:
        """Generate comprehensive markdown report."""
        analysis = self.analyze_politician(politician_id)

        report = f"# Trading Analysis Report\n\n"
        report += f"**Politician**: {analysis['ensemble']['politician_name']}\n"
        report += f"**Date**: {analysis['ensemble']['analysis_date']}\n\n"

        # Anomaly section
        anomaly = analysis['anomalies']
        report += f"## Anomaly Score: {anomaly['anomaly_score']:.1%} ({anomaly['anomaly_level']})\n\n"

        if anomaly['detected_anomalies']:
            report += "### Detected Anomalies\n\n"
            for a in anomaly['detected_anomalies']:
                report += f"- **{a['type']}**: {a['description']} (Severity: {a['severity']})\n"

        # Critical insights
        critical_insights = [
            i for i in analysis['insights']['insights']
            if i['severity'] in ['CRITICAL', 'HIGH']
        ]

        if critical_insights:
            report += f"\n## Critical Findings ({len(critical_insights)})\n\n"
            for insight in critical_insights:
                report += f"### {insight['title']}\n\n"
                report += f"{insight['description']}\n\n"
                report += f"**Confidence**: {insight['confidence']:.1%}\n\n"
                report += "**Recommendations**:\n"
                for rec in insight['recommendations']:
                    report += f"- {rec}\n"
                report += "\n"

        # Predictions
        ensemble = analysis['ensemble']['ensemble_prediction']
        report += f"## 30-Day Prediction\n\n"
        report += f"- **Predicted Change**: {ensemble['predicted_value']:+.1f} trades\n"
        report += f"- **Confidence**: {ensemble['confidence']:.1%}\n"
        report += f"- **Model Agreement**: {ensemble['model_agreement']:.1%}\n\n"

        return report

# Use the pipeline
pipeline = ResearchPipeline()

# Get top traders
politicians = pipeline.get_politicians(min_trades=50)
print(f"Found {len(politicians)} politicians with sufficient data")

# Analyze top 5
for pol in politicians[:5]:
    print(f"\nAnalyzing {pol['name']}...")
    analysis = pipeline.analyze_politician(pol['id'])

    # Check for red flags
    if analysis['anomalies']['anomaly_level'] in ['HIGH', 'CRITICAL']:
        print(f"  ⚠️ HIGH ANOMALY: {analysis['anomalies']['anomaly_score']:.1%}")

    critical = [i for i in analysis['insights']['insights'] if i['severity'] == 'CRITICAL']
    if critical:
        print(f"  ⚠️ {len(critical)} CRITICAL INSIGHTS")

    # Generate report
    report = pipeline.generate_report(pol['id'])
    with open(f"report_{pol['name'].replace(' ', '_')}.md", "w") as f:
        f.write(report)

# Compare all 5
print("\nRunning comparative analysis...")
top_ids = [p['id'] for p in politicians[:5]]
comparison = pipeline.compare_politicians(top_ids)

print(f"\nNetwork Density: {comparison['network']['network_metrics']['density']:.1%}")
print(f"Clusters Found: {len(comparison['network']['clusters'])}")

# Find unexplained correlations
unexplained = [
    c for c in comparison['correlations']
    if c['potential_explanation']['type'] == 'unexplained'
    and c['correlation']['coefficient'] > 0.7
]

if unexplained:
    print(f"\n⚠️ Found {len(unexplained)} unexplained high correlations:")
    for corr in unexplained:
        print(f"  {corr['politician1']['name']} <-> {corr['politician2']['name']}")
        print(f"    Correlation: {corr['correlation']['coefficient']:.2f}")
```

### Example 2: Real-Time Monitoring

```python
import time
from datetime import datetime

class TradingMonitor:
    def __init__(self, politician_ids: List[str]):
        self.politician_ids = politician_ids
        self.alert_thresholds = {
            'anomaly_score': 0.7,
            'critical_insights': 1,
            'correlation_threshold': 0.8
        }

    def check_anomalies(self):
        """Check all politicians for anomalies."""
        alerts = []

        for pol_id in self.politician_ids:
            response = requests.get(f"{BASE_URL}/analytics/anomaly-detection/{pol_id}")
            result = response.json()

            if result['anomaly_score'] > self.alert_thresholds['anomaly_score']:
                alerts.append({
                    'politician': result['politician_name'],
                    'type': 'anomaly',
                    'score': result['anomaly_score'],
                    'level': result['anomaly_level'],
                    'details': result['detected_anomalies']
                })

        return alerts

    def check_insights(self):
        """Check for critical insights."""
        alerts = []

        for pol_id in self.politician_ids:
            response = requests.get(
                f"{BASE_URL}/analytics/insights/{pol_id}",
                params={"min_severity": "CRITICAL"}
            )
            result = response.json()

            critical = [i for i in result['insights'] if i['severity'] == 'CRITICAL']

            if len(critical) >= self.alert_thresholds['critical_insights']:
                alerts.append({
                    'politician': result['politician_name'],
                    'type': 'critical_insight',
                    'count': len(critical),
                    'insights': critical
                })

        return alerts

    def run_monitoring_loop(self, interval_minutes: int = 60):
        """Run continuous monitoring."""
        print(f"Starting monitoring for {len(self.politician_ids)} politicians...")
        print(f"Checking every {interval_minutes} minutes")

        while True:
            print(f"\n[{datetime.now()}] Running checks...")

            # Check anomalies
            anomaly_alerts = self.check_anomalies()
            if anomaly_alerts:
                print(f"\n⚠️ {len(anomaly_alerts)} ANOMALY ALERTS")
                for alert in anomaly_alerts:
                    print(f"  {alert['politician']}: {alert['score']:.1%} ({alert['level']})")

            # Check critical insights
            insight_alerts = self.check_insights()
            if insight_alerts:
                print(f"\n⚠️ {len(insight_alerts)} CRITICAL INSIGHT ALERTS")
                for alert in insight_alerts:
                    print(f"  {alert['politician']}: {alert['count']} critical findings")

            if not anomaly_alerts and not insight_alerts:
                print("  ✓ No alerts")

            # Wait for next check
            time.sleep(interval_minutes * 60)

# Run monitor
monitor = TradingMonitor(top_politician_ids)
monitor.run_monitoring_loop(interval_minutes=60)
```

---

## Research Use Cases

### 1. Academic Research

**Question**: "Do politicians trade on cyclical patterns that align with earnings seasons?"

```python
# Get all politicians with sufficient data
politicians = requests.get(f"{BASE_URL}/patterns/politicians", params={"min_trades": 50}).json()

cycle_results = []

for pol in politicians:
    # Get ensemble prediction (includes Fourier analysis)
    response = requests.get(f"{BASE_URL}/analytics/ensemble/{pol['id']}")
    result = response.json()

    # Extract dominant cycle
    fourier_pred = next(
        p for p in result['individual_predictions']
        if p['model_name'] == 'fourier'
    )

    cycle_period = fourier_pred['supporting_evidence'].get('top_cycle_period')

    if cycle_period:
        cycle_results.append({
            'politician': pol['name'],
            'party': pol['party'],
            'cycle_period': cycle_period,
            'confidence': fourier_pred['confidence']
        })

# Analysis
df = pd.DataFrame(cycle_results)

# Quarterly earnings cycle is ~90 days
quarterly_traders = df[df['cycle_period'].between(80, 100)]
print(f"{len(quarterly_traders)} politicians trade on ~quarterly cycles")

# Monthly options expiry is ~21-30 days
monthly_traders = df[df['cycle_period'].between(18, 32)]
print(f"{len(monthly_traders)} politicians trade on ~monthly cycles")
```

### 2. Investigative Journalism

**Question**: "Which politicians show coordinated trading with no obvious explanation?"

```python
# Get all politicians
all_pols = requests.get(f"{BASE_URL}/patterns/politicians", params={"min_trades": 30}).json()
all_ids = [p['id'] for p in all_pols]

# Analyze correlations in batches (max 20 at a time)
batch_size = 20
unexplained_high_corr = []

for i in range(0, len(all_ids), batch_size):
    batch = all_ids[i:i+batch_size]

    response = requests.get(
        f"{BASE_URL}/analytics/correlation/pairwise",
        params={
            "politician_ids": batch,
            "correlation_threshold": 0.7
        }
    )

    correlations = response.json()

    # Filter for unexplained
    unexplained = [
        c for c in correlations
        if c['potential_explanation']['type'] == 'unexplained'
    ]

    unexplained_high_corr.extend(unexplained)

# Sort by correlation strength
unexplained_high_corr.sort(key=lambda x: x['correlation']['coefficient'], reverse=True)

print(f"Found {len(unexplained_high_corr)} unexplained high correlations")
print("\nTop 10 Most Suspicious:")
for corr in unexplained_high_corr[:10]:
    print(f"\n{corr['politician1']['name']} <-> {corr['politician2']['name']}")
    print(f"  Correlation: {corr['correlation']['coefficient']:.2f}")
    print(f"  P-value: {corr['correlation']['p_value']:.4f}")
    print(f"  Lag: {corr['correlation']['optimal_lag_days']} days")
```

### 3. Compliance Monitoring

**Question**: "Which politicians require immediate investigation based on all analytics?"

```python
# Get all politicians
politicians = requests.get(f"{BASE_URL}/patterns/politicians", params={"min_trades": 30}).json()

high_priority = []

for pol in politicians:
    # Get comprehensive insights
    response = requests.get(
        f"{BASE_URL}/analytics/insights/{pol['id']}",
        params={"min_confidence": 0.7}
    )
    result = response.json()

    # Check if investigation required
    if result['summary']['requires_investigation']:
        priority = result['summary']['investigation_priority']
        risk_score = result['summary']['overall_risk_score']
        critical_count = result['summary']['critical_findings']

        high_priority.append({
            'name': pol['name'],
            'party': pol['party'],
            'priority': priority,
            'risk_score': risk_score,
            'critical_findings': critical_count,
            'summary': result['recommended_actions']
        })

# Sort by risk score
high_priority.sort(key=lambda x: x['risk_score'], reverse=True)

print(f"🚨 {len(high_priority)} Politicians Require Investigation\n")

for i, pol in enumerate(high_priority[:10], 1):
    print(f"{i}. {pol['name']} ({pol['party']})")
    print(f"   Priority: {pol['priority']}")
    print(f"   Risk Score: {pol['risk_score']:.1%}")
    print(f"   Critical Findings: {pol['critical_findings']}")
    print(f"   Actions:")
    for action in pol['summary'][:3]:
        print(f"     • {action}")
    print()
```

---

## Best Practices

1. **Use Caching**: Results are cached for 1 hour. Repeated requests are fast.

2. **Batch Operations**: For multi-politician analysis, use batch endpoints or parallelize requests.

3. **Interpret Confidence Scores**:
   - >0.85: High confidence
   - 0.7-0.85: Moderate confidence
   - <0.7: Low confidence (use with caution)

4. **Check Model Agreement**: Low agreement suggests uncertainty or unprecedented patterns.

5. **Combine Multiple Signals**: Don't rely on single metric. Use ensemble + insights + anomaly detection together.

6. **Monitor Anomaly Scores**: Scores >0.7 warrant investigation.

7. **Verify Correlations**: High correlation ≠ causation. Look for explanatory factors.

---

## Limitations

1. **Not Predictive Trading Signals**: This is a research tool, not financial advice.

2. **Past Patterns ≠ Future Behavior**: Historical analysis doesn't guarantee future patterns.

3. **Data Quality**: Analysis quality depends on complete, accurate trade disclosures.

4. **Correlation vs Causation**: High correlations may be coincidental.

5. **Model Assumptions**: Each model has biases and limitations.

6. **Computational Intensive**: Large-scale analyses may take time.

---

## Support

- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **Research API Guide**: See `RESEARCH_API_GUIDE.md`
- **GitHub**: https://github.com/ElliottSax/quant
- **Issues**: https://github.com/ElliottSax/quant/issues

---

**Last Updated**: November 14, 2025
**API Version**: 1.0.0
**Status**: Production Ready - Research Use Only
