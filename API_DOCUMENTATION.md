# API Documentation - Quant Trading Platform

**Version**: 1.0.0
**Last Updated**: January 26, 2026
**Base URL**: `https://api.yourplatform.com` (production) or `http://localhost:8000` (development)

---

## 📚 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication-endpoints)
  - [Statistics](#statistics-endpoints)
  - [Market Data](#market-data-endpoints)
  - [Politicians](#politicians-endpoints)
  - [Trades](#trades-endpoints)
  - [Export](#export-endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Pagination](#pagination)
- [Filtering & Sorting](#filtering--sorting)
- [Best Practices](#best-practices)

---

## 🌟 Overview

The Quant Trading Platform API provides programmatic access to political stock trading data, market information, and advanced analytics. The API follows REST principles and returns JSON responses.

### Key Features

- **Real-time Market Data**: Access live stock quotes and historical price data
- **Political Trade Tracking**: Monitor stock trades by government officials
- **Advanced Analytics**: Pattern detection, regime analysis, and predictive models
- **Data Export**: Download data in multiple formats (JSON, CSV, Excel, Markdown)
- **Secure Authentication**: JWT-based authentication with 2FA support
- **Rate Limiting**: Fair usage policies to ensure platform stability

### API Conventions

- **HTTP Methods**: `GET` for retrieval, `POST` for creation, `PUT`/`PATCH` for updates, `DELETE` for removal
- **Status Codes**: Standard HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- **Date Format**: ISO 8601 format (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- **Timestamps**: UTC timezone
- **IDs**: UUIDs (universally unique identifiers)

---

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Most endpoints require authentication, though some public endpoints are available without auth.

### Registration

Create a new user account:

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "trader123",
  "password": "SecurePassword123!"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "trader123",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-26T12:00:00.000Z"
}
```

### Login

Obtain an access token:

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the `Authorization` header:

```bash
GET /api/v1/stats/overview
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh

Tokens expire after 1 hour. Refresh your token:

```bash
POST /api/v1/auth/refresh
Authorization: Bearer <your_current_token>
```

### Logout

Invalidate your token:

```bash
POST /api/v1/auth/logout
Authorization: Bearer <your_token>
```

---

## ⏱️ Rate Limiting

To ensure fair usage and platform stability, API requests are rate-limited:

| Tier | Per Minute | Per Hour | Notes |
|------|------------|----------|-------|
| Anonymous | 30 req/min | 500 req/hour | Public endpoints only |
| Authenticated | 60 req/min | 2000 req/hour | Standard users |
| Premium | 120 req/min | 5000 req/hour | Premium subscribers |
| API Key | 300 req/min | 15000 req/hour | Dedicated API access |

### Rate Limit Headers

Response headers indicate your current rate limit status:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642345678
```

### Rate Limit Exceeded

When rate limit is exceeded, you'll receive:

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "status_code": 429,
  "retry_after": 30
}
```

---

## ❌ Error Handling

The API uses standard HTTP status codes and returns consistent error responses.

### Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or invalid |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary outage |

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "error_code": "INVALID_PARAMETER",
  "field": "email",
  "timestamp": "2026-01-26T12:00:00.000Z"
}
```

### Common Error Codes

- `INVALID_CREDENTIALS`: Login failed
- `INVALID_PARAMETER`: Bad request parameter
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INSUFFICIENT_PERMISSIONS`: Forbidden action
- `VALIDATION_ERROR`: Request validation failed

---

## 📊 API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "trader123",
  "password": "SecurePassword123!"
}
```

**Validation Rules**:
- Email: Valid email format, unique
- Username: 3-50 characters, alphanumeric + underscore
- Password: Min 8 characters, 1 uppercase, 1 lowercase, 1 number

---

#### POST /api/v1/auth/login
Authenticate and receive access token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

#### POST /api/v1/auth/logout
Invalidate current token (requires auth).

**Headers**: `Authorization: Bearer <token>`

**Response**: 204 No Content

---

#### GET /api/v1/auth/me
Get current user information (requires auth).

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "trader123",
  "is_active": true,
  "created_at": "2026-01-26T12:00:00.000Z"
}
```

---

### Statistics Endpoints

#### GET /api/v1/stats/overview
Get platform statistics overview.

**Query Parameters**: None

**Response**:
```json
{
  "total_trades": 15234,
  "total_politicians": 535,
  "total_tickers": 1247,
  "total_value": "1250000000.00",
  "last_updated": "2026-01-26T12:00:00.000Z",
  "average_trades_per_day": 42.5
}
```

**Caching**: 5 minutes

---

#### GET /api/v1/stats/leaderboard
Get politician trading leaderboard.

**Query Parameters**:
- `limit` (int, default: 20, max: 100): Number of results
- `days` (int, default: 30): Time range in days
- `sort_by` (string, default: "total_trades"): Sort field

**Response**:
```json
{
  "leaderboard": [
    {
      "politician_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "party": "Independent",
      "state": "CA",
      "chamber": "senate",
      "total_trades": 145,
      "total_value": "5000000.00",
      "win_rate": 0.67,
      "rank": 1
    }
  ],
  "count": 20,
  "total": 535
}
```

---

#### GET /api/v1/stats/tickers
Get most traded ticker symbols.

**Query Parameters**:
- `limit` (int, default: 20, max: 100): Number of results

**Response**:
```json
{
  "tickers": [
    {
      "ticker": "AAPL",
      "trade_count": 423,
      "politician_count": 87,
      "total_value": "45000000.00",
      "buy_count": 245,
      "sell_count": 178
    }
  ],
  "count": 20
}
```

---

#### GET /api/v1/stats/by-party
Get trading statistics by political party.

**Response**:
```json
{
  "parties": [
    {
      "party": "Democratic",
      "total_trades": 7821,
      "total_politicians": 268,
      "average_trades_per_politician": 29.2,
      "total_value": "650000000.00"
    }
  ]
}
```

---

#### GET /api/v1/stats/volume
Get trade volume over time.

**Query Parameters**:
- `start_date` (date, ISO format): Start date
- `end_date` (date, ISO format): End date

**Response**:
```json
{
  "data": [
    {
      "date": "2026-01-20",
      "trade_count": 45,
      "buy_count": 28,
      "sell_count": 17,
      "total_value": "2500000.00"
    }
  ],
  "start_date": "2026-01-01",
  "end_date": "2026-01-26"
}
```

---

### Market Data Endpoints

#### GET /api/v1/market-data/public/quote/{symbol}
Get real-time quote for a symbol (no auth required).

**Path Parameters**:
- `symbol` (string): Stock ticker symbol

**Query Parameters**:
- `provider` (string, default: "yahoo_finance"): Data provider

**Response**:
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 2.50,
  "change_percent": 1.69,
  "volume": 45678900,
  "bid": 150.24,
  "ask": 150.26,
  "high": 151.00,
  "low": 148.50,
  "open": 149.00,
  "previous_close": 147.75,
  "timestamp": "2026-01-26T16:00:00.000Z"
}
```

---

#### GET /api/v1/market-data/public/quotes
Get quotes for multiple symbols (no auth required).

**Query Parameters**:
- `symbols` (array[string], max: 20): Stock ticker symbols

**Example**:
```bash
GET /api/v1/market-data/public/quotes?symbols=AAPL&symbols=GOOGL&symbols=MSFT
```

**Response**:
```json
{
  "quotes": {
    "AAPL": {
      "symbol": "AAPL",
      "price": 150.25,
      "change": 2.50
    },
    "GOOGL": {
      "symbol": "GOOGL",
      "price": 2850.00,
      "change": -15.30
    }
  },
  "count": 2,
  "timestamp": "2026-01-26T16:00:00.000Z"
}
```

**Note**: Authenticated users can request up to 50 symbols.

---

#### GET /api/v1/market-data/public/historical/{symbol}
Get historical price data (no auth required).

**Path Parameters**:
- `symbol` (string): Stock ticker symbol

**Query Parameters**:
- `start_date` (datetime, ISO): Start date/time
- `end_date` (datetime, ISO, optional): End date/time (default: now)
- `interval` (string, default: "1d"): Data interval (1m, 5m, 15m, 1h, 1d)

**Example**:
```bash
GET /api/v1/market-data/public/historical/AAPL?start_date=2026-01-01T00:00:00Z&end_date=2026-01-26T23:59:59Z&interval=1d
```

**Response**:
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-26T23:59:59Z",
  "bars": [
    {
      "timestamp": "2026-01-01T00:00:00Z",
      "open": 145.00,
      "high": 147.50,
      "low": 144.25,
      "close": 146.75,
      "volume": 52000000
    }
  ],
  "count": 26
}
```

**Limits**:
- Public: Max 1 year range
- Authenticated: Max 10 years range

---

#### GET /api/v1/market-data/public/company/{symbol}
Get company information (no auth required).

**Response**:
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "description": "Apple Inc. designs, manufactures, and markets smartphones...",
  "website": "https://www.apple.com",
  "employees": 164000,
  "market_cap": 2500000000000,
  "pe_ratio": 25.5
}
```

---

#### GET /api/v1/market-data/public/market-status
Get current market status (no auth required).

**Response**:
```json
{
  "is_open": true,
  "market": "US",
  "timestamp": "2026-01-26T16:00:00Z",
  "message": "Market is open"
}
```

---

### Politicians Endpoints

#### GET /api/v1/politicians
List all politicians (requires auth).

**Query Parameters**:
- `limit` (int, default: 20, max: 100): Results per page
- `offset` (int, default: 0): Pagination offset
- `chamber` (string, optional): Filter by chamber (senate, house)
- `party` (string, optional): Filter by party
- `state` (string, optional): Filter by state

**Response**:
```json
{
  "politicians": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "chamber": "senate",
      "party": "Independent",
      "state": "CA",
      "bioguide_id": "D000001",
      "trade_count": 145,
      "last_trade_date": "2026-01-25"
    }
  ],
  "count": 20,
  "total": 535,
  "limit": 20,
  "offset": 0
}
```

---

#### GET /api/v1/politicians/{politician_id}
Get politician details (requires auth).

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "chamber": "senate",
  "party": "Independent",
  "state": "CA",
  "bioguide_id": "D000001",
  "district": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2026-01-26T12:00:00Z",
  "statistics": {
    "total_trades": 145,
    "total_value": "5000000.00",
    "win_rate": 0.67,
    "first_trade": "2024-01-15",
    "last_trade": "2026-01-25"
  }
}
```

---

### Trades Endpoints

#### GET /api/v1/trades
List all trades (requires auth).

**Query Parameters**:
- `limit` (int, default: 20, max: 100)
- `offset` (int, default: 0)
- `politician_id` (uuid, optional): Filter by politician
- `ticker` (string, optional): Filter by ticker
- `transaction_type` (string, optional): buy, sell, exchange
- `start_date` (date, optional): Filter by date range
- `end_date` (date, optional): Filter by date range

**Response**:
```json
{
  "trades": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "politician_id": "550e8400-e29b-41d4-a716-446655440000",
      "politician_name": "John Doe",
      "ticker": "AAPL",
      "transaction_type": "buy",
      "transaction_date": "2026-01-20",
      "disclosure_date": "2026-01-25",
      "amount_min": "1000.00",
      "amount_max": "15000.00",
      "source_url": "https://example.com/disclosure/123"
    }
  ],
  "count": 20,
  "total": 15234,
  "limit": 20,
  "offset": 0
}
```

---

### Export Endpoints

#### GET /api/v1/export/trades/{politician_id}
Export trade data for a politician.

**Query Parameters**:
- `format` (string, default: "csv"): Export format (json, csv, xlsx, md)
- `start_date` (date, optional): Filter start date
- `end_date` (date, optional): Filter end date

**Response**: File download with appropriate content-type

**Example**:
```bash
GET /api/v1/export/trades/550e8400-e29b-41d4-a716-446655440000?format=csv
```

Returns CSV file with headers:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="John_Doe_trades.csv"
```

---

#### GET /api/v1/export/analysis/{politician_id}
Export pattern analysis results.

**Query Parameters**:
- `format` (string, default: "json"): Export format (json, md)
- `include_fourier` (bool, default: true): Include Fourier analysis
- `include_hmm` (bool, default: true): Include regime detection
- `include_dtw` (bool, default: true): Include pattern matching

**Response**:
```json
{
  "politician": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe"
  },
  "export_date": "2026-01-26T12:00:00Z",
  "analyses": {
    "fourier": {
      "total_trades": 145,
      "dominant_cycles": [
        {
          "period_days": 30,
          "category": "monthly",
          "strength": 0.85,
          "confidence": 0.92
        }
      ]
    },
    "hmm": {
      "current_regime": "high_activity",
      "confidence": 0.87
    },
    "dtw": {
      "matches_found": 12,
      "prediction_30d": 5.2
    }
  }
}
```

---

## 📝 Request/Response Examples

### Python Example

```python
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
email = "user@example.com"
password = "SecurePassword123!"

