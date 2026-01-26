#!/bin/bash
# Quant Trading Platform - Deployment Script
# Supports: Railway, Heroku, DigitalOcean

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}\n"
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
    echo -e "   $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Generate secure secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

# Pre-deployment check
print_header "Pre-Deployment Check"
if [ -f "quant/backend/scripts/pre_deployment_check.py" ]; then
    python3 quant/backend/scripts/pre_deployment_check.py
    if [ $? -ne 0 ]; then
        print_error "Pre-deployment check failed. Please fix issues before deploying."
        exit 1
    fi
else
    print_warning "Pre-deployment check script not found. Skipping..."
fi

# Main menu
print_header "Quant Trading Platform - Deployment"
echo "Choose your deployment platform:"
echo ""
echo "1. Railway (Recommended - Easiest, 5 min)"
echo "2. Heroku (Popular - 7 min)"
echo "3. DigitalOcean App Platform (Balanced - 10 min)"
echo "4. Manual Setup Instructions"
echo "5. Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        # Railway Deployment
        print_header "Railway Deployment"

        # Check if Railway CLI is installed
        if ! command_exists railway; then
            print_warning "Railway CLI not installed."
            echo ""
            echo "Install Railway CLI:"
            echo "  npm install -g @railway/cli"
            echo "  # or"
            echo "  brew install railway"
            echo ""
            read -p "Install now using npm? (y/n): " install_railway
            if [ "$install_railway" = "y" ]; then
                npm install -g @railway/cli
            else
                print_error "Please install Railway CLI and try again."
                exit 1
            fi
        fi

        print_success "Railway CLI found"

        # Login to Railway
        print_info "Logging into Railway..."
        railway login

        # Initialize project
        print_info "Initializing Railway project..."
        railway init

        # Add PostgreSQL
        print_info "Adding PostgreSQL database..."
        railway add --database postgres

        # Generate and set environment variables
        print_info "Setting environment variables..."
        SECRET_KEY=$(generate_secret_key)

        railway variables set ENVIRONMENT=production
        railway variables set DEBUG=false
        railway variables set SECRET_KEY="$SECRET_KEY"

        print_success "Environment variables set"

        # Deploy
        print_info "Deploying application..."
        railway up

        # Get domain
        print_info "Setting up domain..."
        railway domain

        print_success "Deployment complete!"
        echo ""
        print_info "Your API is now live! Check Railway dashboard for URL."
        echo ""
        print_info "Next steps:"
        echo "  1. Visit Railway dashboard to get your URL"
        echo "  2. Test: curl https://your-app.railway.app/health"
        echo "  3. View API docs: https://your-app.railway.app/api/v1/docs"
        ;;

    2)
        # Heroku Deployment
        print_header "Heroku Deployment"

        # Check if Heroku CLI is installed
        if ! command_exists heroku; then
            print_warning "Heroku CLI not installed."
            echo ""
            echo "Install Heroku CLI:"
            echo "  brew install heroku/brew/heroku"
            echo "  # or download from: https://devcenter.heroku.com/articles/heroku-cli"
            echo ""
            print_error "Please install Heroku CLI and try again."
            exit 1
        fi

        print_success "Heroku CLI found"

        # Login to Heroku
        print_info "Logging into Heroku..."
        heroku login

        # Get app name
        read -p "Enter app name (e.g., quant-trading-platform): " app_name

        # Create app
        print_info "Creating Heroku app..."
        heroku create "$app_name"

        # Add PostgreSQL
        print_info "Adding PostgreSQL addon..."
        heroku addons:create heroku-postgresql:mini

        # Add Redis (optional)
        read -p "Add Redis addon? (y/n): " add_redis
        if [ "$add_redis" = "y" ]; then
            heroku addons:create heroku-redis:mini
        fi

        # Set environment variables
        print_info "Setting environment variables..."
        SECRET_KEY=$(generate_secret_key)

        heroku config:set ENVIRONMENT=production
        heroku config:set DEBUG=false
        heroku config:set SECRET_KEY="$SECRET_KEY"

        print_success "Environment variables set"

        # Check git setup
        if [ ! -d ".git" ]; then
            print_warning "Not a git repository. Initializing..."
            git init
            git add .
            git commit -m "Initial commit for Heroku deployment"
        fi

        # Deploy
        print_info "Deploying to Heroku..."
        git push heroku main || git push heroku master

        # Run migrations
        print_info "Running database migrations..."
        heroku run "cd quant/backend && alembic upgrade head"

        # Open app
        print_success "Deployment complete!"
        echo ""
        heroku open
        ;;

    3)
        # DigitalOcean
        print_header "DigitalOcean App Platform Deployment"

        echo "Manual deployment via DigitalOcean web UI:"
        echo ""
        echo "1. Go to https://cloud.digitalocean.com/apps"
        echo "2. Click 'Create App'"
        echo "3. Connect your GitHub repository"
        echo "4. Select branch: main"
        echo "5. Configure build settings:"
        echo "   Build Command: cd quant/backend && pip install -r requirements.txt"
        echo "   Run Command: cd quant/backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "6. Add PostgreSQL database"
        echo "7. Set environment variables:"
        echo "   ENVIRONMENT=production"
        echo "   DEBUG=false"
        echo "   SECRET_KEY=$(generate_secret_key)"
        echo "8. Click 'Deploy'"
        echo ""
        print_info "After deployment, visit your app URL to verify."
        ;;

    4)
        # Manual instructions
        print_header "Manual Deployment Instructions"

        echo "Required environment variables:"
        echo ""
        echo "export ENVIRONMENT=production"
        echo "export DEBUG=false"
        echo "export SECRET_KEY=$(generate_secret_key)"
        echo "export DATABASE_URL=postgresql://user:password@host:5432/dbname"
        echo ""
        echo "Installation:"
        echo "  cd quant/backend"
        echo "  pip install -r requirements.txt"
        echo ""
        echo "Database migration:"
        echo "  alembic upgrade head"
        echo ""
        echo "Start server:"
        echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
        echo ""
        print_info "See ONE_CLICK_DEPLOY.md for platform-specific guides."
        ;;

    5)
        print_info "Deployment cancelled."
        exit 0
        ;;

    *)
        print_error "Invalid choice."
        exit 1
        ;;
esac

# Post-deployment verification
print_header "Post-Deployment Verification"
echo ""
read -p "Enter your deployed app URL (e.g., https://your-app.railway.app): " app_url

if [ -n "$app_url" ]; then
    print_info "Testing health endpoint..."
    if curl -s "$app_url/health" | grep -q "healthy\|ok"; then
        print_success "Health check passed"
    else
        print_warning "Health check failed. App may still be starting up."
    fi

    print_info "Testing public API..."
    if curl -s "$app_url/api/v1/market-data/public/quote/AAPL" | grep -q "AAPL\|symbol"; then
        print_success "Public API working"
    else
        print_warning "Public API test failed. Check logs."
    fi

    echo ""
    print_success "Deployment verification complete!"
    echo ""
    print_info "Access your API:"
    echo "  API Docs: $app_url/api/v1/docs"
    echo "  ReDoc: $app_url/api/v1/redoc"
    echo "  Health: $app_url/health"
fi

echo ""
print_header "Deployment Complete! 🎉"
echo ""
echo "Next steps:"
echo "  1. Test your API endpoints"
echo "  2. Set up monitoring (see WEEK_5_PLAN.md)"
echo "  3. Configure custom domain (optional)"
echo "  4. Set up backups"
echo ""
