#!/bin/bash
# Automated deployment script for Quant Backtesting Platform
# Run this after: railway login && vercel login

set -e  # Exit on error

echo "🚀 Quant Platform Deployment Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if logged in
echo "🔍 Checking authentication..."
if ! railway whoami &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Railway. Run: railway login${NC}"
    exit 1
fi

if ! vercel whoami &>/dev/null; then
    echo -e "${RED}❌ Not logged in to Vercel. Run: vercel login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authenticated to both Railway and Vercel${NC}"
echo ""

# ============================================
# STEP 1: Deploy Backend to Railway
# ============================================
echo -e "${BLUE}📦 Step 1: Deploying Backend to Railway...${NC}"
cd quant/backend

# Check if project exists
if ! railway status &>/dev/null; then
    echo "Creating new Railway project..."
    railway init
fi

# Add environment variables
echo "Setting environment variables..."
railway variables set PROJECT_NAME="QuantBacktestingPlatform"
railway variables set VERSION="1.0.0"
railway variables set API_V1_STR="/api/v1"
railway variables set ENVIRONMENT="production"
railway variables set DATABASE_URL="sqlite+aiosqlite:///./quant.db"
railway variables set SECRET_KEY="$(openssl rand -base64 32)"
railway variables set JWT_SECRET_KEY="$(openssl rand -base64 32)"
railway variables set FINNHUB_API_KEY="d6fl2j9r01qqnmbp36ogd6fl2j9r01qqnmbp36p0"
railway variables set BACKEND_CORS_ORIGINS='["*"]'

# Deploy
echo "Deploying backend..."
railway up --detach

# Get backend URL
echo "Waiting for deployment..."
sleep 10
BACKEND_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Could not get Railway domain automatically."
    echo "Please get it from: railway open"
    read -p "Enter your Railway backend URL (e.g., quant-backend.railway.app): " BACKEND_URL
fi

echo -e "${GREEN}✅ Backend deployed to: https://${BACKEND_URL}${NC}"
echo ""

# ============================================
# STEP 2: Deploy Frontend to Vercel
# ============================================
echo -e "${BLUE}🌐 Step 2: Deploying Frontend to Vercel...${NC}"
cd ../frontend

# Deploy to Vercel
echo "Deploying frontend..."
vercel --prod --yes \
    -e NEXT_PUBLIC_API_URL="https://${BACKEND_URL}/api/v1"

FRONTEND_URL=$(vercel inspect --prod 2>/dev/null | grep -oP 'https://[^\s]+' | head -1 || echo "")

if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="https://quant-frontend.vercel.app"
    echo "Using default frontend URL: $FRONTEND_URL"
fi

echo -e "${GREEN}✅ Frontend deployed to: ${FRONTEND_URL}${NC}"
echo ""

# ============================================
# STEP 3: Update Backend CORS
# ============================================
echo -e "${BLUE}🔧 Step 3: Updating Backend CORS...${NC}"
cd ../backend
railway variables set BACKEND_CORS_ORIGINS="[\"${FRONTEND_URL}\",\"https://*.vercel.app\"]"
echo -e "${GREEN}✅ CORS updated${NC}"
echo ""

# ============================================
# DONE
# ============================================
echo "===================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "===================================="
echo ""
echo "📊 Backend API: https://${BACKEND_URL}"
echo "   API Docs: https://${BACKEND_URL}/docs"
echo ""
echo "🌐 Frontend: ${FRONTEND_URL}"
echo ""
echo "Next steps:"
echo "1. Test the deployment by visiting: ${FRONTEND_URL}"
echo "2. Check API documentation: https://${BACKEND_URL}/docs"
echo "3. Run a backtest to verify everything works"
echo "4. Launch on Product Hunt (see MARKETING_LAUNCH_GUIDE.md)"
echo ""
