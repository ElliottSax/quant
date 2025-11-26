#!/bin/bash
# =============================================================================
# SSL Certificate Initialization Script (Let's Encrypt)
# =============================================================================

set -e

# Configuration
DOMAIN=${1:-yourdomain.com}
EMAIL=${2:-admin@yourdomain.com}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# Validation
# =============================================================================
if [ "$DOMAIN" == "yourdomain.com" ]; then
    log_error "Please provide your actual domain name"
    echo "Usage: ./init-ssl.sh yourdomain.com admin@yourdomain.com"
    exit 1
fi

log_info "Initializing SSL certificates for ${DOMAIN}..."

# =============================================================================
# Create directories
# =============================================================================
mkdir -p certbot/conf
mkdir -p certbot/www

# =============================================================================
# Download recommended TLS parameters
# =============================================================================
log_info "Downloading recommended TLS parameters..."

if [ ! -f "certbot/conf/options-ssl-nginx.conf" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > certbot/conf/options-ssl-nginx.conf
fi

if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > certbot/conf/ssl-dhparams.pem
fi

log_info "TLS parameters downloaded ✓"

# =============================================================================
# Create dummy certificate for nginx startup
# =============================================================================
log_info "Creating dummy certificate..."

CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"
mkdir -p "certbot/conf/live/${DOMAIN}"

docker-compose -f docker-compose.production.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout '${CERT_PATH}/privkey.pem' \
    -out '${CERT_PATH}/fullchain.pem' \
    -subj '/CN=localhost'" certbot

log_info "Dummy certificate created ✓"

# =============================================================================
# Start nginx
# =============================================================================
log_info "Starting nginx..."
docker-compose -f docker-compose.production.yml up -d nginx

# =============================================================================
# Delete dummy certificate
# =============================================================================
log_info "Removing dummy certificate..."
docker-compose -f docker-compose.production.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${DOMAIN} && \
  rm -Rf /etc/letsencrypt/archive/${DOMAIN} && \
  rm -Rf /etc/letsencrypt/renewal/${DOMAIN}.conf" certbot

# =============================================================================
# Request actual certificate
# =============================================================================
log_info "Requesting Let's Encrypt certificate for ${DOMAIN}..."

# Request certificate for domain and www subdomain
docker-compose -f docker-compose.production.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email ${EMAIL} \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    -d api.${DOMAIN} \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal" certbot

if [ $? -eq 0 ]; then
    log_info "SSL certificate obtained successfully ✓"
else
    log_error "Failed to obtain SSL certificate"
    exit 1
fi

# =============================================================================
# Reload nginx
# =============================================================================
log_info "Reloading nginx..."
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload

log_info "=========================================="
log_info "SSL initialization completed! 🔒"
log_info "=========================================="
log_info ""
log_info "Your SSL certificate is ready for:"
log_info "  - ${DOMAIN}"
log_info "  - www.${DOMAIN}"
log_info "  - api.${DOMAIN}"
log_info ""
log_info "Certificate will auto-renew via certbot service"
