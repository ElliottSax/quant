# Advanced Analytics API Reference

Quick reference for Task #14 advanced analytics endpoints.

## Table of Contents

- [Options Analysis](#options-analysis)
- [Sentiment Analysis](#sentiment-analysis)
- [Pattern Recognition](#pattern-recognition)
- [Configuration](#configuration)
- [Examples](#examples)

---

## Options Analysis

### Calculate Gamma Exposure (GEX)

```http
POST /api/v1/analytics/options/gamma-exposure
```

**Query Parameters:**
- `ticker` (string, required): Stock ticker symbol

**Response:**
```json
{
  "ticker": "AAPL",
  "timestamp": "2026-02-03T12:00:00Z",
  "total_gamma": 150000000,
  "net_gamma": 50000000,
  "gamma_flip_price": 175.50,
  "market_stance": "bullish",
  "key_strikes": [[175, 25000000], [180, 20000000]],
  "explanation": "Positive net gamma suggests...",
  "cached": false
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/options/gamma-exposure?ticker=AAPL"
```

---

### Complete Options Analysis

```http
GET /api/v1/analytics/options/{ticker}
```

**Path Parameters:**
- `ticker` (string, required): Stock ticker symbol

**Response:**
```json
{
  "ticker": "AAPL",
  "timestamp": "2026-02-03T12:00:00Z",
  "gamma_exposure": {
    "total_gamma": 150000000,
    "net_gamma": 50000000,
    "market_stance": "bullish",
    ...
  },
  "options_flow": {
    "call_volume": 50000,
    "put_volume": 30000,
    "call_put_ratio": 1.67,
    "sentiment": "bullish",
    ...
  },
  "unusual_activities": [
    {
      "activity_type": "high_volume",
      "strike": 180,
      "unusual_score": 85,
      ...
    }
  ],
  "overall_sentiment": "bullish",
  "confidence": 0.75,
  "summary": "Options analysis for AAPL..."
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/options/AAPL"
```

---

## Sentiment Analysis

### Politician Sentiment

```http
GET /api/v1/analytics/sentiment/politician/{politician_id}
```

**Path Parameters:**
- `politician_id` (UUID, required): Politician UUID

**Query Parameters:**
- `lookback_days` (int, optional): Days to look back (1-30, default: 7)
- `sources` (array[string], optional): Specific sources to analyze

**Response:**
```json
{
  "entity_id": "uuid-here",
  "entity_name": "Nancy Pelosi",
  "entity_type": "politician",
  "timestamp": "2026-02-03T12:00:00Z",
  "overall_score": 0.25,
  "overall_category": "positive",
  "confidence": 0.70,
  "source_breakdown": {
    "news_api": 0.30,
    "gdelt": 0.20,
    "social_media": 0.25
  },
  "items_analyzed": 45,
  "positive_count": 25,
  "negative_count": 10,
  "neutral_count": 10,
  "trend_24h": 0.05,
  "summary": "Analyzed 45 items...",
  "cached": false
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/sentiment/politician/{uuid}?lookback_days=7"
```

---

### Ticker Sentiment

```http
GET /api/v1/analytics/sentiment/ticker/{ticker}
```

**Path Parameters:**
- `ticker` (string, required): Stock ticker symbol

**Query Parameters:**
- `lookback_days` (int, optional): Days to look back (1-30, default: 7)

**Response:**
```json
{
  "entity_id": "AAPL",
  "entity_name": "AAPL",
  "entity_type": "ticker",
  "overall_score": 0.45,
  "overall_category": "positive",
  "confidence": 0.80,
  "source_breakdown": {
    "news_api": 0.50,
    "gdelt": 0.40
  },
  "items_analyzed": 120,
  "summary": "Analyzed 120 items for AAPL..."
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/sentiment/ticker/AAPL?lookback_days=7"
```

---

## Pattern Recognition

### Analyze Patterns

```http
GET /api/v1/analytics/patterns
```

**Query Parameters:**
- `lookback_days` (int, optional): Days to analyze (30-365, default: 90)
- `min_cluster_size` (int, optional): Minimum cluster size (2-10, default: 3)
- `min_correlation` (float, optional): Minimum correlation (0.3-1.0, default: 0.6)

**Response:**
```json
{
  "timestamp": "2026-02-03T12:00:00Z",
  "clusters": [
    {
      "cluster_id": 0,
      "politicians": ["Politician A", "Politician B", "Politician C"],
      "politician_ids": ["uuid1", "uuid2", "uuid3"],
      "avg_correlation": 0.75,
      "trade_overlap": 0.60,
      "common_tickers": ["AAPL", "MSFT", "GOOGL"],
      "cluster_size": 3,
      "confidence": 0.75,
      "description": "Cluster of 3 politicians trading 3 common tickers"
    }
  ],
  "correlated_patterns": [
    {
      "politician_ids": ["uuid1", "uuid2"],
      "politician_names": ["Politician A", "Politician B"],
      "correlation_score": 0.85,
      "common_trades": 12,
      "time_window_days": 7,
      "common_tickers": ["AAPL", "TSLA"],
      "pattern_strength": "strong",
      "statistical_significance": 0.01
    }
  ],
  "total_patterns_detected": 15,
  "summary": "Pattern recognition analysis: Found 5 trading clusters..."
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/patterns?lookback_days=90&min_correlation=0.6"
```

---

### Politician Correlation Matrix

```http
GET /api/v1/analytics/correlations/politicians
```

**Query Parameters:**
- `lookback_days` (int, optional): Days to analyze (30-365, default: 90)
- `min_trades` (int, optional): Minimum trades required (1-20, default: 5)

**Response:**
```json
{
  "timestamp": "2026-02-03T12:00:00Z",
  "lookback_days": 90,
  "matrix": {
    "uuid1": {
      "uuid2": 0.85,
      "uuid3": 0.45
    }
  },
  "top_correlations": [
    {
      "politician1_id": "uuid1",
      "politician2_id": "uuid2",
      "correlation": 0.85,
      "p_value": 0.01
    }
  ],
  "summary": "Correlation matrix for 50 politicians"
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/correlations/politicians?lookback_days=90"
```

---

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# NewsAPI (newsapi.org)
# Free tier: 100 requests/day
NEWS_API_KEY=your_newsapi_key_here

# Twitter/X API
# Essential tier: Free (500k tweets/month)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### API Keys Setup

1. **NewsAPI** (Optional but recommended)
   - Sign up: https://newsapi.org/register
   - Free tier: 100 requests/day
   - Get API key from dashboard

2. **Twitter/X API** (Optional)
   - Apply: https://developer.twitter.com/
   - Essential tier is free
   - Get Bearer Token from dashboard

3. **GDELT** (No setup required)
   - Completely free
   - No API key needed
   - Automatically works

### Database Migration

Run the migration to create analytics tables:

```bash
cd /mnt/e/projects/quant/quant/backend
alembic upgrade head
```

---

## Examples

### Python Client

```python
import httpx
import asyncio

async def analyze_options():
    async with httpx.AsyncClient() as client:
        # Gamma exposure
        response = await client.post(
            "http://localhost:8000/api/v1/analytics/options/gamma-exposure",
            params={"ticker": "AAPL"}
        )
        data = response.json()
        print(f"Net Gamma: {data['net_gamma']}")

        # Complete analysis
        response = await client.get(
            "http://localhost:8000/api/v1/analytics/options/AAPL"
        )
        data = response.json()
        print(f"Sentiment: {data['overall_sentiment']}")

asyncio.run(analyze_options())
```

### JavaScript Client

```javascript
// Gamma exposure
const response = await fetch(
  'http://localhost:8000/api/v1/analytics/options/gamma-exposure?ticker=AAPL',
  { method: 'POST' }
);
const data = await response.json();
console.log('Net Gamma:', data.net_gamma);

// Sentiment analysis
const sentimentResponse = await fetch(
  'http://localhost:8000/api/v1/analytics/sentiment/ticker/AAPL?lookback_days=7'
);
const sentiment = await sentimentResponse.json();
console.log('Overall Score:', sentiment.overall_score);

// Pattern recognition
const patternsResponse = await fetch(
  'http://localhost:8000/api/v1/analytics/patterns?lookback_days=90'
);
const patterns = await patternsResponse.json();
console.log('Clusters:', patterns.clusters.length);
```

### Complete Analysis Workflow

```python
import httpx
import asyncio

async def complete_politician_analysis(politician_id: str):
    """Complete analytics pipeline for a politician"""

    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000/api/v1"

        # 1. Get politician sentiment
        sentiment_resp = await client.get(
            f"{base_url}/analytics/sentiment/politician/{politician_id}"
        )
        sentiment = sentiment_resp.json()

        # 2. Get their recent trades
        trades_resp = await client.get(
            f"{base_url}/trades",
            params={"politician_id": politician_id, "limit": 10}
        )
        trades = trades_resp.json()

        # 3. Analyze options for each ticker
        ticker_analyses = []
        for trade in trades.get("trades", []):
            ticker = trade["ticker"]

            options_resp = await client.get(
                f"{base_url}/analytics/options/{ticker}"
            )
            options = options_resp.json()

            ticker_sentiment_resp = await client.get(
                f"{base_url}/analytics/sentiment/ticker/{ticker}"
            )
            ticker_sentiment = ticker_sentiment_resp.json()

            ticker_analyses.append({
                "ticker": ticker,
                "options": options,
                "sentiment": ticker_sentiment
            })

        # 4. Check for patterns
        patterns_resp = await client.get(
            f"{base_url}/analytics/patterns",
            params={"lookback_days": 90}
        )
        patterns = patterns_resp.json()

        # Return complete analysis
        return {
            "politician_sentiment": sentiment,
            "ticker_analyses": ticker_analyses,
            "patterns": patterns
        }

# Run analysis
analysis = asyncio.run(complete_politician_analysis("politician-uuid-here"))
print(f"Overall Politician Sentiment: {analysis['politician_sentiment']['overall_category']}")
print(f"Tickers Analyzed: {len(analysis['ticker_analyses'])}")
print(f"Patterns Detected: {analysis['patterns']['total_patterns_detected']}")
```

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (politician/ticker not found) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## Rate Limits

| Tier | Requests/Minute | Requests/Hour |
|------|----------------|---------------|
| Free | 20 | 500 |
| Basic | 60 | 2000 |
| Premium | 200 | 10000 |

Expensive endpoints (pattern recognition) have additional limits:
- Pattern Analysis: 10 req/min
- Correlation Matrix: 5 req/min

---

## Caching

All endpoints use intelligent caching:

| Endpoint | Cache TTL | Storage |
|----------|-----------|---------|
| Gamma Exposure | 5 minutes | Database |
| Options Analysis | 5 minutes | Database |
| Sentiment (Politician) | 1 hour | Database |
| Sentiment (Ticker) | 1 hour | Database |
| Pattern Recognition | 30 minutes | Database |

Cache headers:
- `X-Cache-Hit: true/false` - Indicates if response was cached
- `X-Cache-Age: {seconds}` - Age of cached data

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "detail": "Error message here",
  "error_code": "INVALID_TICKER",
  "timestamp": "2026-02-03T12:00:00Z"
}
```

Common error codes:
- `INVALID_TICKER` - Ticker symbol not found
- `POLITICIAN_NOT_FOUND` - Politician UUID not found
- `INSUFFICIENT_DATA` - Not enough data for analysis
- `API_KEY_MISSING` - Required API key not configured
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## Testing

### Quick Test

```bash
# Test options analysis
curl "http://localhost:8000/api/v1/analytics/options/AAPL"

# Test sentiment analysis
curl "http://localhost:8000/api/v1/analytics/sentiment/ticker/AAPL"

# Test pattern recognition
curl "http://localhost:8000/api/v1/analytics/patterns"
```

### Run Test Suite

```bash
cd /mnt/e/projects/quant
python test_advanced_analytics.py
```

### Interactive Testing

Use the built-in Swagger UI:
```
http://localhost:8000/docs
```

Navigate to "advanced-analytics-v2" section to test all endpoints interactively.

---

## Support

For issues or questions:
1. Check logs: `tail -f logs/app.log`
2. Verify API keys are set: `echo $NEWS_API_KEY`
3. Check database migration: `alembic current`
4. Test dependencies: `python test_advanced_analytics.py`

---

## Version

**API Version**: v1
**Implementation Date**: 2026-02-03
**Status**: Production Ready

---
