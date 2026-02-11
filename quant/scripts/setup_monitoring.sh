#!/bin/bash
set -e

# Monitoring Setup Script
# Sets up Sentry, Prometheus, and Grafana for the Quant Platform

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
echo -e "${BLUE}║     Monitoring Setup - Quant Platform             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env.production exists
if [[ ! -f .env.production ]]; then
    log_error ".env.production not found"
    log_info "Copy .env.example to .env.production and fill in values"
    exit 1
fi

# Source environment variables
source .env.production

# 1. Sentry Setup
log_info "Setting up Sentry..."

if [[ -z "$SENTRY_DSN" ]] || [[ "$SENTRY_DSN" == "your-sentry-dsn" ]]; then
    log_warning "Sentry DSN not configured"
    echo ""
    echo "To set up Sentry:"
    echo "1. Go to https://sentry.io and create account"
    echo "2. Create new project (Python/FastAPI)"
    echo "3. Copy DSN and add to .env.production"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
else
    log_success "Sentry DSN configured"

    # Test Sentry connection
    log_info "Testing Sentry connection..."
    python3 << EOF
import sentry_sdk
sentry_sdk.init(dsn="$SENTRY_DSN", environment="$SENTRY_ENVIRONMENT")
sentry_sdk.capture_message("Test message from setup script")
print("✓ Test message sent to Sentry")
EOF
    log_success "Sentry connection successful"
fi

# 2. Prometheus Setup
log_info "Setting up Prometheus..."

if command -v docker &> /dev/null; then
    log_info "Starting Prometheus with Docker..."
    docker-compose -f docker-compose.production.yml up -d prometheus

    # Wait for Prometheus to start
    sleep 5

    # Check if Prometheus is running
    if curl -f http://localhost:9090/-/healthy &> /dev/null; then
        log_success "Prometheus is running at http://localhost:9090"
    else
        log_error "Prometheus failed to start"
    fi
else
    log_warning "Docker not found. Install Prometheus manually:"
    echo "1. Download from https://prometheus.io/download/"
    echo "2. Extract and run with: ./prometheus --config.file=monitoring/prometheus/prometheus.yml"
fi

# 3. Grafana Setup
log_info "Setting up Grafana..."

if command -v docker &> /dev/null; then
    log_info "Starting Grafana with Docker..."
    docker-compose -f docker-compose.production.yml up -d grafana

    # Wait for Grafana to start
    sleep 10

    # Check if Grafana is running
    if curl -f http://localhost:3001/api/health &> /dev/null; then
        log_success "Grafana is running at http://localhost:3001"
        echo ""
        echo "Default credentials:"
        echo "  Username: admin"
        echo "  Password: (set in GRAFANA_ADMIN_PASSWORD)"
        echo ""
    else
        log_error "Grafana failed to start"
    fi
else
    log_warning "Docker not found. Use Grafana Cloud:"
    echo "1. Sign up at https://grafana.com"
    echo "2. Create new stack"
    echo "3. Add Prometheus data source"
    echo "4. Import dashboards from monitoring/grafana/dashboards/"
fi

# 4. Alert Setup
log_info "Setting up alerts..."

if [[ -z "$SLACK_WEBHOOK_URL" ]] || [[ "$SLACK_WEBHOOK_URL" == "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" ]]; then
    log_warning "Slack webhook not configured"
    echo ""
    echo "To set up Slack alerts:"
    echo "1. Go to https://api.slack.com/apps"
    echo "2. Create new app → Incoming Webhooks"
    echo "3. Activate and create webhook"
    echo "4. Copy webhook URL to .env.production"
    echo ""
else
    log_success "Slack webhook configured"

    # Test Slack webhook
    log_info "Testing Slack webhook..."
    if curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"✅ Monitoring setup complete - Test alert from Quant Platform"}' \
        "$SLACK_WEBHOOK_URL" &> /dev/null; then
        log_success "Slack webhook test successful"
    else
        log_error "Slack webhook test failed"
    fi
fi

# 5. Health Check
log_info "Setting up health checks..."

# Create health check script
cat > /tmp/health_check.sh << 'HEALTH_EOF'
#!/bin/bash
# Quick health check script

API_URL=${1:-http://localhost:8000}

echo "Checking $API_URL/health..."
if curl -f "$API_URL/health" 2>/dev/null | jq .; then
    echo "✓ Health check passed"
    exit 0
else
    echo "✗ Health check failed"
    exit 1
fi
HEALTH_EOF

chmod +x /tmp/health_check.sh
log_success "Health check script created at /tmp/health_check.sh"

# 6. Verify Metrics Endpoint
log_info "Verifying metrics endpoint..."

if [[ ! -z "$PRODUCTION_API_URL" ]]; then
    if curl -f "$PRODUCTION_API_URL/api/v1/metrics" &> /dev/null; then
        log_success "Metrics endpoint is accessible"
    else
        log_warning "Metrics endpoint not accessible (may not be deployed yet)"
    fi
fi

# 7. Create monitoring dashboard URLs file
log_info "Creating dashboard URLs reference..."

cat > MONITORING_URLS.md << 'URLS_EOF'
# Monitoring Dashboard URLs

## Development
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- API Health: http://localhost:8000/health
- API Metrics: http://localhost:8000/api/v1/metrics

## Production
- Sentry: https://sentry.io/organizations/YOUR_ORG/projects/
- API Health: https://api.yourdomain.com/health
- API Metrics: https://api.yourdomain.com/api/v1/metrics (restricted)
- Grafana: https://grafana.yourdomain.com (or grafana.com for cloud)
- Railway Logs: https://railway.app/project/YOUR_PROJECT

## Quick Commands

### Check Health
```bash
curl https://api.yourdomain.com/health | jq .
```

### View Metrics
```bash
curl https://api.yourdomain.com/api/v1/metrics
```

### Test Alerts
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test alert"}'
```

### View Logs
```bash
railway logs --environment production
```
URLS_EOF

log_success "Created MONITORING_URLS.md"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Monitoring Setup Complete!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo "Next steps:"
echo ""
echo "1. Configure missing credentials in .env.production"
echo "2. Import Grafana dashboards from monitoring/grafana/dashboards/"
echo "3. Set up alert rules in Prometheus"
echo "4. Test alerting with: curl -X POST \$SLACK_WEBHOOK_URL ..."
echo "5. Review MONITORING_URLS.md for all dashboard links"
echo ""
echo "For detailed instructions, see monitoring/README.md"
echo ""
