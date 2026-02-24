# SECURITY HARDENING GUIDE

## Frontend Security Enhancements

### Issue 1: Missing Error Boundaries

**Create Global Error Boundary:**

```typescript
// app/error.tsx (Root error boundary)
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const router = useRouter()

  useEffect(() => {
    // Log error to monitoring service
    console.error('Application error:', error)

    // Send to error tracking (e.g., Sentry)
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error)
    }
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-destructive mb-4">
            Something went wrong!
          </h2>
          <p className="text-muted-foreground mb-8">
            We're sorry, but something unexpected happened.
            {error.digest && (
              <span className="block mt-2 text-sm">
                Error ID: {error.digest}
              </span>
            )}
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => reset()}
              className="btn-primary"
            >
              Try again
            </button>
            <button
              onClick={() => router.push('/')}
              className="btn-secondary"
            >
              Go home
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}


// app/dashboard/error.tsx (Scoped error boundary)
'use client'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div className="p-8 bg-destructive/10 rounded-lg">
      <h3 className="text-xl font-semibold text-destructive mb-2">
        Dashboard Error
      </h3>
      <p className="text-sm text-muted-foreground mb-4">
        Failed to load dashboard data
      </p>
      <button onClick={() => reset()} className="btn-sm btn-primary">
        Retry
      </button>
    </div>
  )
}
```

---

### Issue 2: Content Security Policy (CSP)

**Add Security Headers:**

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()'
  },
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.vercel-insights.com;
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' https://api.yourdomain.com wss://api.yourdomain.com;
      frame-ancestors 'self';
      base-uri 'self';
      form-action 'self';
    `.replace(/\s{2,}/g, ' ').trim()
  }
]

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
}
```

---

### Issue 3: XSS Protection via Input Sanitization

**Create Sanitization Utility:**

```typescript
// lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify'

/**
 * Sanitize HTML to prevent XSS attacks
 */
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'title'],
  })
}

/**
 * Sanitize user input (remove HTML entirely)
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .trim()
}

/**
 * Escape HTML special characters
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  }
  return text.replace(/[&<>"'/]/g, (char) => map[char])
}

/**
 * Validate and sanitize URL
 */
export function sanitizeUrl(url: string): string {
  try {
    const parsed = new URL(url)
    // Only allow http and https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return ''
    }
    return parsed.href
  } catch {
    return ''
  }
}
```

**Usage in Components:**

```typescript
// components/PoliticianBio.tsx
import { sanitizeHtml } from '@/lib/sanitize'

export function PoliticianBio({ bio }: { bio: string }) {
  return (
    <div
      dangerouslySetInnerHTML={{
        __html: sanitizeHtml(bio)
      }}
    />
  )
}

// components/TradeForm.tsx
import { sanitizeInput } from '@/lib/sanitize'

export function TradeForm() {
  const handleSubmit = (data: FormData) => {
    const ticker = sanitizeInput(data.get('ticker') as string)
    const notes = sanitizeInput(data.get('notes') as string)

    // ... submit sanitized data
  }
}
```

---

### Issue 4: CSRF Protection

**Implement CSRF Token:**

```typescript
// lib/csrf.ts
import { cookies } from 'next/headers'
import crypto from 'crypto'

const CSRF_TOKEN_NAME = 'csrf_token'
const CSRF_HEADER_NAME = 'X-CSRF-Token'

/**
 * Generate CSRF token
 */
export function generateCsrfToken(): string {
  return crypto.randomBytes(32).toString('hex')
}

/**
 * Get or create CSRF token
 */
export async function getCsrfToken(): Promise<string> {
  const cookieStore = cookies()
  let token = cookieStore.get(CSRF_TOKEN_NAME)?.value

  if (!token) {
    token = generateCsrfToken()
    cookieStore.set(CSRF_TOKEN_NAME, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 60 * 60 * 24, // 24 hours
    })
  }

  return token
}

/**
 * Verify CSRF token
 */
export async function verifyCsrfToken(token: string): Promise<boolean> {
  const cookieStore = cookies()
  const storedToken = cookieStore.get(CSRF_TOKEN_NAME)?.value

  if (!storedToken || !token) {
    return false
  }

  // Constant-time comparison to prevent timing attacks
  return crypto.timingSafeEqual(
    Buffer.from(storedToken),
    Buffer.from(token)
  )
}
```

