#!/bin/bash

# Quick Deploy Helper
# Interactive deployment script for first-time deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Header
clear
echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        Quant Analytics Platform - Quick Deploy            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Welcome message
echo -e "${BLUE}Welcome to the Quant Analytics Platform deployment wizard!${NC}"
echo ""
echo "This script will help you:"
echo "  • Set up your production environment"
echo "  • Configure required services"
echo "  • Deploy to Railway and Vercel"
echo "  • Set up monitoring"
echo ""
echo -e "${YELLOW}Note: Make sure you have completed the prerequisites in DEPLOYMENT_GUIDE.md${NC}"
echo ""
read -p "Press Enter to continue or Ctrl+C to exit..."
clear

# Step 1: Check prerequisites
echo -e "${CYAN}${BOLD}Step 1: Checking Prerequisites${NC}"
echo ""

missing_tools=()

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    missing_tools+=("Railway CLI (npm i -g @railway/cli)")
fi

# Check Vercel CLI
if ! command -v vercel &> /dev/null; then
    missing_tools+=("Vercel CLI (npm i -g vercel)")
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    missing_tools+=("Python 3")
fi

# Check Git
if ! command -v git &> /dev/null; then
    missing_tools+=("Git")
fi

if [ ${#missing_tools[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required tools are installed${NC}"
else
    echo -e "${RED}✗ Missing required tools:${NC}"
    printf '%s\n' "${missing_tools[@]}"
    echo ""
    echo "Please install the missing tools and run this script again."
    exit 1
fi

echo ""
read -p "Press Enter to continue..."
clear

# Step 2: Environment setup
echo -e "${CYAN}${BOLD}Step 2: Environment Configuration${NC}"
echo ""

if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating .env.production from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env.production
        echo -e "${GREEN}✓ Created .env.production${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env.production already exists${NC}"
fi

echo ""
echo "You need to configure the following in .env.production:"
echo ""
echo "  1. Database credentials (Supabase)"
echo "  2. Redis connection (Railway/Redis Cloud)"
echo "  3. Secret keys (generate with Python)"
echo "  4. Sentry DSN (error tracking)"
echo "  5. API keys (Polygon, SendGrid, etc.)"
echo ""
echo -e "${YELLOW}Open .env.production now and fill in the values${NC}"
echo ""
read -p "Press Enter when done..."
clear

# Step 3: Generate secrets
echo -e "${CYAN}${BOLD}Step 3: Generate Secret Keys${NC}"
echo ""

echo "Generating secure random keys..."
echo ""

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

echo -e "${GREEN}Generated SECRET_KEY:${NC}"
echo "$SECRET_KEY"
echo ""
echo -e "${GREEN}Generated JWT_SECRET_KEY:${NC}"
echo "$JWT_SECRET"
echo ""
echo -e "${YELLOW}Copy these to your .env.production file${NC}"
echo ""
read -p "Press Enter when done..."
clear

# Step 4: Service setup guide
echo -e "${CYAN}${BOLD}Step 4: Service Setup${NC}"
echo ""

echo "Please set up the following services:"
echo ""
echo -e "${BOLD}1. Supabase (Database)${NC}"
echo "   • Go to https://supabase.com"
echo "   • Create new project"
echo "   • Enable TimescaleDB extension"
echo "   • Copy connection string to .env.production"
echo ""
echo -e "${BOLD}2. Railway (Backend + Redis)${NC}"
echo "   • Go to https://railway.app"
echo "   • Create new project"
echo "   • Add Redis service"
echo "   • Get connection URLs"
echo ""
echo -e "${BOLD}3. Sentry (Error Tracking)${NC}"
echo "   • Go to https://sentry.io"
echo "   • Create new project (FastAPI)"
echo "   • Copy DSN to .env.production"
echo ""
echo -e "${BOLD}4. SendGrid (Email)${NC}"
echo "   • Go to https://sendgrid.com"
echo "   • Create API key"
echo "   • Copy to .env.production"
echo ""
read -p "Press Enter when all services are set up..."
clear

# Step 5: Deploy backend
echo -e "${CYAN}${BOLD}Step 5: Deploy Backend to Railway${NC}"
echo ""

read -p "Deploy backend now? (y/n): " deploy_backend

if [[ $deploy_backend =~ ^[Yy]$ ]]; then
    echo ""
    echo "Logging in to Railway..."
    railway login

    echo ""
    echo "Linking project..."
    railway link

    echo ""
    echo "Setting environment variables from .env.production..."
    railway variables --environment production < .env.production

    echo ""
    echo "Deploying backend..."
    cd backend
    railway up --environment production
    cd ..

    echo ""
    echo -e "${GREEN}✓ Backend deployed to Railway${NC}"
else
    echo -e "${YELLOW}Skipping backend deployment${NC}"
fi

echo ""
read -p "Press Enter to continue..."
clear

# Step 6: Run migrations
echo -e "${CYAN}${BOLD}Step 6: Database Migrations${NC}"
echo ""

read -p "Run database migrations? (y/n): " run_migrations

if [[ $run_migrations =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your production DATABASE_URL: " db_url

    export DATABASE_URL="$db_url"

    echo "Running migrations..."
    cd backend
    alembic upgrade head
    cd ..

    echo ""
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${YELLOW}Skipping migrations${NC}"
fi

echo ""
read -p "Press Enter to continue..."
clear

# Step 7: Deploy frontend
echo -e "${CYAN}${BOLD}Step 7: Deploy Frontend to Vercel${NC}"
echo ""

read -p "Deploy frontend now? (y/n): " deploy_frontend

if [[ $deploy_frontend =~ ^[Yy]$ ]]; then
    echo ""
    echo "Logging in to Vercel..."
    vercel login

    echo ""
    echo "Deploying frontend..."
    cd frontend
    vercel --prod
    cd ..

    echo ""
    echo -e "${GREEN}✓ Frontend deployed to Vercel${NC}"
else
    echo -e "${YELLOW}Skipping frontend deployment${NC}"
fi

echo ""
read -p "Press Enter to continue..."
clear

# Step 8: Setup monitoring
echo -e "${CYAN}${BOLD}Step 8: Setup Monitoring${NC}"
echo ""

read -p "Set up monitoring now? (y/n): " setup_monitoring

if [[ $setup_monitoring =~ ^[Yy]$ ]]; then
    echo ""
    ./scripts/setup_monitoring.sh
    echo ""
    echo -e "${GREEN}✓ Monitoring setup complete${NC}"
else
    echo -e "${YELLOW}Skipping monitoring setup${NC}"
    echo "You can run ./scripts/setup_monitoring.sh later"
fi

echo ""
read -p "Press Enter to continue..."
clear

# Step 9: Run smoke tests
echo -e "${CYAN}${BOLD}Step 9: Smoke Tests${NC}"
echo ""

read -p "Run smoke tests? (y/n): " run_tests

if [[ $run_tests =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your production API URL (e.g., https://api.yourdomain.com): " api_url

    echo ""
    echo "Running smoke tests..."
    python3 scripts/smoke_test.py --url "$api_url" --verbose

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    else
        echo ""
        echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    fi
else
    echo -e "${YELLOW}Skipping smoke tests${NC}"
fi

echo ""
read -p "Press Enter to continue..."
clear

# Final summary
echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              Deployment Complete! 🚀                       ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${GREEN}${BOLD}Your Quant Analytics Platform is deployed!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Visit your frontend URL and test the application"
echo "  2. Check Sentry for any errors"
echo "  3. Review Grafana dashboards"
echo "  4. Monitor logs for the first hour"
echo "  5. Test all critical features"
echo ""
echo "Resources:"
echo "  • Deployment Guide: DEPLOYMENT_GUIDE.md"
echo "  • Production Checklist: PRODUCTION_CHECKLIST.md"
echo "  • Monitoring Guide: monitoring/README.md"
echo ""
echo "Support:"
echo "  • GitHub Issues: https://github.com/yourorg/quant/issues"
echo "  • Documentation: See README.md"
echo ""
echo -e "${YELLOW}Remember to:${NC}"
echo "  • Keep .env.production secure (never commit to git)"
echo "  • Monitor error rates for the first 24 hours"
echo "  • Set up regular backups"
echo "  • Test the rollback procedure"
echo ""
echo -e "${CYAN}Happy deploying! 🎉${NC}"
echo ""
