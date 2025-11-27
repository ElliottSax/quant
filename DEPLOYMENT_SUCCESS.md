# 🚀 Production Deployment Guide

## Quick Local Production Deployment

This guide will deploy the platform in production mode on your local machine.

### Prerequisites ✅
- [x] Docker installed
- [x] Docker Compose installed
- [x] Git repository cloned
- [x] Environment file configured

### Deployment Steps

#### 1. Stop Development Services
```bash
# Kill development processes
pkill -f uvicorn
pkill -f "next dev"

# Or manually stop them with Ctrl+C
```

#### 2. Configure Environment (DONE ✅)
The production environment file has been created at:
```
quant/backend/.env
```

**IMPORTANT:** Before deploying to a public server, update these values:
- `SECRET_KEY` - Generate new: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `POSTGRES_PASSWORD` - Change from default
- `MINIO_ROOT_PASSWORD` - Change from default
- `CORS_ORIGINS` - Set to your domain
- `ALLOWED_HOSTS` - Set to your domain

#### 3. Deploy with Docker Compose
```bash
cd /mnt/e/projects/quant

# Build images (first time or after code changes)
docker-compose -f docker-compose.production.yml build

# Start all services
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

#### 4. Verify Deployment
```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# Test backend health
curl http://localhost:8000/health

# Test API docs
curl http://localhost:8000/docs
```

### Service URLs

**Backend Services:**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Frontend:**
- Web App: http://localhost:3000

**Infrastructure:**
- PostgreSQL: localhost:5432
- Redis (Main): localhost:6379
- Redis (ML): localhost:6380
- MLflow: http://localhost:5000
- MinIO Console: http://localhost:9001
  - Username: `minioadmin`
  - Password: See `.env` (MINIO_ROOT_PASSWORD)
- Prometheus (if enabled): http://localhost:9090
- Grafana (if enabled): http://localhost:3001
  - Username: `admin`
  - Password: See `.env` (GRAFANA_ADMIN_PASSWORD)

### Production Architecture

The Docker Compose production setup includes:

**1. Database Layer**
- PostgreSQL 15 (Primary database)
- Persistent volume for data
- Automated backups
- Health checks

**2. Caching Layer**
- Redis (Main) - API cache, Celery broker
- Redis ML - ML results cache
- Persistent volumes
- Memory limits

**3. Application Layer**
- Backend API (3 replicas for load balancing)
- Celery Workers (background tasks)
- Celery Beat (task scheduler)
- Resource limits configured

**4. Storage Layer**
- MinIO (S3-compatible object storage)
- MLflow artifact storage
- Backup storage

**5. ML/Tracking Layer**
- MLflow Tracking Server
- Experiment logging
- Model registry

**6. Monitoring Layer (Optional)**
- Prometheus - Metrics collection
- Grafana - Dashboards
- Node Exporter - System metrics
- cAdvisor - Container metrics

**7. Proxy Layer**
- Nginx - Reverse proxy
- SSL termination
- Load balancing
- Static file serving

### Useful Commands

**View Logs:**
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f postgres
docker-compose -f docker-compose.production.yml logs -f celery-worker
```

**Service Management:**
```bash
# Stop all services
docker-compose -f docker-compose.production.yml down

# Stop and remove volumes (WARNING: Deletes data!)
docker-compose -f docker-compose.production.yml down -v

# Restart a service
docker-compose -f docker-compose.production.yml restart backend

# Scale backend replicas
docker-compose -f docker-compose.production.yml up -d --scale backend=5
```

**Database Operations:**
```bash
# Connect to PostgreSQL
docker exec -it quant-postgres psql -U quant_user -d quant_db

# Backup database
docker exec quant-postgres pg_dump -U quant_user quant_db > backup.sql

# Restore database
docker exec -i quant-postgres psql -U quant_user quant_db < backup.sql

# Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

**Monitoring:**
```bash
# Check resource usage
docker stats

# Check service health
docker-compose -f docker-compose.production.yml ps

# View system metrics
docker exec quant-backend curl localhost:8000/metrics
```

### Performance Tuning

**Backend Replicas:**
The production setup runs 3 backend instances by default. Adjust based on load:
```yaml
# In docker-compose.production.yml
deploy:
  replicas: 5  # Increase for higher load