**Add CSRF Middleware:**

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyCsrfToken } from './lib/csrf'

export async function middleware(request: NextRequest) {
  // Only check CSRF for state-changing methods
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method)) {
    const token = request.headers.get('X-CSRF-Token')

    if (!token || !(await verifyCsrfToken(token))) {
      return NextResponse.json(
        { error: 'Invalid CSRF token' },
        { status: 403 }
      )
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
```

**Usage in API Client:**

```typescript
// lib/api-client.ts
import { getCsrfToken } from './csrf'

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Add CSRF token for state-changing requests
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || 'GET')) {
    const csrfToken = await getCsrfToken()
    options.headers = {
      ...options.headers,
      'X-CSRF-Token': csrfToken,
    }
  }

  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}
```

---

## Backend Security Enhancements

### Issue 5: SQL Injection Prevention Audit

**Review and Secure Raw SQL:**

```python
# app/utils/query_validator.py
"""
SQL injection prevention utilities.
"""

import re
from app.core.exceptions import BadRequestException

ALLOWED_SORT_COLUMNS = {
    'trades': ['transaction_date', 'disclosure_date', 'ticker', 'amount_min'],
    'politicians': ['name', 'party', 'state', 'chamber'],
}

def validate_sort_column(table: str, column: str) -> str:
    """
    Validate sort column to prevent SQL injection.

    Args:
        table: Table name
        column: Column name

    Returns:
        Validated column name

    Raises:
        BadRequestException: If column is invalid
    """
    if table not in ALLOWED_SORT_COLUMNS:
        raise BadRequestException(f"Invalid table: {table}")

    allowed_columns = ALLOWED_SORT_COLUMNS[table]

    if column not in allowed_columns:
        raise BadRequestException(
            f"Invalid sort column. Allowed: {', '.join(allowed_columns)}"
        )

    return column


def validate_identifier(identifier: str) -> str:
    """
    Validate SQL identifier (table/column name).

    Args:
        identifier: Identifier to validate

    Returns:
        Validated identifier

    Raises:
        BadRequestException: If identifier is invalid
    """
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise BadRequestException(f"Invalid identifier: {identifier}")

    # Prevent SQL keywords
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'EXEC', 'EXECUTE', 'UNION', 'WHERE', 'FROM'
    ]

    if identifier.upper() in sql_keywords:
        raise BadRequestException(f"SQL keyword not allowed: {identifier}")

    return identifier
```

---

### Issue 6: Sensitive Data Logging Filter

**Implement Log Sanitization:**

```python
# app/core/logging.py

import re
from typing import Any

# Patterns that might contain sensitive data
SENSITIVE_PATTERNS = [
    (re.compile(r'("password"\s*:\s*")[^"]*(")', re.IGNORECASE), r'\1***REDACTED***\2'),
    (re.compile(r'("token"\s*:\s*")[^"]*(")', re.IGNORECASE), r'\1***REDACTED***\2'),
    (re.compile(r'("secret"\s*:\s*")[^"]*(")', re.IGNORECASE), r'\1***REDACTED***\2'),
    (re.compile(r'("api_key"\s*:\s*")[^"]*(")', re.IGNORECASE), r'\1***REDACTED***\2'),
    (re.compile(r'("authorization"\s*:\s*")[^"]*(")', re.IGNORECASE), r'\1***REDACTED***\2'),
    # Email addresses
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), r'***EMAIL***'),
    # Credit cards (simple pattern)
    (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), r'***CARD***'),
]


def sanitize_log_message(message: str) -> str:
    """
    Remove sensitive data from log messages.

    Args:
        message: Log message

    Returns:
        Sanitized message
    """
    sanitized = message

    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


class SanitizingFormatter(logging.Formatter):
    """Log formatter that sanitizes sensitive data."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with sanitization."""
        # Sanitize the message
        original_msg = record.getMessage()
        record.msg = sanitize_log_message(original_msg)

        # Format normally
        formatted = super().format(record)

        return formatted


