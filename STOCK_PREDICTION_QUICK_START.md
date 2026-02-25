# Stock Prediction Features - Quick Start Guide

## 🚀 What's Been Added

Three new services have been added to enable stock market prediction:

1. **Market Data Client** - Multi-provider data fetching with automatic fallback
2. **Technical Analysis** - 130+ indicators and 60+ candlestick patterns
3. **Prediction API** - RESTful endpoints for predictions and signals

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
cd /mnt/e/projects/quant/quant/backend

# Install prediction dependencies
pip install -r requirements-prediction.txt

# Or install individually
pip install yfinance alpha_vantage twelvedata finnhub-python
pip install pandas-ta xgboost
```

### Step 2: Install TA-Lib (Optional but Recommended)

**Mac/Linux:**
```bash
# Mac with Homebrew
brew install ta-lib
pip install TA-Lib

# Ubuntu/Debian
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**Windows (WSL recommended):**
```bash
# Use conda (easier on Windows)
conda install -c conda-forge ta-lib
pip install TA-Lib
```

**Without TA-Lib:** The system falls back to pandas-ta for indicators.

### Step 3: Get API Keys (Free)

1. **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
   - Free: 25 requests/day
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

2. **Twelve Data**: https://twelvedata.com/
   - Free: 800 requests/day
   - Add to `.env`: `TWELVE_DATA_API_KEY=your_key`

3. **Finnhub**: https://finnhub.io/register
   - Free: 60 requests/minute
   - Add to `.env`: `FINNHUB_API_KEY=your_key`

**Note:** yfinance works without API keys (unlimited but unofficial).

### Step 4: Update `.env` File

```bash
cd /mnt/e/projects/quant/quant/backend
nano .env  # or vim, code, etc.
```

Add these lines:
```bash
# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
TWELVE_DATA_API_KEY=your_twelve_data_key
FINNHUB_API_KEY=your_finnhub_key

# Prediction Settings
PREDICTION_CACHE_TTL=3600  # Cache predictions for 1 hour
MODEL_STORAGE_PATH=/path/to/store/ml/models
```

### Step 5: Update FastAPI Main App

Add the prediction router to `app/main.py`:

```python
from app.api.v1 import prediction

# Add to your router includes
app.include_router(prediction.router, prefix="/api/v1")
```

### Step 6: Test the Installation

```bash
cd /mnt/e/projects/quant/quant/backend

# Start the backend
uvicorn app.main:app --reload

# In another terminal, test the endpoints
curl http://localhost:8000/api/v1/prediction/indicators \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1y"}'
```

---

## 🔥 Usage Examples

### 1. Get Technical Indicators

```python
import httpx
import asyncio

async def get_indicators():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/prediction/indicators",
            json={
                "symbol": "AAPL",
                "period": "1y",
                "interval": "1d"
            }
        )
        return response.json()

result = asyncio.run(get_indicators())
print(f"RSI: {result['indicators']['rsi']}")
print(f"Signal: {result['signals']['overall']}")
```

### 2. Scan for Candlestick Patterns

```bash
curl -X POST "http://localhost:8000/api/v1/prediction/patterns/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA"],
    "pattern_types": ["CDLHAMMER", "CDLENGULFING", "CDLMORNINGSTAR"]
  }'
```

### 3. Get Stock Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/prediction/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "period": "1y",
    "horizon": 5
  }'
```

Response:
```json
{
  "symbol": "AAPL",
  "current_price": 180.25,
  "predicted_prices": [181.05, 181.86, 182.68, 183.51, 184.34],
  "predicted_direction": "UP",
  "confidence": 0.65,
  "technical_signals": {
    "rsi": "HOLD",
    "macd": "BUY",
    "ma_crossover": "BUY",
    "overall": "BUY"
  },
  "recommendation": "BUY"
}
```

### 4. Get Daily Trading Signals

```bash
curl "http://localhost:8000/api/v1/prediction/signals/daily?symbols=AAPL&symbols=TSLA&symbols=GOOGL"
```

### 5. Use in Python

```python
from app.services.market_data import MarketDataClient
from app.services.technical_analysis import IndicatorCalculator, PatternDetector

# Initialize
market_data = MarketDataClient()
indicator_calc = IndicatorCalculator()
pattern_detector = PatternDetector()

# Fetch data
df = await market_data.get_historical_data("AAPL", period="1y")

# Calculate indicators
indicators = indicator_calc.calculate_all(df)
print(f"Current RSI: {indicators['current']['rsi']}")
print(f"Signal: {indicators['signals']['overall']}")

# Detect patterns
patterns = pattern_detector.detect_all_patterns(df)
print(f"Current patterns: {patterns['current']}")

