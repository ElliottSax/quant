# Hybrid Revenue Model Setup Guide

This document outlines the setup required for the Quant platform's hybrid revenue model.

## Overview

The platform uses a 4-tier subscription model:
- **Free**: Unlimited backtests, ad-supported
- **Starter**: $9.99/month - Ad-free, faster backtests
- **Professional**: $29/month - Advanced features, API access
- **Enterprise**: Custom pricing

## Revenue Streams

1. **Affiliate Commissions** - Broker referral links ($40-75 per signup)
2. **Subscription Revenue** - $9.99 and $29 monthly tiers
3. **Ad Revenue** - Sponsor ads on free tier (trading platforms)
4. **Referral Credits** - Users earn $10 per referred friend

## Environment Variables Required

### Stripe Configuration
```bash
# Stripe API Key
STRIPE_SECRET_KEY=sk_live_xxxxx

# Stripe Price IDs (create these in Stripe Dashboard)
STRIPE_STARTER_PRICE_ID=price_starter_monthly
STRIPE_STARTER_YEARLY_PRICE_ID=price_starter_yearly
STRIPE_PROFESSIONAL_PRICE_ID=price_professional_monthly
STRIPE_PROFESSIONAL_YEARLY_PRICE_ID=price_professional_yearly
STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_monthly
STRIPE_ENTERPRISE_YEARLY_PRICE_ID=price_enterprise_yearly

# Stripe Webhook Secret
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Frontend Configuration
```bash
# Stripe Publishable Key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
```

## Stripe Setup Steps

1. **Create Products in Stripe Dashboard**
   - Navigate to: Products > Add Products
   - Create 4 products: Free, Starter, Professional, Enterprise

2. **Create Price Objects**
   - For each paid tier, create monthly and yearly prices:
     - Starter: $9.99/month, $99.90/year
     - Professional: $29/month, $290/year
     - Enterprise: Use custom pricing in dashboard
   - Copy the Price IDs and add to `.env`

3. **Set Up Webhook**
   - Endpoint: `https://your-domain.com/api/v1/subscriptions/webhooks/stripe`
   - Events: `customer.subscription.created`, `customer.subscription.deleted`, `customer.subscription.updated`
   - Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

4. **Test Keys**
   - Use test keys from Stripe Dashboard in development
   - Switch to live keys in production

## Database Schema

### User Model Updates
The User model now includes:

```python
# Subscription Management (Hybrid Model)
subscription_tier: str  # 'free', 'starter', 'professional', 'enterprise'
stripe_customer_id: Optional[str]
stripe_subscription_id: Optional[str]
subscription_status: Optional[str]  # 'active', 'canceled', 'past_due'
subscription_period_end: Optional[datetime]
ad_free: bool  # For starter+ tiers
trial_started_at: Optional[datetime]
trial_ends_at: Optional[datetime]
trial_used: bool

# Referral System
referral_code: Optional[str]  # Unique per user
referral_credit_balance: float  # $10 per successful referral
referred_by_user_id: Optional[str]

# Usage Tracking
backtests_this_month: int
last_backtest_reset: Optional[datetime]
```

### Migration Required
Run Alembic migration to add these fields:
```bash
cd backend
alembic upgrade head
```

## API Endpoints

### Subscription Endpoints
- `GET /api/v1/subscription/tiers` - Get available tiers
- `GET /api/v1/subscription/status` - Get user's current subscription
- `GET /api/v1/subscription/usage` - Get monthly usage stats
- `POST /api/v1/subscription/upgrade` - Upgrade subscription
- `POST /api/v1/subscription/start-trial` - Start 7-day free trial
- `POST /api/v1/subscription/cancel` - Cancel subscription
- `GET /api/v1/subscription/referral/code` - Get referral code
- `POST /api/v1/subscription/referral/track` - Track referral signup

### Affiliate Endpoints
- `GET /api/v1/affiliate/brokers/recommendations` - Get broker recommendations
- `GET /api/v1/affiliate/brokers/all` - Get all available brokers
- `POST /api/v1/affiliate/track-click` - Track affiliate link click
- `GET /api/v1/affiliate/link/{broker_name}` - Get tracking link with UTM

## Frontend Components

### New Components Added

1. **AdBanner** (`components/ads/AdBanner.tsx`)
   - Displays ads for free tier users
   - Sponsor ads for trading platforms
   - Upgrade prompts

2. **ReferralCode** (`components/referral/ReferralCode.tsx`)
   - Display referral code
   - Share functionality
   - Credit balance tracking

3. **SubscriptionStatus** (`components/subscription/SubscriptionStatus.tsx`)
   - Current tier display
   - Trial countdown
   - Features list
   - Upgrade button

4. **Pricing Page** (`app/pricing/page.tsx`)
   - 3 tier comparison
   - Billing cycle toggle
   - CTA buttons with Stripe integration

5. **FreeTrialBanner** (`components/upsell/FreeTrialBanner.tsx`)
   - Prominent trial offer
   - Limited time messaging

6. **FeatureComparison** (`components/upsell/FeatureComparison.tsx`)
   - Interactive tier comparison
   - Feature matrix
   - Pricing details

## Testing Checklist

### Backend Testing
- [ ] Create user → assigned to free tier
- [ ] Free tier → unlimited backtests
- [ ] Upgrade to Starter → charges $9.99, removes ads
- [ ] Upgrade to Professional → charges $29, enables API access
- [ ] Free trial → 7-day trial without payment
- [ ] Referral signup → referrer gets $10 credit
- [ ] Affiliate click tracking → recorded in database
- [ ] Stripe webhook → subscription updates on renewal/cancellation

### Frontend Testing
- [ ] Pricing page loads all 3 tiers
- [ ] CTA buttons route to checkout
- [ ] Referral code displays correctly
- [ ] Ad banner shows only for free tier
- [ ] Trial countdown shows correct days
- [ ] Affiliate links track clicks

### Integration Testing
- [ ] Free → Starter upgrade flow
- [ ] Starter → Professional upgrade flow
- [ ] Professional → cancel downgrade to free
- [ ] Trial expiration → downgrades to free
- [ ] Referral code validation → adds credit

## Revenue Projections

At scale (100K users):
- **Free tier users (90%)**: 90,000 users
  - 5% convert to Starter: 4,500 × $9.99 × 12 = $540K/year
  - 1% convert to Professional: 900 × $29 × 12 = $313K/year
- **Affiliate commissions**: 90K × 20% clicks × 5% conversions × $50 avg = $450K/year
- **Ad revenue**: 90K × $0.25 CPM × 100 impressions/user/month = $270K/year
- **Total annual revenue**: ~$1.6M

## Important Notes

1. **Free tier is unlimited** - No quota enforcement to maximize growth
2. **Ad-free at $9.99** - Low friction upgrade option
3. **Professional for power users** - API access + alerts for $29
4. **Enterprise for organizations** - Custom pricing, white label
5. **Affiliate links prominent** - Multiple placements in results
6. **Trial removes ads** - Converted users keep ad-free experience

## Support & Debugging

- Stripe Dashboard: Monitor subscriptions and payments
- Webhook Events: Check for failed payment attempts
- User Model: Check tier, trial dates, referral credits
- Affiliate Events: Track clicks and conversions

For issues:
- Check `.env` has all required Stripe keys
- Verify Stripe webhook is configured
- Ensure database migration was applied
- Check browser console for frontend errors
