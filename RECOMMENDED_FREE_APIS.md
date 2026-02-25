# Recommended Free APIs for Stock Market Data (2026)

Complete guide to the best free APIs for enhancing your backtesting platform with market data, news, sentiment, and fundamentals.

---

## 🏆 Top Recommended APIs

### 1. ⭐ Finnhub (ALREADY INTEGRATED)

**Status**: ✅ Implemented
**Free Tier**: 60 requests/minute
**Best For**: Real-time quotes, news sentiment, analyst data

**Features**:
- ✅ Real-time stock quotes (US markets)
- ✅ Company news with sentiment scores
- ✅ Market news aggregation
- ✅ Analyst recommendations
- ✅ Price targets
- ✅ Earnings calendar
- ✅ Stock symbols search

**Setup**:
```bash
# Already integrated!
# Just add to .env:
FINNHUB_API_KEY=your_key_here

# Get key at: https://finnhub.io/register
```

**API Endpoints** (Already Built):
```bash
# Real-time quote
GET /api/v1/finnhub/demo/quote/{symbol}

# News sentiment
GET /api/v1/finnhub/demo/sentiment/{symbol}

# Company news
GET /api/v1/finnhub/demo/news/{symbol}

# Market news
GET /api/v1/finnhub/demo/market-news

# Analyst recommendations
GET /api/v1/finnhub/demo/recommendations/{symbol}
```

