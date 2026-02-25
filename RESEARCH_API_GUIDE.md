# Research API Guide
## Pattern Analysis & Data Export Endpoints

**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api/v1`
**Purpose**: Academic research, transparency, public oversight
**Not for**: Trading signals, financial advice

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pattern Analysis Endpoints](#pattern-analysis-endpoints)
3. [Data Export Endpoints](#data-export-endpoints)
4. [Authentication](#authentication)
5. [Rate Limits](#rate-limits)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

---

## Quick Start

### 1. Find Politicians with Data

```bash
curl "http://localhost:8000/api/v1/patterns/politicians?min_trades=30"
```

**Response**:
```json
[
  {
    "id": "uuid-here",
    "name": "Nancy Pelosi",
    "party": "Democratic",
    "state": "CA",
    "chamber": "house",
    "trade_count": 80,
    "first_trade": "2022-02-04",
    "last_trade": "2024-11-04",
    "days_active": 1005,
    "suitable_for_analysis": {
      "fourier": true,
      "hmm": false,
      "dtw": false
    }
  }
]
```

### 2. Run Pattern Analysis

```bash
# Fourier cycle detection
curl "http://localhost:8000/api/v1/patterns/analyze/{politician_id}/fourier"

# HMM regime detection
curl "http://localhost:8000/api/v1/patterns/analyze/{politician_id}/regime"

# DTW pattern matching
curl "http://localhost:8000/api/v1/patterns/analyze/{politician_id}/patterns"

# All three analyses
curl "http://localhost:8000/api/v1/patterns/analyze/{politician_id}/comprehensive"
```

### 3. Export Data

```bash
# Export trades as CSV
curl "http://localhost:8000/api/v1/export/trades/{politician_id}?format=csv" > trades.csv

# Export analysis as JSON
curl "http://localhost:8000/api/v1/export/analysis/{politician_id}?format=json" > analysis.json

# Export all politicians
curl "http://localhost:8000/api/v1/export/batch/all-politicians?format=csv" > all_trades.csv
```

---

## Pattern Analysis Endpoints

### GET /patterns/politicians

List all politicians with trading data.

**Query Parameters**:
- `min_trades` (int, default: 10): Minimum trades required

**Response**: Array of politicians with suitability indicators

**Example**:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/patterns/politicians",
    params={"min_trades": 50}
)

politicians = response.json()
for pol in politicians:
    print(f"{pol['name']}: {pol['trade_count']} trades")
```

---

### GET /patterns/analyze/{politician_id}/fourier

Detect cyclical trading patterns using Fourier Transform.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `min_strength` (float, 0-1, default: 0.05): Minimum cycle strength
- `min_confidence` (float, 0-1, default: 0.6): Minimum confidence
- `include_forecast` (bool, default: true): Include 30-day forecast

**Response Model**: `FourierAnalysisResponse`

**Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/patterns/analyze/{politician_id}/fourier",
    params={
        "min_confidence": 0.7,
        "include_forecast": True
    }
)

analysis = response.json()
print(f"Found {len(analysis['dominant_cycles'])} cycles")

for cycle in analysis['dominant_cycles']:
    print(f"  {cycle['category']}: {cycle['period_days']:.1f} days "
          f"(confidence: {cycle['confidence']:.1%})")
```

**Research Questions This Answers**:
- "Does this politician trade on a regular schedule?"
- "What is the dominant trading frequency?"
- "Are cycles aligned with earnings seasons?"
- "How predictable is the trading pattern?"

**Output Fields**:
```json
{
  "politician_id": "uuid",
  "politician_name": "string",
  "analysis_date": "datetime",
  "total_trades": 80,
  "date_range_start": "2022-02-04",
  "date_range_end": "2024-11-04",
  "dominant_cycles": [
    {
      "period_days": 21.3,
      "strength": 0.856,
      "confidence": 0.92,
      "category": "monthly",
      "frequency": 0.0469
    }
  ],
  "total_cycles_found": 5,
  "forecast_30d": [0.1, 0.3, ...],
  "summary": "Found 5 significant cycles:\n\n1. Monthly: 21.3 days..."
}
```

---

### GET /patterns/analyze/{politician_id}/regime

Identify trading regimes using Hidden Markov Models.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `n_states` (int, 2-6, default: 4): Number of regimes to detect

**Response Model**: `RegimeAnalysisResponse`

**Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/patterns/analyze/{politician_id}/regime",
    params={"n_states": 3}
)

analysis = response.json()
print(f"Current regime: {analysis['current_regime_name']}")
print(f"Confidence: {analysis['regime_confidence']:.1%}")
print(f"Expected duration: {analysis['expected_duration_days']:.1f} days")

print("\nAll regimes:")
for regime in analysis['regimes']:
    print(f"  {regime['name']}: {regime['frequency']:.1%} of time")
```

