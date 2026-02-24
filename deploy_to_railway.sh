#!/bin/bash

# 🚀 Railway Deployment Script - Quant Stock Prediction Platform
# Run this script to deploy your backend to Railway

set -e  # Exit on error

echo "=============================================="
echo "🚀 Railway Deployment - Stock Prediction API"
echo "=============================================="
echo ""

# Navigate to backend directory
cd /mnt/e/projects/quant/quant/backend

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Step 1: Login
echo "📝 Step 1: Login to Railway"
echo "This will open your browser..."
railway login

if [ $? -ne 0 ]; then
    echo "❌ Login failed. Please try again."
    exit 1
fi

echo "✅ Login successful"
echo ""

# Step 2: Initialize or link project
echo "📝 Step 2: Initialize Railway Project"
echo ""
echo "Choose an option:"
echo "  1) Create NEW project"
echo "  2) Link to EXISTING project"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo "Creating new Railway project..."
    railway init
elif [ "$choice" == "2" ]; then
    echo "Linking to existing project..."
    railway link
else
    echo "❌ Invalid choice"
    exit 1
fi

echo "✅ Project configured"
echo ""

# Step 3: Add PostgreSQL
echo "📝 Step 3: Add PostgreSQL Database"
read -p "Add PostgreSQL database? (y/n): " add_db

if [ "$add_db" == "y" ]; then
    echo "Adding PostgreSQL..."
    railway add --database postgresql
    echo "✅ PostgreSQL added"
else
    echo "⚠️  Skipping PostgreSQL (you'll need to add it manually)"
fi

echo ""

# Step 4: Set environment variables
echo "📝 Step 4: Set Environment Variables"
echo ""

echo "Generating secure keys..."
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

echo "Setting required variables..."
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PROJECT_NAME="Quant Analytics Platform"
railway variables set API_V1_STR=/api/v1
railway variables set VERSION=1.0.0
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set BACKEND_CORS_ORIGINS="http://localhost:3000,https://your-app.vercel.app"

echo "✅ Core variables set"
echo ""

# Optional: API Keys
echo "📝 Step 5: Optional API Keys"
echo ""

read -p "Add Alpha Vantage API key? (y/n): " add_av
if [ "$add_av" == "y" ]; then
    read -p "Enter Alpha Vantage API key: " av_key
    railway variables set ALPHA_VANTAGE_API_KEY="$av_key"
fi

read -p "Add Polygon API key? (y/n): " add_polygon
if [ "$add_polygon" == "y" ]; then
    read -p "Enter Polygon API key: " polygon_key
    railway variables set POLYGON_API_KEY="$polygon_key"
fi

read -p "Add Finnhub API key? (y/n): " add_finnhub
if [ "$add_finnhub" == "y" ]; then
    read -p "Enter Finnhub API key: " finnhub_key
    railway variables set FINNHUB_API_KEY="$finnhub_key"
fi

echo ""
echo "📝 Step 6: Deploy to Railway"
echo ""

read -p "Ready to deploy? (y/n): " deploy_now

if [ "$deploy_now" == "y" ]; then
    echo "🚀 Deploying..."
    railway up

    echo ""
    echo "=============================================="
    echo "✅ Deployment Complete!"
    echo "=============================================="
    echo ""

    # Get deployment URL
    echo "📡 Getting deployment URL..."
    RAILWAY_URL=$(railway domain 2>/dev/null || echo "")

    if [ -n "$RAILWAY_URL" ]; then
        echo "🌐 Your API is live at:"
        echo "   API: https://$RAILWAY_URL"
        echo "   Docs: https://$RAILWAY_URL/docs"
        echo "   Health: https://$RAILWAY_URL/health"
    else
        echo "Run 'railway domain' to get your deployment URL"
    fi

    echo ""
    echo "📋 Next Steps:"
    echo "   1. Test health endpoint: curl https://your-url.railway.app/health"
    echo "   2. View API docs: https://your-url.railway.app/docs"
    echo "   3. Check logs: railway logs"
    echo "   4. Run migrations: railway run alembic upgrade head"
    echo ""
    echo "📚 Full guide: RAILWAY_DEPLOYMENT_STEPS.md"
    echo ""
else
    echo "⏸️  Deployment cancelled"
    echo "Run 'railway up' when ready to deploy"
fi

echo ""
echo "🎉 Setup Complete!"
