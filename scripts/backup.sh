#!/bin/bash
# =============================================================================
# Database Backup Script with S3 Upload
# =============================================================================

set -e

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Load environment variables
# =============================================================================
if [ -f "quant/backend/.env" ]; then
    source quant/backend/.env
else
    log_error ".env file not found"
    exit 1
fi

# =============================================================================
# Create backup directory
# =============================================================================
mkdir -p ${BACKUP_DIR}

# =============================================================================
# Backup PostgreSQL
# =============================================================================
log_info "Creating PostgreSQL backup..."

POSTGRES_BACKUP="${BACKUP_DIR}/postgres_${TIMESTAMP}.sql"

docker-compose -f docker-compose.production.yml exec -T postgres \
    pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > ${POSTGRES_BACKUP}.gz

if [ $? -eq 0 ]; then
    log_info "PostgreSQL backup created: ${POSTGRES_BACKUP}.gz"
    POSTGRES_SIZE=$(du -h ${POSTGRES_BACKUP}.gz | cut -f1)
    log_info "Backup size: ${POSTGRES_SIZE}"
else
    log_error "PostgreSQL backup failed"
    exit 1
fi

# =============================================================================
# Backup Redis (if needed)
# =============================================================================
log_info "Creating Redis backup..."

docker-compose -f docker-compose.production.yml exec -T redis redis-cli SAVE
docker cp $(docker-compose -f docker-compose.production.yml ps -q redis):/data/dump.rdb ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb

if [ $? -eq 0 ]; then
    gzip ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb
    log_info "Redis backup created: ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb.gz"
fi

# =============================================================================
# Upload to S3 (if configured)
# =============================================================================
if [ ! -z "${BACKUP_S3_BUCKET}" ] && [ ! -z "${AWS_ACCESS_KEY_ID}" ]; then
    log_info "Uploading backups to S3..."

    aws s3 cp ${POSTGRES_BACKUP}.gz s3://${BACKUP_S3_BUCKET}/postgres/$(basename ${POSTGRES_BACKUP}.gz)
    aws s3 cp ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb.gz s3://${BACKUP_S3_BUCKET}/redis/redis_${TIMESTAMP}.rdb.gz

    log_info "Backups uploaded to S3 ✓"
else
    log_info "S3 upload skipped (not configured)"
fi

# =============================================================================
# Cleanup old backups
# =============================================================================
log_info "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."

find ${BACKUP_DIR} -name "postgres_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "redis_*.rdb.gz" -mtime +${RETENTION_DAYS} -delete

log_info "Backup completed successfully ✓"

# =============================================================================
# Summary
# =============================================================================
echo ""
log_info "Backup Summary:"
log_info "  PostgreSQL: ${POSTGRES_BACKUP}.gz (${POSTGRES_SIZE})"
log_info "  Redis: ${BACKUP_DIR}/redis_${TIMESTAMP}.rdb.gz"
log_info "  Retention: ${RETENTION_DAYS} days"
echo ""
