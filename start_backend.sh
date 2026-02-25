#!/bin/bash

# Start Backend Server Script
# This script sets up and runs the Quant Analytics Platform backend

set -e

echo "=========================================="
echo "Starting Quant Analytics Platform Backend"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to backend directory
cd quant/backend

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if docker ps | grep -q quant-postgres; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo "Starting PostgreSQL..."
    docker start quant-postgres 2>/dev/null || {
        echo -e "${RED}❌ PostgreSQL container not found${NC}"
        echo "Creating new PostgreSQL container..."
        docker run -d --name quant-postgres \
            -e POSTGRES_USER=quant_user \
            -e POSTGRES_PASSWORD=quant_password \
            -e POSTGRES_DB=quant_db \
            -p 5432:5432 \
            postgres:15
        sleep 5
    }
    echo -e "${GREEN}✅ PostgreSQL started${NC}"
fi

# Check if Redis is running
echo -e "${YELLOW}Checking Redis...${NC}"
if docker ps | grep -q redis; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not running. Some features may be limited.${NC}"
fi

# Set environment variables
echo -e "${YELLOW}Setting environment variables...${NC}"
export ENVIRONMENT=${ENVIRONMENT:-development}
export DEBUG=${DEBUG:-true}
export PROJECT_NAME="Quant Analytics Platform"
export VERSION="1.0.0"
export API_V1_STR="/api/v1"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="30"
export REFRESH_TOKEN_EXPIRE_DAYS="7"
export BACKEND_CORS_ORIGINS='["http://localhost:3000","http://localhost:8000"]'

# Use override if not using pip
echo -e "${YELLOW}Starting server with Python directly...${NC}"
echo ""

# Create a simple startup Python script
cat > start_server.py << 'EOF'
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Add current directory to path
sys.path.insert(0, '.')

print("Loading application...")

try:
    # Try to import and run with uvicorn
    import uvicorn
    from app.main import app
    
    print("✅ Application loaded successfully")
    print("")
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/v1/docs")
    print("Press CTRL+C to stop")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("")
    print("Please install dependencies:")
    print("  pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings")
    print("  pip install python-jose passlib python-multipart redis psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
EOF

# Try to run with Python
python3 start_server.py || {
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Server failed to start${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Install dependencies manually:"
    echo "   pip install --break-system-packages fastapi uvicorn sqlalchemy pydantic"
    echo ""
    echo "2. Or use Docker instead:"
    echo "   docker-compose up"
    echo ""
    echo "3. Or create a virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo "   uvicorn app.main:app --reload"
    exit 1
}