**Why It's Great**:
- Most generous free tier (60 req/min vs Alpha Vantage's 25/day)
- AI-powered sentiment scores
- Real-time data
- No expiration on free tier

**Limitations**:
- US stocks only (no international)
- Historical data limited on free tier

**Documentation**: https://finnhub.io/docs/api

---

### 2. 🔥 EODHD (End of Day Historical Data)

**Free Tier**: Generous (exact limits vary)
**Best For**: Fundamentals, historical data, international stocks

**Features**:
- ✅ 150,000+ tickers (60+ exchanges)
- ✅ Historical EOD prices (stocks, ETFs, indices)
- ✅ Fundamental data (P/E, EPS, revenue, etc.)
- ✅ Dividends & splits
- ✅ US stock options data
- ✅ Macroeconomic indicators
- ✅ News API with sentiment

**Setup**:
```bash
pip install eodhd

# .env
EODHD_API_KEY=your_key_here

# Get key at: https://eodhd.com/register
```

**Example Integration**:
```python
# app/services/eodhd_client.py
import requests

class EODHDClient:
    BASE_URL = "https://eodhd.com/api"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_fundamentals(self, symbol):
        """Get fundamental data"""
        url = f"{self.BASE_URL}/fundamentals/{symbol}"
        params = {"api_token": self.api_key, "fmt": "json"}
        return requests.get(url, params=params).json()

    def get_historical(self, symbol, start_date, end_date):
        """Get historical EOD data"""
        url = f"{self.BASE_URL}/eod/{symbol}"
        params = {
            "api_token": self.api_key,
            "from": start_date,
            "to": end_date,
            "fmt": "json"
        }
        return requests.get(url, params=params).json()
```

**Use Cases**:
1. **Fundamental Filters**: "Only backtest stocks with P/E < 15"
2. **International Portfolios**: Test global stocks
3. **Dividend Strategies**: Factor in dividend payments
4. **Options Backtesting**: Test covered calls, spreads

**Why It's Great**:
- Comprehensive fundamental data
- International coverage
- US options included
- Affordable paid tiers ($19.99/month)

**Limitations**:
- EOD data only (not real-time on free tier)
- API limits on free tier

**Documentation**: https://eodhd.com/financial-apis/

---

### 3. 💎 Financial Modeling Prep (FMP)

**Free Tier**: 250 requests/day
**Best For**: All-in-one financial data

**Features**:
- ✅ Stock prices (real-time & historical)
- ✅ Fundamental data (income statements, balance sheets, cash flow)
- ✅ Financial ratios (50+ ratios)
- ✅ SEC filings
- ✅ Earnings calendar
- ✅ Stock screener
- ✅ Insider trades
- ✅ Institutional holders

**Setup**:
```bash
pip install fmpsdk

# .env
FMP_API_KEY=your_key_here

# Get key at: https://site.financialmodelingprep.com/register
```

**Example Integration**:
```python
from fmpsdk import settings, company_valuation

# Configure
settings.DEFAULT_API_KEY = "your_key_here"

# Get financial ratios
ratios = company_valuation.financial_ratios("AAPL")

# Get income statement
income = company_valuation.income_statement("AAPL")

# Get key metrics
metrics = company_valuation.key_metrics("AAPL")
```

**Use Cases**:
1. **Value Investing**: Filter by P/E, P/B, PEG ratios
2. **Growth Screening**: Find high-revenue-growth stocks
3. **Financial Health**: Check debt ratios, current ratio
4. **Insider Activity**: Track insider buying/selling

**Why It's Great**:
- Most comprehensive API (all-in-one)
- Clean, well-documented endpoints
- Affordable paid tiers ($14/month)

**Limitations**:
- 250 req/day on free tier (can hit limits quickly)
- Rate limited

**Documentation**: https://site.financialmodelingprep.com/developer/docs

---

### 4. 📊 Twelve Data

**Free Tier**: 800 API credits/day
**Best For**: Multi-asset time series (stocks, forex, crypto)

**Features**:
- ✅ Time series data (1min to 1month intervals)
- ✅ Technical indicators (120+ indicators)
- ✅ Forex & crypto (in addition to stocks)
- ✅ WebSocket streaming (real-time)
- ✅ Global exchanges

**Setup**:
```bash
pip install twelvedata

# .env
TWELVE_DATA_API_KEY=your_key_here

# Get key at: https://twelvedata.com/register
```

**Example Integration**:
```python
from twelvedata import TDClient

td = TDClient(apikey="your_key_here")

# Get time series
ts = td.time_series(
    symbol="AAPL",
    interval="1day",
    outputsize=252,  # 1 year
    timezone="America/New_York"
)
data = ts.as_pandas()

# Get technical indicator
rsi = td.rsi(
    symbol="AAPL",
    interval="1day",
    time_period=14
)
```

**Use Cases**:
1. **Multi-Timeframe Backtesting**: Test strategies on 1min, 5min, 1h, 1day
2. **Forex Portfolios**: Add currency pairs to portfolio
3. **Crypto Integration**: Mix stocks and crypto
4. **Technical Analysis**: Pre-calculated indicators

**Why It's Great**:
- Multiple asset classes
- WebSocket for real-time data
- 120+ pre-calculated technical indicators

**Limitations**:
- 800 credits/day (each request costs credits)
- Complex credit system

**Documentation**: https://twelvedata.com/docs

---

### 5. 📰 Marketaux

**Free Tier**: 100 requests/day
**Best For**: News aggregation with sentiment

**Features**:
- ✅ Global financial news
- ✅ AI-powered sentiment analysis
- ✅ Multiple sources aggregated
- ✅ Filtered by ticker, sector, topic
- ✅ Supports 50+ languages

**Setup**:
```bash
# .env
MARKETAUX_API_KEY=your_key_here

# Get key at: https://www.marketaux.com/account/signup
```

**Example Integration**:
```python
import requests

class MarketauxClient:
    BASE_URL = "https://api.marketaux.com/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_news(self, symbols=None, limit=10):
        """Get financial news"""
        url = f"{self.BASE_URL}/news/all"
        params = {
            "api_token": self.api_key,
            "symbols": ",".join(symbols) if symbols else None,
            "limit": limit,
            "language": "en"
        }
        return requests.get(url, params=params).json()
```

**Use Cases**:
1. **News-Based Alerts**: "Alert me when AAPL has negative news"
2. **Sentiment Dashboard**: Track portfolio-wide sentiment
3. **Event-Driven Backtesting**: "How do stocks perform after negative news?"

**Why It's Great**:
- Multi-source aggregation
- AI sentiment scores
- Real-time updates

**Limitations**:
- 100 requests/day on free tier
- Sentiment not always accurate

**Documentation**: https://www.marketaux.com/documentation

---

### 6. 💹 Alpha Vantage

**Free Tier**: 25 requests/day (very limited)
**Best For**: Technical indicators, fallback option

**Features**:
- ✅ Stock time series
- ✅ 50+ technical indicators (pre-calculated)
- ✅ Forex & crypto
- ✅ Fundamental data
- ✅ Sector performance

**Setup**:
```bash
pip install alpha_vantage

# .env
ALPHA_VANTAGE_API_KEY=your_key_here

# Get key at: https://www.alphavantage.co/support/#api-key
```

**Why It's Here**:
- Well-established, reliable
- Good documentation
- Useful for technical indicators

**Why NOT Primary Choice**:
- Only 25 requests/day (too limiting)
- Finnhub, EODHD, FMP are all better

**Documentation**: https://www.alphavantage.co/documentation/

---

### 7. 🎯 StockGeist

**Free Tier**: Limited (check website)
**Best For**: Social sentiment (Twitter, Reddit, news)

**Features**:
- ✅ Real-time social sentiment
- ✅ Twitter/Reddit mentions tracking
- ✅ News sentiment
- ✅ Sentiment trends over time

**Setup**:
```bash
# .env
STOCKGEIST_API_KEY=your_key_here

# Get key at: https://www.stockgeist.ai/
```

**Use Cases**:
1. **Meme Stock Tracking**: Track WallStreetBets mentions
2. **Social Sentiment Alerts**: "Alert when TSLA sentiment spikes"
3. **Contrarian Indicators**: Fade extreme sentiment

**Why It's Great**:
- Unique social data
- Real-time sentiment shifts
- Retail trader focus

**Limitations**:
- Niche use case
- Sentiment can be noisy

**Documentation**: https://www.stockgeist.ai/stock-market-api/

---

## 🚀 Recommended Integration Priority

### Phase 1: Foundation (Already Done)
1. ✅ **Yahoo Finance** (yfinance) - Free historical data
2. ✅ **Finnhub** - Real-time quotes + sentiment

### Phase 2: Fundamentals (Next - 1 day)
3. 🔜 **EODHD** or **Financial Modeling Prep**
   - Add fundamental filtering
   - "Only backtest stocks with P/E < 15"

### Phase 3: Enhanced Analytics (Week 2)
4. 🔜 **Marketaux** - Multi-source news aggregation
5. 🔜 **Twelve Data** - Multi-timeframe analysis

### Phase 4: Advanced Features (Month 2)
6. 🔜 **StockGeist** - Social sentiment
7. 🔜 **Alpha Vantage** - Technical indicators (fallback)

---

## 📊 Comparison Matrix

| API | Free Tier | Real-Time | Fundamentals | News | Sentiment | International |
|-----|-----------|-----------|--------------|------|-----------|---------------|
| **Finnhub** ⭐ | 60/min | ✅ | ❌ | ✅ | ✅ | ❌ |
| **EODHD** ⭐ | Generous | ❌ | ✅ | ✅ | ✅ | ✅ |
| **FMP** ⭐ | 250/day | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Twelve Data** | 800/day | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Marketaux** | 100/day | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Alpha Vantage** | 25/day | ❌ | ✅ | ❌ | ❌ | ❌ |
| **StockGeist** | Limited | ✅ | ❌ | ✅ | ✅ | ❌ |

**Legend**:
- ⭐ = Highly recommended
- ✅ = Included
- ❌ = Not included

---

## 💡 Use Case Recommendations

### For Backtesting Platform:
1. **Historical Data**: Yahoo Finance (free, unlimited) ✅
2. **Real-Time Quotes**: Finnhub (60/min) ✅
3. **Fundamentals**: EODHD or FMP
4. **News/Sentiment**: Finnhub + Marketaux
5. **Technical Indicators**: Calculate in-house or Twelve Data

### For Portfolio Analysis:
1. **Correlation Data**: Yahoo Finance ✅
2. **Sector Info**: FMP or EODHD
3. **Macro Data**: EODHD or Alpha Vantage

### For Day Trading:
1. **Intraday Data**: Twelve Data (WebSocket)
2. **Level 2 Quotes**: Need paid service
3. **Real-Time News**: Finnhub + Marketaux

### For Fundamental Analysis:
1. **Financial Statements**: FMP (most comprehensive)
2. **Ratios & Metrics**: EODHD or FMP
3. **SEC Filings**: FMP

---

## 🔧 Implementation Guide

### Quick Start: Add EODHD Fundamentals

**Step 1**: Install
```bash
pip install requests
```

**Step 2**: Create Client
```python
# app/services/eodhd_client.py
import os
import requests
from typing import Optional, Dict, Any

class EODHDClient:
    BASE_URL = "https://eodhd.com/api"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("EODHD_API_KEY")
        self.enabled = bool(self.api_key)

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data for a symbol"""
        if not self.enabled:
            raise ValueError("EODHD API key not configured")

        url = f"{self.BASE_URL}/fundamentals/{symbol}"
        params = {"api_token": self.api_key, "fmt": "json"}

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_pe_ratio(self, symbol: str) -> float:
        """Get P/E ratio"""
        data = self.get_fundamentals(symbol)
        return data.get("Highlights", {}).get("PERatio", 0)

    def get_eps(self, symbol: str) -> float:
        """Get EPS"""
        data = self.get_fundamentals(symbol)
        return data.get("Highlights", {}).get("EarningsShare", 0)
```

**Step 3**: Add API Endpoint
```python
# app/api/v1/fundamentals.py
from fastapi import APIRouter, HTTPException
from app.services.eodhd_client import EODHDClient

router = APIRouter(prefix="/fundamentals", tags=["fundamentals"])

@router.get("/demo/{symbol}")
async def get_fundamentals(symbol: str):
    """Get fundamental data for a symbol"""
    client = EODHDClient()

    if not client.enabled:
        raise HTTPException(
            status_code=503,
            detail="EODHD API not configured"
        )

    try:
        data = client.get_fundamentals(symbol)
        return {
            "symbol": symbol,
            "pe_ratio": data.get("Highlights", {}).get("PERatio"),
            "eps": data.get("Highlights", {}).get("EarningsShare"),
            "market_cap": data.get("Highlights", {}).get("MarketCapitalization"),
            "dividend_yield": data.get("Highlights", {}).get("DividendYield"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 4**: Add to .env
```bash
EODHD_API_KEY=your_key_here
```

---

## 💰 Cost Comparison (Paid Tiers)

When you outgrow free tiers:

| API | Free Limit | Paid Tier 1 | Features |
|-----|------------|-------------|----------|
| **Finnhub** | 60/min | $59/mo | Real-time US + Crypto |
| **EODHD** | Limited | $19.99/mo | All features |
| **FMP** | 250/day | $14/mo | 750/day + real-time |
| **Twelve Data** | 800/day | $79/mo | 8K/day + WebSocket |
| **Marketaux** | 100/day | $39/mo | 1K/day |

**Most Cost-Effective**: EODHD ($19.99/mo for everything)

---

## 🎯 Quick Reference

### Get Started Today (5 minutes):
1. ✅ **Finnhub**: Already integrated! Just add API key
2. 🔜 **EODHD**: Sign up → Add key → Get fundamentals
3. 🔜 **Marketaux**: Sign up → Add key → Get news sentiment

### Coming Soon (Add Later):
4. **FMP**: When you need financial statements
5. **Twelve Data**: When you add multi-timeframe analysis
6. **StockGeist**: When you add social sentiment

---

## 📚 Resources

**API Comparison Articles**:
- [Financial Data APIs Compared (2026)](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
- [Best Real-Time Stock Market Data APIs](https://site.financialmodelingprep.com/education/other/best-realtime-stock-market-data-apis-in-)
- [Top Stock Data Providers 2026](https://brightdata.com/blog/web-data/best-stock-data-providers)

**API Documentation**:
- Finnhub: https://finnhub.io/docs/api
- EODHD: https://eodhd.com/financial-apis/
- FMP: https://site.financialmodelingprep.com/developer/docs
- Twelve Data: https://twelvedata.com/docs
- Marketaux: https://www.marketaux.com/documentation

---

**Status**: ✅ Research Complete
**Next**: Add EODHD for fundamentals
**Time**: 30 minutes per API integration
