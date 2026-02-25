#!/bin/bash

# Start Frontend Script
# This script runs the Next.js frontend for the Quant Analytics Platform

set -e

echo "=========================================="
echo "Starting Quant Analytics Frontend"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "${YELLOW}Checking backend API...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API not responding at http://localhost:8000${NC}"
    echo "Make sure the backend is running first!"
fi

echo ""
echo -e "${BLUE}Starting frontend with Docker...${NC}"

# Create a simple docker-compose for frontend only
cat > docker-compose-frontend.yml << 'EOF'
version: '3.8'

services:
  frontend:
    image: node:18-alpine
    container_name: quant-frontend-ui
    working_dir: /app
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
      - NODE_ENV=development
    volumes:
      - ./quant/frontend:/app
    command: sh -c "npm install && npm run dev"
    network_mode: "host"
EOF

# Start the frontend
docker-compose -f docker-compose-frontend.yml up -d

echo ""
echo -e "${YELLOW}Waiting for frontend to start...${NC}"

# Wait for the frontend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}=========================================${NC}"
        echo -e "${GREEN}✅ Frontend Successfully Started!${NC}"
        echo -e "${GREEN}=========================================${NC}"
        echo ""
        echo "Access your application at:"
        echo ""
        echo -e "${BLUE}🌐 User Interface: ${NC}http://localhost:3000"
        echo -e "${BLUE}📊 Dashboard: ${NC}http://localhost:3000/dashboard"
        echo -e "${BLUE}🔐 Login: ${NC}http://localhost:3000/login"
        echo -e "${BLUE}📈 Politicians: ${NC}http://localhost:3000/politicians"
        echo ""
        echo -e "${YELLOW}Backend API: ${NC}http://localhost:8000"
        echo -e "${YELLOW}API Docs: ${NC}http://localhost:8000/api/v1/docs"
        echo ""
        echo -e "${GREEN}The platform is ready for use!${NC}"
        
        # Open browser (if available)
        if command -v xdg-open > /dev/null; then
            xdg-open http://localhost:3000
        elif command -v open > /dev/null; then
            open http://localhost:3000
        else
            echo ""
            echo "Open your browser and navigate to: http://localhost:3000"
        fi
        
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${YELLOW}Frontend is taking longer to start. Check logs:${NC}"
echo "docker logs -f quant-frontend-ui"