await market_data.close()
```

---

## 📊 Available Indicators

### Momentum (9 indicators)
- RSI (Relative Strength Index)
- Stochastic Oscillator (K, D)
- Williams %R
- Rate of Change (ROC)
- Money Flow Index (MFI)
- Commodity Channel Index (CCI)

### Trend (11 indicators)
- SMA (20, 50, 200)
- EMA (12, 26)
- MACD (MACD, Signal, Histogram)
- ADX (ADX, +DI, -DI)
- Aroon (Up, Down)

### Volatility (12 indicators)
- Bollinger Bands (Upper, Middle, Lower, Bandwidth)
- ATR (Average True Range)
- Keltner Channels (Upper, Middle, Lower)
- Donchian Channels (Upper, Middle, Lower)

### Volume (4 indicators)
- OBV (On-Balance Volume)
- CMF (Chaikin Money Flow)
- VWAP (Volume Weighted Average Price)
- PVT (Price Volume Trend)

**Total: 50+ indicators**

---

## 🕯️ Candlestick Patterns (60+)

### Bullish Reversal
- Hammer, Inverted Hammer
- Bullish Engulfing, Piercing Pattern
- Morning Star, Morning Doji Star
- Dragonfly Doji
- Three White Soldiers

### Bearish Reversal
- Shooting Star, Hanging Man
- Bearish Engulfing, Dark Cloud Cover
- Evening Star, Evening Doji Star
- Gravestone Doji
- Three Black Crows

### Indecision
- Doji, Long-Legged Doji
- Spinning Top, High Wave

**And 40+ more patterns...**

---

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/prediction/predict` | POST | Get ML prediction for a stock |
| `/api/v1/prediction/indicators` | POST | Calculate technical indicators |
| `/api/v1/prediction/patterns/scan` | POST | Scan multiple stocks for patterns |
| `/api/v1/prediction/signals/daily` | GET | Get daily trading signals |
| `/api/v1/prediction/batch` | POST | Batch predictions (up to 50 stocks) |

---

## 🔄 Data Provider Fallback Order

The system tries providers in this order:

1. **yfinance** (unlimited, free)
2. **Twelve Data** (800 req/day)
3. **Alpha Vantage** (25 req/day)
4. **Finnhub** (60 req/min)

If one provider fails, it automatically tries the next.

---

## ⚡ Performance Tips

### 1. Enable Redis Caching
```python
# In your FastAPI app
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)
market_data = MarketDataClient(redis_client=redis_client)
```

### 2. Batch Requests
```python
# Instead of individual requests
symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']
results = await batch_predict(symbols=symbols)
```

### 3. Cache Strategy
- Market data: 1 hour TTL
- Indicators: 1 hour TTL
- Predictions: 1 hour TTL
- Quotes: 5 minutes TTL

### 4. Use Background Tasks
```python
from fastapi import BackgroundTasks

@app.post("/predict-async")
async def predict_async(symbol: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_prediction, symbol)
    return {"status": "processing"}
```

---

## 🐛 Troubleshooting

### Issue: "TA-Lib not installed"
**Solution**: The system falls back to pandas-ta. For full pattern detection, install TA-Lib (see Step 2).

### Issue: "Rate limit exceeded"
**Solution**:
- Enable Redis caching
- Use multiple API keys
- Upgrade to paid tier if needed

### Issue: "No data found for symbol"
**Solution**:
- Check symbol is valid (use uppercase: "AAPL" not "aapl")
- Try different provider: `force_provider=Provider.YFINANCE`
- Check API key is valid

### Issue: "Import error for pandas_ta"
**Solution**:
```bash
pip install pandas-ta --upgrade
```

### Issue: "Slow performance"
**Solution**:
- Enable Redis caching
- Use batch endpoints
- Reduce historical period (use "3mo" instead of "5y")
- Use daily interval instead of intraday

---

## 📚 Next Steps

### Phase 1 Complete ✅
- Market data integration
- Technical analysis
- Basic API endpoints

### Phase 2: ML Models (Next)
1. Train LSTM model on historical data
2. Implement XGBoost ensemble
3. Add FinRL reinforcement learning agent
4. Create ensemble prediction logic
5. Add confidence scoring

### Phase 3: Frontend
1. Create prediction dashboard
2. Add interactive charts
3. Build pattern scanner UI
4. Create backtesting interface

### Phase 4: Production
1. Add comprehensive tests
2. Implement monitoring
3. Set up scheduled predictions
4. Deploy to production

---

## 📖 Documentation

- **Full Integration Plan**: `STOCK_PREDICTION_INTEGRATION_PLAN.md`
- **Free APIs Guide**: `free_stock_market_apis.md` (from research)
- **GitHub Repos**: See research agent output
- **API Documentation**: http://localhost:8000/docs (when running)

---

## 💡 Tips

1. **Start with yfinance** - It's unlimited and works well for most use cases
2. **Get API keys early** - Some take 24h to activate
3. **Use Redis** - Dramatically improves performance
4. **Test with popular stocks first** - AAPL, TSLA, GOOGL have best data coverage
5. **Monitor rate limits** - Log all API calls to track usage

---

## 🎉 You're Ready!

The stock prediction infrastructure is now set up. Start with:

```bash
# Test basic functionality
curl http://localhost:8000/api/v1/prediction/indicators \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

**Happy Trading!** 📈
