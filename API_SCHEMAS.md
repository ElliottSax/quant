# API Schemas & Data Models

**Version**: 1.0.0
**Last Updated**: January 26, 2026

---

## 📚 Table of Contents

- [Overview](#overview)
- [Authentication Schemas](#authentication-schemas)
- [User Schemas](#user-schemas)
- [Politician Schemas](#politician-schemas)
- [Trade Schemas](#trade-schemas)
- [Market Data Schemas](#market-data-schemas)
- [Statistics Schemas](#statistics-schemas)
- [Error Schemas](#error-schemas)

---

## Overview

This document describes all data schemas used in the Quant Trading Platform API. All schemas follow Pydantic models for validation.

### Data Types

- **string**: Text data
- **integer**: Whole numbers
- **number**: Decimal numbers (float)
- **boolean**: true/false
- **date**: ISO 8601 date (YYYY-MM-DD)
- **datetime**: ISO 8601 datetime with timezone
- **uuid**: Universally unique identifier
- **array**: List of items
- **object**: Nested JSON object

---

## Authentication Schemas

### UserRegisterRequest

User registration request body.

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| email | string | ✅ | Valid email, unique | User email address |
| username | string | ✅ | 3-50 chars, alphanumeric+underscore | Unique username |
| password | string | ✅ | Min 8 chars, 1 upper, 1 lower, 1 number | Password |

**Example**:
```json
{
  "email": "user@example.com",
  "username": "trader123",
  "password": "SecurePassword123!"
}
```

---

### UserLoginRequest

User login request body.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | ✅ | User email address |
| password | string | ✅ | User password |

**Example**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

---

### TokenResponse

Authentication token response.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT access token |
| token_type | string | Always "bearer" |
| expires_in | integer | Seconds until expiration (3600) |

**Example**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## User Schemas

### User

User account information.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | uuid | ✅ | Unique user identifier |
| email | string | ✅ | User email address |
| username | string | ✅ | Unique username |
| is_active | boolean | ✅ | Account active status |
| is_superuser | boolean | ✅ | Admin privileges |
| created_at | datetime | ✅ | Account creation timestamp |
| updated_at | datetime | ✅ | Last update timestamp |
| last_login | datetime | ❌ | Last login timestamp |
| email_verified | boolean | ✅ | Email verification status |
| two_factor_enabled | boolean | ✅ | 2FA enabled status |

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "trader123",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-01-26T12:00:00.000Z",
  "updated_at": "2026-01-26T12:00:00.000Z",
  "last_login": "2026-01-26T11:30:00.000Z",
  "email_verified": true,
  "two_factor_enabled": false
}
```

---

## Politician Schemas

### Politician

Political official information.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | uuid | ✅ | Unique politician identifier |
| name | string | ✅ | Full name |
| chamber | string | ✅ | "senate" or "house" |
| party | string | ✅ | Political party |
| state | string | ✅ | Two-letter state code |
| district | string | ❌ | District number (House only) |
| bioguide_id | string | ✅ | Bioguide identifier |
| created_at | datetime | ✅ | Record creation timestamp |
| updated_at | datetime | ✅ | Last update timestamp |

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "chamber": "senate",
  "party": "Independent",
  "state": "CA",
  "district": null,
  "bioguide_id": "D000001",
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2026-01-26T12:00:00.000Z"
}
```

**Enums**:
- **chamber**: `"senate"`, `"house"`
- **party**: `"Democratic"`, `"Republican"`, `"Independent"`, `"Other"`

---

### PoliticianWithStats

Politician with trading statistics.

**Extends**: Politician

**Additional Fields**:

| Field | Type | Description |
|-------|------|-------------|
| trade_count | integer | Total number of trades |
| total_value | string (decimal) | Total trading value |
| win_rate | number | Success rate (0.0-1.0) |
| first_trade_date | date | Date of first trade |
| last_trade_date | date | Date of most recent trade |
| average_trade_value | string (decimal) | Average trade value |

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "chamber": "senate",
  "party": "Independent",
  "state": "CA",
  "trade_count": 145,
  "total_value": "5000000.00",
  "win_rate": 0.67,
  "first_trade_date": "2024-01-15",
  "last_trade_date": "2026-01-25",
  "average_trade_value": "34482.76"
}
```

---

## Trade Schemas

### Trade

Stock trade transaction.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | uuid | ✅ | Unique trade identifier |
| politician_id | uuid | ✅ | Related politician ID |
| ticker | string | ✅ | Stock ticker symbol |
| transaction_type | string | ✅ | Type of transaction |
| transaction_date | date | ✅ | Date of transaction |
| disclosure_date | date | ✅ | Date disclosed |
| amount_min | string (decimal) | ✅ | Minimum amount |
| amount_max | string (decimal) | ✅ | Maximum amount |
| source_url | string | ✅ | Source disclosure URL |
| created_at | datetime | ✅ | Record creation timestamp |
| updated_at | datetime | ✅ | Last update timestamp |

**Example**:
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "politician_id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "AAPL",
  "transaction_type": "buy",
  "transaction_date": "2026-01-20",
  "disclosure_date": "2026-01-25",
  "amount_min": "1000.00",
  "amount_max": "15000.00",
  "source_url": "https://example.com/disclosure/123",
  "created_at": "2026-01-25T12:00:00.000Z",
  "updated_at": "2026-01-25T12:00:00.000Z"
}
```

**Enums**:
- **transaction_type**: `"buy"`, `"sell"`, `"exchange"`, `"partial_buy"`, `"partial_sell"`

---

### TradeWithPolitician

Trade with politician details included.

**Extends**: Trade

**Additional Fields**:

| Field | Type | Description |
|-------|------|-------------|
| politician_name | string | Politician's name |
| politician_party | string | Politician's party |
| politician_state | string | Politician's state |
| politician_chamber | string | Politician's chamber |

**Example**:
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "politician_id": "550e8400-e29b-41d4-a716-446655440000",
  "politician_name": "John Doe",
  "politician_party": "Independent",
  "politician_state": "CA",
  "politician_chamber": "senate",
  "ticker": "AAPL",
  "transaction_type": "buy",
  "transaction_date": "2026-01-20",
  "disclosure_date": "2026-01-25",
  "amount_min": "1000.00",
  "amount_max": "15000.00"
}
```

---

## Market Data Schemas

### MarketQuote

Real-time market quote.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | string | ✅ | Stock ticker symbol |
| price | number | ✅ | Current price |
| change | number | ✅ | Price change |
| change_percent | number | ✅ | Percent change |
| volume | integer | ✅ | Trading volume |
| bid | number | ❌ | Bid price |
| ask | number | ❌ | Ask price |
| high | number | ❌ | Day high |
| low | number | ❌ | Day low |
| open | number | ❌ | Opening price |
| previous_close | number | ❌ | Previous close |
| timestamp | datetime | ✅ | Quote timestamp |

**Example**:
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

### MarketBar

Historical price bar (OHLCV).

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| timestamp | datetime | ✅ | Bar timestamp |
| open | number | ✅ | Opening price |
| high | number | ✅ | Highest price |
| low | number | ✅ | Lowest price |
| close | number | ✅ | Closing price |
| volume | integer | ✅ | Trading volume |

**Example**:
```json
{
  "timestamp": "2026-01-26T00:00:00.000Z",
  "open": 149.00,
  "high": 151.00,
  "low": 148.50,
  "close": 150.25,
  "volume": 52000000
}
```

---

### CompanyInfo

Company information.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| symbol | string | ✅ | Stock ticker symbol |
| name | string | ✅ | Company name |
| sector | string | ❌ | Business sector |
| industry | string | ❌ | Industry classification |
| description | string | ❌ | Company description |
| website | string | ❌ | Company website |
| employees | integer | ❌ | Number of employees |
| market_cap | number | ❌ | Market capitalization |
| pe_ratio | number | ❌ | Price-to-earnings ratio |

**Example**:
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

## Statistics Schemas

### StatsOverview

Platform statistics overview.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| total_trades | integer | Total number of trades |
| total_politicians | integer | Total number of politicians |
| total_tickers | integer | Total unique ticker symbols |
| total_value | string (decimal) | Total trading value |
| average_trades_per_day | number | Average daily trades |
| last_updated | datetime | Last update timestamp |

**Example**:
```json
{
  "total_trades": 15234,
  "total_politicians": 535,
  "total_tickers": 1247,
  "total_value": "1250000000.00",
  "average_trades_per_day": 42.5,
  "last_updated": "2026-01-26T12:00:00.000Z"
}
```

---

### LeaderboardEntry

Politician leaderboard entry.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| politician_id | uuid | Politician ID |
| name | string | Politician name |
| party | string | Political party |
| state | string | State |
| chamber | string | Chamber |
| total_trades | integer | Total number of trades |
| total_value | string (decimal) | Total trading value |
| win_rate | number | Success rate (0.0-1.0) |
| rank | integer | Leaderboard rank |

**Example**:
```json
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
```

---

### TickerStats

Ticker trading statistics.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| ticker | string | Stock ticker symbol |
| trade_count | integer | Number of trades |
| politician_count | integer | Number of politicians trading |
| total_value | string (decimal) | Total trading value |
| buy_count | integer | Number of buy transactions |
| sell_count | integer | Number of sell transactions |

**Example**:
```json
{
  "ticker": "AAPL",
  "trade_count": 423,
  "politician_count": 87,
  "total_value": "45000000.00",
  "buy_count": 245,
  "sell_count": 178
}
```

---

## Error Schemas

### ErrorResponse

Standard error response.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| detail | string | ✅ | Human-readable error message |
| status_code | integer | ✅ | HTTP status code |
| error_code | string | ❌ | Machine-readable error code |
| field | string | ❌ | Field that caused error (validation) |
| timestamp | datetime | ✅ | Error timestamp |

**Example**:
```json
{
  "detail": "Email already registered",
  "status_code": 400,
  "error_code": "EMAIL_EXISTS",
  "field": "email",
  "timestamp": "2026-01-26T12:00:00.000Z"
}
```

---

### ValidationError

Field validation error.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| field | string | Field name |
| message | string | Validation error message |
| type | string | Error type |

**Example**:
```json
{
  "detail": "Validation error",
  "status_code": 422,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "type": "value_error"
    }
  ]
}
```

---

## Pagination Schema

### PaginatedResponse

Generic paginated response wrapper.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| items | array | List of items (type varies) |
| count | integer | Number of items in this page |
| total | integer | Total number of items |
| limit | integer | Items per page |
| offset | integer | Offset from start |
| has_more | boolean | More items available |

**Example**:
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

---

## Field Validation Rules

### Common Rules

- **UUID**: Valid UUID v4 format
- **Email**: Valid email format, max 255 characters
- **Password**: Min 8 characters, 1 uppercase, 1 lowercase, 1 number
- **Username**: 3-50 characters, alphanumeric + underscore
- **Ticker**: 1-10 uppercase letters
- **Amount**: Positive decimal, max 2 decimal places
- **Date**: ISO 8601 format (YYYY-MM-DD)
- **Datetime**: ISO 8601 with timezone

### String Lengths

- **email**: Max 255 characters
- **username**: 3-50 characters
- **name**: Max 255 characters
- **ticker**: 1-10 characters
- **party**: Max 50 characters
- **state**: 2 characters (uppercase)
- **chamber**: Max 10 characters

### Number Ranges

- **limit**: 1-100
- **offset**: >= 0
- **days**: 1-3650 (10 years max)
- **win_rate**: 0.0-1.0

---

**Last Updated**: January 26, 2026
**API Version**: 1.0.0
