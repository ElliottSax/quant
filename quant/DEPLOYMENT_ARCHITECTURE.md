# Deployment Architecture

Visual guide to the Quant Analytics Platform production infrastructure.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Internet / Users                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS
                                  ▼
                    ┌─────────────────────────┐
                    │      Cloudflare         │
                    │   DNS + CDN + SSL       │
                    └─────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                  │
                 ▼                                  ▼
    ┌────────────────────────┐        ┌────────────────────────┐
    │       Vercel           │        │      Railway           │
    │  Frontend (Next.js)    │        │   Backend (FastAPI)    │
    │  • Static assets       │        │   • REST API           │
    │  • SSR pages           │        │   • WebSockets         │
    │  • Edge functions      │        │   • Background jobs    │
    └────────────────────────┘        └────────────────────────┘
                 │                                  │
                 │                     ┌────────────┴────────────┐
                 │                     │                          │
                 │                     ▼                          ▼
                 │         ┌────────────────────┐    ┌────────────────────┐
                 │         │    Supabase        │    │   Redis Cloud      │
                 │         │  PostgreSQL +      │    │   • Cache          │
                 │         │  TimescaleDB       │    │   • Sessions       │
                 │         │  • User data       │    │   • Task queue     │
                 │         │  • Trade data      │    │   • Rate limits    │
                 │         │  • Time-series     │    └────────────────────┘
                 │         └────────────────────┘
                 │                     │
                 │                     ▼
                 │         ┌────────────────────┐
                 └────────►│   Supabase Auth    │
                           │   Authentication   │
                           └────────────────────┘
```

## 📊 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Services                             │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   FastAPI   │  │   Celery    │  │  Database   │                 │
│  │   Backend   │  │   Workers   │  │  (Postgres) │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│         │                │                 │                         │
│         └────────────────┴─────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                 │
          ▼                ▼                 ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Sentry  │    │Prometheus│    │ Railway  │
    │  Errors  │    │ Metrics  │    │   Logs   │
    │  • Traces│    │  • Gauges│    │  • JSON  │
    │  • Events│    │  • Counts│    │  • Stdout│
    └──────────┘    └──────────┘    └──────────┘
          │                │                 │
          │                ▼                 │
          │         ┌──────────┐            │
          │         │ Grafana  │            │
          │         │Dashboards│            │
          │         └──────────┘            │
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                           ▼
                    ┌──────────┐
                    │  Alerts  │
                    │  • Slack │
                    │  • Email │
                    └──────────┘
```

## 🔄 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Developer Workflow                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ git push
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                               │
│                                                                       │
│  On Pull Request:                                                    │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  1. Run Tests (Backend + Frontend)                     │         │
│  │  2. Run Linting (Black, Ruff, ESLint)                 │         │
│  │  3. Security Scan (Trivy, Safety)                     │         │
│  │  4. Docker Build Verification                          │         │
│  │  5. Code Coverage Report                               │         │
│  └────────────────────────────────────────────────────────┘         │
│                              │                                        │
│                              │ Merge to main                          │
│                              ▼                                        │
│  On Push to Main:                                                    │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  1. Run All Tests                                      │         │
│  │  2. Build Docker Images                                │         │
│  │  3. Deploy Backend (Railway)                           │         │
│  │  4. Deploy Frontend (Vercel)                           │         │
│  │  5. Run Database Migrations                            │         │
│  │  6. Run Smoke Tests                                    │         │
│  │  7. Create Git Tag                                     │         │
│  │  8. Send Notifications                                 │         │
│  │                                                         │         │
│  │  If failure → Automatic Rollback                       │         │
│  └────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
```

## 🗄️ Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      User Request                             │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │      Cloudflare         │
              │  • DDoS protection      │
              │  • SSL termination      │
              │  • CDN caching          │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │       Nginx             │
              │  • Load balancing       │
              │  • Rate limiting        │
              │  • Request routing      │
              └─────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  │                    │
                  ▼                    ▼
        ┌──────────────┐     ┌──────────────┐
        │   Frontend   │     │   Backend    │
        │   (Next.js)  │────►│   (FastAPI)  │
        └──────────────┘     └──────────────┘
                                     │
                        ┌────────────┼────────────┐
                        │            │            │
                        ▼            ▼            ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │   Auth   │  │  Cache   │  │ Database │
              │(Supabase)│  │ (Redis)  │  │(Postgres)│
              └──────────┘  └──────────┘  └──────────┘
```

## 🔐 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Cloudflare DDoS Protection                          │     │
│  │  • SSL/TLS Encryption (TLS 1.2+)                       │     │
│  │  • HSTS Headers                                        │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Application Security                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Rate Limiting (per IP, per user)                    │     │
│  │  • CORS Configuration                                  │     │
│  │  • Security Headers (CSP, X-Frame-Options)             │     │
│  │  • Input Validation (Pydantic)                         │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Authentication & Authorization                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • JWT Tokens (short-lived)                            │     │
│  │  • Refresh Tokens (HttpOnly cookies)                   │     │
│  │  • 2FA Support (TOTP)                                  │     │
│  │  • Email Verification                                  │     │
│  │  • Password Hashing (bcrypt)                           │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Database Encryption at Rest                         │     │
│  │  • Encrypted Backups                                   │     │
│  │  • SQL Injection Protection (ORM)                      │     │
│  │  • Sensitive Data Masking                              │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Monitoring & Audit                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  • Security Event Logging                              │     │
│  │  • Failed Login Tracking                               │     │
│  │  • Anomaly Detection                                   │     │
│  │  • Audit Trails                                        │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Deployment Process