**Research Questions This Answers**:
- "What is the current trading regime?"
- "How frequently does behavior change?"
- "What triggers regime transitions?"
- "Is the politician defensive or aggressive now?"

**Output Fields**:
```json
{
  "politician_id": "uuid",
  "politician_name": "string",
  "current_regime": 2,
  "current_regime_name": "Bull Market",
  "regime_confidence": 0.87,
  "expected_duration_days": 18.4,
  "regimes": [
    {
      "regime_id": 0,
      "name": "High Activity",
      "avg_return": 0.52,
      "volatility": 0.89,
      "frequency": 0.42,
      "sample_size": 120
    }
  ],
  "transition_probabilities": {
    "High Activity": 0.15,
    "Low Activity": 0.03
  },
  "summary": "Current Regime: Bull Market (State 2)..."
}
```

---

### GET /patterns/analyze/{politician_id}/patterns

Find similar historical patterns using Dynamic Time Warping.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `window_size` (int, 7-90, default: 30): Pattern window in days
- `top_k` (int, 1-20, default: 5): Number of matches to return
- `similarity_threshold` (float, 0-1, default: 0.6): Min similarity

**Response Model**: `DTWAnalysisResponse`

**Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/patterns/analyze/{politician_id}/patterns",
    params={
        "window_size": 30,
        "top_k": 10,
        "similarity_threshold": 0.7
    }
)

analysis = response.json()
print(f"Found {analysis['matches_found']} similar periods")
print(f"30-day prediction: {analysis['prediction_30d']:+.1f} trades")

print("\nTop matches:")
for match in analysis['top_matches'][:3]:
    print(f"  {match['match_date']}: {match['similarity_score']:.1%} similarity")
    if match['outcome_30d_trades']:
        print(f"    → {match['outcome_30d_trades']:+.1f} trades in next 30 days")
```

**Research Questions This Answers**:
- "Has this pattern occurred before?"
- "What happened after similar patterns?"
- "Is current behavior unusual?"
- "Can we predict future trading?"

---

### GET /patterns/analyze/{politician_id}/comprehensive

Run all three analyses simultaneously.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Response Model**: `ComprehensiveAnalysisResponse`

**Example**:
```python
response = requests.get(
    f"http://localhost:8000/api/v1/patterns/analyze/{politician_id}/comprehensive"
)

analysis = response.json()

# Access all three analyses
fourier = analysis['fourier']
hmm = analysis['hmm']
dtw = analysis['dtw']

# Key insights
print("Key Insights:")
for insight in analysis['key_insights']:
    print(f"  • {insight}")
```

**Research Questions This Answers**:
- "Give me the complete picture"
- "What's the comprehensive trading profile?"
- "How do all models agree/disagree?"

---

### GET /patterns/compare

Compare patterns across multiple politicians.

**Query Parameters**:
- `politician_ids` (list[uuid]): Politicians to compare (max 10)
- `analysis_type` (enum): fourier | hmm | dtw | comprehensive

**Example**:
```python
response = requests.get(
    "http://localhost:8000/api/v1/patterns/compare",
    params={
        "politician_ids": [id1, id2, id3],
        "analysis_type": "fourier"
    }
)

comparison = response.json()

# Check for coordinated cycles
if 'cycle_correlation' in comparison:
    cycles = comparison['cycle_correlation']['cycles']
    print(f"Cycle periods: {cycles}")
    print(comparison['cycle_correlation']['interpretation'])
```

**Research Questions This Answers**:
- "Do these politicians trade in sync?"
- "Are there party-based patterns?"
- "Who has similar behavior?"

---

## Data Export Endpoints

### GET /export/trades/{politician_id}

Export raw trade data.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `format` (enum): json | csv | xlsx | md
- `start_date` (date, optional): Filter start
- `end_date` (date, optional): Filter end

**Example**:
```python
# CSV export
response = requests.get(
    f"http://localhost:8000/api/v1/export/trades/{politician_id}",
    params={"format": "csv"}
)

with open("trades.csv", "wb") as f:
    f.write(response.content)

# Excel export with metadata
response = requests.get(
    f"http://localhost:8000/api/v1/export/trades/{politician_id}",
    params={"format": "xlsx"}
)

with open("trades.xlsx", "wb") as f:
    f.write(response.content)
```

---

### GET /export/analysis/{politician_id}

Export pattern analysis results.

**Path Parameters**:
- `politician_id` (uuid): Politician identifier

**Query Parameters**:
- `format` (enum): json | md
- `include_fourier` (bool, default: true)
- `include_hmm` (bool, default: true)
- `include_dtw` (bool, default: true)

**Example**:
```python
# JSON export for programmatic use
response = requests.get(
    f"http://localhost:8000/api/v1/export/analysis/{politician_id}",
    params={
        "format": "json",
        "include_fourier": True,
        "include_hmm": True,
        "include_dtw": False
    }
)

