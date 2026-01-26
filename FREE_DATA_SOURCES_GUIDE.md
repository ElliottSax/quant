# Free Data Sources Guide

**Last Updated**: January 26, 2026

---

## 🎉 Yes! The Platform CAN Pull Free Data

The Quant Trading Platform is configured to pull data from **multiple free sources**, including:

1. ✅ **Yahoo Finance** (100% free, no API key needed)
2. ✅ **Your Discovery Project** (your own ML predictions)
3. ✅ **Alpha Vantage** (free tier: 5 calls/min, 500/day)
4. ✅ **Finnhub** (free tier: 60 calls/min)
5. ✅ **Polygon.io** (free tier available)
6. ✅ **IEX Cloud** (free tier available)

---

## 📊 Data Source Breakdown

### 1. Yahoo Finance (Primary - 100% Free)

**Status**: ✅ **Fully Integrated & Working**
**API Key Required**: ❌ No
**Rate Limits**: None (reasonable use expected)

**What You Get**:
- Real-time stock quotes
- Historical price data (OHLCV)
- Company information
- Adjusted prices
- Dividend data

**Usage**:
```python
# Already working! Default provider
response = requests.get("http://localhost:8000/api/v1/market-data/public/quote/AAPL")
```

**Advantages**:
- ✅ No API key needed
- ✅ No rate limits
- ✅ Comprehensive data
- ✅ Works out of the box

**Current Status**: **ACTIVE & DEFAULT**

---

### 2. Discovery Project Integration

**Status**: ✅ **Fully Integrated**
**API Key Required**: ❌ No (uses local files)
**Rate Limits**: None

**What You Get**:
- ML stock predictions (UP/DOWN)
- Confidence scores
- Cyclical pattern analysis
- Regime detection
- Pattern matching signals
- Trading alerts
- Multi-horizon predictions (7d, 14d, 30d)

**Your Discovery Project Path**:
```
/mnt/e/projects/discovery/data/
├── predictions/
│   ├── predictions_latest.json
│   └── multi_horizon_predictions.json
├── analysis/
│   └── 24x7/
│       └── cycle_*.json
├── pipeline/
│   ├── analytics_*.json
│   └── trades_*.json
└── alerts/
    └── alert_summary.json
```

**Available Endpoints**:
```bash
# Get discovery status
GET /api/v1/discovery/status

# Get ML predictions
GET /api/v1/discovery/predictions?limit=20&min_confidence=0.7

# Get prediction for specific stock
GET /api/v1/discovery/predictions/AAPL

# Get multi-horizon predictions
GET /api/v1/discovery/predictions/multi-horizon

# Get cycle analysis
GET /api/v1/discovery/analysis/cycles?limit=10

# Get pipeline analytics
GET /api/v1/discovery/analytics

# Get recent trades
GET /api/v1/discovery/trades?limit=50&ticker=AAPL

# Get alerts
GET /api/v1/discovery/alerts?limit=20
```

**Current Status**: **ACTIVE & WORKING**

---

### 3. Alpha Vantage (Free Tier)

**Status**: ✅ Integrated, needs API key
**API Key Required**: ✅ Yes (free)
**Rate Limits**: 5 calls/min, 500 calls/day

**What You Get**:
- Real-time quotes
- Historical data
- Technical indicators
- Fundamental data

**Setup**:
```bash
# 1. Get free API key from: https://www.alphavantage.co/support/#api-key

# 2. Add to .env file
echo "ALPHA_VANTAGE_API_KEY=your_key_here" >> .env

# 3. Use in API
curl "http://localhost:8000/api/v1/market-data/public/quote/AAPL?provider=alpha_vantage"
```

**Free Tier Limits**:
- ✅ 5 API requests per minute
- ✅ 500 API requests per day
- ✅ No credit card required

**Current Status**: **READY TO USE** (just add API key)

---

### 4. Finnhub (Free Tier)

