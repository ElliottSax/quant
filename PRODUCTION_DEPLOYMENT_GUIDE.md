# 🚀 Production Deployment Guide
## Quant Analytics Platform

**Complete guide for deploying to production**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Environment Configuration](#environment-configuration)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [Initial Deployment](#initial-deployment)
6. [Post-Deployment](#post-deployment)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Scaling](#scaling)

---

## Prerequisites

### Server Requirements

**Minimum Specifications:**
- **CPU**: 4 cores (8 recommended)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS or Debian 11+

**Network:**
- Static IP address
- Domain name with DNS configured
- Ports 80 and 443 open

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git
- curl
- AWS CLI (optional, for S3 backups)

---

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### 3. Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 4. Configure Firewall

```bash
# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 5. Create Deployment User

```bash
# Create user
sudo adduser deploy

# Add to docker group
sudo usermod -aG docker deploy

# Switch to deploy user
su - deploy
```

---

## Environment Configuration

### 1. Clone Repository

```bash
cd /home/deploy
git clone https://github.com/yourusername/quant.git
cd quant
```

### 2. Create Environment File

```bash
cd quant/backend
cp .env.production.example .env
```

### 3. Configure Environment Variables

Edit `.env` and update the following **critical** values:

```bash
# SECURITY - CHANGE THESE!
SECRET_KEY=<generate-with-openssl-rand-hex-32>
POSTGRES_PASSWORD=<strong-password>
GRAFANA_ADMIN_PASSWORD=<strong-password>

# DOMAIN
DOMAIN=yourdomain.com
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com","https://api.yourdomain.com"]

# EMAIL (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# SENTRY (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# AWS (for backups - optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
BACKUP_S3_BUCKET=your-backup-bucket
```

### 4. Generate SECRET_KEY

```bash
openssl rand -hex 32
```

Copy the output to `SECRET_KEY` in `.env`

### 5. Update Nginx Configuration

Edit `nginx/nginx.conf` and replace all instances of `yourdomain.com` with your actual domain.

---

## SSL Certificate Setup

### 1. Configure DNS

Before proceeding, ensure DNS is configured:

```bash
# Test DNS resolution
nslookup yourdomain.com
nslookup www.yourdomain.com
nslookup api.yourdomain.com
```

All should point to your server's IP address.

### 2. Initialize SSL Certificates

```bash
cd /home/deploy/quant
./scripts/init-ssl.sh yourdomain.com admin@yourdomain.com
```

This script will:
- Download TLS parameters
- Create temporary certificates
- Request Let's Encrypt certificates
- Configure auto-renewal

### 3. Verify SSL

Visit `https://yourdomain.com` - you should see a valid SSL certificate.

Check certificate details:
```bash
curl -vI https://yourdomain.com 2>&1 | grep -i 'SSL certificate'
```

---

## Initial Deployment

### 1. Deploy Services

```bash
cd /home/deploy/quant
./scripts/deploy.sh
```

The deployment script will:
- ✅ Run pre-deployment checks
- ✅ Create database backup
- ✅ Pull latest code
- ✅ Build Docker images
- ✅ Run database migrations
- ✅ Deploy all services
- ✅ Run health checks
- ✅ Clean up old images

### 2. Monitor Deployment

Watch the logs during deployment:

```bash
docker-compose -f docker-compose.production.yml logs -f
```

### 3. Verify Services

Check all containers are running:

```bash
docker-compose -f docker-compose.production.yml ps
```

Expected output:
```
NAME                  STATUS    PORTS
quant-backend         Up        0.0.0.0:8000->8000/tcp
quant-frontend        Up        0.0.0.0:3000->3000/tcp
quant-postgres        Up        0.0.0.0:5432->5432/tcp
quant-redis           Up        0.0.0.0:6379->6379/tcp
quant-redis-ml        Up        0.0.0.0:6380->6379/tcp
quant-celery-worker   Up
quant-celery-beat     Up
quant-nginx           Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
quant-prometheus      Up        0.0.0.0:9090->9090/tcp
quant-grafana         Up        0.0.0.0:3001->3000/tcp
```

---

## Post-Deployment

### 1. Create Admin User

```bash
docker-compose -f docker-compose.production.yml exec backend python -m app.cli create-admin
```

Enter admin credentials when prompted.

### 2. Access the Application

**Frontend:** https://yourdomain.com
**API Docs:** https://api.yourdomain.com/api/v1/docs
**Grafana:** http://your-server-ip:3001

### 3. Configure Grafana

1. Login to Grafana (default: admin/your-password)
2. Add Prometheus data source (http://prometheus:9090)
3. Import dashboards from `monitoring/grafana/dashboards/`

### 4. Test Functionality

```bash
# Test backend health
curl https://api.yourdomain.com/health

# Test frontend
curl https://yourdomain.com

# Create test user
curl -X POST https://api.yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123"
  }'
```

---

## Monitoring & Maintenance

### Daily Tasks

**Check System Health:**
```bash
# Check all services
docker-compose -f docker-compose.production.yml ps

# Check disk space
df -h

# Check memory usage
free -h

# Check Docker resource usage
docker stats --no-stream
```

### Weekly Tasks

**Backup Database:**
```bash
./scripts/backup.sh
```

Backups are stored in `backups/` and automatically uploaded to S3 (if configured).

**Review Logs:**
```bash
# Backend errors
docker-compose -f docker-compose.production.yml logs backend | grep ERROR

# Celery tasks
docker-compose -f docker-compose.production.yml logs celery-worker

# Nginx access
docker-compose -f docker-compose.production.yml logs nginx
```

### Monthly Tasks

**Update Dependencies:**
```bash
# Update Docker images
docker-compose -f docker-compose.production.yml pull

# Rebuild and deploy
./scripts/deploy.sh
```

**Review Security:**
- Check for CVEs in dependencies
- Review access logs for suspicious activity
- Rotate secrets if needed
- Review user accounts

### Automated Monitoring

**Prometheus Metrics:** http://your-server-ip:9090
- Service uptime
- Request rates
- Error rates
- Resource usage

**Grafana Dashboards:** http://your-server-ip:3001
- System overview
- API performance
- Database metrics
- Cache hit rates

**Set Up Alerts:**

Edit `monitoring/prometheus.yml` and add alerting rules:

```yaml
groups:
  - name: quant_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs [service-name]

# Restart service
docker-compose -f docker-compose.production.yml restart [service-name]

# Full restart
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.production.yml ps postgres

# Check database logs
docker-compose -f docker-compose.production.yml logs postgres

# Connect to database
docker-compose -f docker-compose.production.yml exec postgres psql -U quant_prod_user quant_prod_db
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart memory-hungry services
docker-compose -f docker-compose.production.yml restart celery-worker

# Adjust resource limits in docker-compose.production.yml
```

### SSL Certificate Issues

```bash
# Renew certificates manually
docker-compose -f docker-compose.production.yml run --rm certbot renew

# Check certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Rollback Deployment

```bash
# Restore from backup
gunzip backups/postgres_TIMESTAMP.sql.gz
docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U quant_prod_user quant_prod_db < backups/postgres_TIMESTAMP.sql

# Checkout previous version
git log --oneline
git checkout <commit-hash>
./scripts/deploy.sh
```

---

## Scaling

### Horizontal Scaling (Multiple Servers)

For high-traffic deployments:

1. **Set up load balancer** (AWS ELB, DigitalOcean Load Balancer, etc.)
2. **Use external PostgreSQL** (AWS RDS, DigitalOcean Managed Database)
3. **Use external Redis** (AWS ElastiCache, Redis Cloud)
4. **Scale backend replicas:**

```yaml
# In docker-compose.production.yml
backend:
  deploy:
    replicas: 5  # Increase number of instances
```

### Vertical Scaling (Bigger Server)

Upgrade server resources and adjust Docker resource limits:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
```

### Database Scaling

**Read Replicas:**
- Configure PostgreSQL replication
- Update connection strings for read-only queries

**Connection Pooling:**
```python
# In app/core/database.py
engine = create_async_engine(
    settings.async_database_url,
    pool_size=50,  # Increase pool size
    max_overflow=100,
)
```

---

## Security Best Practices

### 1. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.production.yml pull
```

### 2. Firewall Configuration

```bash
# Only allow necessary ports
sudo ufw status
sudo ufw deny <port>  # Close unused ports
```

### 3. Secret Rotation

Rotate secrets every 90 days:
- Database passwords
- SECRET_KEY
- API keys
- SSL certificates (auto-renewed by Let's Encrypt)

### 4. Access Control

- Use SSH keys (disable password auth)
- Implement IP whitelisting for admin panels
- Use VPN for sensitive operations
- Enable 2FA for critical accounts

### 5. Backup Strategy

- **Daily:** Automated database backups
- **Weekly:** Full system backup
- **Monthly:** Backup verification/restore test
- **Offsite:** S3 or similar cloud storage

---

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_trades_politician ON trades(politician_id);
CREATE INDEX idx_trades_date ON trades(transaction_date);

-- Analyze tables
ANALYZE trades;
ANALYZE politicians;
```

### 2. Cache Optimization

```python
# Increase cache TTLs for stable data
CACHE_DEFAULT_TTL=7200  # 2 hours
CACHE_ML_RESULTS_TTL=86400  # 24 hours
```

### 3. CDN Integration

Use Cloudflare or AWS CloudFront for:
- Static assets
- Image optimization
- DDoS protection
- Global distribution

---

## Backup & Disaster Recovery

### Automated Backups

Add to crontab:

```bash
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/deploy/quant/scripts/backup.sh >> /var/log/quant-backup.log 2>&1
```

### Disaster Recovery Plan

1. **Server Failure:**
   - Provision new server
   - Restore from S3 backup
   - Update DNS
   - Deploy application

2. **Data Corruption:**
   - Identify corruption point
   - Restore from latest good backup
   - Replay transaction log if available

3. **Security Breach:**
   - Isolate affected systems
   - Rotate all credentials
   - Audit logs for unauthorized access
   - Restore from clean backup

---

## Support & Resources

### Logs Location

- **Backend:** `/app/logs/` (inside container)
- **Nginx:** `/var/log/nginx/`
- **Docker:** `docker-compose logs`

### Important Commands

```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# Execute command in container
docker-compose -f docker-compose.production.yml exec backend bash

# Database console
docker-compose -f docker-compose.production.yml exec postgres psql -U quant_prod_user quant_prod_db

# Redis console
docker-compose -f docker-compose.production.yml exec redis redis-cli
```

### Getting Help

- **Documentation:** Check `/docs` folder
- **Issues:** GitHub Issues
- **Logs:** Always check logs first
- **Community:** Stack Overflow with tag `quant-analytics`

---

## Checklist

Before going live, verify:

- [ ] DNS configured correctly
- [ ] SSL certificates installed and valid
- [ ] All environment variables set
- [ ] Database backups configured
- [ ] Monitoring dashboards set up
- [ ] Admin user created
- [ ] Firewall configured
- [ ] Health checks passing
- [ ] Error tracking (Sentry) configured
- [ ] Email notifications working
- [ ] Load tested
- [ ] Disaster recovery plan documented
- [ ] Team trained on deployment process

---

## 🎉 Congratulations!

Your Quant Analytics Platform is now running in production!

**Access Points:**
- 🌐 **Frontend:** https://yourdomain.com
- 📊 **API:** https://api.yourdomain.com/api/v1/docs
- 📈 **Grafana:** http://your-server-ip:3001
- 🔬 **MLflow:** http://your-server-ip:5000

**Next Steps:**
1. Configure monitoring alerts
2. Set up automated backups
3. Train your team
4. Start using the platform!

---

*For questions or issues, refer to the troubleshooting section or check the logs.*
