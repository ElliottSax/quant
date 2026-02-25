#!/bin/bash

# Production Readiness Verification Script
# Checks that all critical configurations are in place before deployment

set -e

echo "=================================="
echo "Quant Platform - Production Readiness Check"
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
    ((ERRORS++))
}

warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo "ℹ $1"
}

# Check 1: Environment files exist
echo "1. Checking environment files..."
if [ -f "/mnt/e/projects/quant/.env.production.example" ]; then
    success ".env.production.example exists"
else
    error ".env.production.example missing"
fi

if [ -f "/mnt/e/projects/quant/quant/frontend/.env.production.example" ]; then
    success "Frontend .env.production.example exists"
else
    error "Frontend .env.production.example missing"
fi

if [ -f "/mnt/e/projects/quant/quant/backend/.env.example" ]; then
    success "Backend .env.example exists"
else
    error "Backend .env.example missing"
fi

echo ""

# Check 2: Vercel configuration
echo "2. Checking Vercel configuration..."
if [ -f "/mnt/e/projects/quant/vercel.json" ]; then
    success "Root vercel.json exists"
else
    warning "Root vercel.json missing (optional)"
fi

if [ -f "/mnt/e/projects/quant/quant/frontend/vercel.json" ]; then
    success "Frontend vercel.json exists"
else
    warning "Frontend vercel.json missing (will use defaults)"
fi

if [ -f "/mnt/e/projects/quant/quant/frontend/next.config.js" ]; then
    success "next.config.js exists"

    # Check for security headers
    if grep -q "X-Content-Type-Options" "/mnt/e/projects/quant/quant/frontend/next.config.js"; then
        success "Security headers configured"
    else
        warning "Security headers not found in next.config.js"
    fi
else
    error "next.config.js missing"
fi

echo ""

# Check 3: Backend configuration
echo "3. Checking backend configuration..."
if [ -f "/mnt/e/projects/quant/quant/backend/requirements.txt" ]; then
    success "requirements.txt exists"

    # Check for critical dependencies
    if grep -q "fastapi" "/mnt/e/projects/quant/quant/backend/requirements.txt"; then
        success "FastAPI dependency present"
    else
        error "FastAPI not in requirements.txt"
    fi

    if grep -q "stripe" "/mnt/e/projects/quant/quant/backend/requirements.txt"; then
        success "Stripe dependency present"
    else
        warning "Stripe not in requirements.txt (needed for payments)"
    fi

    if grep -q "sentry-sdk" "/mnt/e/projects/quant/quant/backend/requirements.txt"; then
        success "Sentry SDK present (error tracking)"
    else
        warning "Sentry SDK not in requirements.txt (recommended for production)"
    fi
else
    error "requirements.txt missing"
fi

if [ -f "/mnt/e/projects/quant/quant/backend/app/main.py" ]; then
    success "Backend main.py exists"

    # Check for CORS middleware
    if grep -q "CORSMiddleware" "/mnt/e/projects/quant/quant/backend/app/main.py"; then
        success "CORS middleware configured"
    else
        warning "CORS middleware not found"
    fi

    # Check for rate limiting
    if grep -q "RateLimitMiddleware\|rate_limit" "/mnt/e/projects/quant/quant/backend/app/main.py"; then
        success "Rate limiting configured"
    else
        warning "Rate limiting not found (recommended for production)"
    fi
else
    error "Backend main.py missing"
fi

echo ""

# Check 4: Stripe integration
echo "4. Checking Stripe integration..."
if [ -f "/mnt/e/projects/quant/quant/backend/app/api/v1/subscriptions.py" ]; then
    success "Subscription endpoint exists"

    # Check for webhook handler
    if grep -q "stripe_webhook\|webhooks/stripe" "/mnt/e/projects/quant/quant/backend/app/api/v1/subscriptions.py"; then
        success "Stripe webhook handler exists"
    else
        error "Stripe webhook handler not found"
    fi

    # Check for webhook signature verification
    if grep -q "STRIPE_WEBHOOK_SECRET\|construct_event" "/mnt/e/projects/quant/quant/backend/app/api/v1/subscriptions.py"; then
        success "Webhook signature verification present"
    else
        error "Webhook signature verification missing (SECURITY RISK)"
    fi
else
    error "Subscription endpoint missing"
fi

echo ""

# Check 5: Database migrations
echo "5. Checking database setup..."
if [ -f "/mnt/e/projects/quant/quant/backend/alembic.ini" ]; then
    success "Alembic configuration exists"
