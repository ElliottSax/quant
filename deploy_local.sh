#!/bin/bash

echo "🚀 Deploying Quant Analytics Platform (Local Production)"
echo "========================================================"
echo ""

cd /mnt/e/projects/quant

# Stop development services
echo "Stopping development services..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Deploy with Docker Compose
echo "Starting production services..."
docker-compose -f docker-compose.production.yml up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "Service Status:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Access URLs:"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Frontend: http://localhost:3000"
echo ""
echo "View logs: docker-compose -f docker-compose.production.yml logs -f"