def setup_logging():
    """Set up application logging with sanitization."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Create sanitizing formatter
    formatter = SanitizingFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ... rest of logging setup with sanitizing formatter
```

---

### Issue 7: Rate Limiting Documentation

**Document Rate Limits in OpenAPI:**

```python
# app/api/v1/auth.py

from fastapi import APIRouter, status
from fastapi.openapi.models import Response as OpenAPIResponse

router = APIRouter()

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Login successful",
            "headers": {
                "X-RateLimit-Limit": {
                    "description": "Request limit per window",
                    "schema": {"type": "integer"}
                },
                "X-RateLimit-Remaining": {
                    "description": "Remaining requests in current window",
                    "schema": {"type": "integer"}
                },
                "X-RateLimit-Reset": {
                    "description": "Unix timestamp when limit resets",
                    "schema": {"type": "integer"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rate limit exceeded",
                        "limit": 5,
                        "remaining": 0,
                        "reset": 1704067200,
                        "tier": "free"
                    }
                }
            }
        }
    },
    summary="User login",
    description="""
    Authenticate user and return JWT tokens.

    **Rate Limits:**
    - Free tier: 5 requests/minute
    - Basic tier: 10 requests/minute
    - Premium tier: 20 requests/minute

    **Security:**
    - Account locks after 5 failed attempts
    - Lockout duration: 30 minutes
    """
)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    """Login endpoint with documented rate limits."""
    # ... implementation
    pass
```

---

### Issue 8: Secrets Management

**Integrate with Environment-Based Secrets:**

```python
# app/core/secrets.py
"""
Secrets management with support for multiple backends.
"""

import os
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from app.core.logging import get_logger

logger = get_logger(__name__)


class SecretBackend(ABC):
    """Abstract base for secret backends."""

    @abstractmethod
    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret value."""
        pass


class EnvironmentSecrets(SecretBackend):
    """Get secrets from environment variables."""

    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from environment."""
        return os.getenv(key)


class AWSSecretsManager(SecretBackend):
    """Get secrets from AWS Secrets Manager."""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None

    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            import boto3
            from botocore.exceptions import ClientError

            if not self._client:
                self._client = boto3.client('secretsmanager', region_name=self.region)

            response = self._client.get_secret_value(SecretId=key)
            return response['SecretString']

        except ClientError as e:
            logger.error(f"Failed to get secret from AWS: {e}")
            return None
        except ImportError:
            logger.error("boto3 not installed. Install with: pip install boto3")
            return None


class HashiCorpVault(SecretBackend):
    """Get secrets from HashiCorp Vault."""

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    async def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault."""
        try:
            import hvac

            client = hvac.Client(url=self.url, token=self.token)
            secret = client.secrets.kv.v2.read_secret_version(path=key)
            return secret['data']['data']['value']

        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            return None


