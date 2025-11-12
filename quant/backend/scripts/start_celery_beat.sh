#!/bin/bash
# Start Celery Beat scheduler for Quant Analytics Platform

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Beat Scheduler for Quant Analytics Platform${NC}"
echo "=========================================================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not detected${NC}"
    echo "Activating venv..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Error: venv not found. Run: python -m venv venv${NC}"
        exit 1
    fi
fi

# Check if Redis is running
echo "Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running${NC}"
    echo "Start Redis with: redis-server"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Set log level (default: INFO)
LOG_LEVEL=${LOG_LEVEL:-INFO}

# Remove old beat schedule file
if [ -f "celerybeat-schedule.db" ]; then
    echo "Removing old beat schedule..."
    rm celerybeat-schedule.db
fi

echo ""
echo "Configuration:"
echo "  Log Level: $LOG_LEVEL"
echo "  Schedule: Daily scraping + Weekly full sync"
echo ""

# Start beat scheduler
echo -e "${GREEN}Starting Celery Beat...${NC}"
exec celery -A app.celery_app beat \
    --loglevel=$LOG_LEVEL \
    --pidfile=/tmp/celerybeat.pid