with open("analysis.json", "w") as f:
    json.dump(response.json(), f, indent=2)

# Markdown report for reading
response = requests.get(
    f"http://localhost:8000/api/v1/export/analysis/{politician_id}",
    params={"format": "md"}
)

with open("report.md", "w") as f:
    f.write(response.text)
```

---

### GET /export/batch/all-politicians

Batch export all politician data.

**Query Parameters**:
- `format` (enum): csv | json
- `min_trades` (int, default: 30): Minimum trades

**Example**:
```python
# Export complete dataset
response = requests.get(
    "http://localhost:8000/api/v1/export/batch/all-politicians",
    params={
        "format": "csv",
        "min_trades": 50
    }
)

# This may take several minutes
with open("all_politicians.csv", "wb") as f:
    f.write(response.content)

# Load into pandas
import pandas as pd
df = pd.read_csv("all_politicians.csv")
print(f"Loaded {len(df)} trades")
```

---

## Authentication

Currently, the research API is publicly accessible. Future versions may require API keys for rate limiting.

```python
# Future authentication (not yet implemented)
headers = {
    "Authorization": "Bearer YOUR_API_KEY"
}

response = requests.get(url, headers=headers)
```

---

## Rate Limits

**Current Limits**:
- 60 requests per minute
- 1000 requests per hour

**Headers**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699564800
```

**429 Response**:
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Examples

### Complete Research Workflow

```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/api/v1"

# 1. Find politicians
response = requests.get(f"{BASE_URL}/patterns/politicians", params={"min_trades": 50})
politicians = response.json()

# 2. Analyze each
results = {}
for pol in politicians[:5]:  # Top 5
    pol_id = pol['id']

    # Run comprehensive analysis
    response = requests.get(f"{BASE_URL}/patterns/analyze/{pol_id}/comprehensive")
    results[pol['name']] = response.json()

    # Export raw data
    response = requests.get(f"{BASE_URL}/export/trades/{pol_id}", params={"format": "csv"})
    with open(f"data_{pol['name'].replace(' ', '_')}.csv", "wb") as f:
        f.write(response.content)

# 3. Compare top traders
top_ids = [p['id'] for p in politicians[:3]]
response = requests.get(
    f"{BASE_URL}/patterns/compare",
    params={"politician_ids": top_ids, "analysis_type": "fourier"}
)
comparison = response.json()

print("Cycle comparison:")
print(comparison['cycle_correlation'])
```

### Async Batch Processing

```python
import asyncio
import aiohttp

async def analyze_politician(session, pol_id):
    url = f"http://localhost:8000/api/v1/patterns/analyze/{pol_id}/fourier"
    async with session.get(url) as response:
        return await response.json()

async def batch_analyze(politician_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_politician(session, pid) for pid in politician_ids]
        results = await asyncio.gather(*tasks)
        return results

# Analyze 10 politicians simultaneously
results = asyncio.run(batch_analyze(politician_ids))
```

---

## Best Practices

### 1. Cache Results Locally

Analysis computations are expensive. Cache results locally:

```python
import hashlib
import json
import os

def cache_key(politician_id, analysis_type):
    return hashlib.md5(f"{politician_id}:{analysis_type}".encode()).hexdigest()

def get_cached_or_fetch(politician_id, analysis_type):
    cache_file = f"cache/{cache_key(politician_id, analysis_type)}.json"

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)

    # Fetch from API
    response = requests.get(f"{BASE_URL}/patterns/analyze/{politician_id}/{analysis_type}")
    result = response.json()

    # Cache
    os.makedirs("cache", exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(result, f)

    return result
```

### 2. Handle Rate Limits

```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

response = session.get(url)
```

### 3. Error Handling

```python
def safe_analyze(politician_id):
    try:
        response = requests.get(f"{BASE_URL}/patterns/analyze/{politician_id}/fourier")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Politician {politician_id} not found")
        elif e.response.status_code == 400:
            print(f"Insufficient data: {e.response.json()['detail']}")
        else:
            print(f"Error: {e}")
        return None
```

### 4. Respect the Server

- Use batch endpoints when possible
- Implement exponential backoff
- Cache aggressively
- Run analyses during off-peak hours
- Don't hammer endpoints in tight loops

---

## Support & Feedback

**Documentation**: http://localhost:8000/api/v1/docs (Interactive Swagger UI)
**GitHub**: https://github.com/ElliottSax/quant
**Issues**: https://github.com/ElliottSax/quant/issues

---

**Last Updated**: November 14, 2025
**API Version**: 1.0.0
**Status**: Production Ready
