#!/bin/bash

# ========================================
# FREE TIER DEPLOYMENT SCRIPT
# Quant Analytics Platform
# ========================================
# Deploys entire platform to free tier services
# Total Cost: $0/month
# ========================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ========================================
# PRE-FLIGHT CHECKS
# ========================================
print_header "Pre-flight Checks"

# Check Node.js
if ! command_exists node; then
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check npm
if ! command_exists npm; then
    print_error "npm not found. Please install npm"
    exit 1
fi
print_success "npm found: $(npm --version)"

# Check Git
if ! command_exists git; then
    print_error "Git not found. Please install git"
    exit 1
fi
print_success "Git found: $(git --version)"

echo ""

# ========================================
# INSTALL CLI TOOLS
# ========================================
print_header "Installing Deployment CLIs"

# Install Vercel CLI
if ! command_exists vercel; then
    print_info "Installing Vercel CLI..."
    npm install -g vercel
    print_success "Vercel CLI installed"
else
    print_success "Vercel CLI already installed"
fi

# Install Railway CLI
if ! command_exists railway; then
    print_info "Installing Railway CLI..."
    npm install -g @railway/cli
    print_success "Railway CLI installed"
else
    print_success "Railway CLI already installed"
fi

echo ""

# ========================================
# SETUP CREDENTIALS
# ========================================
print_header "Authentication Setup"

# Login to Vercel
print_info "Logging into Vercel..."
print_warning "This will open your browser. Please authenticate."
sleep 2
if vercel whoami > /dev/null 2>&1; then
    print_success "Already logged into Vercel as: $(vercel whoami)"
else
    vercel login
    print_success "Logged into Vercel"
fi

# Login to Railway
print_info "Logging into Railway..."
print_warning "This will open your browser. Please authenticate."
sleep 2
if railway whoami > /dev/null 2>&1; then
    print_success "Already logged into Railway as: $(railway whoami)"
else
    railway login
    print_success "Logged into Railway"
fi

echo ""

# ========================================
# FREE SERVICES SETUP GUIDE
# ========================================
print_header "Free Services Setup Required"

echo ""
print_warning "Please setup these FREE services before continuing:"
echo ""
echo "1️⃣  Supabase PostgreSQL (FREE 500MB)"
echo "   → https://supabase.com/dashboard"
echo "   → Create new project"
echo "   → Copy DATABASE_URL from Settings → Database"
echo ""
echo "2️⃣  Upstash Redis (FREE 10K commands/day)"
echo "   → https://console.upstash.com"
echo "   → Create new database"
echo "   → Copy REDIS_URL"
echo ""
echo "3️⃣  Cloudflare R2 (FREE 10GB)"
echo "   → https://dash.cloudflare.com"
echo "   → R2 → Create bucket → Get API credentials"
echo "   → Copy AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
echo ""
echo "4️⃣  (Optional) Sentry Error Tracking (FREE 5K errors/month)"
echo "   → https://sentry.io"
echo "   → Create project → Copy DSN"
echo ""

read -p "Have you setup these services? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Please setup the services above and run this script again"
    exit 0
fi

echo ""

# ========================================
# DEPLOY BACKEND TO RAILWAY
# ========================================
print_header "Deploying Backend to Railway"

cd quant/backend || exit 1

# Initialize Railway project
if [ ! -f "railway.toml" ]; then
    print_error "railway.toml not found!"
    exit 1
fi

print_info "Initializing Railway project..."
railway init || true

# Set environment variables
print_info "Setting environment variables..."
print_warning "You'll need to provide your service credentials"

# SECRET_KEY
read -p "Enter SECRET_KEY (or press Enter to generate): " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -base64 32)
    print_success "Generated SECRET_KEY: $SECRET_KEY"
fi
railway variables set SECRET_KEY="$SECRET_KEY"

# DATABASE_URL
read -p "Enter Supabase DATABASE_URL: " DATABASE_URL
railway variables set DATABASE_URL="$DATABASE_URL"

