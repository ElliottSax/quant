# Comprehensive Guide to Free Stock Market Prediction & Analysis APIs (2026)

This guide provides a detailed overview of free APIs for stock market data, prediction, and analysis, including rate limits, key features, and Python implementation examples.

---

## Table of Contents
1. [Stock Market Data APIs](#stock-market-data-apis)
2. [Technical Analysis APIs](#technical-analysis-apis)
3. [News & Sentiment Analysis APIs](#news--sentiment-analysis-apis)
4. [Economic Data APIs](#economic-data-apis)
5. [Trading & Paper Trading APIs](#trading--paper-trading-apis)
6. [Quick Comparison Table](#quick-comparison-table)

---

## Stock Market Data APIs

### 1. Alpha Vantage
**URL:** https://www.alphavantage.co/

**Free Tier Limits:**
- 25 API requests per day
- 5 API requests per minute

**Key Features:**
- 50+ technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands, etc.)
- Real-time and historical stock data
- Fundamental data (income statements, balance sheets, cash flow)
- 200,000+ stock tickers across 20+ global exchanges
- 20+ years of historical data
- Forex, cryptocurrency, and commodity data
- AI-powered news sentiment analysis
- Economic indicators

**Authentication:**
- API key required (free registration)

**Python Library:**
```python
# Using requests library
import requests

API_KEY = 'your_api_key'
symbol = 'AAPL'

# Get daily stock data
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
response = requests.get(url)
data = response.json()

# Get RSI indicator
url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={API_KEY}'
response = requests.get(url)
rsi_data = response.json()
```

**Alternative Python Package:**
```bash
pip install alpha-vantage
```

```python
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
data, meta_data = ts.get_daily(symbol='AAPL', outputsize='full')

ti = TechIndicators(key='YOUR_API_KEY', output_format='pandas')
rsi_data, meta_data = ti.get_rsi(symbol='AAPL', interval='daily')
```

---

### 2. Twelve Data
**URL:** https://twelvedata.com/

**Free Tier Limits:**
- 800 API calls per day
- 8 API requests per minute

**Key Features:**
- Real-time, intraday, and end-of-day data
- 100,000+ symbols (stocks, forex, crypto, ETFs, indices)
- Global coverage across major exchanges
- Technical indicators
- WebSocket streaming
- 99.95% uptime
- Time series data with multiple intervals (1min, 5min, 15min, 30min, 1h, daily, weekly, monthly)

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install twelvedata
```

```python
from twelvedata import TDClient

td = TDClient(apikey="YOUR_API_KEY")

# Get time series data
ts = td.time_series(
    symbol="AAPL",
    interval="1day",
    outputsize=30,
    timezone="America/New_York",
)
data = ts.as_pandas()

# Get technical indicator
rsi = td.time_series(
    symbol="AAPL",
    interval="1day",
    outputsize=30,
).with_rsi(time_period=14).as_pandas()
```

---

### 3. Polygon.io
**URL:** https://polygon.io/

**Free Tier Limits:**
- 5 API calls per minute
- Delayed data (15-minute delay)

**Key Features:**
- Real-time and historical stock data
- Options, forex, and crypto data
- Aggregates (bars) data
- Tick-level data
- WebSocket streaming for real-time updates
- Low latency infrastructure
- Market holidays and status

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install polygon-api-client
```

```python
from polygon import RESTClient

client = RESTClient(api_key="YOUR_API_KEY")

# Get aggregates (bars)
aggs = client.get_aggs(
    ticker="AAPL",
    multiplier=1,
    timespan="day",
    from_="2023-01-01",
    to="2023-12-31"
)

for agg in aggs:
    print(agg)

# Get previous close
previous_close = client.get_previous_close_agg("AAPL")
print(previous_close)
```

---

### 4. Yahoo Finance (yfinance)
**URL:** https://finance.yahoo.com/ (unofficial API via yfinance library)

**Free Tier Limits:**
- No official limits
- Unofficial API - subject to rate limiting and blocking
- Frequent 429 "Too Many Requests" errors with heavy use

**Key Features:**
- Historical and current stock prices
- OHLCV data
- Dividends and stock splits
- Financial statements
- Options data
- Real-time quotes (with delays)
- Multiple markets worldwide

**Authentication:**
- No API key required

**Python Library:**
```bash
pip install yfinance
```

```python
import yfinance as yf

# Download stock data
ticker = yf.Ticker("AAPL")

# Get historical data
hist = ticker.history(period="1y")
print(hist.head())

# Get financial data
financials = ticker.financials
balance_sheet = ticker.balance_sheet
cashflow = ticker.cashflow

# Get real-time quote
info = ticker.info
print(f"Current Price: {info['currentPrice']}")

# Download multiple tickers
data = yf.download("AAPL MSFT GOOGL", start="2023-01-01", end="2023-12-31")
```

**Important Notes:**
- Completely free but unreliable for production use
- Yahoo can block IPs with heavy usage
- Intended for personal use only
- Data may be incomplete or inconsistent

---

### 5. Finnhub
**URL:** https://finnhub.io/

**Free Tier Limits:**
- 60 API calls per minute
- Limited historical data (typically few years)

**Key Features:**
- Real-time stock prices
- Company fundamentals
- Financial statements
- News and sentiment analysis
- Technical indicators
- Earnings calendar
- IPO calendar
- Forex and crypto data
- Economic calendar
- Pattern recognition

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install finnhub-python
```

```python
import finnhub

# Setup client
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")

# Stock candles
res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
print(res)

# Company profile
profile = finnhub_client.company_profile2(symbol='AAPL')

# News sentiment
sentiment = finnhub_client.news_sentiment('AAPL')

# Technical indicators
indicators = finnhub_client.technical_indicator(
    symbol="AAPL:US",
    resolution='D',
    _from=1580988249,
    to=1591852249,
    indicator='rsi',
    indicator_fields={"timeperiod": 14}
)
```

---

### 6. Financial Modeling Prep (FMP)
**URL:** https://site.financialmodelingprep.com/

**Free Tier Limits:**
- 250 API requests per day
- 500MB bandwidth per month (trailing 30 days)

**Key Features:**
- 30+ years of historical data
- Real-time and historical stock prices
- Financial statements (income, balance sheet, cash flow)
- Company fundamentals
- Multiple time intervals (1min, 5min, 15min, 30min, 1h, 4h, daily)
- Ratios and metrics
- Insider trading data
- Stock screener
- ETF and mutual fund data
- Technical indicators

**Authentication:**
- API key required (free registration, no credit card)

**Python Library:**
```python
import requests

API_KEY = 'your_api_key'

# Get historical data
symbol = 'AAPL'
url = f'https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={API_KEY}'
response = requests.get(url)
data = response.json()

# Get financial statements
url = f'https://financialmodelingprep.com/api/v3/income-statement/{symbol}?apikey={API_KEY}'
income_statement = requests.get(url).json()

# Get technical indicators
url = f'https://financialmodelingprep.com/api/v3/technical_indicator/daily/{symbol}?period=14&type=rsi&apikey={API_KEY}'
technical_data = requests.get(url).json()
```

---

### 7. Tiingo
**URL:** https://www.tiingo.com/

**Free Tier Limits:**
- 50 symbols per hour
- 500 requests per hour
- 30+ years of daily data
- 5 years of fundamental data

**Key Features:**
- Daily, intraday, and real-time stock prices
- Company fundamentals
- News data
- 82,468+ global securities
- Cryptocurrency data
- IEX real-time data
- Forex data
- Data validation via proprietary EOD Price Engine

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install tiingo
```

```python
from tiingo import TiingoClient

config = {'api_key': 'YOUR_API_KEY'}
client = TiingoClient(config)

# Get ticker metadata
ticker_metadata = client.get_ticker_metadata("AAPL")

# Get historical prices
historical_prices = client.get_ticker_price(
    "AAPL",
    startDate='2023-01-01',
    endDate='2023-12-31',
    frequency='daily'
)

# Get intraday data (requires paid plan)
intraday_data = client.get_ticker_price(
    "AAPL",
    startDate='2023-01-01',
    frequency='5min'
)

# Get news
news = client.get_news(tickers=['AAPL'], startDate='2023-01-01')
```

---

### 8. Nasdaq Data Link (formerly Quandl)
**URL:** https://data.nasdaq.com/

**Free Tier Limits:**
- **Anonymous users:** 20 calls per 10 minutes, 50 calls per day
- **Registered users (free):** 300 calls per 10 seconds, 2,000 calls per 10 minutes, 50,000 calls per day

**Key Features:**
- 765,000+ time series datasets
- Economic data
- Financial data
- Alternative data
- Some datasets are free, others require paid subscription
- Historical data for stocks, futures, forex
- Python SDK, Excel Add-in, API access

**Authentication:**
- API key optional but recommended (free registration)

**Python Library:**
```bash
pip install nasdaq-data-link
```

```python
import nasdaqdatalink

nasdaqdatalink.ApiConfig.api_key = 'YOUR_API_KEY'

# Get data from a dataset
data = nasdaqdatalink.get('WIKI/AAPL')

# Get specific date range
data = nasdaqdatalink.get('WIKI/AAPL', start_date='2023-01-01', end_date='2023-12-31')

# Get specific columns
data = nasdaqdatalink.get('WIKI/AAPL', columns=['Close', 'Volume'])

# Search for datasets
results = nasdaqdatalink.search('crude oil', per_page=10)
```

---

### 9. Marketstack
**URL:** https://marketstack.com/

**Free Tier Limits:**
- 100 API requests per month
- HTTPS not available in free tier
- No intraday data (daily only)

**Key Features:**
- 125,000+ stock tickers
- 72+ worldwide stock exchanges
- 30 years of historical data
- End-of-day prices
- Intraday data (paid plans only)
- Market indices

**Authentication:**
- API key required (free registration)

**Python Library:**
```python
import requests

API_KEY = 'your_access_key'

# Get end-of-day data
params = {
    'access_key': API_KEY,
    'symbols': 'AAPL'
}

api_result = requests.get('http://api.marketstack.com/v1/eod', params)
data = api_result.json()

# Get intraday data (requires paid plan)
params = {
    'access_key': API_KEY,
    'symbols': 'AAPL',
    'interval': '1hour'
}

api_result = requests.get('http://api.marketstack.com/v1/intraday', params)
intraday_data = api_result.json()
```

---

### 10. EOD Historical Data (EODHD)
**URL:** https://eodhd.com/

**Free Tier Limits:**
- 20 API calls per day
- 1 year of historical data only
- Demo tickers only: AAPL.US, TSLA.US, VTI.US, AMZN.US, BTC-USD.CC, EURUSD.FOREX

**Key Features:**
- 150,000+ tickers worldwide
- End-of-day and intraday data
- Fundamental data
- Technical indicators
- Real-time data (demo tickers only on free tier)
- Stock splits and dividends
- Options data
- Economic calendar

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install eodhd
```

```python
from eodhd import APIClient

api = APIClient("YOUR_API_KEY")

# Get end-of-day data
data = api.get_eod_historical_stock_market_data(
    symbol='AAPL.US',
    period='d',
    from_date='2023-01-01',
    to_date='2023-12-31'
)

# Get real-time data (demo tickers only on free tier)
real_time = api.get_real_time_stock_price(symbol='AAPL.US')

# Get fundamentals
fundamentals = api.get_fundamental_equity(symbol='AAPL.US')

# Get technical indicators
indicators = api.get_technical_indicator(
    symbol='AAPL.US',
    function='sma',
    period=50,
    from_date='2023-01-01',
    to_date='2023-12-31'
)
```

---

### 11. World Trading Data
**URL:** https://www.worldtradingdata.com/

**Free Tier Limits:**
- 60 API requests per minute

**Key Features:**
- Real-time and historical stock data
- Forex data
- Cryptocurrency data
- Intraday data
- Stock search
- Multiple global markets

**Authentication:**
- API key required (free registration)

**Python Library:**
```python
import requests

API_KEY = 'your_api_key'

# Get real-time data
url = f'https://api.worldtradingdata.com/api/v1/stock?symbol=AAPL&api_token={API_KEY}'
response = requests.get(url)
data = response.json()

# Get historical data
url = f'https://api.worldtradingdata.com/api/v1/history?symbol=AAPL&date_from=2023-01-01&api_token={API_KEY}'
historical = requests.get(url).json()

# Get intraday data
url = f'https://api.worldtradingdata.com/api/v1/intraday?symbol=AAPL&interval=1&api_token={API_KEY}'
intraday = requests.get(url).json()
```

---

## Technical Analysis APIs

### 1. TAAPI.IO
**URL:** https://taapi.io/

**Free Tier Limits:**
- Varies by plan (check current pricing)
- Rate limits apply

**Key Features:**
- 200+ technical indicators
- Popular indicators: MA, SMA, EMA, RSI, MACD, Stochastic, StochRSI
- Bollinger Bands, ATR, CCI, Williams %R, ADX
- Works on US stocks, Forex, and cryptocurrencies
- Developer-friendly API
- Real-time calculations
- Historical indicator data

**Authentication:**
- API key required

**Python Library:**
```python
import requests

API_KEY = 'your_api_key'

# Get RSI
url = f'https://api.taapi.io/rsi?secret={API_KEY}&exchange=binance&symbol=BTC/USDT&interval=1h'
response = requests.get(url)
rsi_data = response.json()

# Get MACD
url = f'https://api.taapi.io/macd?secret={API_KEY}&exchange=binance&symbol=BTC/USDT&interval=1d'
macd_data = requests.get(url).json()

# Get multiple indicators at once
url = f'https://api.taapi.io/bulk?secret={API_KEY}'
body = {
    "construct": {
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "interval": "1h",
        "indicators": [
            {"indicator": "rsi"},
            {"indicator": "macd"},
            {"indicator": "bbands"}
        ]
    }
}
response = requests.post(url, json=body)
indicators = response.json()
```

---

### 2. Alpha Vantage (Technical Indicators)
See [Alpha Vantage](#1-alpha-vantage) above for main API details.

**50+ Technical Indicators Include:**
- **Momentum:** RSI, MACD, Stochastic, Williams %R, ADX, CCI, AROON, MOM, BOP
- **Moving Averages:** SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, T3
- **Volatility:** Bollinger Bands, ATR, NATR
- **Volume:** OBV, AD, ADOSC
- **Overlap Studies:** Bollinger Bands, SAR, MIDPOINT, MIDPRICE

**Example:**
```python
import requests

API_KEY = 'your_api_key'
symbol = 'AAPL'

# RSI
url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={API_KEY}'
rsi = requests.get(url).json()

# MACD
url = f'https://www.alphavantage.co/query?function=MACD&symbol={symbol}&interval=daily&series_type=close&apikey={API_KEY}'
macd = requests.get(url).json()

# Bollinger Bands
url = f'https://www.alphavantage.co/query?function=BBANDS&symbol={symbol}&interval=daily&time_period=20&series_type=close&apikey={API_KEY}'
bbands = requests.get(url).json()

# Stochastic
url = f'https://www.alphavantage.co/query?function=STOCH&symbol={symbol}&interval=daily&apikey={API_KEY}'
stoch = requests.get(url).json()
```

---

### 3. TA-Lib (Local Computation)
**URL:** https://github.com/mrjbq7/ta-lib

**Note:** This is not an API but a Python library for computing technical indicators locally using your own data.

**Free Tier Limits:**
- None - runs locally

**Key Features:**
- 200+ technical indicators
- Very fast C-based implementation
- No API calls needed
- Works with any data source

**Python Library:**
```bash
# Installation can be tricky, requires C dependencies
pip install TA-Lib
```

```python
import talib
import numpy as np

# Assuming you have price data
close = np.array([...])  # your close prices
high = np.array([...])
low = np.array([...])
volume = np.array([...])

# Calculate RSI
rsi = talib.RSI(close, timeperiod=14)

# Calculate MACD
macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

# Calculate Bollinger Bands
upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20)

# Calculate SMA
sma = talib.SMA(close, timeperiod=30)

# Calculate EMA
ema = talib.EMA(close, timeperiod=30)

# Many more indicators available
adx = talib.ADX(high, low, close, timeperiod=14)
cci = talib.CCI(high, low, close, timeperiod=14)
stoch_k, stoch_d = talib.STOCH(high, low, close)
```

---

### 4. pandas-ta (Local Computation)
**URL:** https://github.com/twopirllc/pandas-ta

**Note:** Python library for technical analysis, not an API.

**Python Library:**
```bash
pip install pandas-ta
```

```python
import pandas as pd
import pandas_ta as ta

# Load your data into a DataFrame
df = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# Calculate RSI
df['RSI'] = ta.rsi(df['close'], length=14)

# Calculate MACD
macd = ta.macd(df['close'])
df = df.join(macd)

# Calculate Bollinger Bands
bbands = ta.bbands(df['close'], length=20)
df = df.join(bbands)

# Calculate multiple indicators at once
df.ta.strategy(ta.Strategy(
    name="Quick Strategy",
    ta=[
        {"kind": "sma", "length": 50},
        {"kind": "ema", "length": 20},
        {"kind": "rsi"},
        {"kind": "macd"}
    ]
))
```

---

## News & Sentiment Analysis APIs

### 1. Alpha Vantage News Sentiment
See [Alpha Vantage](#1-alpha-vantage) above for main API details.

**Sentiment Features:**
- AI-powered sentiment analysis
- News articles with sentiment scores
- Topic classification
- Ticker relevance scoring
- Real-time and historical news

**Example:**
```python
import requests

API_KEY = 'your_api_key'

# Get news sentiment
url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={API_KEY}'
response = requests.get(url)
news_data = response.json()

# Process sentiment
for article in news_data.get('feed', []):
    print(f"Title: {article['title']}")
    print(f"Overall Sentiment: {article['overall_sentiment_label']}")
    print(f"Sentiment Score: {article['overall_sentiment_score']}")

    # Ticker-specific sentiment
    for ticker_sentiment in article.get('ticker_sentiment', []):
        if ticker_sentiment['ticker'] == 'AAPL':
            print(f"AAPL Sentiment: {ticker_sentiment['ticker_sentiment_label']}")
            print(f"AAPL Score: {ticker_sentiment['ticker_sentiment_score']}")
```

---

### 2. Finnhub News Sentiment
See [Finnhub](#5-finnhub) above for main API details.

**Sentiment Features:**
- Company news sentiment
- Bullish/Bearish percentages
- News article counts
- Buzz and sentiment scores

**Example:**
```python
import finnhub

finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")

# Get news sentiment
sentiment = finnhub_client.news_sentiment('AAPL')

print(f"Buzz: {sentiment['buzz']}")
print(f"Bullish Percent: {sentiment['sentiment']['bullishPercent']}")
print(f"Bearish Percent: {sentiment['sentiment']['bearishPercent']}")

# Get company news
news = finnhub_client.company_news('AAPL', _from='2023-01-01', to='2023-12-31')
for article in news[:5]:
    print(f"Headline: {article['headline']}")
    print(f"Summary: {article['summary']}")
```

---

### 3. NewsAPI
**URL:** https://newsapi.org/

**Free Tier Limits:**
- 100 requests per day
- 1 month of historical data

**Key Features:**
- News from 150,000+ sources
- 13 languages
- Category filtering
- Keyword search
- Source filtering
- Not specifically for financial news but can be filtered

**Authentication:**
- API key required (free registration)

**Python Library:**
```bash
pip install newsapi-python
```

```python
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='YOUR_API_KEY')

# Get stock-related news
articles = newsapi.get_everything(
    q='AAPL OR Apple stock',
    sources='bloomberg,financial-times,wall-street-journal',
    language='en',
    sort_by='publishedAt'
)

for article in articles['articles'][:5]:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']['name']}")
    print(f"Published: {article['publishedAt']}")
    print(f"URL: {article['url']}")
```

---

### 4. Marketaux
**URL:** https://www.marketaux.com/

**Free Tier Limits:**
- 100 API calls per month (check current limits)

**Key Features:**
- Global stock market news
- Financial news aggregation
- Sentiment analysis
- Entity extraction
- Industry filtering
- Real-time news updates

**Authentication:**
- API key required (free registration)

**Python Library:**
```python
import requests

API_KEY = 'your_api_key'

# Get financial news
url = f'https://api.marketaux.com/v1/news/all?symbols=AAPL&filter_entities=true&language=en&api_token={API_KEY}'
response = requests.get(url)
news = response.json()

for article in news.get('data', []):
    print(f"Title: {article['title']}")
    print(f"Published: {article['published_at']}")
    print(f"Sentiment: {article.get('sentiment', 'N/A')}")
    print(f"Entities: {article.get('entities', [])}")
```

---

### 5. Stock News API
**URL:** https://stocknewsapi.com/

**Free Tier Limits:**
- Limited free tier (check website for current limits)

**Key Features:**
- Stock market news aggregation
- Sentiment analysis (positive, negative, neutral)
- News categorization
- Ticker-specific news
- Real-time updates

**Authentication:**
- API key required (free tier available)

**Python Library:**
```python
import requests

API_KEY = 'your_api_key'

# Get news with sentiment
url = f'https://stocknewsapi.com/api/v1?tickers=AAPL&items=50&token={API_KEY}'
response = requests.get(url)
news = response.json()

for article in news.get('data', []):
    print(f"Title: {article['title']}")
    print(f"Sentiment: {article['sentiment']}")
    print(f"Source: {article['source_name']}")
    print(f"URL: {article['news_url']}")
```

---

## Economic Data APIs

### 1. FRED (Federal Reserve Economic Data)
**URL:** https://fred.stlouisfed.org/docs/api/fred/

**Free Tier Limits:**
- Completely free
- Reasonable rate limits for non-commercial use

**Key Features:**
- 765,000+ economic time series
- Data from Federal Reserve and other sources
- GDP, inflation, unemployment, interest rates
- Historical economic data
- No cost, just requires API key

**Authentication:**
- API key required (free registration at https://fredaccount.stlouisfed.org/apikeys)

**Python Library:**
```bash
pip install fredapi
```

```python
from fredapi import Fred

fred = Fred(api_key='YOUR_API_KEY')

# Get GDP data
gdp = fred.get_series('GDP')
print(gdp.tail())

# Get unemployment rate
unemployment = fred.get_series('UNRATE')

# Get federal funds rate
fed_funds = fred.get_series('FEDFUNDS')

# Get inflation (CPI)
cpi = fred.get_series('CPIAUCSL')

# Get S&P 500
sp500 = fred.get_series('SP500')

# Search for series
search_results = fred.search('unemployment rate')
for result in search_results.head():
    print(result['id'], result['title'])

# Get series info
info = fred.get_series_info('GDP')
print(info)
```

---

### 2. World Bank API
**URL:** https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation

**Free Tier Limits:**
- Completely free
- No authentication required for most data

**Key Features:**
- Global economic indicators
- Country-level data
- Development indicators
- Historical data going back decades
- GDP, inflation, trade, demographics

**Authentication:**
- None required (optional registration for higher limits)

**Python Library:**
```bash
pip install wbdata
```

```python
import wbdata
import datetime

# Get indicators
indicators = {
    'NY.GDP.MKTP.CD': 'GDP',
    'SP.POP.TOTL': 'Population'
}

# Get data for specific countries
data = wbdata.get_dataframe(indicators, country=['US', 'CN'])
print(data)

# Get data for a date range
date_range = (datetime.datetime(2015, 1, 1), datetime.datetime(2023, 1, 1))
data = wbdata.get_dataframe(indicators, country='US', data_date=date_range)

# Search for indicators
wbdata.search_indicators('gdp')

# Get all countries
countries = wbdata.get_country()
for country in countries[:5]:
    print(country['name'], country['id'])
```

---

### 3. IMF (International Monetary Fund) API
**URL:** https://www.imf.org/external/datamapper/api/help

**Free Tier Limits:**
- Free access
- No authentication required

**Key Features:**
- Global economic data
- Economic indicators
- Financial statistics
- Country comparisons
- World Economic Outlook data

**Authentication:**
- None required

**Python Library:**
```python
import requests
import pandas as pd

# Get GDP data
url = 'https://www.imf.org/external/datamapper/api/v1/NGDPD'
response = requests.get(url)
gdp_data = response.json()

# Get inflation data
url = 'https://www.imf.org/external/datamapper/api/v1/PCPIPCH'
inflation_data = requests.get(url).json()

# Get data for specific countries
countries = ['USA', 'CHN', 'JPN']
for country in countries:
    if country in gdp_data['values']['NGDPD']:
        print(f"{country}: {gdp_data['values']['NGDPD'][country]}")
```

---

## Trading & Paper Trading APIs

### 1. Alpaca Trading API
**URL:** https://alpaca.markets/

**Free Tier:**
- Paper trading completely free
- Basic market data plan free (IEX exchange for equities)
- No commissions on trades

**Key Features:**
- Commission-free trading
- Paper trading environment with $100K virtual cash
- Real-time market data (limited on free tier)
- Stocks, ETFs, and crypto trading
- Options trading
- Automated trading support
- WebSocket streaming
- Same API for paper and live trading

**Authentication:**
- API key and secret required (free account registration)

**Python Library:**
```bash
pip install alpaca-trade-api
```

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# Paper trading credentials
API_KEY = 'your_api_key'
SECRET_KEY = 'your_secret_key'

# Initialize trading client
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# Get account information
account = trading_client.get_account()
print(f"Buying Power: ${account.buying_power}")
print(f"Portfolio Value: ${account.portfolio_value}")

# Place a market order
market_order_data = MarketOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)
market_order = trading_client.submit_order(order_data=market_order_data)

# Get positions
positions = trading_client.get_all_positions()
for position in positions:
    print(f"{position.symbol}: {position.qty} shares @ ${position.avg_entry_price}")

# Get historical data
data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
request_params = StockBarsRequest(
    symbol_or_symbols="AAPL",
    timeframe=TimeFrame.Day,
    start=datetime(2023, 1, 1)
)
bars = data_client.get_stock_bars(request_params)

# Cancel all orders
trading_client.cancel_orders()
```

---

## Quick Comparison Table

| API | Free Daily Limits | Historical Data | Technical Indicators | Sentiment | Python Library | Best For |
|-----|------------------|-----------------|---------------------|-----------|----------------|----------|
| **Alpha Vantage** | 25 requests/day | 20+ years | 50+ indicators | Yes | alpha-vantage | Technical analysis, beginners |
| **Twelve Data** | 800 requests/day | Extensive | Yes | Limited | twelvedata | Reliable development, global coverage |
| **Polygon.io** | 5 requests/min | Extensive | Limited | No | polygon-api-client | Real-time data, WebSocket |
| **Yahoo Finance** | Unofficial (no limit) | 20+ years | No (compute locally) | No | yfinance | Quick prototyping, personal projects |
| **Finnhub** | 60 requests/min | Limited years | Yes | Yes | finnhub-python | News sentiment, fundamentals |
| **FMP** | 250 requests/day | 30+ years | Yes | No | requests | Fundamental analysis |
| **Tiingo** | 50 symbols/hour | 30+ years | Limited | No | tiingo | Research, validated data |
| **Nasdaq Data Link** | 50,000/day (registered) | Varies by dataset | No | No | nasdaq-data-link | Economic data, alternative data |
| **Marketstack** | 100 requests/month | 30 years | No | No | requests | Simple EOD data |
| **EODHD** | 20 requests/day | 1 year (free) | Yes | No | eodhd | Demo/testing |
| **FRED** | Unlimited (reasonable use) | Decades | No | No | fredapi | Economic indicators |
| **Alpaca** | Unlimited (paper trading) | Free basic plan | No | No | alpaca-trade-api | Paper trading, automation |
| **TAAPI.IO** | Varies | N/A | 200+ indicators | No | requests | Technical indicator calculations |

---

## Machine Learning & Prediction Resources

While most APIs provide data rather than predictions, here are approaches for stock prediction:

### 1. Build Your Own ML Models

**Data Sources:**
- Use APIs above to gather historical data
- Combine price data with technical indicators
- Incorporate sentiment analysis from news APIs
- Add economic indicators from FRED

**Python Libraries for ML:**
```bash
pip install scikit-learn tensorflow keras xgboost lightgbm prophet
```

**Example Workflow:**
```python
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import talib

# Gather data
ticker = yf.Ticker("AAPL")
df = ticker.history(period="5y")

# Add technical indicators
df['RSI'] = talib.RSI(df['Close'])
df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['Close'])
df['SMA_20'] = talib.SMA(df['Close'], timeperiod=20)
df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)

# Create target variable (next day's return)
df['Target'] = df['Close'].pct_change().shift(-1)

# Drop NaN values
df = df.dropna()

# Prepare features
features = ['RSI', 'MACD', 'MACD_signal', 'SMA_20', 'SMA_50', 'Volume']
X = df[features]
y = df['Target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
print(f"MSE: {mse}, R2: {r2}")
```

---

### 2. Sentiment Analysis for Predictions

**Approach:**
```python
import finnhub
from transformers import pipeline
import pandas as pd

# Initialize sentiment analyzer
sentiment_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# Get news
finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
news = finnhub_client.company_news('AAPL', _from='2023-01-01', to='2023-12-31')

# Analyze sentiment
sentiments = []
for article in news:
    result = sentiment_analyzer(article['headline'][:512])[0]
    sentiments.append({
        'date': article['datetime'],
        'headline': article['headline'],
        'sentiment': result['label'],
        'score': result['score']
    })

sentiment_df = pd.DataFrame(sentiments)

# Aggregate daily sentiment
sentiment_df['date'] = pd.to_datetime(sentiment_df['date'], unit='s')
daily_sentiment = sentiment_df.groupby(sentiment_df['date'].dt.date)['score'].mean()

# Combine with price data for prediction model
```

---

### 3. Time Series Forecasting

**Using Facebook Prophet:**
```python
from prophet import Prophet
import yfinance as yf

# Get data
df = yf.download('AAPL', start='2020-01-01', end='2023-12-31')
df = df.reset_index()
df = df[['Date', 'Close']]
df.columns = ['ds', 'y']

# Train model
model = Prophet(daily_seasonality=True)
model.fit(df)

# Make future predictions
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Plot
model.plot(forecast)
model.plot_components(forecast)
```

---

### 4. Deep Learning with LSTM

**Example:**
```python
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf

# Get data
df = yf.download('AAPL', start='2018-01-01', end='2023-12-31')
data = df['Close'].values.reshape(-1, 1)

# Scale data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# Prepare sequences
sequence_length = 60
X, y = [], []
for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i, 0])
    y.append(scaled_data[i, 0])
X, y = np.array(X), np.array(y)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Build LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, y, batch_size=32, epochs=10)

# Make predictions
predictions = model.predict(X)
predictions = scaler.inverse_transform(predictions)
```

---

## Best Practices & Tips

### 1. Rate Limiting
- Implement exponential backoff for retries
- Cache responses when possible
- Use multiple APIs to distribute load
- Consider paid tiers for production use

### 2. Data Quality
- Always validate data from free APIs
- Cross-reference multiple sources
- Handle missing data appropriately
- Be aware of data delays (15-min for some free tiers)

### 3. Cost Management
- Start with free tiers for development
- Monitor your API usage
- Upgrade strategically based on bottlenecks
- Consider cost per use case

### 4. Legal & Terms of Service
- Read each API's terms of service
- Respect rate limits
- Don't redistribute data unless allowed
- Be aware of commercial use restrictions

### 5. Code Example: Multi-API Data Fetcher
```python
import requests
from typing import Dict, List, Optional
import time

class MultiAPIStockData:
    def __init__(self, alpha_vantage_key: str, finnhub_key: str, fmp_key: str):
        self.av_key = alpha_vantage_key
        self.fh_key = finnhub_key
        self.fmp_key = fmp_key

    def get_stock_data(self, symbol: str) -> Dict:
        """Fetch data from multiple APIs with fallback"""
        data = {}

        # Try Alpha Vantage first
        try:
            av_data = self._get_alpha_vantage(symbol)
            data['alpha_vantage'] = av_data
        except Exception as e:
            print(f"Alpha Vantage error: {e}")

        # Try Finnhub as backup
        try:
            fh_data = self._get_finnhub(symbol)
            data['finnhub'] = fh_data
        except Exception as e:
            print(f"Finnhub error: {e}")

        # Try FMP for fundamentals
        try:
            fmp_data = self._get_fmp(symbol)
            data['fmp'] = fmp_data
        except Exception as e:
            print(f"FMP error: {e}")

        return data

    def _get_alpha_vantage(self, symbol: str) -> Dict:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.av_key}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _get_finnhub(self, symbol: str) -> Dict:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.fh_key}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _get_fmp(self, symbol: str) -> Dict:
        url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={self.fmp_key}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

# Usage
fetcher = MultiAPIStockData(
    alpha_vantage_key='YOUR_AV_KEY',
    finnhub_key='YOUR_FH_KEY',
    fmp_key='YOUR_FMP_KEY'
)

data = fetcher.get_stock_data('AAPL')
print(data)
```

---

## Additional Resources

### Python Libraries for Analysis
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib/seaborn**: Data visualization
- **scikit-learn**: Machine learning
- **tensorflow/keras**: Deep learning
- **prophet**: Time series forecasting
- **statsmodels**: Statistical modeling
- **backtrader**: Backtesting trading strategies

### Learning Resources
- **QuantConnect**: Algorithmic trading platform with free tier
- **Quantopian Archive**: Educational materials (platform shut down but resources remain)
- **Kaggle**: Stock prediction competitions and datasets
- **arXiv**: Academic papers on quantitative finance

### Communities
- r/algotrading
- r/quant
- QuantConnect Community
- Elite Trader Forums
- Stack Exchange - Quantitative Finance

---

## Conclusion

This guide covers the major free APIs available for stock market prediction and analysis as of 2026. Key takeaways:

1. **For beginners**: Start with Yahoo Finance (yfinance) or Alpha Vantage
2. **For technical analysis**: Alpha Vantage, TAAPI.IO, or compute locally with TA-Lib
3. **For sentiment analysis**: Finnhub, Alpha Vantage News API
4. **For economic data**: FRED API (completely free and comprehensive)
5. **For paper trading**: Alpaca Trading API
6. **For production**: Consider paid tiers from Polygon, Twelve Data, or Alpha Vantage

Remember that free tiers have limitations. For serious trading or high-frequency applications, paid plans are recommended. Always validate data quality and implement proper error handling and rate limiting in your applications.

---

**Last Updated:** February 2026
**Maintained By:** Stock Market API Research
**License:** Free to use and modify

## Sources

This guide was compiled from the following sources:

- [Alpha Vantage Official Website](https://www.alphavantage.co/)
- [Financial Data APIs Compared (2026)](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
- [Alpha Vantage Complete Guide (2026)](https://alphalog.ai/blog/alphavantage-api-complete-guide)
- [Best Stock APIs (2026)](https://hackernoon.com/best-stock-apis-in-2026-an-in-depth-review)
- [Yahoo Finance API Python Guide](https://python.plainenglish.io/yahoo-finance-api-python-complete-guide-with-examples-limits-and-best-alternatives-7d75342d7482)
- [yfinance PyPI](https://pypi.org/project/yfinance/)
- [IEX Cloud Shutdown Analysis](https://www.alphavantage.co/iexcloud_shutdown_analysis_and_migration/)
- [Finnhub API Documentation](https://finnhub.io/docs/api/rate-limit)
- [Financial Modeling Prep Official Site](https://site.financialmodelingprep.com/)
- [Tiingo Free Data Sources](https://medium.com/@avetik.babayan/free-data-sources-for-stock-api-meet-tiingo-07d967815a80)
- [Nasdaq Data Link Documentation](https://docs.data.nasdaq.com/)
- [NewsAPI Official](https://newsapi.org/)
- [Marketaux Official Site](https://www.marketaux.com/)
- [Marketstack Official Documentation](https://marketstack.com/)
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [EODHD Official Site](https://eodhd.com/)
- [Alpaca Trading API Docs](https://docs.alpaca.markets/)
- [CoinAPI Official Site](https://www.coinapi.io/)
- [TAAPI.IO Official Site](https://taapi.io/)
