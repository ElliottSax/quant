#!/bin/bash
set -e

# Deployment Script for Production
# Usage: ./scripts/deploy.sh [staging|production]

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Quant Analytics Platform Deployment           ║${NC}"
echo -e "${BLUE}║     Environment: ${ENVIRONMENT}                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI not found. Install with: npm i -g @railway/cli"
    exit 1
fi
log_success "Railway CLI found"

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    log_error "Not logged in to Railway. Run: railway login"
    exit 1
fi
log_success "Railway authentication verified"

# Check for required environment variables
if [[ "$ENVIRONMENT" == "production" ]]; then
    log_info "Checking production credentials..."

    required_vars=(
        "PRODUCTION_DATABASE_URL"
        "PRODUCTION_REDIS_URL"
        "SENTRY_DSN"
        "SECRET_KEY"
    )

    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        printf '  - %s\n' "${missing_vars[@]}"
        exit 1
    fi
    log_success "All required environment variables present"
fi

# Run tests
log_info "Running tests..."
cd "$PROJECT_ROOT/backend"

if ! pytest tests/ -v --tb=short; then
    log_error "Tests failed. Aborting deployment."
    exit 1
fi
log_success "All tests passed"

# Build check
log_info "Checking build..."
cd "$PROJECT_ROOT/backend"

if ! python -m py_compile app/**/*.py; then
    log_error "Python syntax check failed"
    exit 1
fi
log_success "Build check passed"

# Database migration check
log_info "Checking database migrations..."
cd "$PROJECT_ROOT/backend"

# Check for pending migrations
if alembic current 2>&1 | grep -q "Can't locate revision"; then
    log_warning "No database connection or pending migrations"
fi
log_success "Migration check complete"

# Confirm deployment
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo ""
    log_warning "You are about to deploy to PRODUCTION"
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
fi

# Deploy to Railway
log_info "Deploying to Railway ($ENVIRONMENT)..."
cd "$PROJECT_ROOT/backend"

if railway up --service backend --environment "$ENVIRONMENT"; then
    log_success "Backend deployed successfully"
else
    log_error "Backend deployment failed"
    exit 1
fi

# Wait for deployment to be ready
log_info "Waiting for deployment to be ready..."
sleep 30

# Run database migrations
log_info "Running database migrations..."

if [[ "$ENVIRONMENT" == "production" ]]; then
    DATABASE_URL="$PRODUCTION_DATABASE_URL"
else
    DATABASE_URL="$STAGING_DATABASE_URL"
fi

if alembic upgrade head; then
    log_success "Migrations completed"
else
    log_error "Migration failed"
    log_warning "Consider rolling back the deployment"
    exit 1
fi

# Run smoke tests
log_info "Running smoke tests..."

if [[ "$ENVIRONMENT" == "production" ]]; then
    API_URL="$PRODUCTION_API_URL"
else
    API_URL="$STAGING_API_URL"
fi

if python "$SCRIPT_DIR/smoke_test.py" --url "$API_URL"; then
    log_success "Smoke tests passed"
else
    log_error "Smoke tests failed"
    log_warning "Deployment may have issues. Check logs."
    exit 1
fi

# Create deployment tag
log_info "Creating deployment tag..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TAG="deploy-${ENVIRONMENT}-${TIMESTAMP}"

git tag -a "$TAG" -m "Deployment to $ENVIRONMENT at $TIMESTAMP"
git push origin "$TAG"
log_success "Created tag: $TAG"

# Success
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Deployment Completed Successfully!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Environment: $ENVIRONMENT"
log_info "API URL: $API_URL"
log_info "Tag: $TAG"
log_info "Time: $(date)"
echo ""
log_info "Next steps:"
echo "  1. Monitor logs: railway logs --service backend --environment $ENVIRONMENT"
echo "  2. Check metrics: https://grafana.yourdomain.com"
echo "  3. Verify in browser: $API_URL/api/v1/docs"
echo ""
