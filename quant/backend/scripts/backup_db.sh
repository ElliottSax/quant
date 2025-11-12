#!/bin/bash
# Database backup script for PostgreSQL

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="quant_db_${TIMESTAMP}.sql.gz"

# Database connection details (from environment variables)
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-quant_db}"
DB_USER="${POSTGRES_USER:-quant_user}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Starting database backup...${NC}"
echo "Database: $DB_NAME"
echo "Timestamp: $TIMESTAMP"
echo "Backup file: $BACKUP_FILE"
echo ""

# Perform backup
if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then

    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo "Backup location: $BACKUP_DIR/$BACKUP_FILE"

    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo "Backup size: $BACKUP_SIZE"

else
    echo -e "${RED}✗ Backup failed!${NC}"
    exit 1
fi

# Clean up old backups
echo ""
echo -e "${YELLOW}Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"

OLD_BACKUPS=$(find "$BACKUP_DIR" -name "quant_db_*.sql.gz" -type f -mtime +$RETENTION_DAYS)

if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | while read -r file; do
        echo "Removing: $file"
        rm -f "$file"
    done
    echo -e "${GREEN}✓ Cleanup completed${NC}"
else
    echo "No old backups to remove"
fi

# Show remaining backups
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/quant_db_*.sql.gz 2>/dev/null || echo "No backups found"

echo ""
echo -e "${GREEN}Backup process completed!${NC}"