# REDIS_URL
read -p "Enter Upstash REDIS_URL: " REDIS_URL
railway variables set REDIS_URL="$REDIS_URL"
railway variables set REDIS_ML_URL="$REDIS_URL"  # Use same Redis for now

# Cloudflare R2
read -p "Enter Cloudflare R2 Access Key ID: " R2_ACCESS_KEY
read -p "Enter Cloudflare R2 Secret Access Key: " R2_SECRET_KEY
read -p "Enter Cloudflare R2 Endpoint URL: " R2_ENDPOINT
railway variables set AWS_ACCESS_KEY_ID="$R2_ACCESS_KEY"
railway variables set AWS_SECRET_ACCESS_KEY="$R2_SECRET_KEY"
railway variables set AWS_S3_ENDPOINT_URL="$R2_ENDPOINT"

# Other variables
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"
railway variables set API_V1_STR="/api/v1"
railway variables set PROJECT_NAME="Quant Analytics Platform"

print_info "Deploying to Railway..."
railway up

# Get Railway URL
RAILWAY_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4 || echo "")

if [ -z "$RAILWAY_URL" ]; then
    print_warning "Could not automatically get Railway URL"
    read -p "Enter your Railway app URL (e.g., https://your-app.railway.app): " RAILWAY_URL
fi

print_success "Backend deployed to: $RAILWAY_URL"

# Update CORS
print_info "Setting CORS for frontend..."
railway variables set BACKEND_CORS_ORIGINS="https://localhost:3000,$RAILWAY_URL"

cd ../..

echo ""

# ========================================
# DEPLOY FRONTEND TO VERCEL
# ========================================
print_header "Deploying Frontend to Vercel"

cd quant/frontend || exit 1

# Create .env.production
print_info "Creating production environment file..."
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=$RAILWAY_URL
NODE_ENV=production
NEXT_PUBLIC_ENV=production
EOF

print_info "Deploying to Vercel..."
vercel --prod

# Get Vercel URL
VERCEL_URL=$(vercel inspect --json | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")

if [ -z "$VERCEL_URL" ]; then
    print_warning "Could not automatically get Vercel URL"
    read -p "Enter your Vercel app URL (e.g., https://your-app.vercel.app): " VERCEL_URL
fi

print_success "Frontend deployed to: $VERCEL_URL"

cd ../..

echo ""

# ========================================
# UPDATE BACKEND CORS
# ========================================
print_header "Updating Backend CORS"

cd quant/backend || exit 1

print_info "Adding Vercel URL to CORS..."
railway variables set BACKEND_CORS_ORIGINS="$VERCEL_URL,$RAILWAY_URL,http://localhost:3000"

print_info "Redeploying backend with updated CORS..."
railway up --detach

cd ../..

echo ""

# ========================================
# RUN DATABASE MIGRATIONS
# ========================================
print_header "Database Setup"

print_info "Running database migrations..."
cd quant/backend || exit 1

# Run migrations via Railway
railway run alembic upgrade head || print_warning "Migration failed - you may need to run manually"

cd ../..

echo ""

# ========================================
# DEPLOYMENT SUMMARY
# ========================================
print_header "🎉 DEPLOYMENT COMPLETE!"

echo ""
echo "📊 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "Backend API: $RAILWAY_URL"
print_success "Frontend App: $VERCEL_URL"
print_success "Monthly Cost: \$0 🎉"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Test your app: $VERCEL_URL"
echo "2. Check backend health: $RAILWAY_URL/health"
echo "3. View API docs: $RAILWAY_URL/api/v1/docs"
echo "4. Monitor Railway: https://railway.app/dashboard"
echo "5. Monitor Vercel: https://vercel.com/dashboard"
echo ""
echo "🔧 Useful Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  railway logs        # View backend logs"
echo "  vercel logs         # View frontend logs"
echo "  railway status      # Check backend status"
echo "  vercel inspect      # Check frontend status"
echo ""
echo "📚 Documentation:"
echo "  - FREE_COMPUTE_STRATEGY.md"
echo "  - .env.free-tier.example"
echo ""
print_success "Your platform is now running on 100% FREE infrastructure!"
echo ""
