#!/bin/bash
set -e

echo "🚀 Railway Deployment Script"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found${NC}"
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check authentication
echo "Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Railway${NC}"
    echo ""
    echo "To deploy programmatically, you need a Railway token:"
    echo "1. Go to: https://railway.app/account/tokens"
    echo "2. Create a new token"
    echo "3. Set environment variable: export RAILWAY_TOKEN=your_token_here"
    echo ""
    echo "Or run: railway login (requires browser)"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Railway CLI authenticated${NC}"
echo ""

# Check if project exists
PROJECT_NAME="quant-backend"
echo "Checking for existing Railway project..."

if ! railway status &> /dev/null; then
    echo -e "${YELLOW}⚠️  No Railway project found${NC}"
    echo "Initializing new Railway project..."
    railway init --name "$PROJECT_NAME"
    echo -e "${GREEN}✅ Project initialized: $PROJECT_NAME${NC}"
else
    echo -e "${GREEN}✅ Railway project found${NC}"
fi

echo ""
echo "Setting environment variables..."

# Set required environment variables
railway variables set PROJECT_NAME="QuantBacktesting" \
    VERSION="1.0.0" \
    API_V1_STR="/api/v1" \
    ENVIRONMENT="production" \
    DATABASE_URL="sqlite+aiosqlite:///./quant.db" \
    PYTHONUNBUFFERED="1" \
    PYTHONDONTWRITEBYTECODE="1"

echo -e "${GREEN}✅ Environment variables set${NC}"
echo ""

# Generate secure keys if not exists
echo "Generating secure keys..."
SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')

railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"

echo -e "${GREEN}✅ Secure keys generated and set${NC}"
echo ""

# Deploy
echo "Deploying to Railway..."
echo -e "${YELLOW}This may take 3-5 minutes...${NC}"
echo ""

railway up --detach

echo ""
echo -e "${GREEN}✅ Deployment initiated!${NC}"
echo ""

# Wait for deployment
echo "Waiting for deployment to complete..."
sleep 30

# Get deployment URL
echo "Fetching deployment URL..."
RAILWAY_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$RAILWAY_URL" ]; then
    echo -e "${YELLOW}⚠️  Generating Railway domain...${NC}"
    railway domain
    sleep 5
    RAILWAY_URL=$(railway domain 2>/dev/null || echo "pending")
fi

echo ""
echo "=============================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=============================="
echo ""
echo "Railway URL: https://$RAILWAY_URL"
echo ""
echo "Test your deployment:"
echo "  Health:      curl https://$RAILWAY_URL/health"
echo "  Strategies:  curl https://$RAILWAY_URL/api/v1/backtesting/demo/strategies"
echo "  API Docs:    https://$RAILWAY_URL/api/v1/docs"
echo ""
echo "View logs:     railway logs"
echo "View status:   railway status"
echo "Open dashboard: railway open"
echo ""
