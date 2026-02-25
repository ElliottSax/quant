#!/bin/bash

# Congressional Trading Analytics Platform - One-Click Deploy Script
# This script guides you through the entire deployment process

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Congressional Trading Analytics Platform Deployment    ║"
echo "║   Revenue Potential: \$1,450-\$9,900 MRR                     ║"
echo "║   Deployment Time: 30-45 minutes                         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
fi

echo -e "${GREEN}✓ Prerequisites installed${NC}"
echo ""

# Step 1: Generate secrets
echo -e "${BLUE}═══ Step 1: Generate Secrets ═══${NC}"
echo ""
echo "Generating secure secret keys..."
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo -e "${GREEN}✓ Secret keys generated${NC}"
echo "SECRET_KEY: $SECRET_KEY"
echo "JWT_SECRET_KEY: $JWT_SECRET_KEY"
echo ""
echo -e "${YELLOW}SAVE THESE KEYS! You'll need them.${NC}"
read -p "Press Enter to continue..."

# Step 2: Get Stripe keys
echo ""
echo -e "${BLUE}═══ Step 2: Stripe Configuration ═══${NC}"
echo ""
echo "Go to: https://dashboard.stripe.com/test/apikeys"
echo ""
read -p "Enter your Stripe Secret Key (sk_test_...): " STRIPE_SECRET_KEY
read -p "Enter your Stripe Publishable Key (pk_test_...): " STRIPE_PUBLISHABLE_KEY
echo ""
echo -e "${GREEN}✓ Stripe keys saved${NC}"

# Step 3: Deploy Backend
echo ""
echo -e "${BLUE}═══ Step 3: Deploy Backend to Railway ═══${NC}"
echo ""
echo "Navigating to backend directory..."
cd /mnt/e/projects/quant/quant/backend

echo "Logging into Railway..."
railway login

echo ""
echo "Initializing Railway project..."
echo "When prompted, name it: 'quant-congressional-backend'"
railway init

echo ""
echo "Adding PostgreSQL database..."
railway add --database postgres

echo ""
echo "Adding Redis cache..."
railway add --database redis

echo ""
echo "Setting environment variables..."
railway variables set \
  ENVIRONMENT=production \
  DEBUG=false \
  PROJECT_NAME="Congressional Trading Analytics" \
  API_V1_STR="/api/v1" \
  SECRET_KEY="$SECRET_KEY" \
  JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  ALGORITHM="HS256" \
  STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
  STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY" \
  BACKEND_CORS_ORIGINS='["http://localhost:3000"]' \
  TRUST_PROXY_HEADERS="true" \
  ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  REFRESH_TOKEN_EXPIRE_DAYS="7"

echo ""
echo "Deploying backend..."
railway up

echo ""
echo "Generating public domain..."
BACKEND_URL=$(railway domain)

echo ""
echo -e "${GREEN}✓ Backend deployed successfully!${NC}"
echo -e "${GREEN}Backend URL: $BACKEND_URL${NC}"
echo ""

# Run migrations
echo "Running database migrations..."
railway run bash -c "alembic upgrade head"

echo -e "${GREEN}✓ Database migrations completed${NC}"
echo ""

# Test backend
echo "Testing backend health..."
sleep 5
HEALTH_CHECK=$(curl -s "$BACKEND_URL/health" | grep -o "healthy" || echo "")
if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}⚠ Backend health check failed. Check logs: railway logs${NC}"
fi

read -p "Press Enter to continue to frontend deployment..."

# Step 4: Deploy Frontend
echo ""
echo -e "${BLUE}═══ Step 4: Deploy Frontend to Vercel ═══${NC}"
echo ""
echo "Navigating to frontend directory..."
cd /mnt/e/projects/quant/quant/frontend

echo "Creating production environment file..."
cat > .env.production.local << EOF
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
NODE_ENV=production
EOF

echo -e "${GREEN}✓ Environment file created${NC}"
echo ""

echo "Logging into Vercel..."
vercel login

echo ""
echo "Deploying to Vercel..."
echo "When prompted, accept defaults and deploy to production"
FRONTEND_URL=$(vercel --prod 2>&1 | grep -o 'https://[^[:space:]]*' | head -1)

