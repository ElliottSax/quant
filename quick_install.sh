#!/bin/bash
# Quick Installation Script for Quant Project Dependencies

set -e  # Exit on error

echo "=========================================="
echo "Quant Project - Quick Dependency Install"
echo "=========================================="
echo ""

# Check if running in WSL/Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✓ Linux/WSL detected"
else
    echo "⚠ This script is designed for Linux/WSL"
    echo "  Modify for your OS if needed"
fi

echo ""
echo "Choose installation method:"
echo "  1) Create new virtual environment (RECOMMENDED)"
echo "  2) System-wide install (--break-system-packages)"
echo "  3) Exit"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "Creating virtual environment..."
        cd /mnt/e/projects/quant/quant/backend

        # Create venv
        python3 -m venv venv_quant
        echo "✓ Virtual environment created"

        # Activate
        source venv_quant/bin/activate
        echo "✓ Virtual environment activated"

        # Upgrade pip
        pip install --upgrade pip
        echo "✓ pip upgraded"

        # Install dependencies
        echo ""
        echo "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
        echo "✓ All dependencies installed"

        # Verify
        echo ""
        echo "Running verification..."
        python3 verify_deployment.py

        echo ""
        echo "=========================================="
        echo "✅ Installation Complete!"
        echo "=========================================="
        echo ""
        echo "To use the virtual environment:"
        echo "  cd /mnt/e/projects/quant/quant/backend"
        echo "  source venv_quant/bin/activate"
        echo ""
        echo "Then run:"
        echo "  alembic upgrade head"
        echo "  uvicorn app.main:app --reload"
        ;;

    2)
        echo ""
        echo "Installing pandas-ta system-wide..."
        pip install pandas-ta --break-system-packages
        echo "✓ pandas-ta installed"

        echo ""
        read -p "Install optional providers? (y/n): " install_optional
        if [[ $install_optional == "y" ]]; then
            echo "Installing optional providers..."
            pip install alpha-vantage twelvedata finnhub-python --break-system-packages
            echo "✓ Optional providers installed"
        fi

        echo ""
        echo "Running verification..."
        cd /mnt/e/projects/quant/quant/backend
        python3 verify_deployment.py

        echo ""
        echo "=========================================="
        echo "✅ Installation Complete!"
        echo "=========================================="
        echo ""
        echo "Next steps:"
        echo "  cd /mnt/e/projects/quant/quant/backend"
        echo "  alembic upgrade head"
        echo "  uvicorn app.main:app --reload"
        ;;

    3)
        echo "Installation cancelled."
        exit 0
        ;;

    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
