# Production Deployment Checklist

Use this checklist before, during, and after production deployment.

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing locally
- [ ] All tests passing in CI/CD
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities (run `safety check`)
- [ ] No TODO/FIXME comments in critical paths
- [ ] Linting passes (Black, Ruff)
- [ ] Type checking passes (MyPy)

### Configuration
- [ ] `.env.production` configured with all variables
- [ ] All secrets rotated from defaults
- [ ] SECRET_KEY generated (64 chars)
- [ ] JWT_SECRET_KEY generated (64 chars)
- [ ] Database credentials secured
- [ ] API keys obtained and configured
- [ ] CORS origins set to production domains only
- [ ] Rate limiting configured appropriately

### Infrastructure
- [ ] Railway account created and configured
- [ ] Vercel account created and configured
- [ ] Supabase database created
- [ ] Redis instance provisioned
- [ ] Domain purchased and configured
- [ ] DNS records created
- [ ] SSL certificates obtained (or using Cloudflare)

### Database
- [ ] Production database created
- [ ] TimescaleDB extension enabled
- [ ] Database backed up
- [ ] Migration scripts tested
- [ ] Rollback plan documented
- [ ] Connection pooling configured

### Monitoring
- [ ] Sentry account created
- [ ] Sentry DSN configured
- [ ] Prometheus configured
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] Slack webhook configured
- [ ] Email alerts configured
- [ ] Health check endpoint tested

### Security
- [ ] Security headers enabled
- [ ] HTTPS enforced
- [ ] Rate limiting enabled
- [ ] SQL injection protection verified
- [ ] XSS protection verified
- [ ] CSRF protection enabled
- [ ] Input validation in place
- [ ] Authentication working
- [ ] Authorization working
- [ ] Session management secure

### Performance
- [ ] Database indexes created
- [ ] Query optimization done
- [ ] Caching enabled
- [ ] CDN configured (if using)
- [ ] Image optimization done
- [ ] Bundle size acceptable
- [ ] Load testing completed
- [ ] Response times acceptable (<1s)

### Documentation
- [ ] README.md updated
- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] API documentation current
- [ ] Environment variables documented
- [ ] Runbooks created for common issues
- [ ] Team trained on procedures

### Communication
- [ ] Deployment scheduled
- [ ] Team notified of deployment window
- [ ] Stakeholders informed
- [ ] Status page prepared
- [ ] Communication channels ready (Slack)

## Deployment Checklist

### Initial Deployment

#### Backend Deployment
- [ ] Login to Railway: `railway login`
- [ ] Set environment: `railway environment production`
- [ ] Upload environment variables
- [ ] Deploy backend: `railway up`
- [ ] Check deployment status: `railway status`
- [ ] View logs: `railway logs`
- [ ] Verify health: `curl https://api.yourdomain.com/health`

#### Frontend Deployment
- [ ] Login to Vercel: `vercel login`
- [ ] Set environment variables
- [ ] Deploy frontend: `vercel --prod`
- [ ] Verify deployment: `curl https://yourdomain.com`
- [ ] Test in browser

#### Database Migration
- [ ] Set DATABASE_URL environment variable
- [ ] Run migrations: `alembic upgrade head`
- [ ] Verify: `alembic current`
- [ ] Test database connectivity

#### Post-Deployment Verification
- [ ] Run smoke tests: `python scripts/smoke_test.py --url https://api.yourdomain.com`
- [ ] Check all endpoints in API docs
- [ ] Verify frontend loads correctly
- [ ] Test user registration
- [ ] Test user login
- [ ] Test core functionality
- [ ] Check metrics endpoint
- [ ] Verify Sentry receiving events
- [ ] Check Prometheus scraping metrics
- [ ] View Grafana dashboards

### Monitoring Setup
- [ ] Sentry receiving events
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards showing data
- [ ] Alerts firing correctly (test)
- [ ] Slack notifications working
- [ ] Log aggregation working
- [ ] Error tracking working

### Performance Verification
- [ ] Response times acceptable (<1s)
- [ ] No memory leaks
- [ ] Database queries optimized
- [ ] Cache hit rate acceptable (>80%)
- [ ] No N+1 queries
- [ ] Connection pool healthy

## Post-Deployment Checklist

### Immediate (0-30 minutes)
- [ ] All smoke tests passed
- [ ] No errors in Sentry
- [ ] Response times normal
- [ ] Database queries normal
- [ ] Memory usage normal
- [ ] CPU usage normal
- [ ] No 5xx errors
- [ ] Key features working