**Status**: ✅ Integrated, needs API key
**API Key Required**: ✅ Yes (free)
**Rate Limits**: 60 calls/min

**What You Get**:
- Real-time quotes
- Company news
- Market sentiment
- Technical indicators

**Setup**:
```bash
# 1. Get free API key from: https://finnhub.io/register

# 2. Add to .env file
echo "FINNHUB_API_KEY=your_key_here" >> .env

# 3. Use in API
curl "http://localhost:8000/api/v1/market-data/public/quote/AAPL?provider=finnhub"
```

**Free Tier Limits**:
- ✅ 60 API calls per minute
- ✅ No credit card required

**Current Status**: **READY TO USE** (just add API key)

---

### 5. Polygon.io (Free Tier)

**Status**: ✅ Integrated, needs API key
**API Key Required**: ✅ Yes (free)
**Rate Limits**: Varies by tier

**What You Get**:
- Real-time quotes (delayed 15 min on free tier)
- Historical data
- Market aggregates

**Setup**:
```bash
# 1. Get free API key from: https://polygon.io/pricing

# 2. Add to .env file
echo "POLYGON_API_KEY=your_key_here" >> .env

# 3. Use in API
curl "http://localhost:8000/api/v1/market-data/public/quote/AAPL?provider=polygon"
```

**Free Tier Limits**:
- ✅ Delayed quotes (15 min)
- ✅ Historical data access
- ✅ No credit card required

**Current Status**: **READY TO USE** (just add API key)

---

### 6. IEX Cloud (Free Tier)

**Status**: ✅ Integrated, needs API key
**API Key Required**: ✅ Yes (free)
**Rate Limits**: 50,000 core messages/month

**What You Get**:
- Real-time quotes
- Historical data
- Company information

**Setup**:
```bash
# 1. Get free API key from: https://iexcloud.io/cloud-login#/register

# 2. Add to .env file
echo "IEX_API_KEY=your_key_here" >> .env
```

**Free Tier Limits**:
- ✅ 50,000 messages per month
- ✅ No credit card required

**Current Status**: **READY TO USE** (just add API key)

---

## 🚀 Quick Setup Guide

### Option 1: Use Yahoo Finance (Recommended - No Setup)

**Already working!** Yahoo Finance is the default provider and requires no configuration.

```bash
# Get quote (works immediately)
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL

# Get historical data
curl "http://localhost:8000/api/v1/market-data/public/historical/AAPL?start_date=2026-01-01T00:00:00Z"

# Get multiple quotes
curl "http://localhost:8000/api/v1/market-data/public/quotes?symbols=AAPL&symbols=GOOGL&symbols=MSFT"
```

### Option 2: Use Your Discovery Project

**Already integrated!** If your discovery project has generated data files:

```bash
# Check if discovery data is available
curl http://localhost:8000/api/v1/discovery/status

# Get ML predictions
curl http://localhost:8000/api/v1/discovery/predictions

# Get prediction for AAPL
curl http://localhost:8000/api/v1/discovery/predictions/AAPL
```

### Option 3: Add Free API Keys (Optional)

Add any or all of these to your `.env` file:

```bash
# Alpha Vantage (5 calls/min, 500/day)
ALPHA_VANTAGE_API_KEY=your_key_here

# Finnhub (60 calls/min)
FINNHUB_API_KEY=your_key_here

# Polygon.io (delayed quotes)
POLYGON_API_KEY=your_key_here

# IEX Cloud (50k messages/month)
IEX_API_KEY=your_key_here
```

Then select provider in API calls:
```bash
curl "http://localhost:8000/api/v1/market-data/public/quote/AAPL?provider=alpha_vantage"
```

---

## 📈 What Data Can You Get for Free?

### Market Data (Yahoo Finance - No Limits)

✅ **Real-time Quotes**
- Current price, bid, ask
- Volume, change, percent change
- Previous close, high, low