```

**Database Connection Pool:**
Configure in `.env`:
```bash
DB_POOL_SIZE=20  # Connections per backend instance
DB_MAX_OVERFLOW=10  # Additional connections when needed
```

**Redis Memory:**
```bash
# Adjust maxmemory in docker-compose.production.yml
command: redis-server --maxmemory 1gb  # Increase as needed
```

**Celery Workers:**
```bash
# Scale workers
docker-compose -f docker-compose.production.yml up -d --scale celery-worker=4
```

### Security Checklist

**Before Public Deployment:**
- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Configure CORS origins
- [ ] Enable rate limiting
- [ ] Set up automated backups
- [ ] Configure monitoring alerts
- [ ] Review and update ALLOWED_HOSTS
- [ ] Disable DEBUG mode (already disabled)
- [ ] Secure MinIO access
- [ ] Set up log rotation
- [ ] Configure fail2ban (optional)
- [ ] Enable two-factor authentication (optional)

### Backup & Recovery

**Automated Backups:**
Backups run daily at 2 AM (configurable in `.env`):
```bash
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # Cron format
BACKUP_RETENTION_DAYS=30
```

**Manual Backup:**
```bash
# Database
docker exec quant-postgres pg_dump -U quant_user -F c quant_db > quant_backup_$(date +%Y%m%d).dump

# Full system backup
docker-compose -f docker-compose.production.yml down
tar -czf quant_full_backup_$(date +%Y%m%d).tar.gz .
docker-compose -f docker-compose.production.yml up -d
```

**Restore from Backup:**
```bash
# Restore database
docker exec -i quant-postgres pg_restore -U quant_user -d quant_db < backup.dump

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### Troubleshooting

**Services Won't Start:**
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check resource usage
docker stats

# Rebuild images
docker-compose -f docker-compose.production.yml build --no-cache
```

**Database Connection Issues:**
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.production.yml logs postgres

# Test connection
docker exec quant-postgres pg_isready -U quant_user

# Reset database (WARNING: Deletes data!)
docker-compose -f docker-compose.production.yml down -v
docker volume rm quant_postgres_data
docker-compose -f docker-compose.production.yml up -d
```

**High Memory Usage:**
```bash
# Check container stats
docker stats

# Reduce backend replicas
docker-compose -f docker-compose.production.yml up -d --scale backend=2

# Reduce Redis memory
# Edit maxmemory in docker-compose.production.yml
```

**API Performance Issues:**
```bash
# Enable profiling
# In .env: ENABLE_PROFILING=true

# Check slow queries
docker exec quant-postgres psql -U quant_user -d quant_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Clear Redis cache
docker exec quant-redis redis-cli FLUSHALL
```

### Scaling Guide

**Horizontal Scaling (Multiple Servers):**
1. Set up load balancer (Nginx, HAProxy, or cloud LB)
2. Deploy backend on multiple servers
3. Use shared PostgreSQL and Redis instances
4. Configure sticky sessions for WebSocket

**Vertical Scaling (More Resources):**
```yaml
# In docker-compose.production.yml
deploy:
  resources:
    limits:
      cpus: '4'  # Increase
      memory: 4G  # Increase
```

**Database Scaling:**
- Set up PostgreSQL read replicas
- Use connection pooling (PgBouncer)
- Consider sharding for very large datasets

**Caching Strategy:**
- Increase Redis memory
- Use Redis Cluster for distributed caching
- Implement CDN for static assets

### Monitoring & Alerts

**Prometheus Queries:**
```promql
# API request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Database connections
pg_stat_database_numbackends

# Redis memory usage
redis_memory_used_bytes
```

**Grafana Dashboards:**
- System Overview
- API Performance
- Database Metrics
- Cache Hit Rate
- Celery Task Metrics

**Alert Rules:**
- API response time > 1s
- Error rate > 1%
- Database connections > 80% of max
- Disk usage > 80%
- Memory usage > 90%

### Update & Maintenance

**Rolling Update:**
```bash
# Pull latest code
git pull

# Rebuild and restart (zero downtime with multiple replicas)
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d --no-deps --build backend

# Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

**Maintenance Mode:**
```bash
# Scale down to 1 replica
docker-compose -f docker-compose.production.yml up -d --scale backend=1

# Perform maintenance
# ... your maintenance tasks ...

# Scale back up
docker-compose -f docker-compose.production.yml up -d --scale backend=3
```

### Cost Optimization

**For Cloud Deployment:**
- Use spot/preemptible instances for Celery workers
- Enable autoscaling for backend instances
- Use managed database services (RDS, Cloud SQL)
- Implement caching aggressively
- Use CDN for static assets
- Enable compression
- Set up log aggregation to reduce storage

---

## Deployment Status

**Current Status:** Ready to Deploy ✅

**Checklist:**
- [x] Docker Compose configuration
- [x] Production Dockerfile
- [x] Environment configuration
- [x] Deployment scripts
- [x] Documentation

**Next Steps:**
1. Review and update `.env` file
2. Run deployment script
3. Verify services
4. Configure monitoring
5. Set up backups
6. Configure SSL (for public deployment)

---

**Deployment Command:**
```bash
cd /mnt/e/projects/quant
./deploy_production.sh
```

or manually:
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

*Production Deployment Guide - Quant Analytics Platform v1.0.0*
