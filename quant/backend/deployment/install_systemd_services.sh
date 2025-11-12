#!/bin/bash
# Install systemd services for Celery workers

# Exit on error
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installing Celery Systemd Services${NC}"
echo "===================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   echo "Use: sudo ./install_systemd_services.sh"
   exit 1
fi

# Create required directories
echo "Creating directories..."
mkdir -p /var/run/celery
mkdir -p /var/log/celery
chown quant:www-data /var/run/celery
chown quant:www-data /var/log/celery
echo -e "${GREEN}✓ Directories created${NC}"

# Copy service files
echo "Installing service files..."
cp deployment/systemd/celery-worker.service /etc/systemd/system/
cp deployment/systemd/celery-beat.service /etc/systemd/system/
cp deployment/systemd/celery-flower.service /etc/systemd/system/
echo -e "${GREEN}✓ Service files installed${NC}"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd reloaded${NC}"

# Enable services
echo "Enabling services..."
systemctl enable celery-worker.service
systemctl enable celery-beat.service
systemctl enable celery-flower.service
echo -e "${GREEN}✓ Services enabled${NC}"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To start the services:"
echo "  sudo systemctl start celery-worker"
echo "  sudo systemctl start celery-beat"
echo "  sudo systemctl start celery-flower"
echo ""
echo "To check status:"
echo "  sudo systemctl status celery-worker"
echo "  sudo systemctl status celery-beat"
echo "  sudo systemctl status celery-flower"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u celery-worker -f"
echo "  sudo journalctl -u celery-beat -f"
echo "  tail -f /var/log/celery/worker.log"
echo ""
echo "Flower monitoring dashboard will be available at:"
echo "  http://localhost:5555/flower"