✅ **Historical Data**
- OHLCV bars (Open, High, Low, Close, Volume)
- Adjusted close prices
- Multiple intervals (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
- Up to 10 years of history (authenticated users)

✅ **Company Information**
- Company name, sector, industry
- Description
- Website, employees
- Market cap, P/E ratio

### Discovery ML Predictions (Your Own Data)

✅ **Stock Predictions**
- UP/DOWN predictions
- Confidence scores (0-1)
- Signal breakdown (cyclical, regime, pattern, ML)
- Multi-horizon predictions (7d, 14d, 30d)

✅ **Pattern Analysis**
- Cyclical trading patterns
- Regime detection (high/normal/low activity)
- DTW pattern matching
- Motif discovery

✅ **Trading Intelligence**
- Recent politician trades
- Large transaction alerts
- Top traded stocks
- Sector distribution
- Most active politicians

---

## 💡 Usage Examples

### Example 1: Get Free Market Data

```python
import requests

API_URL = "http://localhost:8000"

# Get real-time quote (Yahoo Finance - Free)
quote = requests.get(f"{API_URL}/api/v1/market-data/public/quote/AAPL").json()
print(f"AAPL: ${quote['price']} ({quote['change_percent']:+.2f}%)")

# Get multiple quotes
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
response = requests.get(
    f"{API_URL}/api/v1/market-data/public/quotes",
    params={"symbols": symbols}
)
quotes = response.json()['quotes']

for symbol, quote in quotes.items():
    print(f"{symbol}: ${quote['price']}")

# Get historical data (last 30 days)
from datetime import datetime, timedelta

start = (datetime.utcnow() - timedelta(days=30)).isoformat()
response = requests.get(
    f"{API_URL}/api/v1/market-data/public/historical/AAPL",
    params={"start_date": start, "interval": "1d"}
)
data = response.json()
print(f"Got {data['count']} bars of historical data")
```

### Example 2: Use Discovery ML Predictions

```python
# Get ML predictions
predictions = requests.get(
    f"{API_URL}/api/v1/discovery/predictions",
    params={"limit": 10, "min_confidence": 0.7}
).json()

for pred in predictions:
    print(f"{pred['ticker']}: {pred['prediction']} "
          f"(confidence: {pred['confidence']:.1%})")

# Get specific stock prediction
aapl_pred = requests.get(
    f"{API_URL}/api/v1/discovery/predictions/AAPL"
).json()

print(f"AAPL Prediction: {aapl_pred['prediction']}")
print(f"Confidence: {aapl_pred['confidence']:.1%}")
print(f"Regime: {aapl_pred['regime']}")
print(f"Patterns: {aapl_pred['patterns_found']}")

# Get recent trading alerts
alerts = requests.get(
    f"{API_URL}/api/v1/discovery/alerts",
    params={"limit": 20}
).json()

print(f"Recent alerts: {alerts['count']}")
for alert in alerts['alerts'][:5]:
    print(f"- {alert['type']}: {alert['message']}")
```

### Example 3: Combine Market Data + ML Predictions

```python
# Get ML prediction for a stock
prediction = requests.get(
    f"{API_URL}/api/v1/discovery/predictions/AAPL"
).json()

# Get current market price
quote = requests.get(
    f"{API_URL}/api/v1/market-data/public/quote/AAPL"
).json()

# Combine insights
print(f"Stock: AAPL")
print(f"Current Price: ${quote['price']}")
print(f"Change: {quote['change_percent']:+.2f}%")
print(f"ML Prediction: {prediction['prediction']}")
print(f"Confidence: {prediction['confidence']:.1%}")
print(f"Recommendation: {'BUY' if prediction['prediction'] == 'UP' else 'SELL'}")
```

---

## 🎯 Best Free Data Strategy

### Recommended Setup

1. **Use Yahoo Finance as Primary** (No API key needed)
   - For real-time quotes
   - For historical data
   - For company information

2. **Use Your Discovery Project** (Free, your own data)
   - For ML predictions
   - For trading alerts
   - For pattern analysis

3. **Optional: Add One Free API** (for redundancy)
   - Alpha Vantage OR Finnhub
   - As backup if Yahoo Finance has issues

### Cost: $0.00

With this setup, you get:
- ✅ Unlimited market data (Yahoo Finance)
- ✅ ML predictions (Discovery)
- ✅ Trading alerts (Discovery)
- ✅ Pattern analysis (Discovery)
- ✅ Historical data (Yahoo Finance)
- ✅ No API costs

---

## 🔍 Check What's Working

### Test All Free Sources

```bash
# 1. Test Yahoo Finance (should work immediately)
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL
# Expected: {"symbol":"AAPL","price":150.25,...}

# 2. Test Discovery integration
curl http://localhost:8000/api/v1/discovery/status
# Expected: {"available":true,"predictions_count":...}

# 3. Test available providers
curl http://localhost:8000/api/v1/market-data/public/providers
# Expected: {"providers":["yahoo_finance",...],"default":"yahoo_finance"}

# 4. Test market status
curl http://localhost:8000/api/v1/market-data/public/market-status
# Expected: {"is_open":true/false,"market":"US",...}
```

---

## 📊 Data Comparison

| Feature | Yahoo Finance | Discovery | Alpha Vantage | Finnhub |
|---------|---------------|-----------|---------------|---------|
| **Cost** | Free | Free | Free | Free |
| **API Key** | No | No | Yes | Yes |
| **Rate Limit** | None | None | 5/min | 60/min |
| **Real-time Quotes** | ✅ | ❌ | ✅ | ✅ |
| **Historical Data** | ✅ | ❌ | ✅ | ✅ |
| **ML Predictions** | ❌ | ✅ | ❌ | ❌ |
| **Trading Alerts** | ❌ | ✅ | ❌ | ❌ |
| **Pattern Analysis** | ❌ | ✅ | ❌ | ❌ |
| **Setup Time** | 0 min | 0 min | 2 min | 2 min |

**Recommendation**: Use Yahoo Finance + Discovery for best free experience!

---

## 🚀 Getting Started in 30 Seconds

```bash
# 1. Start the backend
cd quant/backend
python -m uvicorn app.main:app --reload

# 2. Test free market data
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL

# 3. Test discovery predictions (if data exists)
curl http://localhost:8000/api/v1/discovery/predictions

# Done! You're using 100% free data sources.
```

---

## ❓ FAQ

**Q: Do I need API keys?**
A: No! Yahoo Finance works without any API keys. Discovery uses your local data.

**Q: Are there rate limits?**
A: Yahoo Finance has no rate limits (reasonable use). Discovery has no limits.

**Q: Is the data real-time?**
A: Yes! Yahoo Finance provides real-time quotes. Discovery provides ML predictions based on your latest analysis.

**Q: What if Yahoo Finance goes down?**
A: Add a free API key for Alpha Vantage or Finnhub as backup.

**Q: Where does Discovery data come from?**
A: From your own discovery project at `/mnt/e/projects/discovery/data/`

**Q: How often is Discovery data updated?**
A: Whenever your discovery project runs its analysis pipeline.

---

## ✅ Summary

**YES!** The platform can pull free data from:

1. ✅ **Yahoo Finance** - Working now, no setup needed
2. ✅ **Your Discovery Project** - Working now, uses local files
3. ✅ **4 other free APIs** - Ready to use, just add optional API keys

**Total Cost**: $0.00
**Setup Time**: 0 minutes (Yahoo Finance + Discovery)
**Data Quality**: Excellent

You're all set to use 100% free data sources! 🎉

---

**Last Updated**: January 26, 2026
**Platform**: Quant Trading Platform v1.0.0
