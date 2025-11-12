#!/bin/bash
# Start Celery worker for Quant Analytics Platform

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Worker for Quant Analytics Platform${NC}"
echo "=================================================="

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

# Check if PostgreSQL is accessible
echo "Checking database connection..."
if ! python -c "import asyncio; from sqlalchemy.ext.asyncio import create_async_engine; from app.core.config import settings; asyncio.run(create_async_engine(settings.DATABASE_URL).connect())" > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Could not connect to database${NC}"
    echo "Make sure DATABASE_URL is correctly configured in .env"
fi

# Set log level (default: INFO)
LOG_LEVEL=${LOG_LEVEL:-INFO}

# Set concurrency (default: 2)
CONCURRENCY=${CONCURRENCY:-2}

echo ""
echo "Configuration:"
echo "  Log Level: $LOG_LEVEL"
echo "  Concurrency: $CONCURRENCY"
echo "  Queue: celery (default)"
echo ""

# Start worker
echo -e "${GREEN}Starting Celery worker...${NC}"
exec celery -A app.celery_app worker \
    --loglevel=$LOG_LEVEL \
    --concurrency=$CONCURRENCY \
    --max-tasks-per-child=10 \
    --task-events \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    -Q celery
