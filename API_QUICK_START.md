# API Quick Start Guide

**Get started with the Quant Trading Platform API in 5 minutes!**

---

## 🚀 Quick Start

### 1. Get Your API Token

```bash
# Register a new account
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "username": "your_username",
    "password": "SecurePass123!"
  }'

# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "SecurePass123!"
  }'

# Save the access_token from the response
export API_TOKEN="your_access_token_here"
```

### 2. Make Your First Request

```bash
# Get platform statistics
curl http://localhost:8000/api/v1/stats/overview \
  -H "Authorization: Bearer $API_TOKEN"
```

### 3. Explore the Data

```bash
# Get top trading politicians
curl "http://localhost:8000/api/v1/stats/leaderboard?limit=10" \
  -H "Authorization: Bearer $API_TOKEN"

# Get market quote (no auth required)
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL

# Get politician trades
curl "http://localhost:8000/api/v1/trades?limit=20" \
  -H "Authorization: Bearer $API_TOKEN"
```

---

## 💻 Code Examples

### Python

```python
import requests

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "your@email.com"
PASSWORD = "SecurePass123!"

# Login
response = requests.post(
    f"{API_URL}/api/v1/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)
token = response.json()["access_token"]

# Set up headers
headers = {"Authorization": f"Bearer {token}"}

# Get statistics
stats = requests.get(f"{API_URL}/api/v1/stats/overview", headers=headers).json()
print(f"Total trades: {stats['total_trades']}")

# Get leaderboard
leaderboard = requests.get(
    f"{API_URL}/api/v1/stats/leaderboard?limit=5",
    headers=headers
).json()

for i, politician in enumerate(leaderboard['leaderboard'], 1):
    print(f"{i}. {politician['name']} - {politician['total_trades']} trades")
```

### JavaScript

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

async function main() {
  // Login
  const loginResp = await axios.post(`${API_URL}/api/v1/auth/login`, {
    email: 'your@email.com',
    password: 'SecurePass123!'
  });

  const token = loginResp.data.access_token;

  // Set up axios with token
  const api = axios.create({
    baseURL: API_URL,
    headers: { Authorization: `Bearer ${token}` }
  });

  // Get statistics
  const stats = await api.get('/api/v1/stats/overview');
  console.log(`Total trades: ${stats.data.total_trades}`);

  // Get leaderboard
  const leaderboard = await api.get('/api/v1/stats/leaderboard?limit=5');
  leaderboard.data.leaderboard.forEach((pol, i) => {
    console.log(`${i+1}. ${pol.name} - ${pol.total_trades} trades`);
  });
}

main();
```

---

## 🔑 Common Use Cases

### 1. Monitor a Politician's Trades

```python
politician_id = "550e8400-e29b-41d4-a716-446655440000"

# Get politician details
politician = requests.get(
    f"{API_URL}/api/v1/politicians/{politician_id}",
    headers=headers
).json()

# Get their trades
trades = requests.get(
    f"{API_URL}/api/v1/trades?politician_id={politician_id}&limit=20",
    headers=headers
).json()

print(f"{politician['name']} recent trades:")
for trade in trades['trades']:
    print(f"- {trade['transaction_date']}: {trade['transaction_type']} "
          f"{trade['ticker']} ${trade['amount_min']}-${trade['amount_max']}")
```

### 2. Track Popular Stocks

```python
# Get most traded tickers
tickers = requests.get(
    f"{API_URL}/api/v1/stats/tickers?limit=10",
    headers=headers
).json()

for ticker in tickers['tickers']:
    print(f"{ticker['ticker']}: {ticker['trade_count']} trades "
          f"by {ticker['politician_count']} politicians")
```

### 3. Export Data for Analysis

```python
# Export trades to CSV
politician_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(
    f"{API_URL}/api/v1/export/trades/{politician_id}?format=csv",
    headers=headers
)

# Save to file
with open('trades.csv', 'wb') as f:
    f.write(response.content)

print("Trades exported to trades.csv")
```

### 4. Monitor Market in Real-Time

```python
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

# Get quotes (no auth needed)
response = requests.get(
    f"{API_URL}/api/v1/market-data/public/quotes",
    params={'symbols': symbols}
)

quotes = response.json()['quotes']
for symbol, quote in quotes.items():
    print(f"{symbol}: ${quote['price']} ({quote['change_percent']:+.2f}%)")
```

---

## 📖 Interactive Documentation

Visit the interactive API docs at:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

These provide:
- Complete API reference
- Try-it-out functionality
- Request/response examples
- Schema definitions

---

## 🔗 Next Steps

1. **Read Full Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Explore Schemas**: [API_SCHEMAS.md](API_SCHEMAS.md)
3. **Set Up Rate Limiting**: Understand limits and best practices
4. **Enable 2FA**: Secure your account
5. **Get API Key**: For higher rate limits

---

## 💡 Tips

- **Cache responses**: Many endpoints cache for 5 minutes
- **Use filters**: Request only the data you need
- **Batch requests**: Use multi-symbol endpoints
- **Handle errors**: Check status codes and retry on 429/5xx
- **Monitor limits**: Check `X-RateLimit-*` headers

---

## 🆘 Need Help?

- **Documentation**: Full API docs in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Support**: support@yourplatform.com
- **Issues**: https://github.com/yourorg/quant-platform/issues

---

**Happy Coding!** 🚀
