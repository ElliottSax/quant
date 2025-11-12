# Production Deployment Guide

Complete guide for deploying the Quant Analytics Platform to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Application Deployment](#application-deployment)
6. [HTTPS/SSL Configuration](#httpsssl-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup Configuration](#backup-configuration)
9. [CI/CD Setup](#cicd-setup)
10. [Post-Deployment](#post-deployment)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services
- ✅ Ubuntu 20.04+ or similar Linux distribution
- ✅ Docker & Docker Compose installed
- ✅ Domain name configured and pointing to your server
- ✅ SSL certificate (Let's Encrypt recommended)
- ✅ At least 2GB RAM, 2 CPU cores, 20GB storage

### Required Accounts
- GitHub account (for repository)
- Docker Hub account (optional, for custom images)
- Sentry account (for error monitoring)
- Domain registrar access

---

## Initial Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Logout and login to apply group changes
```

### 2. Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/quant
sudo chown $USER:$USER /opt/quant

# Clone repository
cd /opt/quant
git clone https://github.com/ElliottSax/quant.git .
```

---

## Environment Configuration

### 1. Generate Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate database password
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
```

### 2. Create Production Environment File

```bash
cd /opt/quant/quant
cp .env.example .env
nano .env
```

**Required Environment Variables:**

```env
# Application
ENVIRONMENT=production
DEBUG=false

# Security - CRITICAL: Change these!
SECRET_KEY=<generated-secret-key-from-step-1>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://quant_user:<secure-password>@postgres:5432/quant_db
POSTGRES_USER=quant_user
POSTGRES_PASSWORD=<secure-password-from-step-1>
POSTGRES_DB=quant_db

# Redis
REDIS_URL=redis://redis:6379/0

# CORS - Update with your domain
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# External APIs (optional)
POLYGON_API_KEY=your-polygon-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_API_VERSION=v1
```

### 3. Secure Environment File

```bash
# Restrict permissions
chmod 600 .env
```

---

## Database Setup

### 1. Create Docker Network

```bash
cd /opt/quant/quant/infrastructure/docker
docker-compose up -d postgres redis
```

### 2. Wait for Services

```bash
# Check if services are healthy
docker-compose ps

# Wait until postgres shows "healthy"
docker-compose logs -f postgres
```

### 3. Run Database Migrations

```bash
cd /opt/quant/quant/backend

# Option 1: Using Docker
docker-compose exec backend alembic upgrade head

# Option 2: Local Python
pip install -r requirements.txt
alembic upgrade head
```

### 4. Create First Superuser

```bash
# Using CLI
cd /opt/quant/quant/backend
python -m app.cli create-superuser

# Or manually via Docker
docker-compose exec backend python -m app.cli create-superuser
```

---

## Application Deployment

### 1. Update Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: quant-postgres
    env_file:
      - ../../.env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - quant-network
    restart: always

  redis:
    image: redis:7-alpine
    container_name: quant-redis
    volumes:
      - redis_data:/data
    networks:
      - quant-network
    restart: always
    command: redis-server --appendonly yes

  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile.prod
    container_name: quant-backend
    env_file:
      - ../../.env
    depends_on:
      - postgres
      - redis
    networks:
      - quant-network
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: quant-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
    networks:
      - quant-network
    restart: always

volumes:
  postgres_data:
  redis_data:

networks:
  quant-network:
    driver: bridge
```

### 2. Start Production Services

```bash
cd /opt/quant/quant/infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## HTTPS/SSL Configuration

### 1. Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificate

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 3. Configure Nginx

Create `/opt/quant/quant/infrastructure/docker/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
        limit_req zone=api_limit burst=20 nodelay;
    }
}
```

### 4. Copy SSL Certificates

```bash
sudo mkdir -p /opt/quant/quant/infrastructure/docker/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/quant/quant/infrastructure/docker/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/quant/quant/infrastructure/docker/ssl/
sudo chown -R $USER:$USER /opt/quant/quant/infrastructure/docker/ssl
chmod 600 /opt/quant/quant/infrastructure/docker/ssl/*
```

### 5. Auto-Renew Certificates

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job
sudo crontab -e

# Add this line:
0 0 1 * * certbot renew --quiet && systemctl reload nginx
```

---

## Monitoring Setup

### 1. Configure Sentry

1. Create account at [sentry.io](https://sentry.io)
2. Create new project for "Python/FastAPI"
3. Copy DSN and add to `.env`:

```env
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
```

### 2. Set Up Log Monitoring

```bash
# Install log rotation
sudo nano /etc/logrotate.d/quant

# Add:
/opt/quant/quant/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
}
```

### 3. System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Optional: Set up Prometheus & Grafana
# See: docs/monitoring/prometheus-setup.md
```

---

## Backup Configuration

### 1. Set Up Automated Backups

```bash
# Create backup directory
sudo mkdir -p /backups/quant
sudo chown $USER:$USER /backups/quant

# Test backup script
cd /opt/quant/quant/backend/scripts
./backup_db.sh

# Add to crontab
crontab -e

# Add daily backup at 2 AM:
0 2 * * * cd /opt/quant/quant/backend/scripts && ./backup_db.sh >> /var/log/quant-backup.log 2>&1
```

### 2. Test Restore Process

```bash
# List backups
ls -lh /backups/

# Test restore (CAUTION: This will replace data!)
./restore_db.sh /backups/quant_db_YYYYMMDD_HHMMSS.sql.gz
```

### 3. Off-Site Backup

```bash
# Install rclone for cloud backup
curl https://rclone.org/install.sh | sudo bash

# Configure rclone (follow prompts)
rclone config

# Add to backup script to sync to cloud
rclone sync /backups/quant remote:quant-backups
```

---

## CI/CD Setup

### 1. GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets):

```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
```

### 2. GitHub Actions

The CI/CD pipeline is already configured in `.github/workflows/ci.yml`

It will automatically:
- Run tests on every push/PR
- Run security scans
- Build Docker images
- Push to Docker Hub (on main branch)

### 3. Deploy Webhook (Optional)

Set up automatic deployment on push to main:

```bash
# Install webhook
sudo apt install webhook -y

# Create webhook config
# See: docs/deployment/webhook-setup.md
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test health endpoint
curl https://yourdomain.com/health

# Test API docs
curl https://yourdomain.com/api/v1/docs
```

### 2. Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils -y

# Run load test
ab -n 1000 -c 10 https://yourdomain.com/api/v1/trades/

# Or use wrk
sudo apt install wrk -y
wrk -t4 -c100 -d30s https://yourdomain.com/api/v1/trades/
```

### 3. Security Audit

```bash
# Run security scan
docker run --rm -v /opt/quant:/src aquasec/trivy fs /src

# Check SSL configuration
openssl s_client -connect yourdomain.com:443 -tls1_2

# Test with SSL Labs
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check database is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U quant_user -d quant_db -c "SELECT 1;"
```

#### 2. Backend Not Starting

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Wrong SECRET_KEY format (check length)
# - Database not ready (wait longer)
# - Port already in use (check with: netstat -tlnp | grep 8000)
```

#### 3. CORS Errors

```bash
# Verify CORS origins in .env
# Must include protocol: https://yourdomain.com

# Check nginx configuration
docker-compose exec nginx nginx -t
```

#### 4. High Memory Usage

```bash
# Check container stats
docker stats

# Reduce worker count in Dockerfile.prod:
# --workers 2  (instead of 4)

# Add memory limits in docker-compose:
deploy:
  resources:
    limits:
      memory: 512M
```

### Useful Commands

```bash
# View all logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Access container shell
docker-compose exec backend bash

# Run database query
docker-compose exec postgres psql -U quant_user -d quant_db

# Export database
docker-compose exec postgres pg_dump -U quant_user quant_db > backup.sql
```

---

## Maintenance

### Regular Tasks

**Daily:**
- ✅ Check application logs
- ✅ Verify backups completed
- ✅ Monitor error rates in Sentry

**Weekly:**
- ✅ Review security updates
- ✅ Check disk space
- ✅ Review performance metrics
- ✅ Test backup restoration

**Monthly:**
- ✅ Update dependencies
- ✅ Review and rotate logs
- ✅ Security audit
- ✅ Performance optimization

### Update Procedure

```bash
# Pull latest changes
cd /opt/quant
git pull origin main

# Rebuild containers
cd quant/infrastructure/docker
docker-compose -f docker-compose.prod.yml build

# Run migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl https://yourdomain.com/health
```

---

## Support

- **Documentation:** https://github.com/ElliottSax/quant
- **Issues:** https://github.com/ElliottSax/quant/issues
- **API Docs:** https://yourdomain.com/api/v1/docs

---

## Checklist

### Pre-Deployment
- [ ] Server prepared with Docker
- [ ] Domain configured
- [ ] SSL certificate obtained
- [ ] Environment variables configured
- [ ] Sentry project created

### Deployment
- [ ] Repository cloned
- [ ] Database initialized
- [ ] Migrations run
- [ ] Superuser created
- [ ] Services started
- [ ] Nginx configured with SSL
- [ ] Health check passing

### Post-Deployment
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] CI/CD pipeline tested
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated

---

**You're now production-ready! 🚀**