else
    warning "alembic.ini missing (database migrations)"
fi

if [ -d "/mnt/e/projects/quant/quant/backend/alembic/versions" ]; then
    MIGRATION_COUNT=$(find "/mnt/e/projects/quant/quant/backend/alembic/versions" -name "*.py" | wc -l)
    if [ "$MIGRATION_COUNT" -gt 0 ]; then
        success "Database migrations exist ($MIGRATION_COUNT migrations)"
    else
        warning "No database migrations found"
    fi
else
    warning "alembic/versions directory missing"
fi

echo ""

# Check 6: Frontend dependencies
echo "6. Checking frontend dependencies..."
if [ -f "/mnt/e/projects/quant/quant/frontend/package.json" ]; then
    success "Frontend package.json exists"

    # Check for critical dependencies
    if grep -q '"next"' "/mnt/e/projects/quant/quant/frontend/package.json"; then
        success "Next.js dependency present"
    else
        error "Next.js not in package.json"
    fi

    # Check for build script
    if grep -q '"build".*"next build"' "/mnt/e/projects/quant/quant/frontend/package.json"; then
        success "Build script configured"
    else
        error "Build script missing or incorrect"
    fi
else
    error "Frontend package.json missing"
fi

echo ""

# Check 7: Security configurations
echo "7. Checking security configurations..."

# Check backend config
if [ -f "/mnt/e/projects/quant/quant/backend/app/core/config.py" ]; then
    success "Backend config.py exists"

    # Check for secret key validation
    if grep -q "validate_secret_key\|SECRET_KEY" "/mnt/e/projects/quant/quant/backend/app/core/config.py"; then
        success "Secret key configuration present"
    else
        warning "Secret key validation not found"
    fi

    # Check for CORS origins
    if grep -q "BACKEND_CORS_ORIGINS" "/mnt/e/projects/quant/quant/backend/app/core/config.py"; then
        success "CORS origins configuration present"
    else
        error "CORS origins not configured"
    fi

    # Check for Stripe webhook secret
    if grep -q "STRIPE_WEBHOOK_SECRET" "/mnt/e/projects/quant/quant/backend/app/core/config.py"; then
        success "Stripe webhook secret configuration present"
    else
        error "Stripe webhook secret not in config (CRITICAL)"
    fi
else
    error "Backend config.py missing"
fi

echo ""

# Check 8: Documentation
echo "8. Checking deployment documentation..."
if [ -f "/mnt/e/projects/quant/VERCEL_DEPLOYMENT_GUIDE.md" ]; then
    success "Vercel deployment guide exists"
else
    warning "VERCEL_DEPLOYMENT_GUIDE.md missing"
fi

if [ -f "/mnt/e/projects/quant/DEPLOYMENT_CHECKLIST.md" ]; then
    success "Deployment checklist exists"
else
    warning "DEPLOYMENT_CHECKLIST.md missing"
fi

echo ""

# Check 9: Critical files
echo "9. Checking critical files..."
CRITICAL_FILES=(
    "/mnt/e/projects/quant/quant/backend/app/main.py"
    "/mnt/e/projects/quant/quant/backend/app/core/config.py"
    "/mnt/e/projects/quant/quant/backend/app/core/database.py"
    "/mnt/e/projects/quant/quant/backend/requirements.txt"
    "/mnt/e/projects/quant/quant/frontend/package.json"
    "/mnt/e/projects/quant/quant/frontend/next.config.js"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$(basename "$file") exists"
    else
        error "$(basename "$file") missing"
    fi
done

echo ""

# Summary
echo "=================================="
echo "Summary"
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ PERFECT! No errors or warnings.${NC}"
    echo -e "${GREEN}Your platform is production-ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review VERCEL_DEPLOYMENT_GUIDE.md"
    echo "2. Follow DEPLOYMENT_CHECKLIST.md"
    echo "3. Deploy backend to Railway"
    echo "4. Deploy frontend to Vercel"
    echo "5. Configure Stripe webhooks"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ WARNINGS: $WARNINGS warning(s) found.${NC}"
    echo "Your platform is mostly ready, but review warnings above."
    echo ""
    echo "Warnings are non-critical but recommended to fix."
    echo ""
    exit 0
else
    echo -e "${RED}✗ ERRORS: $ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo ""
    echo "Fix the errors above before deploying to production."
    echo "Errors marked as CRITICAL or SECURITY RISK must be fixed."
    echo ""
    exit 1
fi