class SecretsManager:
    """Unified secrets management."""

    def __init__(self):
        """Initialize with appropriate backend based on environment."""
        env = os.getenv('ENVIRONMENT', 'development')

        if env == 'production':
            # Try AWS first, fall back to environment
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            if os.getenv('AWS_ACCESS_KEY_ID'):
                self.backend = AWSSecretsManager(region=aws_region)
                logger.info("Using AWS Secrets Manager")
            else:
                self.backend = EnvironmentSecrets()
                logger.info("Using environment variables for secrets")
        else:
            self.backend = EnvironmentSecrets()
            logger.info("Using environment variables for secrets (development)")

    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value.

        Args:
            key: Secret key
            default: Default value if not found

        Returns:
            Secret value or default
        """
        value = await self.backend.get_secret(key)
        return value if value is not None else default


# Global instance
secrets_manager = SecretsManager()
```

**Update Configuration:**

```python
# app/core/config.py

from app.core.secrets import secrets_manager

class Settings(BaseSettings):
    # ... existing fields ...

    @classmethod
    async def load_secrets(cls) -> "Settings":
        """Load configuration with secrets from secrets manager."""
        settings = cls()

        # Override with secrets from backend if available
        if settings.ENVIRONMENT == "production":
            db_password = await secrets_manager.get("DATABASE_PASSWORD")
            if db_password:
                settings.POSTGRES_PASSWORD = db_password

            secret_key = await secrets_manager.get("SECRET_KEY")
            if secret_key:
                settings.SECRET_KEY = secret_key

            # ... other secrets ...

        return settings
```

---

## Security Checklist

### Application Security
- [ ] Error boundaries on all pages
- [ ] Content Security Policy configured
- [ ] XSS protection via input sanitization
- [ ] CSRF tokens implemented
- [ ] SQL injection prevention audited
- [ ] Sensitive data filtered from logs
- [ ] Rate limits documented in API
- [ ] Secrets management configured

### Authentication & Authorization
- [x] JWT tokens with expiration
- [x] Refresh token rotation
- [x] Account lockout after failed attempts
- [ ] Email verification on registration
- [ ] Password reset flow
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (optional)

### Data Protection
- [ ] Encryption at rest (database)
- [ ] Encryption in transit (TLS/SSL)
- [ ] PII data anonymization
- [ ] GDPR compliance features
- [ ] Data retention policies
- [ ] Secure file uploads

### Infrastructure
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] API gateway with WAF
- [ ] DDoS protection
- [ ] Regular security scans
- [ ] Dependency vulnerability scanning

### Monitoring & Incident Response
- [ ] Security event logging
- [ ] Anomaly detection
- [ ] Intrusion detection system
- [ ] Incident response plan
- [ ] Security breach notifications
- [ ] Regular security audits

## Testing Security

```python
# tests/test_security/test_xss_protection.py
"""Test XSS protection."""

def test_xss_in_trade_notes(client: TestClient, auth_headers: dict):
    """Test XSS attempts are blocked."""
    response = client.post(
        "/api/v1/trades",
        headers=auth_headers,
        json={
            "ticker": "AAPL",
            "notes": "<script>alert('XSS')</script>",
            # ... other fields
        }
    )

    # Should either reject or sanitize
    assert response.status_code in [400, 201]

    if response.status_code == 201:
        data = response.json()
        assert "<script>" not in data["notes"]


# tests/test_security/test_sql_injection.py
"""Test SQL injection protection."""

def test_sql_injection_in_ticker(client: TestClient):
    """Test SQL injection attempts are blocked."""
    response = client.get(
        "/api/v1/trades",
        params={"ticker": "AAPL' OR '1'='1"}
    )

    # Should return 400 Bad Request, not expose SQL error
    assert response.status_code == 400
    assert "invalid ticker" in response.json()["detail"].lower()


# tests/test_security/test_rate_limiting.py
"""Test rate limiting."""

import asyncio

async def test_rate_limit_enforcement(client: TestClient):
    """Test rate limiting works."""
    # Make requests rapidly
    responses = []
    for i in range(10):
        response = client.get("/api/v1/trades")
        responses.append(response.status_code)

    # Should see 429 (Too Many Requests) eventually
    assert 429 in responses
```

## Penetration Testing

```bash
# scripts/security_scan.sh
#!/bin/bash

echo "=== Security Scan ==="

# 1. Dependency vulnerabilities
echo "Checking for vulnerable dependencies..."
pip-audit

# 2. OWASP ZAP scan
echo "Running OWASP ZAP..."
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8000 \
    -r zap_report.html

# 3. SQL injection scan
echo "Testing for SQL injection..."
sqlmap -u "http://localhost:8000/api/v1/trades?ticker=AAPL" \
    --batch --smart

# 4. SSL/TLS check
echo "Checking SSL/TLS configuration..."
testssl.sh https://yourdomain.com

# 5. Security headers
echo "Checking security headers..."
curl -I https://yourdomain.com | grep -E "(X-|Strict-|Content-Security)"

echo "=== Scan Complete ==="
```

## Security Incident Response Plan

1. **Detection**: Monitor logs for suspicious activity
2. **Assessment**: Determine scope and severity
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore normal operations
6. **Post-Incident**: Review and improve