# 1. Register
response = requests.post(
    f"{API_BASE_URL}/api/v1/auth/register",
    json={
        "email": email,
        "username": "trader123",
        "password": password
    }
)
print(f"Registration: {response.status_code}")

# 2. Login
response = requests.post(
    f"{API_BASE_URL}/api/v1/auth/login",
    json={
        "email": email,
        "password": password
    }
)
token = response.json()["access_token"]
print(f"Token: {token[:20]}...")

# 3. Set up headers
headers = {"Authorization": f"Bearer {token}"}

# 4. Get statistics
response = requests.get(
    f"{API_BASE_URL}/api/v1/stats/overview",
    headers=headers
)
stats = response.json()
print(f"Total trades: {stats['total_trades']}")

# 5. Get leaderboard
response = requests.get(
    f"{API_BASE_URL}/api/v1/stats/leaderboard?limit=10",
    headers=headers
)
leaderboard = response.json()
print(f"Top trader: {leaderboard['leaderboard'][0]['name']}")

# 6. Get market quote
response = requests.get(
    f"{API_BASE_URL}/api/v1/market-data/public/quote/AAPL"
)
quote = response.json()
print(f"AAPL price: ${quote['price']}")

# 7. Get multiple quotes
response = requests.get(
    f"{API_BASE_URL}/api/v1/market-data/public/quotes",
    params={"symbols": ["AAPL", "GOOGL", "MSFT"]},
    headers=headers
)
quotes = response.json()
print(f"Got {quotes['count']} quotes")

