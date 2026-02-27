# Deployment Guide - Hybrid Revenue Model

## Overview

This guide covers deploying the Quant platform with the hybrid revenue model to production.

## Pre-Deployment Checklist

### Phase 1: Configuration & Secrets (1 hour)

#### Backend Environment Setup
```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/quant_db
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_STARTER_PRICE_ID=price_xxxxx
STRIPE_STARTER_YEARLY_PRICE_ID=price_xxxxx
STRIPE_PROFESSIONAL_PRICE_ID=price_xxxxx
STRIPE_PROFESSIONAL_YEARLY_PRICE_ID=price_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=false
```

#### Frontend Environment Setup
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://api.quant.platform.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
```

### Phase 2: Database Setup (30 min)

Database migration has already been applied (010_add_hybrid_model_fields).

**Production Database Setup:**
- Create PostgreSQL database
- Run Alembic migrations
- Verify new columns exist: ad_free, referral_code, referral_credit_balance, referred_by_user_id

### Phase 3: Build & Testing (1 hour)

#### Backend Build
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend Build
```bash
cd frontend
npm run build
npm run start
```

### Phase 4: Production Deployment

**Backend:**
- Deploy to production environment
- Verify database connectivity
- Test Stripe webhook endpoint

**Frontend:**
- Deploy to Vercel/production host
- Verify critical pages load
- Test subscription flow

## Success Criteria

✅ All when:
- Website loads < 3 seconds
- API responds < 200ms (p95)
- Error rate < 0.1%
- Stripe webhooks 100% success
- 3+ successful test subscriptions

## Support

For deployment issues, check logs and error monitoring dashboards.
