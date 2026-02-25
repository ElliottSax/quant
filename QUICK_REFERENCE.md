# 📘 Quick Reference Guide

## Essential Commands

### Deployment
```bash
# Initial deployment
./scripts/deploy.sh

# Initialize SSL
./scripts/init-ssl.sh yourdomain.com admin@yourdomain.com

# Backup database
./scripts/backup.sh
```

### Service Management
```bash
# View all services
docker-compose -f docker-compose.production.yml ps

# Start services
docker-compose -f docker-compose.production.yml up -d

# Stop services
docker-compose -f docker-compose.production.yml down

# Restart a service
docker-compose -f docker-compose.production.yml restart backend

# Scale a service
docker-compose -f docker-compose.production.yml up -d --scale backend=5
```

### Logs
```bash
# All logs (follow)
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 backend

# Error logs only
docker-compose -f docker-compose.production.yml logs backend | grep ERROR
```

### Database
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres psql -U quant_prod_user quant_prod_db

# Backup
docker-compose -f docker-compose.production.yml exec -T postgres \
  pg_dump -U quant_prod_user quant_prod_db | gzip > backup.sql.gz

# Restore
gunzip < backup.sql.gz | docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U quant_prod_user quant_prod_db

# Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### Redis
```bash
# Connect to Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli

# Flush cache
docker-compose -f docker-compose.production.yml exec redis redis-cli FLUSHDB

# Monitor commands
docker-compose -f docker-compose.production.yml exec redis redis-cli MONITOR
```

### Health Checks
```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend
curl https://yourdomain.com

# Check all services
docker-compose -f docker-compose.production.yml ps
```

### SSL/TLS
```bash
# Renew certificates
docker-compose -f docker-compose.production.yml run --rm certbot renew

# Check expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Reload nginx after renewal
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
```

### Monitoring
```bash
# Resource usage
docker stats

# System resources
htop

# Disk usage
df -h

# Check service memory
docker-compose -f docker-compose.production.yml exec backend ps aux
```

### Troubleshooting
```bash
# Container shell
docker-compose -f docker-compose.production.yml exec backend bash

# Run one-off command
docker-compose -f docker-compose.production.yml run --rm backend python -c "print('test')"

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build backend

# Remove all containers and volumes (DANGER!)
docker-compose -f docker-compose.production.yml down -v
```

## Important Files

| File | Purpose |
|------|---------|
| `.env` | Environment configuration |
| `docker-compose.production.yml` | Service orchestration |
| `nginx/nginx.conf` | Reverse proxy config |
| `monitoring/prometheus.yml` | Metrics configuration |
| `scripts/deploy.sh` | Deployment automation |

## Default Ports

| Service | Port | Access |
|---------|------|--------|
| Nginx HTTP | 80 | Public |
| Nginx HTTPS | 443 | Public |
| Backend | 8000 | Internal |
| Frontend | 3000 | Internal |
| PostgreSQL | 5432 | Internal |
| Redis | 6379 | Internal |
| Redis ML | 6380 | Internal |
| Prometheus | 9090 | Internal |
| Grafana | 3001 | Internal |
| MLflow | 5000 | Internal |

## Environment Variables

### Critical (Must Change)
```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
POSTGRES_PASSWORD=<strong-password>
DOMAIN=yourdomain.com
```

### Email
```bash
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Optional
```bash
SENTRY_DSN=<sentry-url>
AWS_ACCESS_KEY_ID=<aws-key>
BACKUP_S3_BUCKET=<bucket-name>
```

## Backup & Restore

### Automated Backup
```bash
# Run backup script
./scripts/backup.sh

# Schedule daily backups (crontab)
0 2 * * * /home/deploy/quant/scripts/backup.sh
```

### Manual Backup
```bash
# PostgreSQL
docker-compose -f docker-compose.production.yml exec -T postgres \
  pg_dump -U quant_prod_user quant_prod_db | gzip > "backup_$(date +%Y%m%d).sql.gz"

# Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli SAVE
docker cp quant-redis:/data/dump.rdb redis_backup.rdb
```

### Restore
```bash
# PostgreSQL
gunzip < backup.sql.gz | docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U quant_prod_user quant_prod_db

# Redis
docker cp redis_backup.rdb quant-redis:/data/dump.rdb
docker-compose -f docker-compose.production.yml restart redis
```

## Security Checklist

- [ ] SECRET_KEY is random and 32+ chars
- [ ] POSTGRES_PASSWORD is strong
- [ ] SSH password auth disabled
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] SSL certificates installed
- [ ] CORS origins restricted
- [ ] Admin accounts secured
- [ ] Backups automated
- [ ] Monitoring configured
- [ ] Logs reviewed regularly

## Performance Tuning

### Database
```sql
-- Add indexes
CREATE INDEX idx_name ON table(column);

-- Analyze tables
ANALYZE table_name;

-- Check slow queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### Redis
```bash
# Check memory usage
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO memory

# Get cache stats
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO stats
```

### Nginx
```bash
# Test configuration
docker-compose -f docker-compose.production.yml exec nginx nginx -t

# Reload config
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
```

## Common Issues

### Service won't start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs [service]

# Restart
docker-compose -f docker-compose.production.yml restart [service]
```

### Out of memory
```bash
# Check usage
docker stats

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### Database connection error
```bash
# Check PostgreSQL
docker-compose -f docker-compose.production.yml ps postgres

# Check credentials
cat quant/backend/.env | grep POSTGRES
```

### SSL issues
```bash
# Renew
docker-compose -f docker-compose.production.yml run --rm certbot renew

# Check expiry
openssl s_client -connect yourdomain.com:443 | openssl x509 -noout -dates
```

## Useful One-Liners

```bash
# Check all container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Find large files
du -ah / | sort -rh | head -n 20

# Network connections
netstat -tuln | grep LISTEN

# Process CPU usage
ps aux --sort=-%cpu | head -10

# Memory usage
ps aux --sort=-%mem | head -10

# Disk I/O
iostat -x 1 10

# Follow all logs
docker-compose -f docker-compose.production.yml logs -f --tail=100
```

## Emergency Contacts

- **On-call Engineer**: [Your number]
- **DevOps Lead**: [Number]
- **CTO**: [Number]
- **Sentry Alerts**: [Email]
- **Status Page**: [URL]

## Support Resources

- **Documentation**: `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **API Docs**: https://api.yourdomain.com/api/v1/docs
- **Monitoring**: http://server-ip:3001
- **Logs**: `docker-compose logs -f`