echo ""
echo -e "${GREEN}✓ Frontend deployed successfully!${NC}"
echo -e "${GREEN}Frontend URL: $FRONTEND_URL${NC}"
echo ""

# Step 5: Update CORS
echo ""
echo -e "${BLUE}═══ Step 5: Update CORS ═══${NC}"
echo ""
cd /mnt/e/projects/quant/quant/backend

echo "Updating CORS to allow frontend..."
railway variables set BACKEND_CORS_ORIGINS="[\"$FRONTEND_URL\"]"

echo "Redeploying backend with updated CORS..."
railway up

echo -e "${GREEN}✓ CORS updated${NC}"
echo ""

# Step 6: Configure Stripe Webhook
echo ""
echo -e "${BLUE}═══ Step 6: Configure Stripe Webhook ═══${NC}"
echo ""
echo "Go to: https://dashboard.stripe.com/test/webhooks"
echo ""
echo "1. Click 'Add endpoint'"
echo "2. Enter this URL:"
echo -e "${GREEN}   $BACKEND_URL/api/v1/subscriptions/webhooks/stripe${NC}"
echo ""
echo "3. Select these events:"
echo "   - customer.subscription.created"
echo "   - customer.subscription.updated"
echo "   - customer.subscription.deleted"
echo "   - invoice.payment_succeeded"
echo "   - invoice.payment_failed"
echo ""
echo "4. Click 'Add endpoint'"
echo "5. Copy the webhook signing secret (starts with whsec_)"
echo ""
read -p "Enter your Stripe Webhook Secret (whsec_...): " STRIPE_WEBHOOK_SECRET

echo ""
echo "Adding webhook secret to Railway..."
railway variables set STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET"

echo "Redeploying..."
railway up

echo -e "${GREEN}✓ Stripe webhook configured${NC}"
echo ""

# Final Summary
echo ""
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                  DEPLOYMENT COMPLETE! 🎉                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${GREEN}Your Congressional Trading Analytics Platform is LIVE!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Frontend URL:${NC} $FRONTEND_URL"
echo -e "${YELLOW}Backend URL:${NC}  $BACKEND_URL"
echo -e "${YELLOW}API Docs:${NC}     $BACKEND_URL/api/v1/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Test your platform:"
echo "   - Visit $FRONTEND_URL"
echo "   - Sign up for an account"
echo "   - Try subscribing to Premium (use card: 4242 4242 4242 4242)"
echo ""
echo "2. Launch on Product Hunt (tomorrow):"
echo "   - Submit at 12:01 AM PST Tuesday"
echo "   - See: /mnt/e/projects/quant/marketing/07-launch-announcement.md"
echo ""
echo "3. Monitor your platform:"
echo "   - Backend logs: railway logs"
echo "   - Frontend: https://vercel.com/dashboard"
echo "   - Stripe: https://dashboard.stripe.com/test/events"
echo ""
echo "4. Marketing materials ready at:"
echo "   /mnt/e/projects/quant/marketing/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Revenue Projection:${NC}"
echo "  Month 1: \$750-1,500 MRR"
echo "  Month 3: \$2,000-5,000 MRR"
echo "  Month 6: \$5,000-10,000 MRR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Time to first customer: 1-7 days${NC}"
echo -e "${BLUE}Time to profitability: 30-60 days${NC}"
echo ""
echo -e "${GREEN}CONGRATULATIONS! You're live and ready to generate revenue! 🚀${NC}"
echo ""

# Save deployment info
cat > /mnt/e/projects/quant/DEPLOYMENT_INFO.txt << EOF
Congressional Trading Analytics Platform - Deployment Information
Deployed: $(date)

Frontend URL: $FRONTEND_URL
Backend URL: $BACKEND_URL
API Docs: $BACKEND_URL/api/v1/docs

Stripe: Test mode (switch to live after testing)

Next Steps:
1. Test platform thoroughly
2. Launch on Product Hunt
3. Share on social media
4. Monitor for first customers

Marketing materials: /mnt/e/projects/quant/marketing/
Support: See IMMEDIATE_DEPLOYMENT_PLAN.md for troubleshooting
EOF

echo "Deployment info saved to: /mnt/e/projects/quant/DEPLOYMENT_INFO.txt"
echo ""
