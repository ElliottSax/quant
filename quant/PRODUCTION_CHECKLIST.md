# Production Deployment Checklist

## Pre-Deployment (72 hours before)

### Planning
- [ ] Notify team of deployment date/time
- [ ] Plan rollback procedure
- [ ] Schedule post-deployment monitoring
- [ ] Prepare communication for users

### Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Test subscription upgrade flow (use Stripe test keys)
- [ ] Test referral code generation
- [ ] Test webhook processing
- [ ] Verify all components build without errors

### Staging Verification
- [ ] Deploy to staging environment
- [ ] Run full end-to-end tests
- [ ] Verify database migrations
- [ ] Test Stripe integration (test mode)
- [ ] Monitor staging for 24 hours

## Deployment Day (4 hours before)

### Pre-Deployment Verification
- [ ] All PRs merged and reviewed
- [ ] Latest code pulled
- [ ] Environment variables ready
- [ ] Database backup created
- [ ] Rollback plan documented

### 1 Hour Before Deployment

```bash
# Verify builds
npm run build  # Frontend
pytest tests/ -v  # Backend

# Check environment variables
env | grep STRIPE
env | grep DATABASE

# Verify service health on staging
curl https://staging.quant.platform.com/health
```

## Deployment Steps

### Step 1: Database Migration (5 min)
```bash
cd backend
alembic current  # Verify current revision
# Already applied: 010_add_hybrid_model_fields
```

### Step 2: Backend Deployment (15 min)
```bash
# Build and deploy
docker build -t quant-api:v1.0 .
docker push registry.example.com/quant-api:v1.0
kubectl set image deployment/quant-api quant-api=registry.example.com/quant-api:v1.0
kubectl rollout status deployment/quant-api
```

### Step 3: Frontend Deployment (10 min)
```bash
npm run build
npm run deploy  # Or: vercel --prod
```

### Step 4: Verification (10 min)
```bash
# Check APIs
curl https://api.quant.platform.com/health
curl https://api.quant.platform.com/api/v1/subscription/tiers

# Check frontend
curl -I https://quant.platform.com
```

## Post-Deployment (1 hour after)

### Immediate Checks
- [ ] Website loads without errors
- [ ] API endpoints respond
- [ ] No critical errors in logs
- [ ] Stripe webhooks receiving events
- [ ] Database performing normally

### Test Subscription Flow
```bash
# Create test account
# Upgrade to Starter ($9.99)
# Verify webhook processed
# Check subscription status updated
```

### Test Referral System
```bash
# Generate referral code
# Share functionality works
# Referral tracking working
```

### Monitor for 1 Hour
- [ ] Error rates normal
- [ ] Response times acceptable
- [ ] No database issues
- [ ] Stripe integration working
- [ ] Ads displaying correctly

## Rollback Procedure

If critical issues found:

```bash
# Backend
kubectl rollout undo deployment/quant-api

# Frontend
vercel rollback

# Verify rollback complete
kubectl rollout status deployment/quant-api
curl https://api.quant.platform.com/health
```

## Post-Deployment (24-48 hours)

### Daily Monitoring
- [ ] Error logs reviewed
- [ ] Failed payments checked
- [ ] Webhook processing rate normal
- [ ] Conversion metrics tracked
- [ ] Revenue tracking verified

### Weekly Metrics
- [ ] Free → Starter conversion rate
- [ ] Free → Professional conversion rate
- [ ] Trial start rate
- [ ] Referral signup rate
- [ ] Payment success rate

## Success Indicators

✅ Deployment successful when:
- All health checks passing
- Error rate < 0.1%
- API response time < 200ms (p95)
- 3+ test subscriptions processed
- Stripe webhooks 100% success rate
- Database performing normally
- Frontend pages load < 3s
- Referral system working
- Ad banners displaying

## Failure Response

🔴 Rollback if:
- Error rate > 1%
- API unavailable
- Database unreachable
- Stripe integration broken
- Payment processing failing
- Critical data corruption

## Post-Deployment Report

After 24 hours, create report:
- Deployment success/issues
- Performance metrics
- User feedback
- Next optimizations

## Important Notes

⚠️ **DO NOT:**
- Deploy without running tests
- Deploy without staging verification
- Skip database migration steps
- Forget to update environment variables
- Deploy without rollback plan

✅ **DO:**
- Verify at each step
- Monitor logs closely
- Have team on standby
- Communicate status updates
- Document any issues

## Contact Information

- **DevOps Lead**: [name/phone]
- **Engineering Lead**: [name/phone]
- **Product Manager**: [name/phone]
- **On-Call**: Check rotation schedule

## Deployment Timeline

| Task | Duration | Owner | Status |
|------|----------|-------|--------|
| DB Migration | 5 min | DevOps | ⏳ |
| Backend Deploy | 15 min | DevOps | ⏳ |
| Frontend Deploy | 10 min | DevOps | ⏳ |
| Verification | 10 min | QA | ⏳ |
| Monitoring | 1 hour | Engineering | ⏳ |

**Total: ~1 hour for deployment + 1 hour monitoring**
