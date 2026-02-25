#!/bin/bash
# =============================================================================
# Production Deployment Script for Quant Analytics Platform
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Pre-deployment Checks
# =============================================================================
log_info "Starting production deployment..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed"
    exit 1
fi

# Check if .env file exists
if [ ! -f "quant/backend/.env" ]; then
    log_error ".env file not found. Please create one from .env.production.example"
    exit 1
fi

log_info "Pre-deployment checks passed ✓"

# =============================================================================
# Backup Database
# =============================================================================
log_info "Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p backups

# Get database credentials from .env
source quant/backend/.env

# Create backup with timestamp
BACKUP_FILE="backups/db_backup_$(date +%Y%m%d_%H%M%S).sql"

docker-compose -f docker-compose.production.yml exec -T postgres \
    pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    log_info "Database backup created: ${BACKUP_FILE} ✓"
else
    log_warn "Database backup failed (continuing anyway)"
fi

# =============================================================================
# Pull Latest Code
# =============================================================================
log_info "Pulling latest code from git..."

git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git pull origin ${CURRENT_BRANCH}

log_info "Code updated ✓"

# =============================================================================
# Build Docker Images
# =============================================================================
log_info "Building Docker images..."

docker-compose -f docker-compose.production.yml build --no-cache

log_info "Docker images built ✓"

# =============================================================================
# Run Database Migrations
# =============================================================================
log_info "Running database migrations..."

docker-compose -f docker-compose.production.yml run --rm backend \
    alembic upgrade head

if [ $? -eq 0 ]; then
    log_info "Database migrations completed ✓"
else
    log_error "Database migrations failed"
    log_error "Rolling back deployment..."
    exit 1
fi

# =============================================================================
# Deploy Services
# =============================================================================
log_info "Deploying services..."

# Stop old containers gracefully
docker-compose -f docker-compose.production.yml down --timeout 30

# Start services in correct order
docker-compose -f docker-compose.production.yml up -d postgres redis redis-ml
sleep 10

docker-compose -f docker-compose.production.yml up -d backend celery-worker celery-beat
sleep 10

docker-compose -f docker-compose.production.yml up -d frontend
sleep 5

docker-compose -f docker-compose.production.yml up -d nginx

log_info "Services deployed ✓"

# =============================================================================
# Health Checks
# =============================================================================
log_info "Running health checks..."

sleep 15  # Wait for services to start

# Check backend health
HEALTH_URL="http://localhost:8000/health"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${HEALTH_URL})

if [ ${HEALTH_RESPONSE} -eq 200 ]; then
    log_info "Backend health check passed ✓"
else
    log_error "Backend health check failed (HTTP ${HEALTH_RESPONSE})"
    log_error "Check logs: docker-compose -f docker-compose.production.yml logs backend"
    exit 1
fi

# Check frontend
FRONTEND_URL="http://localhost:3000"
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${FRONTEND_URL})

if [ ${FRONTEND_RESPONSE} -eq 200 ]; then
    log_info "Frontend health check passed ✓"
else
    log_warn "Frontend health check failed (HTTP ${FRONTEND_RESPONSE})"
fi

# =============================================================================
# Cleanup
# =============================================================================
log_info "Cleaning up old images..."

docker image prune -f

log_info "Cleanup completed ✓"

# =============================================================================
# Deployment Summary
# =============================================================================
echo ""
log_info "=========================================="
log_info "Deployment completed successfully! 🚀"
log_info "=========================================="
echo ""
log_info "Services running:"
docker-compose -f docker-compose.production.yml ps
echo ""
log_info "View logs: docker-compose -f docker-compose.production.yml logs -f"
log_info "Stop services: docker-compose -f docker-compose.production.yml down"
echo ""
log_info "Access the application:"
log_info "  Frontend: https://yourdomain.com"
log_info "  API Docs: https://api.yourdomain.com/api/v1/docs"
log_info "  Grafana: http://localhost:3001"
echo ""
