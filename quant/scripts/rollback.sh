#!/bin/bash
set -e

# Rollback Script for Production
# Usage: ./scripts/rollback.sh [staging|production] [tag]

ENVIRONMENT=${1:-production}
TARGET_TAG=${2}
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
echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║          ROLLBACK PROCEDURE                        ║${NC}"
echo -e "${RED}║     Environment: ${ENVIRONMENT}                           ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    log_error "Railway CLI not found. Install with: npm i -g @railway/cli"
    exit 1
fi

# If no tag specified, show recent deployments
if [[ -z "$TARGET_TAG" ]]; then
    log_info "Recent deployment tags:"
    git tag -l "deploy-${ENVIRONMENT}-*" --sort=-creatordate | head -10
    echo ""
    read -p "Enter tag to rollback to (or press Ctrl+C to cancel): " TARGET_TAG
fi

# Verify tag exists
if ! git rev-parse "$TARGET_TAG" >/dev/null 2>&1; then
    log_error "Tag '$TARGET_TAG' not found"
    exit 1
fi

# Show what we're rolling back to
log_info "Rollback details:"
echo "  Environment: $ENVIRONMENT"
echo "  Target tag: $TARGET_TAG"
echo "  Commit: $(git rev-parse --short "$TARGET_TAG")"
echo "  Date: $(git log -1 --format=%ai "$TARGET_TAG")"
echo ""

# Confirm rollback
if [[ "$ENVIRONMENT" == "production" ]]; then
    log_warning "⚠️  YOU ARE ABOUT TO ROLLBACK PRODUCTION ⚠️"
    echo ""
    read -p "Are you ABSOLUTELY sure? Type 'ROLLBACK' to confirm: " -r
    echo ""
    if [[ $REPLY != "ROLLBACK" ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
fi

# Create backup of current state
log_info "Creating backup tag of current state..."
BACKUP_TAG="backup-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
git tag "$BACKUP_TAG"
log_success "Created backup tag: $BACKUP_TAG"

# Checkout target version
log_info "Checking out target version..."
cd "$PROJECT_ROOT"
git checkout "$TARGET_TAG"

# Railway rollback
log_info "Rolling back Railway deployment..."
cd "$PROJECT_ROOT/backend"

if railway rollback --service backend --environment "$ENVIRONMENT"; then
    log_success "Railway rollback successful"
else
    log_error "Railway rollback failed"
    log_warning "Attempting manual deployment..."

    if railway up --service backend --environment "$ENVIRONMENT"; then
        log_success "Manual deployment successful"
    else
        log_error "Manual deployment failed"
        log_error "Restoring from backup..."
        git checkout "$BACKUP_TAG"
        exit 1
    fi
fi

# Wait for rollback to complete
log_info "Waiting for rollback to complete..."
sleep 30

# Check database migration state
log_info "Checking database migration state..."

if [[ "$ENVIRONMENT" == "production" ]]; then
    DATABASE_URL="$PRODUCTION_DATABASE_URL"
    API_URL="$PRODUCTION_API_URL"
else
    DATABASE_URL="$STAGING_DATABASE_URL"
    API_URL="$STAGING_API_URL"
fi

CURRENT_REVISION=$(alembic current 2>&1 | grep -oP '(?<=\()[a-f0-9]+(?=\))')
log_info "Current database revision: $CURRENT_REVISION"

# Ask about database rollback
log_warning "Database migration rollback required?"
read -p "Do you need to rollback database migrations? (yes/no): " -r
echo ""

if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log_info "Available revisions:"
    alembic history | head -20
    echo ""
    read -p "Enter target revision (or 'head' for latest): " TARGET_REVISION

    log_warning "This will modify the database!"
    read -p "Confirm database rollback? (yes/no): " -r
    echo ""

    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Rolling back database to $TARGET_REVISION..."
        if alembic downgrade "$TARGET_REVISION"; then
            log_success "Database rollback successful"
        else
            log_error "Database rollback failed"
            log_warning "Manual intervention required!"
            exit 1
        fi
    fi
fi

# Run smoke tests
log_info "Running smoke tests..."

if python "$SCRIPT_DIR/smoke_test.py" --url "$API_URL"; then
    log_success "Smoke tests passed"
else
    log_error "Smoke tests failed after rollback"
    log_warning "System may be unstable. Check logs immediately."
fi

# Return to previous branch
log_info "Returning to main branch..."
git checkout main

# Create rollback tag
ROLLBACK_TAG="rollback-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
git tag -a "$ROLLBACK_TAG" -m "Rollback to $TARGET_TAG"
git push origin "$ROLLBACK_TAG"
git push origin "$BACKUP_TAG"

# Success
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Rollback Completed                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "Rolled back to: $TARGET_TAG"
log_info "Backup tag: $BACKUP_TAG"
log_info "Rollback tag: $ROLLBACK_TAG"
log_info "Time: $(date)"
echo ""
log_warning "Post-rollback checklist:"
echo "  [ ] Monitor error rates in Sentry"
echo "  [ ] Check application logs"
echo "  [ ] Verify key functionality"
echo "  [ ] Update team on rollback"
echo "  [ ] Investigate original issue"
echo "  [ ] Create postmortem document"
echo ""