```
┌────────────────────────────────────────────────────────────────┐
│  Phase 1: Pre-Deployment                                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  ✓ Run all tests                                     │      │
│  │  ✓ Check code quality (linting, type checking)       │      │
│  │  ✓ Security scan (dependencies, vulnerabilities)     │      │
│  │  ✓ Build Docker images                               │      │
│  │  ✓ Validate environment variables                    │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Phase 2: Deployment                                            │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  1. Backend Deployment (Railway)                     │      │
│  │     • Build new container                            │      │
│  │     • Health check                                   │      │
│  │     • Route traffic                                  │      │
│  │                                                       │      │
│  │  2. Frontend Deployment (Vercel)                     │      │
│  │     • Build static assets                            │      │
│  │     • Deploy to edge                                 │      │
│  │     • Invalidate cache                               │      │
│  │                                                       │      │
│  │  3. Database Migration                               │      │
│  │     • Backup current state                           │      │
│  │     • Run migrations                                 │      │
│  │     • Verify schema                                  │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Phase 3: Post-Deployment                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  ✓ Run smoke tests                                   │      │
│  │  ✓ Verify all services healthy                       │      │
│  │  ✓ Check error rates (Sentry)                        │      │
│  │  ✓ Monitor performance (Grafana)                     │      │
│  │  ✓ Create deployment tag                             │      │
│  │  ✓ Send notifications                                │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Success!   │
                     └──────────────┘
```

## 🔄 Rollback Process

```
┌────────────────────────────────────────────────────────────────┐
│  Issue Detected                                                 │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Assess Severity │
                  └──────────────────┘
                            │
                 ┌──────────┴──────────┐
                 │                      │
                 ▼                      ▼
        ┌────────────────┐    ┌────────────────┐
        │   Critical     │    │  Non-Critical  │
        │   Immediate    │    │   Monitor      │
        │   Rollback     │    └────────────────┘
        └────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│  Rollback Steps                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  1. Notify team (Slack)                              │      │
│  │  2. Create backup of current state                   │      │
│  │  3. Rollback backend (Railway)                       │      │
│  │  4. Rollback frontend (Vercel)                       │      │
│  │  5. Rollback database (if needed)                    │      │
│  │  6. Run smoke tests                                  │      │
│  │  7. Verify stability                                 │      │
│  │  8. Document incident                                │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  System Stable   │
                  └──────────────────┘
```

## 💾 Backup Strategy

```
┌────────────────────────────────────────────────────────────────┐
│  Database Backups (Automated)                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Hourly: Last 24 hours (Supabase automatic)        │      │
│  │  • Daily: Last 7 days (Supabase PITR)                │      │
│  │  • Weekly: Last 4 weeks (Manual to S3)               │      │
│  │  • Monthly: Last 12 months (Archive to S3)           │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Code Backups                                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Git repository (GitHub)                            │      │
│  │  • Deployment tags (automatic)                        │      │
│  │  • Docker images (Railway registry)                   │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Configuration Backups                                          │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Environment variables (encrypted)                  │      │
│  │  • Nginx config (version controlled)                  │      │
│  │  • Prometheus/Grafana config (version controlled)     │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

## 🌍 Geographic Distribution

```
┌─────────────────────────────────────────────────────────────────┐
│  Global Edge Network (Cloudflare)                               │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  US-West │  │ US-East  │  │  Europe  │  │   Asia   │       │
│  │   CDN    │  │   CDN    │  │   CDN    │  │   CDN    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Application Servers                                             │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Vercel Edge     │         │  Railway         │             │
│  │  (Global)        │         │  (US-West)       │             │
│  │  • Next.js SSR   │         │  • FastAPI       │             │
│  │  • Static files  │         │  • WebSockets    │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Database Servers                                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Supabase (US-East)                                  │       │
│  │  • Primary: PostgreSQL + TimescaleDB                 │       │
│  │  • Replicas: Read replicas (optional)                │       │
│  │  • Backup: Cross-region replication                  │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 📈 Scaling Strategy

```
┌────────────────────────────────────────────────────────────────┐
│  Vertical Scaling (Resource Increase)                           │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Backend:  2GB → 4GB → 8GB RAM                       │      │
│  │  Database: 1GB → 2GB → 4GB RAM                       │      │
│  │  Redis:    256MB → 512MB → 1GB                       │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Horizontal Scaling (Instance Increase)                         │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Backend:  1 → 2 → 4 instances (Railway)             │      │
│  │  Workers:  1 → 2 → 4 Celery workers                  │      │
│  │  Database: Add read replicas                         │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  Performance Optimization                                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  • Enable database connection pooling                 │      │
│  │  • Increase Redis cache size                          │      │
│  │  • Add CDN for static assets                          │      │
│  │  • Optimize database queries                          │      │
│  │  • Implement query result caching                     │      │
│  └──────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference

### Service URLs
- **Frontend:** https://yourdomain.com
- **Backend API:** https://api.yourdomain.com
- **API Docs:** https://api.yourdomain.com/api/v1/docs
- **Grafana:** https://grafana.yourdomain.com
- **Prometheus:** http://prometheus-internal:9090 (internal only)

### Key Components
- **Web Server:** Nginx (reverse proxy)
- **Application:** FastAPI (Python 3.11)
- **Frontend:** Next.js 14 (React)
- **Database:** PostgreSQL 15 + TimescaleDB
- **Cache:** Redis 7
- **Queue:** Celery + Redis
- **Monitoring:** Sentry + Prometheus + Grafana

### Deployment Targets
- **Backend:** Railway
- **Frontend:** Vercel
- **Database:** Supabase
- **Cache/Queue:** Redis Cloud
- **CDN:** Cloudflare

---

**For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**