# 8. Logout
response = requests.post(
    f"{API_BASE_URL}/api/v1/auth/logout",
    headers=headers
)
print(f"Logout: {response.status_code}")
```

---

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

// Create API client
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Authentication flow
async function authenticate() {
  // Login
  const loginResponse = await api.post('/api/v1/auth/login', {
    email: 'user@example.com',
    password: 'SecurePassword123!'
  });

  const { access_token } = loginResponse.data;

  // Set token for future requests
  api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

  return access_token;
}

// Get platform statistics
async function getStats() {
  const response = await api.get('/api/v1/stats/overview');
  return response.data;
}

// Get leaderboard
async function getLeaderboard(limit = 20) {
  const response = await api.get('/api/v1/stats/leaderboard', {
    params: { limit }
  });
  return response.data;
}

// Get market quote
async function getQuote(symbol) {
  const response = await api.get(`/api/v1/market-data/public/quote/${symbol}`);
  return response.data;
}

// Main execution
async function main() {
  try {
    // Authenticate
    await authenticate();
    console.log('Authenticated successfully');

    // Get stats
    const stats = await getStats();
    console.log(`Total trades: ${stats.total_trades}`);

    // Get leaderboard
    const leaderboard = await getLeaderboard(10);
    console.log(`Top trader: ${leaderboard.leaderboard[0].name}`);

    // Get quote
    const quote = await getQuote('AAPL');
    console.log(`AAPL price: $${quote.price}`);

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();
```

