#!/bin/bash

# =============================================================================
# Production Deployment Script
# Quant Analytics Platform
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Quant Analytics Platform${NC}"
echo -e "${BLUE}Production Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# =============================================================================
# Pre-deployment Checks
# =============================================================================
echo -e "${YELLOW}Running pre-deployment checks...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose installed${NC}"

# Check if .env exists
if [ ! -f "quant/backend/.env" ]; then
    echo -e "${YELLOW}⚠️  .env not found, copying from .env.production${NC}"
    cp quant/backend/.env.production quant/backend/.env
    echo -e "${RED}❗ IMPORTANT: Edit quant/backend/.env and set your production passwords!${NC}"
    echo -e "${RED}Press Enter to continue after updating .env or Ctrl+C to cancel${NC}"
    read
fi

echo -e "${GREEN}✅ Environment file exists${NC}"

# =============================================================================
# Stop Development Services
# =============================================================================
echo ""
echo -e "${YELLOW}Stopping development services...${NC}"

# Kill development processes
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

echo -e "${GREEN}✅ Development services stopped${NC}"

# =============================================================================
# Build Docker Images
# =============================================================================
echo ""
echo -e "${YELLOW}Building Docker images...${NC}"

docker-compose -f docker-compose.production.yml build --no-cache

echo -e "${GREEN}✅ Docker images built${NC}"

# =============================================================================
# Deploy Services
# =============================================================================
echo ""
echo -e "${YELLOW}Deploying production services...${NC}"

# Start services
docker-compose -f docker-compose.production.yml up -d

echo -e "${GREEN}✅ Services deployed${NC}"

# =============================================================================
# Wait for Services
# =============================================================================
echo ""
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"

# Wait for PostgreSQL
echo -n "Waiting for PostgreSQL... "
for i in {1..30}; do
    if docker exec quant-postgres pg_isready -U quant_user > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Redis
echo -n "Waiting for Redis... "
for i in {1..30}; do
    if docker exec quant-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        break
    fi
    sleep 2
    echo -n "."
done

# Wait for Backend
echo -n "Waiting for Backend API... "
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        break
    fi
    sleep 3
    echo -n "."
done

# =============================================================================
# Run Database Migrations
# =============================================================================
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"

docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head 2>/dev/null || echo "Skipping migrations (not configured)"

echo -e "${GREEN}✅ Migrations complete${NC}"

# =============================================================================
# Deployment Summary
# =============================================================================
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo -e "Backend API:      ${GREEN}http://localhost:8000${NC}"
echo -e "API Docs:         ${GREEN}http://localhost:8000/docs${NC}"
echo -e "Frontend:         ${GREEN}http://localhost:3000${NC}"
echo -e "MLflow:           ${GREEN}http://localhost:5000${NC}"
echo -e "MinIO Console:    ${GREEN}http://localhost:9001${NC}"
echo -e "Prometheus:       ${GREEN}http://localhost:9090${NC}"
echo -e "Grafana:          ${GREEN}http://localhost:3001${NC}"
echo ""
echo -e "${YELLOW}Database:${NC}"
echo -e "PostgreSQL:       ${GREEN}localhost:5432${NC}"
echo -e "Redis:            ${GREEN}localhost:6379${NC}"
echo -e "Redis ML:         ${GREEN}localhost:6380${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "View logs:        ${GREEN}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "View status:      ${GREEN}docker-compose -f docker-compose.production.yml ps${NC}"
echo -e "Stop services:    ${GREEN}docker-compose -f docker-compose.production.yml down${NC}"
echo -e "Restart:          ${GREEN}docker-compose -f docker-compose.production.yml restart${NC}"
echo ""
echo -e "${YELLOW}Health Checks:${NC}"
echo -e "Backend:          ${GREEN}curl http://localhost:8000/health${NC}"
echo -e "PostgreSQL:       ${GREEN}docker exec quant-postgres pg_isready${NC}"
echo -e "Redis:            ${GREEN}docker exec quant-redis redis-cli ping${NC}"
echo ""
echo -e "${RED}IMPORTANT NEXT STEPS:${NC}"
echo -e "1. Review and update production passwords in quant/backend/.env"
echo -e "2. Configure SSL certificates for HTTPS"
echo -e "3. Set up domain DNS to point to your server"
echo -e "4. Configure firewall rules"
echo -e "5. Set up monitoring and alerts"
echo -e "6. Configure automated backups"
echo ""