### Short-term (30 minutes - 2 hours)
- [ ] Monitor error rates
- [ ] Check user feedback
- [ ] Review application logs
- [ ] Monitor database performance
- [ ] Check cache effectiveness
- [ ] Verify background jobs running
- [ ] Monitor API rate limits

### Medium-term (2-24 hours)
- [ ] Review Sentry issues
- [ ] Analyze Prometheus metrics
- [ ] Check Grafana dashboards
- [ ] Review slow query logs
- [ ] Monitor disk usage
- [ ] Check backup completion
- [ ] Review security logs

### Documentation
- [ ] Update deployment log
- [ ] Document any issues encountered
- [ ] Update runbooks if needed
- [ ] Share learnings with team
- [ ] Update deployment checklist

### Communication
- [ ] Notify team of successful deployment
- [ ] Update status page
- [ ] Send summary email
- [ ] Schedule retro meeting (if issues)

## Rollback Checklist

If something goes wrong:

### Immediate Actions (<5 minutes)
- [ ] Assess severity (critical vs. non-critical)
- [ ] Notify team in Slack
- [ ] Initiate rollback: `./scripts/rollback.sh production [TAG]`
- [ ] Monitor rollback progress
- [ ] Verify old version is stable

### Verification (<15 minutes)
- [ ] Run smoke tests on rolled-back version
- [ ] Check error rates returned to normal
- [ ] Verify database state
- [ ] Check all critical features
- [ ] Monitor for 15 minutes

### Post-Rollback (<1 hour)
- [ ] Document what went wrong
- [ ] Capture error logs
- [ ] Save database state
- [ ] Notify stakeholders
- [ ] Plan fix and redeploy

### Post-Mortem (<24 hours)
- [ ] Write incident report
- [ ] Identify root cause
- [ ] Document lessons learned
- [ ] Update deployment process
- [ ] Share with team

## Weekly Maintenance Checklist

- [ ] Review error rates
- [ ] Check disk usage
- [ ] Verify backups
- [ ] Review security alerts
- [ ] Check dependency updates
- [ ] Review performance metrics
- [ ] Clean up old logs
- [ ] Test disaster recovery

## Monthly Checklist

- [ ] Review and rotate secrets
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance review
- [ ] Cost optimization review
- [ ] Documentation review
- [ ] Team retro on deployments
- [ ] Disaster recovery test

## Quarterly Checklist

- [ ] Full security audit
- [ ] Load testing
- [ ] Database optimization
- [ ] Review architecture decisions
- [ ] Update disaster recovery plan
- [ ] Review and update runbooks
- [ ] Infrastructure cost review
- [ ] Capacity planning

## Emergency Contacts

- **DevOps Lead:** [Name] - [Phone] - [Email]
- **Backend Lead:** [Name] - [Phone] - [Email]
- **Frontend Lead:** [Name] - [Phone] - [Email]
- **Database Admin:** [Name] - [Phone] - [Email]
- **On-Call Engineer:** See PagerDuty rotation

## Critical URLs

- **Production API:** https://api.yourdomain.com
- **Production Frontend:** https://yourdomain.com
- **Sentry:** https://sentry.io/organizations/yourorg
- **Grafana:** https://grafana.yourdomain.com
- **Railway:** https://railway.app/project/YOUR_PROJECT
- **Vercel:** https://vercel.com/yourorg/yourproject

## Emergency Procedures

### Complete Outage
1. Check status page: https://status.yourdomain.com
2. Check Railway status: https://railway.app/status
3. Check Vercel status: https://vercel.com/status
4. Review recent deployments
5. Check error logs
6. Initiate rollback if recent deployment
7. Notify stakeholders
8. Update status page

### Database Issues
1. Check database status in Supabase
2. Review slow query logs
3. Check connection pool
4. Verify migrations
5. Check disk space
6. Review recent schema changes
7. Consider read replica failover

### High Error Rate
1. Check Sentry for new errors
2. Review recent deployments
3. Check external service status
4. Review application logs
5. Check database performance
6. Consider rollback
7. Implement hotfix if identified

---

**Version:** 1.0
**Last Updated:** 2024-01-15
**Owner:** DevOps Team

**Notes:**
- Print this checklist for deployment day
- Keep updated with lessons learned
- Review quarterly for improvements