---

### cURL Examples

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "trader123",
    "password": "SecurePassword123!"
  }'

# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }' | jq -r '.access_token')

# Get stats (authenticated)
curl http://localhost:8000/api/v1/stats/overview \
  -H "Authorization: Bearer $TOKEN"

# Get public quote
curl http://localhost:8000/api/v1/market-data/public/quote/AAPL

# Get leaderboard with filters
curl "http://localhost:8000/api/v1/stats/leaderboard?limit=10&days=30" \
  -H "Authorization: Bearer $TOKEN"

# Export trades as CSV
curl "http://localhost:8000/api/v1/export/trades/{politician-id}?format=csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o trades.csv
```

---

## 📄 Pagination

Endpoints that return lists support pagination:

**Query Parameters**:
- `limit` (int, default: 20, max: 100): Items per page
- `offset` (int, default: 0): Number of items to skip

**Response**:
```json
{
  "items": [...],
  "count": 20,
  "total": 535,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

**Example**:
```bash
# Page 1
GET /api/v1/politicians?limit=20&offset=0

# Page 2
GET /api/v1/politicians?limit=20&offset=20

# Page 3
GET /api/v1/politicians?limit=20&offset=40
```

---

## 🔍 Filtering & Sorting

### Filtering

Most list endpoints support filtering via query parameters:

```bash
# Filter politicians by party
GET /api/v1/politicians?party=Democratic

# Filter trades by ticker
GET /api/v1/trades?ticker=AAPL

# Filter by date range
GET /api/v1/trades?start_date=2026-01-01&end_date=2026-01-31

# Combine filters
GET /api/v1/trades?ticker=AAPL&transaction_type=buy&start_date=2026-01-01
```

### Sorting

Some endpoints support sorting:

```bash
# Sort leaderboard by total value
GET /api/v1/stats/leaderboard?sort_by=total_value

# Sort in descending order (default)
GET /api/v1/stats/leaderboard?sort_by=total_trades&order=desc

# Sort in ascending order
GET /api/v1/stats/leaderboard?sort_by=name&order=asc
```

---

## ✅ Best Practices

### 1. Authentication
- **Store tokens securely**: Use environment variables or secure storage
- **Refresh tokens proactively**: Don't wait for 401 errors
- **Handle token expiration**: Implement automatic refresh logic

### 2. Error Handling
- **Check status codes**: Don't assume success
- **Parse error responses**: Extract meaningful error messages
- **Implement retry logic**: For 429 (rate limit) and 5xx errors
- **Log errors**: Track API issues for debugging

### 3. Rate Limiting
- **Respect rate limits**: Monitor `X-RateLimit-*` headers
- **Implement backoff**: Exponential backoff for retries
- **Cache responses**: Cache data when appropriate
- **Batch requests**: Use multi-symbol endpoints when possible

### 4. Performance
- **Use compression**: Enable gzip compression
- **Paginate large results**: Don't fetch all data at once
- **Use filters**: Request only the data you need
- **Cache aggressively**: Many endpoints have server-side caching

### 5. Data Export
- **Use appropriate formats**: CSV for spreadsheets, JSON for programs
- **Stream large files**: Don't load entire files into memory
- **Respect server resources**: Avoid frequent large exports

### 6. Security
- **Use HTTPS in production**: Never send tokens over HTTP
- **Validate SSL certificates**: Don't disable certificate verification
- **Sanitize user input**: When constructing queries from user data
- **Log security events**: Track authentication failures

---

## 📞 Support

- **Documentation**: [https://docs.yourplatform.com](https://docs.yourplatform.com)
- **API Status**: [https://status.yourplatform.com](https://status.yourplatform.com)
- **Support Email**: support@yourplatform.com
- **GitHub**: [https://github.com/yourorg/quant-platform](https://github.com/yourorg/quant-platform)

---

## 📋 Changelog

### Version 1.0.0 (2026-01-26)
- Initial API release
- Authentication endpoints
- Statistics endpoints
- Market data endpoints
- Export functionality
- Rate limiting
- Comprehensive documentation

---

**Last Updated**: January 26, 2026
**API Version**: 1.0.0
